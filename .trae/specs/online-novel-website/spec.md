# 在线小说阅读网站 Spec

## Why
构建一个高性能、全自动化的在线小说阅读平台，支持多书源自动采集、智能推荐、全文搜索，并提供极致的毛玻璃 UI/UX 阅读体验。系统需在 Windows 实验室环境中通过一键脚本完成全部部署。

## What Changes
- 新增完整的四语言全栈架构（Python/FastAPI、Go/gRPC、Rust/PyO3、Next.js/TypeScript）
- 新增自动化爬虫调度与内容去重系统
- 新增毛玻璃风格的前端 UI 设计体系
- 新增一键部署脚本与 Docker Compose 编排
- 新增完整的 CI/CD、测试、监控与压力测试体系

## Impact
- 影响规格：全新增系统
- 涉及代码：后端服务、爬虫微服务、前端应用、数据库迁移、Docker 配置、CI/CD 流程

## ADDED Requirements

### Requirement: 项目结构
系统 SHALL 采用以下目录结构：

```
/workspace/
├── docker-compose.yml          # 统一服务编排
├── start-lab.bat               # Windows 一键启动脚本
├── .github/workflows/ci.yml    # GitHub Actions CI/CD
├── backend/                    # Python FastAPI 后端
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── api/                # API 路由
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic 模式
│   │   ├── services/           # 业务逻辑
│   │   ├── core/               # 配置、安全
│   │   └── db/                 # 数据库连接、迁移
│   └── tests/                  # pytest 测试
├── crawler/                    # Go 爬虫微服务
│   ├── Dockerfile
│   ├── go.mod
│   ├── main.go
│   ├── proto/                  # gRPC 定义
│   ├── pkg/
│   │   ├── engine/             # 协程引擎
│   │   ├── scheduler/          # 任务调度
│   │   ├── dedup/              # SimHash 去重
│   │   ├── proxy/              # 代理池
│   │   └── parser/             # 规则解析
│   └── sources/                # 爬虫规则 JSON
├── compressor/                 # Rust PyO3 压缩扩展
│   ├── Cargo.toml
│   ├── pyproject.toml
│   └── src/
│       └── lib.rs
├── frontend/                   # Next.js 15 前端
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── app/                # App Router 页面
│   │   ├── components/         # 组件库
│   │   ├── lib/                # 工具函数
│   │   ├── styles/             # 全局样式
│   │   └── types/              # TypeScript 类型
│   └── tests/                  # Jest 测试
├── books/                      # 小说本地存储（爬虫输出）
│   └── {小说名}/               # 每本小说一个文件夹
│       ├── 第001章_标题.txt     # 每章节一个 txt 文件
│       ├── 第002章_标题.txt
│       └── ...
├── nginx/                      # Nginx 配置
│   └── nginx.conf
├── grafana/                    # Grafana 仪表盘
│   └── dashboards/
└── reports/                    # 测试报告输出
```

### Requirement: 后端架构
后端 SHALL 使用 FastAPI 框架提供以下能力：

- **用户管理**：注册、登录、JWT 认证
- **书籍服务**：列表、详情、分类、推荐
- **章节服务**：内容获取（含 Rust 压缩解压）、阅读进度
- **搜索服务**：Elasticsearch 全文检索
- **爬虫协调**：通过 gRPC 与 Go 爬虫通信
- **API 性能**：P99 延迟 < 200ms（5000 并发）

#### Scenario: 章节阅读 API
- **WHEN** 用户请求章节内容
- **THEN** 返回解压后的文本，P99 延迟 < 200ms

### Requirement: 爬虫引擎（Go 微服务）
爬虫 SHALL 实现以下能力：

- **核心流程**：
  1. 解析小说详情页，自动获取完整目录列表
  2. 自动排除垃圾 URL（广告页、重复页、无效链接等）
  3. 对章节 URL 进行自然排序（按章节序号）
  4. 逐章抓取内容，每章节生成一个 txt 文件
  5. txt 文件存入 `books/{小说名}/` 文件夹，文件名格式：`第{序号}章_{标题}.txt`
  6. 抓取完成后自动通知 Python 后端加载新内容
- **多核利用**：启动时检测 CPU 核心数，每个逻辑处理器绑定独立协程池
- **线程绑定**：使用 `runtime.LockOSThread` 将工作协程绑定到 OS 线程
- **规则热加载**：启动加载 `sources/*.json`，使用 fsnotify 监控目录变化
- **增量采集**：基于章节哈希判断新增/修改，跳过重复内容
- **SimHash 去重**：计算内容 SimHash 指纹，汉明距离 < 3 视为重复
- **防封策略**：
  - 代理 IP 池自动健康检查（每 60 秒）
  - User-Agent 库远程更新（每 24 小时）
  - 请求间隔随机化（500ms-3000ms）
  - 指数退避重试（最多 5 次）

#### Scenario: 爬虫规则热更新
- **WHEN** 修改 `sources/` 目录下的 JSON 规则文件
- **THEN** 爬虫自动加载新规则，无需重启

#### Scenario: 章节文件存储
- **WHEN** 爬虫完成一个章节的抓取
- **THEN** 在 `books/{小说名}/` 目录下生成 `第{序号}章_{标题}.txt` 文件

#### Scenario: 自动加载
- **WHEN** `books/` 目录下有新的小说文件夹或新章节 txt 文件
- **THEN** Python 后端自动检测并加载到数据库中

### Requirement: 文本压缩扩展（Rust/PyO3）
Rust 扩展 SHALL 提供：

