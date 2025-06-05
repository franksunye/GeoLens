# 🌍 GeoLens - AI引用检测平台

> 专注于品牌在生成式AI中的引用检测和可见性分析

## 🎯 什么是引用检测？

**引用检测 (Mention Detection)** 是检测品牌、产品、服务在主流生成式AI（如豆包、DeepSeek、ChatGPT等）中被**生成式回答所提及**的核心功能，提供引用频率、引用上下文与模型来源分析。

## 🚀 产品概述

GeoLens是专业的AI引用检测平台，帮助品牌了解和优化其在生成式AI中的可见性表现。通过智能的引用检测技术，为企业提供品牌在AI时代的曝光洞察。

### 🎯 核心功能
- 🔍 **引用检测**: 检测品牌在多个AI模型中的被提及情况
- 📊 **引用频率分析**: 统计品牌在不同模型中的引用频率和趋势
- 💬 **上下文分析**: 分析品牌被提及时的上下文和推荐场景
- 🤖 **多模型支持**: 支持豆包、DeepSeek、ChatGPT等主流AI模型
- 📈 **竞品对比**: 对比分析多个品牌的AI可见性表现
- 💡 **优化建议**: 基于检测结果提供品牌曝光优化建议

## 🌐 使用场景

| 场景 | 描述 |
|------|------|
| **品牌曝光扫描** | 检测某品牌在AI模型中的被提及情况 |
| **竞品对比分析** | 输入多个品牌，输出各自被提及概率与上下文 |
| **Prompt反演优化** | 查看某类问题下哪些品牌会被推荐，从而优化内容定位 |
| **客户诊断报告** | 为企业客户生成品牌AI可见性诊断分析报告 |

## 👥 目标用户

- **SaaS品牌主** - 了解产品在AI推荐中的表现
- **市场营销人员** - 监控品牌AI可见性和竞品表现
- **品牌运营/PR团队** - 优化品牌在AI回答中的曝光
- **竞品分析师** - 分析行业品牌在AI中的竞争格局
- **AI优化顾问** - 为客户提供专业的AI可见性咨询

## 🚀 快速开始

### 🏗️ 开发策略：后端优先

本项目采用**后端优先**的开发策略，确保核心业务逻辑的稳定性和可测试性。

### Phase 1: 后端开发 (当前阶段)

#### 环境要求
- Python 3.11+
- SQLite (开发环境，自动创建)
- PostgreSQL 14+ (生产环境)
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
# 编辑 .env 文件配置AI API密钥等信息

# 运行数据库迁移 (自动创建SQLite数据库)
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
- **数据库**: SQLite (开发) + PostgreSQL (生产) + Supabase
- **ORM**: SQLAlchemy + Alembic + aiosqlite
- **认证**: JWT + Supabase Auth
- **缓存**: Redis
- **队列**: Celery + Redis
- **AI集成**: OpenAI GPT-4 API, 豆包API, DeepSeek API
- **引用检测**: 多模型并行检测、实体识别、上下文分析
- **数据分析**: 引用频率统计、竞品对比、趋势分析
- **数据持久化**: Repository模式 + 异步数据库操作
- **测试**: pytest + pytest-asyncio (100% 数据库测试覆盖率)
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

**✅ Sprint 2 (Week 3-4): AI服务集成 - 已完成**
- [x] 豆包(火山引擎) API集成
- [x] DeepSeek API集成
- [x] AI服务抽象层设计
- [x] AI聊天和品牌分析API
- [x] 流式响应支持
- [x] 85%测试覆盖率
- [x] 可扩展AI架构

**✅ Sprint 3 (Week 5-6): 引用检测引擎 - 已完成**
- [x] 内容输入和处理系统 (支持文本、URL、文档输入)
- [x] 多模型引用检测 (支持豆包、DeepSeek、ChatGPT)
- [x] 实体识别和品牌提及检测 (EntityExtractor - 准确率100%)
- [x] 引用频率分析和上下文提取
- [x] 100% 测试覆盖率，49个测试用例全部通过

**✅ Sprint 4 (Week 7-8): SQLite本地持久化 - 已完成**
- [x] SQLite数据库集成和异步操作
- [x] Repository模式数据访问层
- [x] 引用检测历史记录持久化存储
- [x] Prompt模板库管理
- [x] 统计分析和竞品对比功能
- [x] 数据库测试环境完善 (7个专项测试100%通过)

**Sprint 5 (Week 9-10): 云数据库迁移与生产就绪**
- [ ] Supabase云数据库迁移 (SQLite → PostgreSQL)
- [ ] 生产环境优化和部署
- [ ] 前端项目搭建 (React + TypeScript)
- [ ] 基础用户界面开发

### 📋 Phase 2: 前端开发 (3-4周)

**Sprint 6 (Week 11-12): 用户体验与功能增强**
- [ ] 引用检测结果展示界面
- [ ] 数据可视化和图表集成
- [ ] 用户交互优化和动画效果
- [ ] 批量检测和导出功能
- [ ] 端到端测试和性能优化

### 🚀 v1.0 正式版 (Week 13-14)
- [ ] 生产环境部署
- [ ] 用户测试与反馈
- [ ] 性能监控与优化
- [ ] 正式版发布

## 🤝 贡献指南

我们欢迎社区贡献！当前专注于**后端开发**，请查看 [开发指南](docs/30_DEVELOPMENT.md) 了解详细流程。

### 当前贡献重点 (Phase 1)
- 🔥 **引用检测API**: 多模型引用检测端点实现
- 🧪 **测试编写**: 引用检测功能的单元测试和集成测试
- 🤖 **AI模型集成**: 豆包、DeepSeek等AI平台API集成
- 📊 **检测算法优化**: 实体识别和引用频率分析算法

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
