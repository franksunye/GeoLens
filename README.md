# 🌍 GEO Insight - AI搜索可见性优化平台

> 帮助品牌监测与优化其在生成式AI平台（ChatGPT、Gemini、Perplexity）中的曝光表现

## 🎯 产品概述

GEO Insight 是一款专为AI时代设计的品牌可见性监测与优化SaaS平台。随着ChatGPT、Gemini等AI搜索引擎的普及，传统SEO已无法覆盖AI搜索场景。我们的产品帮助企业了解并优化其在AI平台中的表现。

### 核心功能
- 🔍 **AI引用检测**: 监测品牌在AI平台中的提及情况
- 📊 **GEO可见性评分**: 评估网站内容的AI友好度
- 💡 **智能优化建议**: 生成针对AI优化的内容建议
- 📈 **数据分析报告**: 提供详细的可见性分析报告

## 🚀 快速开始

### 🏗️ 开发策略：后端优先

本项目采用**后端优先**的开发策略，确保核心业务逻辑的稳定性和可测试性。

### Phase 1: 后端开发 (当前阶段)

#### 环境要求
- Python 3.11+
- PostgreSQL 14+
- Redis (可选，用于缓存和队列)

#### 后端安装步骤
```bash
# 克隆项目
git clone https://github.com/franksunye/GeoLens.git
cd GeoLens

# 设置后端环境
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库等信息

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --port 8000

# 访问API文档: http://localhost:8000/docs
```

#### 运行后端测试
```bash
# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Phase 2: 前端开发 (后端完成后)

前端开发将在后端API完全稳定并通过所有测试后开始。

## 📚 文档

- [📋 产品待办清单](docs/00_BACKLOG.md) - Sprint规划和功能优先级
- [📝 版本变更记录](docs/01_CHANGELOG.md) - 版本历史和发布计划
- [🏗️ 系统架构设计](docs/10_ARCHITECTURE.md) - 技术架构和部署方案
- [🗄️ 数据库设计](docs/11_DATABASE.md) - 数据模型和安全策略
- [🔌 API接口文档](docs/20_API.md) - RESTful API规范
- [🛠️ 开发指南](docs/30_DEVELOPMENT.md) - 开发环境和编码规范
- [🧪 测试策略](docs/31_TESTING.md) - 测试框架和质量保证

## 🛠️ 技术栈

### 🔥 Phase 1: 后端技术栈 (优先开发)
- **框架**: FastAPI + Python 3.11+
- **数据库**: PostgreSQL + Supabase
- **ORM**: SQLAlchemy + Alembic
- **认证**: JWT + Supabase Auth
- **缓存**: Redis
- **队列**: Celery + Redis
- **AI集成**: OpenAI GPT-4 API
- **测试**: pytest + pytest-cov
- **文档**: OpenAPI (Swagger) 自动生成
- **部署**: Railway / Docker

### 📋 Phase 2: 前端技术栈 (后续开发)
- **框架**: Next.js 14 + TypeScript
- **样式**: Tailwind CSS
- **状态管理**: Zustand + React Query
- **图表**: Recharts
- **测试**: Jest + React Testing Library
- **部署**: Vercel

### 🔧 开发工具
- **API测试**: Postman + 自动化测试套件
- **代码质量**: Black + isort + flake8
- **CI/CD**: GitHub Actions
- **监控**: Sentry + 自定义日志
- **文档**: 自动生成API文档

## 🗺️ 后端优先开发路线图

### 🔥 Phase 1: 后端开发 (6-8周)

**✅ Sprint 1 (Week 1-2): 基础架构 - 已完成**
- [x] 项目文档建立
- [x] FastAPI项目架构搭建
- [x] 数据库设计与ORM配置
- [x] 用户认证系统API
- [x] 项目管理API
- [x] 90%测试覆盖率
- [x] 完整API文档

**Sprint 2 (Week 3-4): AI检测核心**
- [ ] OpenAI/Perplexity API集成
- [ ] AI检测引擎开发
- [ ] 异步任务队列系统
- [ ] 检测结果存储与查询

**Sprint 3 (Week 5-6): 内容分析**
- [ ] 网页爬虫系统
- [ ] 内容分析引擎
- [ ] GEO评分算法
- [ ] 评分历史管理

**Sprint 4 (Week 7-8): 完善与优化**
- [ ] AI优化建议引擎
- [ ] 完整API测试套件
- [ ] 性能优化与安全加固
- [ ] API文档完善

### 📋 Phase 2: 前端开发 (3-4周)

**Sprint 5 (Week 9-10): 基础界面**
- [ ] React项目搭建
- [ ] 用户认证界面
- [ ] 项目管理界面
- [ ] API集成与状态管理

**Sprint 6 (Week 11-12): 功能界面**
- [ ] 检测结果展示
- [ ] 评分可视化
- [ ] 优化建议界面
- [ ] 端到端测试

### 🚀 v1.0 正式版 (Week 13-14)
- [ ] 生产环境部署
- [ ] 用户测试与反馈
- [ ] 性能监控与优化
- [ ] 正式版发布

## 🤝 贡献指南

我们欢迎社区贡献！当前专注于**后端开发**，请查看 [开发指南](docs/30_DEVELOPMENT.md) 了解详细流程。

### 当前贡献重点 (Phase 1)
- 🔥 **后端API开发**: FastAPI端点实现
- 🧪 **测试编写**: 单元测试和集成测试
- 🤖 **AI集成**: OpenAI/Perplexity API集成
- 📊 **算法优化**: GEO评分和检测算法

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/backend-auth`)
3. 编写代码和测试 (确保测试覆盖率 ≥ 90%)
4. 运行测试套件 (`pytest --cov=app`)
5. 提交更改 (`git commit -m 'feat(auth): add user registration API'`)
6. 推送分支 (`git push origin feature/backend-auth`)
7. 创建 Pull Request

### 代码质量要求
- ✅ 所有新代码必须有对应测试
- ✅ 测试覆盖率不低于90%
- ✅ 通过所有CI检查
- ✅ 遵循代码规范 (Black + isort + flake8)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目维护者**: [Ye Sun](https://github.com/franksunye)
- **邮箱**: franksunye@hotmail.com
- **项目地址**: https://github.com/franksunye/GeoLens

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！