- `compress(data: bytes) -> bytes`：gzip 压缩
- `decompress(data: bytes) -> bytes`：零拷贝解压
- 使用 `mimalloc` 作为全局分配器
- 编译为 Python 原生模块，支持 Python 3.11+

### Requirement: 数据库设计
PostgreSQL SHALL 包含以下表结构：

**novels 表**：
- id (UUID, PK)
- title (VARCHAR(200), NOT NULL)
- author (VARCHAR(100))
- cover_url (TEXT)
- category (VARCHAR(50))
- status (ENUM: ongoing, completed, hiatus)
- total_words (BIGINT)
- description (TEXT)
- rating (DECIMAL(3,1))
- source_id (VARCHAR(50))
- source_novel_id (VARCHAR(100))
- created_at, updated_at

**chapters 表**（HASH 分区，8 个分区）：
- id (UUID, PK)
- novel_id (UUID, FK -> novels.id)
- title (VARCHAR(200))
- chapter_index (INTEGER)
- content (BYTEA) -- gzip 压缩后存储
- content_hash (VARCHAR(64), UNIQUE)
- simhash (BIGINT)
- word_count (INTEGER)
- created_at

**reading_progress 表**：
- id (UUID, PK)
- user_id (UUID, FK -> users.id)
- novel_id (UUID, FK -> novels.id)
- chapter_id (UUID, FK -> chapters.id)
- progress_percent (DECIMAL(5,2))
- last_read_at

**archived_chapters 表**：
- 结构与 chapters 相同，用于存储完本超过 1 年的小说章节

#### Scenario: 章节分区
- **WHEN** 插入新章节
- **THEN** 根据 novel_id 的 HASH 值自动路由到对应分区

### Requirement: 前端毛玻璃设计体系
前端 SHALL 遵循以下 UI 规范：

**全局样式定义**：
- 毛玻璃面板背景：
  - 浅色主题：`rgba(255,255,255,0.15)`
  - 深色主题：`rgba(20,20,30,0.45)`
- 必须应用：`backdrop-filter: blur(16px) saturate(180%)`
- 浏览器回退：`-webkit-backdrop-filter` + 纯色半透明降级
- 边框：`1px solid rgba(255,255,255,0.25)`
- 圆角：`1.25rem`（20px）
- 阴影：多层柔和阴影，悬停加深
- 背景：渐变色叠加固定纹理图片
- 移动端降级：纯色半透明，移除 backdrop-filter

**布局结构**：
- 顶部固定导航栏：高度 64px，毛玻璃效果，z-index: 50
- 左侧边栏：宽度 240px，可折叠，毛玻璃面板
- 主内容区：填充剩余宽度
- 阅读器页：隐藏导航和侧边栏，底部固定播放栏 56px

**组件规范**：
- 所有输入框、按钮、下拉菜单继承毛玻璃样式
- 按钮提供 `glass` 变体
- 卡片悬停时阴影加深并微缩放（transform: scale(1.02)）

### Requirement: 前端页面
前端 SHALL 包含以下页面：

**首页 (`/`)**：
- Hero 区域：大幅毛玻璃卡片，推荐语
- 推荐书籍：网格布局，毛玻璃书封卡片
- 侧边排行榜（可选）：毛玻璃面板

**书籍详情页 (`/novel/[id]`)**：
- 顶部：大尺寸毛玻璃信息卡片（封面+元数据）
- 中部：章节列表，毛玻璃分隔线
- 底部：评论区毛玻璃输入区域

**阅读器页 (`/read/[chapter_id]`)**：
- 居中毛玻璃大卡片，max-width: 800px
- 左右悬浮透明圆形毛玻璃翻页按钮
- 支持夜间模式切换
- 虚拟列表技术，首屏渲染 < 1.5s

**书架/用户中心 (`/user/*`)**：
- 收藏网格视图
- 历史时间线
- 设置模态框

### Requirement: 中间件配置
Docker Compose SHALL 包含以下服务：

- **PostgreSQL**：端口 5432，预配置连接池 (pgbouncer)
- **Redis**：端口 6379，用于缓存与 Session
- **Elasticsearch**：端口 9200，全文搜索索引
- **Nginx**：端口 80，反向代理与静态资源
- **Grafana**：端口 3000，监控仪表盘
- **Prometheus**：端口 9090，指标采集

### Requirement: 自动化部署
系统 SHALL 提供：

- `docker-compose.yml`：定义所有服务，包含健康检查
- `start-lab.bat`：Windows 批处理脚本，执行 `docker compose up -d --build`
- 所有服务 90 秒内健康就绪
- 自动启动示例书源数据采集

### Requirement: 测试与质量
- **Python 测试**：pytest，覆盖率 >= 80%
- **Go 测试**：go test，覆盖率 >= 80%
- **前端测试**：Jest，覆盖率 >= 80%
- **压力测试**：k6 脚本，5000 并发用户，生成 HTML 报告
- 测试报告输出至 `reports/` 目录

### Requirement: CI/CD 工作流
GitHub Actions SHALL 实现：

- 代码推送触发
- 运行全部测试（Python/Go/Frontend）
- 构建 Go 二进制与 Rust 扩展
- 构建 Docker 镜像并推送至本地 Registry
- 触发实验室环境更新

### Requirement: Grafana 监控仪表盘
Grafana SHALL 预配置以下面板：

- 爬虫 QPS 实时曲线
- API 延迟分布（P50/P95/P99）
- CPU 各核心占用率
- Redis 缓存命中率
- PostgreSQL 连接数
- Elasticsearch 索引状态

仪表盘配置以 JSON 文件预置，启动即可用。

## MODIFIED Requirements
无（全新系统）

## REMOVED Requirements
无（全新系统）
