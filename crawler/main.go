package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"os/signal"
	"runtime"
	"syscall"

	"novel-crawler/pkg/dedup"
	"novel-crawler/pkg/engine"
	"novel-crawler/pkg/fetcher"
	"novel-crawler/pkg/parser"
	"novel-crawler/pkg/proxy"
	"novel-crawler/pkg/scheduler"
	"novel-crawler/pkg/storage"
	pb "novel-crawler/proto"

	"github.com/fsnotify/fsnotify"
	"go.uber.org/zap"
	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedCrawlerServiceServer
	engine    *engine.Engine
	scheduler *scheduler.Scheduler
	fetcher   *fetcher.Fetcher
	logger    *zap.Logger
	booksDir  string
	sourcesDir string
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func main() {
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	port := getEnv("PORT", "50051")
	booksDir := getEnv("BOOKS_DIR", "/app/books")
	sourcesDir := getEnv("SOURCES_DIR", "/app/sources")

	logger.Info("启动小说爬虫微服务",
		zap.String("port", port),
		zap.String("books_dir", booksDir),
		zap.String("sources_dir", sourcesDir),
		zap.Int("cpu_cores", runtime.NumCPU()),
	)

	if err := os.MkdirAll(booksDir, 0755); err != nil {
		logger.Fatal("创建书籍目录失败", zap.Error(err))
	}
	if err := os.MkdirAll(sourcesDir, 0755); err != nil {
		logger.Fatal("创建书源目录失败", zap.Error(err))
	}

	proxyPool := proxy.NewProxyPool(logger)
	go proxyPool.HealthCheck()

	f := fetcher.NewFetcher(proxyPool, logger)
	go f.UpdateUserAgents()

	crawlHandler := func(task engine.CrawlTask) engine.TaskResult {
		return handleCrawlTask(task, f, booksDir, logger)
	}

	eng := engine.NewEngine(crawlHandler, logger)
	eng.Start()

	sched := scheduler.NewScheduler(eng, f, booksDir, logger)

	rules, err := parser.LoadRules(sourcesDir)
	if err != nil {
		logger.Warn("加载书源规则失败", zap.Error(err))
		rules = make(map[string]*parser.SourceRule)
	}
	eng.UpdateRules(rules)

	for id, rule := range rules {
		sched.AddSource(id, rule.CrawlIntervalSeconds)
	}

	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		logger.Fatal("创建文件监控失败", zap.Error(err))
	}
	defer watcher.Close()

	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				if event.Has(fsnotify.Create) || event.Has(fsnotify.Write) || event.Has(fsnotify.Remove) {
					logger.Info("检测到书源目录变化", zap.String("event", event.String()))
					reloadRules(eng, sched, sourcesDir, logger)
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				logger.Error("文件监控错误", zap.Error(err))
			}
		}
	}()

	if err := watcher.Add(sourcesDir); err != nil {
		logger.Fatal("监控书源目录失败", zap.Error(err))
	}

	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		logger.Fatal("监听端口失败", zap.Error(err))
	}

	grpcServer := grpc.NewServer()
	s := &server{
		engine:     eng,
		scheduler:  sched,
		fetcher:    f,
		logger:     logger,
		booksDir:   booksDir,
		sourcesDir: sourcesDir,
	}
	pb.RegisterCrawlerServiceServer(grpcServer, s)

	go func() {
		logger.Info("gRPC服务启动", zap.String("port", port))
		if err := grpcServer.Serve(lis); err != nil {
			logger.Fatal("gRPC服务启动失败", zap.Error(err))
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("正在优雅关闭...")

	grpcServer.GracefulStop()
	sched.Stop()
	eng.Stop()
	f.Stop()
	proxyPool.Stop()

	logger.Info("服务已关闭")
}

func handleCrawlTask(task engine.CrawlTask, f *fetcher.Fetcher, booksDir string, logger *zap.Logger) engine.TaskResult {
	result := engine.TaskResult{
		SourceID: task.SourceID,
	}

	if task.SourceRule == nil {
		result.Error = fmt.Errorf("书源规则为空")
		return result
	}

	html, err := f.RetryFetch(task.NovelURL, 5)
	if err != nil {
		result.Error = fmt.Errorf("获取详情页失败: %w", err)
		return result
	}

	novelInfo, err := parser.ParseNovelDetail(html, task.SourceRule)
	if err != nil {
		result.Error = fmt.Errorf("解析详情页失败: %w", err)
		return result
	}

	chapterURLs := parser.FilterGarbageURLs(novelInfo.ChapterURLs, task.SourceRule.GarbagePatterns)
	chapterURLs = parser.SortChapterURLs(chapterURLs)

	existingChapters := storage.GetExistingChapters(booksDir, novelInfo.Title)
	existingSet := make(map[int]bool)
	for _, ch := range existingChapters {
		existingSet[ch] = true
	}

	var newCount int
	for i, chapterURL := range chapterURLs {
		chapterIndex := i + 1
		if existingSet[chapterIndex] {
			continue
		}

		chHTML, err := f.RetryFetch(chapterURL, 3)
		if err != nil {
			logger.Warn("获取章节失败", zap.String("url", chapterURL), zap.Error(err))
			continue
		}

		content, err := parser.ParseChapterContent(chHTML, task.SourceRule)
		if err != nil {
			logger.Warn("解析章节失败", zap.String("url", chapterURL), zap.Error(err))
			continue
		}

		fingerprint := dedup.SimHash(content.Content)

		indexStr := fmt.Sprintf("%d", chapterIndex)
		if err := storage.WriteChapter(booksDir, novelInfo.Title, indexStr, content.Title, content.Content); err != nil {
			logger.Warn("写入章节失败", zap.String("title", content.Title), zap.Error(err))
			continue
		}

		logger.Debug("SimHash指纹", zap.String("title", content.Title), zap.Uint64("fingerprint", fingerprint))
		newCount++
	}

	result.NovelTitle = novelInfo.Title
	result.ChaptersCount = newCount

	logger.Info("爬取任务完成",
		zap.String("novel", novelInfo.Title),
		zap.Int("total", len(chapterURLs)),
		zap.Int("new", newCount),
	)

	return result
}

func reloadRules(eng *engine.Engine, sched *scheduler.Scheduler, sourcesDir string, logger *zap.Logger) {
	rules, err := parser.LoadRules(sourcesDir)
	if err != nil {
		logger.Error("重新加载书源规则失败", zap.Error(err))
		return
	}

	oldRules := eng.GetRules()

	for id := range oldRules {
		if _, exists := rules[id]; !exists {
			sched.RemoveSource(id)
		}
	}

	eng.UpdateRules(rules)

	for id, rule := range rules {
		sched.AddSource(id, rule.CrawlIntervalSeconds)
	}

	logger.Info("书源规则已重新加载", zap.Int("count", len(rules)))
}

func (s *server) StartCrawl(ctx context.Context, req *pb.CrawlRequest) (*pb.CrawlResponse, error) {
	s.logger.Info("收到爬取请求",
		zap.String("source_id", req.SourceId),
		zap.String("novel_url", req.NovelUrl),
	)

	rules := s.engine.GetRules()
	rule, exists := rules[req.SourceId]
	if !exists {
		return &pb.CrawlResponse{
			Success: false,
			Message: fmt.Sprintf("书源不存在: %s", req.SourceId),
		}, nil
	}

	task := engine.CrawlTask{
		SourceID:   req.SourceId,
		NovelURL:   req.NovelUrl,
		SourceRule: rule,
	}

	s.engine.Submit(task)

	return &pb.CrawlResponse{
		Success:       true,
		Message:       "任务已提交",
		ChaptersCount: 0,
	}, nil
}

func (s *server) GetStatus(ctx context.Context, req *pb.StatusRequest) (*pb.StatusResponse, error) {
	return &pb.StatusResponse{
		Running:      true,
		ChaptersCrawled: 0,
		CurrentNovel: "",
	}, nil
}

func (s *server) ListSources(ctx context.Context, req *pb.Empty) (*pb.SourceList, error) {
	rules := s.engine.GetRules()
	var sources []*pb.SourceInfo

	for id, rule := range rules {
		sources = append(sources, &pb.SourceInfo{
			Id:      id,
			Name:    rule.Name,
			BaseUrl: rule.BaseURL,
		})
	}

	return &pb.SourceList{Sources: sources}, nil
}
