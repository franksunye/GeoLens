# 🌍 GeoLens - 生成式引擎优化平台

> 专注于GEO (Generative Engine Optimization) - 提升品牌在生成式AI中被推荐和引用的可见性

## 🎯 什么是GEO？

**GEO (Generative Engine Optimization)** = 生成式引擎优化

GEO是一种全新的优化方式，旨在提升品牌在生成式AI（如ChatGPT、Gemini、Claude等）中被推荐、被引用的可见性。它是"SEO在AI搜索时代的替代者"，专门针对AI的理解和推荐机制进行内容优化。

## 🚀 产品概述

GeoLens是全球首个专注于GEO优化的智能平台，帮助企业在AI搜索时代保持竞争优势。当用户向AI提问时，我们确保您的品牌能够被AI优先推荐和引用。

### 🎯 核心功能
- 🤖 **GEO评分算法**: 专有的生成式引擎优化评分系统
- 🔍 **AI引用分析**: 深度分析内容在AI推荐中的表现潜力
- 📊 **内容AI友好度**: 评估内容对生成式AI的适配程度
- 💡 **GEO优化建议**: 针对AI理解机制的内容优化建议
- 📈 **可见性预测**: 预测品牌在AI回答中的出现概率

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
- **AI集成**: OpenAI GPT-4 API, 豆包API, DeepSeek API
- **内容处理**: 智能文本解析和结构化分析
- **GEO分析**: 自研GEO评分算法、内容AI友好度分析、实体提取
- **测试**: pytest + pytest-cov (87% 覆盖率)
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

**Sprint 3 (Week 5-6): GEO分析引擎** ✅ 已完成
- [x] 内容输入和处理系统 (支持文本、URL、文档输入)
- [x] GEO评分算法 (GEOScorer - 专有的生成式引擎优化评分)
- [x] 内容AI友好度分析 (ContentAnalyzer + KeywordAnalyzer)
- [x] 实体提取系统 (EntityExtractor - 品牌和技术实体识别)
- [x] 87% 测试覆盖率，47个新增测试用例

**Sprint 4 (Week 7-8): 数据持久化与高级功能**
- [ ] 数据持久化系统
- [ ] 异步任务队列系统
- [ ] 高级分析功能
- [ ] 用户界面开发
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
- 🤖 **AI集成**: 生成式AI平台API集成
- 📊 **GEO算法优化**: 生成式引擎优化评分算法

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
