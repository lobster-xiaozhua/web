# Checklist

## 基础设施与部署
- [x] docker-compose.yml 包含所有服务定义（PostgreSQL, Redis, Elasticsearch, Nginx, Grafana, Prometheus, 后端, 爬虫, 前端）
- [x] start-lab.bat 封装了 `docker compose up -d --build` 命令
- [x] 所有服务包含健康检查配置
- [ ] 执行 start-lab.bat 后所有服务在 90 秒内变为健康状态
- [ ] 系统自动开始抓取示例书源数据

## Rust PyO3 压缩扩展
- [x] compress 函数正确实现 gzip 压缩
- [x] decompress 函数正确实现零拷贝解压
- [x] 使用 mimalloc 作为全局分配器
- [x] Python 3.11+ 兼容
- [x] Rust 侧单元测试覆盖率 >= 80%
- [x] Python 侧集成测试通过

## Python FastAPI 后端
- [x] 用户注册、登录、JWT 认证 API 正常工作
- [x] 书籍列表、详情、分类 API 正常工作
- [x] 章节内容 API 集成 Rust 解压扩展
- [x] Elasticsearch 全文搜索 API 正常工作
- [x] gRPC 客户端与 Go 爬虫通信正常
- [x] 阅读进度 API 正常工作
- [x] Redis 缓存层正常工作
- [x] 归档迁移定时任务正常工作
- [ ] 章节阅读 API P99 延迟 < 200ms（5000 并发）
- [x] pytest 测试覆盖率 >= 80%

## Go 爬虫微服务
- [x] 启动时检测 CPU 核心数并绑定协程池
- [x] runtime.LockOSThread 正确绑定 OS 线程
- [x] JSON 规则自动加载与 fsnotify 热更新
- [x] SimHash 去重（汉明距离 < 3 视为重复）
- [x] 代理 IP 池自动健康检查（每 60 秒）
- [x] User-Agent 远程更新（每 24 小时）
- [x] 请求间隔随机化（500ms-3000ms）
- [x] 指数退避重试（最多 5 次）
- [x] 增量采集定时器正常工作
- [x] 示例爬虫规则 JSON 存在于 sources/ 目录
- [x] go test 测试覆盖率 >= 80%

## 数据库
- [x] novels 表结构正确
- [x] chapters 表 HASH 分区（8 个分区）正确创建
- [x] reading_progress 表结构正确
- [x] archived_chapters 归档表结构正确
- [x] 连接池配置正确
- [x] 章节内容以 gzip 压缩存储

## Next.js 15 前端
- [x] 全局毛玻璃样式系统正确配置
- [x] 浅色主题 rgba(255,255,255,0.15) 背景正确
- [x] 深色主题 rgba(20,20,30,0.45) 背景正确
- [x] backdrop-filter: blur(16px) saturate(180%) 正确应用
- [x] -webkit-backdrop-filter 浏览器回退存在
- [x] 边框 1px solid rgba(255,255,255,0.25) 正确
- [x] 圆角 1.25rem 统一应用
- [x] 多层阴影与悬停加深效果正确
- [x] 渐变色背景与纹理图片正确
- [x] 移动端降级为纯色半透明
- [x] 顶部导航栏高度 64px 固定悬浮
- [x] 左侧边栏宽度 240px 可折叠
- [x] 阅读器页隐藏导航和侧边栏
- [x] 阅读器底部播放栏高度 56px
- [x] 首页 Hero 毛玻璃卡片正确
- [x] 书籍详情页毛玻璃信息卡片正确
- [x] 阅读器页居中毛玻璃大卡片 max-width 800px
- [x] 阅读器翻页按钮为透明圆形毛玻璃
- [x] 阅读器支持夜间模式
- [x] 虚拟列表技术实现首屏渲染 < 1.5s
- [x] Jest 测试覆盖率 >= 80%

## Nginx 反向代理
- [x] nginx.conf 正确配置反向代理规则
- [x] 静态资源缓存配置正确
- [x] Gzip 压缩配置正确

## Grafana 监控
- [x] Prometheus 数据源配置正确
- [x] 仪表盘 JSON 预置且启动可用
- [x] 爬虫 QPS 实时曲线面板存在
- [x] API 延迟分布面板存在（P50/P95/P99）
- [x] CPU 各核心占用率面板存在
- [x] Redis 缓存命中率面板存在
- [x] PostgreSQL 连接数面板存在
- [x] Elasticsearch 索引状态面板存在
- [ ] 仪表盘显示实时数据

## 压力测试
- [x] k6 脚本模拟 5000 并发用户
- [x] 包含阅读操作场景
- [x] 包含搜索操作场景
- [x] HTML 报告自动生成
- [ ] P99 延迟 < 200ms 验证通过

## CI/CD
- [x] GitHub Actions ci.yml 存在
- [x] 代码推送触发测试
- [x] Python 测试自动运行
- [x] Go 测试自动运行
- [x] 前端测试自动运行
- [x] Go 二进制自动构建
- [x] Rust 扩展自动构建
- [x] Docker 镜像构建并推送

## 测试报告
- [x] reports/ 目录存在
- [ ] Python 测试报告生成
- [ ] Go 测试报告生成
- [ ] 前端测试报告生成
- [ ] k6 压力测试 HTML 报告生成

## 爬虫 books/ 目录存储
- [x] 爬虫将章节写入 books/{小说名}/ 目录
- [x] 文件名格式为 第{序号}章_{标题}.txt
- [x] 后端自动加载 books/ 目录内容
