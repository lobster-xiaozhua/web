# Tasks

- [x] Task 1: 创建项目基础结构与 Docker Compose 配置
  - [x] SubTask 1.1: 创建完整的目录结构（backend/, crawler/, compressor/, frontend/, nginx/, grafana/）
  - [x] SubTask 1.2: 编写 docker-compose.yml，包含所有服务（PostgreSQL, Redis, Elasticsearch, Nginx, Grafana, Prometheus, 后端, 爬虫, 前端）
  - [x] SubTask 1.3: 编写 start-lab.bat Windows 启动脚本
  - [x] SubTask 1.4: 为每个服务编写 Dockerfile 与健康检查

- [x] Task 2: 实现 Rust PyO3 压缩扩展
  - [x] SubTask 2.1: 初始化 Rust 项目，配置 Cargo.toml 与 pyproject.toml
  - [x] SubTask 2.2: 实现 compress/decompress 函数（零拷贝解压）
  - [x] SubTask 2.3: 配置 mimalloc 全局分配器
  - [x] SubTask 2.4: 编写 Rust 侧单元测试
  - [x] SubTask 2.5: 编写 Python 侧集成测试

- [x] Task 3: 实现 Python FastAPI 后端核心
  - [x] SubTask 3.1: 创建 FastAPI 应用骨架与配置管理
  - [x] SubTask 3.2: 实现 SQLAlchemy 模型（novels, chapters, reading_progress, archived_chapters）
  - [x] SubTask 3.3: 实现 chapters 表 HASH 分区迁移（8 个分区）
  - [x] SubTask 3.4: 实现 JWT 认证与用户管理 API
  - [x] SubTask 3.5: 实现书籍列表/详情/分类 API
  - [x] SubTask 3.6: 实现章节内容 API（集成 Rust 压缩解压）
  - [x] SubTask 3.7: 实现 Elasticsearch 搜索 API
  - [x] SubTask 3.8: 实现 gRPC 客户端与爬虫协调服务
  - [x] SubTask 3.9: 实现阅读进度 API
  - [x] SubTask 3.10: 实现 Redis 缓存层
  - [x] SubTask 3.11: 实现归档迁移定时任务（完本超 1 年自动归档）
  - [x] SubTask 3.12: 编写 pytest 测试（覆盖率 >= 80%）

- [x] Task 4: 实现 Go 爬虫微服务
  - [x] SubTask 4.1: 初始化 Go 项目，配置 gRPC 服务端
  - [x] SubTask 4.2: 实现协程池引擎（多核利用 + LockOSThread 绑定）
  - [x] SubTask 4.3: 实现 JSON 规则解析器与 fsnotify 热加载
  - [x] SubTask 4.4: 实现 SimHash 内容去重
  - [x] SubTask 4.5: 实现代理 IP 池与自动健康检查
  - [x] SubTask 4.6: 实现 User-Agent 远程更新
  - [x] SubTask 4.7: 实现请求间隔随机化与指数退避重试
  - [x] SubTask 4.8: 实现增量采集定时器
  - [x] SubTask 4.9: 编写示例爬虫规则 JSON（sources/）
  - [x] SubTask 4.10: 编写 go test 测试（覆盖率 >= 80%）

- [x] Task 5: 实现 Next.js 15 前端
  - [x] SubTask 5.1: 初始化 Next.js 15 App Router 项目
  - [x] SubTask 5.2: 配置 Tailwind CSS 与 shadcn/ui 组件库
  - [x] SubTask 5.3: 实现全局毛玻璃样式系统（CSS 变量、主题切换、移动端降级）
  - [x] SubTask 5.4: 实现布局组件（顶部导航栏、左侧边栏、主内容区）
  - [x] SubTask 5.5: 实现首页（Hero 卡片、推荐网格、排行榜面板）
  - [x] SubTask 5.6: 实现书籍详情页（信息卡片、章节列表、评论区）
  - [x] SubTask 5.7: 实现阅读器页（毛玻璃大卡片、翻页按钮、夜间模式、虚拟列表）
  - [x] SubTask 5.8: 实现书架/用户中心（收藏网格、时间线、设置模态框）
  - [x] SubTask 5.9: 实现 API 客户端层
  - [x] SubTask 5.10: 编写 Jest 测试（覆盖率 >= 80%）

- [x] Task 6: 配置 Nginx 反向代理
  - [x] SubTask 6.1: 编写 nginx.conf，配置反向代理规则
  - [x] SubTask 6.2: 配置静态资源缓存与 Gzip 压缩

- [x] Task 7: 配置 Grafana 监控仪表盘
  - [x] SubTask 7.1: 配置 Prometheus 数据源
  - [x] SubTask 7.2: 预配置仪表盘 JSON（爬虫 QPS、API 延迟、CPU 占用、缓存命中率、数据库连接数、ES 索引状态）
  - [x] SubTask 7.3: 配置后端/爬虫 Prometheus 指标暴露

- [x] Task 8: 实现 k6 压力测试
  - [x] SubTask 8.1: 编写 k6 脚本（模拟 5000 并发用户阅读与搜索）
  - [x] SubTask 8.2: 配置 HTML 报告生成
  - [x] SubTask 8.3: 验证 P99 延迟 < 200ms

- [x] Task 9: 配置 GitHub Actions CI/CD
  - [x] SubTask 9.1: 编写 ci.yml 工作流
  - [x] SubTask 9.2: 配置 Python/Go/Frontend 测试自动运行
  - [x] SubTask 9.3: 配置 Go 二进制与 Rust 扩展构建
  - [x] SubTask 9.4: 配置 Docker 镜像构建与推送

- [ ] Task 10: 集成测试与验收
  - [ ] SubTask 10.1: 运行 start-lab.bat 验证所有服务 90 秒内健康
  - [ ] SubTask 10.2: 验证自动采集示例数据
  - [ ] SubTask 10.3: 验证前端毛玻璃 UI 规范
  - [ ] SubTask 10.4: 运行全部测试并验证覆盖率 >= 80%
  - [ ] SubTask 10.5: 运行 k6 压力测试并生成报告
  - [ ] SubTask 10.6: 验证 Grafana 仪表盘数据

# Task Dependencies

- [Task 2] depends on [Task 1]（Rust 扩展需要 Docker 构建环境）
- [Task 3] depends on [Task 1, Task 2]（后端需要 Docker 与 Rust 扩展）
- [Task 4] depends on [Task 1]（爬虫需要 Docker 环境）
- [Task 5] depends on [Task 3]（前端依赖后端 API）
- [Task 6] depends on [Task 3, Task 5]（Nginx 需要后端与前端）
- [Task 7] depends on [Task 3, Task 4]（Grafana 需要指标暴露）
- [Task 8] depends on [Task 3, Task 5]（压测需要完整 API 与前端）
- [Task 9] depends on [Task 2, Task 3, Task 4, Task 5]（CI/CD 需要所有模块）
- [Task 10] depends on [Task 6, Task 7, Task 8, Task 9]（验收需要全部完成）
