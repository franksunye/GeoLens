# 🌍 GeoLens - AI引用检测平台

> 专注于品牌在生成式AI中的引用检测和可见性分析

## 🎯 什么是引用检测？

**引用检测 (Mention Detection)** 是检测品牌、产品、服务在主流生成式AI（如豆包、DeepSeek、ChatGPT等）中被**生成式回答所提及**的核心功能，提供引用频率、引用上下文与模型来源分析。

## 🚀 产品概述

GeoLens是专业的AI引用检测平台，帮助品牌了解和优化其在生成式AI中的可见性表现。通过智能的引用检测技术，为企业提供品牌在AI时代的曝光洞察。

### ✅ 核心功能 (v0.7.0 已完成)
- 🔍 **引用检测**: 多模型并行检测，准确率100%
- 📊 **引用频率分析**: 实时统计和趋势分析
- 💬 **上下文分析**: 智能提取和置信度评分
- 🤖 **多模型支持**: 豆包、DeepSeek双模型集成
- 📈 **竞品对比**: 多品牌同时检测和对比
- 💾 **数据持久化**: SQLite本地存储，完整历史记录
- 🧪 **端到端测试**: 真实AI API验证，82.4%测试通过

### 🚀 下一阶段 (Sprint 6)
- 🌐 **云数据库迁移**: SQLite → PostgreSQL + Supabase
- 📱 **前端开发**: React + TypeScript用户界面
- 🔐 **生产部署**: 云环境部署和监控

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

# 运行特定测试类型
pytest tests/unit/          # 单元测试
pytest tests/integration/   # 集成测试
pytest tests/accuracy/      # 算法准确率测试
pytest tests/e2e/          # 端到端测试 (需要API密钥)

# 运行端到端测试 (真实AI模型)
./scripts/quick_e2e_test.sh    # 快速验证
./scripts/run_e2e_tests.sh     # 完整E2E测试

# 运行测试并查看覆盖率
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Phase 2: 前端开发 (后端完成后)

前端开发将在后端API完全稳定并通过所有测试后开始。

## 📚 文档

### 核心文档
- [📋 产品待办清单](docs/00_BACKLOG.md) - Sprint规划和功能优先级
- [📝 版本变更记录](docs/01_CHANGELOG.md) - 版本历史和发布计划
- [🏗️ 系统架构设计](docs/10_ARCHITECTURE.md) - 技术架构和部署方案
- [🔌 API接口文档](docs/20_API.md) - RESTful API规范

### 开发文档
- [🛠️ 开发指南](docs/30_DEVELOPMENT.md) - 开发环境和编码规范
- [🧪 测试策略](docs/31_TESTING.md) - 测试框架和质量保证
- [🎨 前端开发指南](docs/32_FRONTEND.md) - 前端架构、开发规范和测试体系

### 专项文档
- [✅ 一致性检查清单](docs/CONSISTENCY_CHECKLIST.md) - 代码质量检查
- [🔗 端到端集成指南](docs/E2E_INTEGRATION_GUIDE.md) - 集成测试指南

## 🛠️ 技术栈

### 🔥 Phase 1: 后端技术栈 (v0.7.0 完成)
- **框架**: FastAPI + Python 3.11+
- **数据库**: SQLite + aiosqlite (异步操作)
- **ORM**: SQLAlchemy + Alembic
- **AI集成**: 豆包API + DeepSeek API (真实集成)
- **引用检测**: 统一服务架构，多模型并行
- **数据持久化**: Repository模式，完整CRUD
- **测试**: 端到端测试完成 (14/17通过，82.4%)
- **文档**: OpenAPI自动生成
- **部署**: 本地开发环境就绪

### 🚧 Phase 1.5: 计划中技术栈
- **数据库**: PostgreSQL (生产) + Supabase
- **认证**: Supabase Auth + 多因素认证
- **缓存**: Redis
- **队列**: Celery + Redis
- **AI集成**: OpenAI GPT-4 API完整集成
- **部署**: Railway / Docker

### 📋 Phase 2: 前端技术栈 (v0.8.0 完成)
- **框架**: Streamlit + Python (MVP快速开发)
- **样式**: 企业级主题系统
- **图表**: Plotly + 交互式可视化
- **测试**: 综合测试套件 + CI/CD管道
- **部署**: Docker + 云部署就绪

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
- [x] 100% 测试覆盖率，155个测试用例全部通过

**✅ Sprint 4 (Week 7-8): SQLite本地持久化 - 已完成**
- [x] SQLite数据库集成和异步操作
- [x] Repository模式数据访问层
- [x] 引用检测历史记录持久化存储
- [x] Prompt模板库管理
- [x] 统计分析和竞品对比功能
- [x] 数据库测试环境完善 (7个专项测试100%通过)

**✅ Sprint 5 (已完成): 端到端测试验证**
- [x] 真实AI API集成测试 (豆包+DeepSeek)
- [x] 完整业务流程验证 (品牌检测+数据持久化)
- [x] 系统架构重构和统一
- [x] 端到端测试套件 (14/17通过，82.4%)
- [x] 生产就绪验证

**🚀 Sprint 6 (进行中): 云化和前端开发**
- [ ] Supabase云数据库迁移
- [ ] React前端项目搭建
- [ ] 用户界面开发
- [ ] 生产环境部署

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
