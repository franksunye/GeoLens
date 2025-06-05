# 🛠️ GeoLens - 开发指南

## 📋 开发环境搭建

### 系统要求
- **Node.js**: 18.0+ (推荐使用 LTS 版本)
- **Python**: 3.11+
- **Git**: 2.30+
- **Docker**: 20.0+ (可选，用于容器化开发)

### 开发工具推荐
- **IDE**: VS Code / PyCharm / WebStorm
- **API测试**: Postman / Insomnia
- **数据库管理**: DBeaver / pgAdmin
- **版本控制**: Git + GitHub Desktop

---

## 🚀 快速开始

### 开发策略：后端优先

本项目采用**后端优先**的开发策略，确保核心业务逻辑的稳定性和可测试性。

### Phase 1: 后端开发环境搭建

#### 1. 克隆项目
```bash
git clone https://github.com/franksunye/GeoLens.git
cd GeoLens
```

#### 2. 后端环境配置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r backend/requirements.txt

# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑环境变量
nano backend/.env
```

#### 3. 数据库设置
```bash
# 当前使用SQLite本地数据库 (自动创建)
# 无需额外配置，数据库文件将自动创建在 data/ 目录

# 运行数据库迁移 (可选，数据库会自动初始化)
cd backend
alembic upgrade head

# 注意：Supabase/PostgreSQL集成计划在未来版本实现
```

#### 4. 启动后端服务
```bash
# 启动开发服务器
cd backend
uvicorn app.main:app --reload --port 8000

# 访问API文档: http://localhost:8000/docs
# 访问ReDoc文档: http://localhost:8000/redoc
```

#### 5. 运行后端测试
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

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

#### 6. 端到端测试配置 ✨ 新增
端到端测试需要真实的AI API密钥。请按以下步骤配置：

##### 创建环境配置文件
```bash
# 复制示例配置文件
cp .env.e2e.example .env.e2e

# 编辑配置文件，填入真实的API密钥
nano .env.e2e
```

##### 配置API密钥
在 `.env.e2e` 文件中设置：
```bash
# 豆包API配置
DOUBAO_API_KEY=your_doubao_api_key_here
DOUBAO_MODEL=doubao-1-5-lite-32k-250115

# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-reasoner

# 测试配置
E2E_TEST_TIMEOUT=60
E2E_MAX_CONCURRENT=3
```

##### 运行端到端测试
```bash
# 快速验证 (推荐首次使用)
./scripts/quick_e2e_test.sh

# 完整测试套件
./scripts/run_e2e_tests.sh

# 运行特定测试
pytest tests/e2e/test_real_ai_connectivity.py -v
pytest tests/e2e/test_full_mention_detection.py -v
```

##### 替代方案：环境变量
如果不想使用配置文件，也可以直接设置环境变量：
```bash
export DOUBAO_API_KEY=your_doubao_key
export DEEPSEEK_API_KEY=your_deepseek_key
./scripts/quick_e2e_test.sh
```

##### 测试覆盖情况
当前端到端测试覆盖：
- ✅ AI模型集成 (豆包 + DeepSeek)
- ✅ 引用检测核心功能
- ✅ 数据持久化
- ✅ 业务场景验证
- ⚠️ 认证授权 (计划中)
- ⚠️ 项目管理 (计划中)

详细覆盖情况请查看：`backend/E2E_COVERAGE_ANALYSIS.md`

---

## 📁 项目结构 (后端优先)

```
GeoLens/
├── backend/                  # 🔥 Phase 1: 后端应用 (优先开发)
│   ├── app/
│   │   ├── main.py          # FastAPI 应用入口
│   │   ├── api/             # API 路由模块
│   │   │   ├── v1/          # API v1 版本
│   │   │   │   ├── auth.py      # 认证相关API
│   │   │   │   ├── projects.py  # 项目管理API
│   │   │   │   ├── mentions.py  # AI检测API
│   │   │   │   ├── geo.py       # GEO评分API
│   │   │   │   └── suggestions.py # 优化建议API
│   │   ├── core/            # 核心配置
│   │   │   ├── config.py    # 应用配置
│   │   │   ├── security.py  # 安全相关
│   │   │   └── deps.py      # 依赖注入
│   │   ├── models/          # 数据模型
│   │   │   ├── user.py      # 用户模型
│   │   │   ├── project.py   # 项目模型
│   │   │   └── mention.py   # 检测记录模型
│   │   ├── schemas/         # Pydantic 模式
│   │   ├── services/        # 业务逻辑层
│   │   │   ├── auth.py      # 认证服务
│   │   │   ├── ai_detection.py # AI检测服务
│   │   │   ├── geo_scoring.py  # GEO评分服务
│   │   │   └── web_scraper.py  # 网页爬虫服务
│   │   ├── utils/           # 工具函数
│   │   └── workers/         # Celery 任务
│   ├── tests/               # 测试文件
│   │   ├── unit/            # 单元测试
│   │   ├── integration/     # 集成测试
│   │   └── conftest.py      # 测试配置
│   ├── alembic/             # 数据库迁移
│   ├── requirements.txt     # Python 依赖
│   ├── .env.example         # 环境变量模板
│   └── Dockerfile           # Docker 配置
├── frontend/                 # 📋 Phase 2: 前端应用 (后续开发)
│   ├── src/                 # (后端完成后开发)
│   └── package.json
├── docs/                     # 📚 项目文档
├── scripts/                  # 🔧 部署脚本
└── docker-compose.yml        # 🐳 Docker 配置
```

---

## 🔧 开发规范

### 代码风格

#### 前端 (TypeScript/React)
```typescript
// 使用 Prettier + ESLint
// 组件命名：PascalCase
export const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  // Hooks 在组件顶部
  const [loading, setLoading] = useState(false);
  
  // 事件处理函数：handle + 动作
  const handleSubmit = async (data: FormData) => {
    // 实现逻辑
  };
  
  return (
    <div className="project-card">
      {/* JSX 内容 */}
    </div>
  );
};
```

#### 后端 (Python/FastAPI)
```python
# 使用 Black + isort + flake8
# 类命名：PascalCase
class ProjectService:
    def __init__(self, db: Session):
        self.db = db
    
    # 方法命名：snake_case
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """创建新项目"""
        # 实现逻辑
        pass

# 函数命名：snake_case
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前用户"""
    # 实现逻辑
    pass
```

### Git 工作流

#### 分支策略
```bash
main          # 生产环境分支
├── develop   # 开发环境分支
├── feature/  # 功能开发分支
├── hotfix/   # 紧急修复分支
└── release/  # 发布准备分支
```

#### 提交规范
```bash
# 提交格式：<type>(<scope>): <description>
git commit -m "feat(auth): add user registration API"
git commit -m "fix(ui): resolve mobile responsive issue"
git commit -m "docs(api): update authentication endpoints"

# 提交类型
feat:     新功能
fix:      错误修复
docs:     文档更新
style:    代码格式调整
refactor: 代码重构
test:     测试相关
chore:    构建工具或辅助工具的变动
```

---

## 🔌 API 开发

### 路由结构
```python
# backend/app/api/v1/endpoints/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project import ProjectService

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新项目"""
    service = ProjectService(db)
    return await service.create_project(project_data, current_user.id)
```

### 数据验证
```python
# backend/app/schemas/project.py
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    domain: str
    description: Optional[str] = None
    target_keywords: List[str] = []
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 100:
            raise ValueError('项目名称长度必须在2-100字符之间')
        return v
    
    @validator('domain')
    def validate_domain(cls, v):
        # 域名格式验证
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('无效的域名格式')
        return v
```

---

## 🎨 前端开发

### 组件开发
```typescript
// frontend/src/components/ProjectCard.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Project } from '@/types/project';

interface ProjectCardProps {
  project: Project;
  onEdit?: (project: Project) => void;
  onDelete?: (projectId: string) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onEdit,
  onDelete
}) => {
  return (
    <Card className="project-card">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          {project.name}
          <Badge variant={project.isActive ? 'default' : 'secondary'}>
            {project.isActive ? '活跃' : '暂停'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-2">
          {project.domain}
        </p>
        <div className="flex gap-2">
          {project.targetKeywords.map((keyword) => (
            <Badge key={keyword} variant="outline">
              {keyword}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
```

### 状态管理 (Zustand)
```typescript
// frontend/src/store/projectStore.ts
import { create } from 'zustand';
import { Project } from '@/types/project';
import { projectApi } from '@/lib/api';

interface ProjectStore {
  projects: Project[];
  loading: boolean;
  error: string | null;
  
  fetchProjects: () => Promise<void>;
  createProject: (data: CreateProjectData) => Promise<void>;
  updateProject: (id: string, data: UpdateProjectData) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  loading: false,
  error: null,
  
  fetchProjects: async () => {
    set({ loading: true, error: null });
    try {
      const projects = await projectApi.getProjects();
      set({ projects, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  createProject: async (data) => {
    const project = await projectApi.createProject(data);
    set(state => ({
      projects: [...state.projects, project]
    }));
  }
}));
```

---

## 🧪 测试策略

### 单元测试
```python
# backend/tests/test_project_service.py
import pytest
from sqlalchemy.orm import Session
from app.services.project import ProjectService
from app.schemas.project import ProjectCreate

@pytest.fixture
def project_service(db_session: Session):
    return ProjectService(db_session)

@pytest.fixture
def sample_project_data():
    return ProjectCreate(
        name="测试项目",
        domain="example.com",
        description="这是一个测试项目"
    )

async def test_create_project(project_service, sample_project_data, test_user):
    """测试创建项目"""
    project = await project_service.create_project(
        sample_project_data, 
        test_user.id
    )
    
    assert project.name == sample_project_data.name
    assert project.domain == sample_project_data.domain
    assert project.user_id == test_user.id
```

### 集成测试
```typescript
// frontend/src/__tests__/ProjectCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProjectCard } from '@/components/ProjectCard';
import { mockProject } from '@/tests/mocks';

describe('ProjectCard', () => {
  it('renders project information correctly', () => {
    render(<ProjectCard project={mockProject} />);
    
    expect(screen.getByText(mockProject.name)).toBeInTheDocument();
    expect(screen.getByText(mockProject.domain)).toBeInTheDocument();
  });
  
  it('calls onEdit when edit button is clicked', () => {
    const onEdit = jest.fn();
    render(<ProjectCard project={mockProject} onEdit={onEdit} />);
    
    fireEvent.click(screen.getByRole('button', { name: /编辑/i }));
    expect(onEdit).toHaveBeenCalledWith(mockProject);
  });
});
```

---

## 🚀 部署流程

### 开发环境部署
```bash
# 使用 Docker Compose
docker-compose -f docker-compose.dev.yml up -d

# 或者分别启动
npm run dev          # 前端
uvicorn main:app --reload  # 后端
```

### 生产环境部署
```bash
# 构建前端
npm run build

# 构建后端镜像
docker build -t geolens-backend ./backend

# 部署到云平台
# Vercel (前端)
vercel --prod

# Railway (后端)
railway up
```

---

## 📊 性能优化

### 前端优化
- **代码分割**: 使用动态导入
- **图片优化**: Next.js Image 组件
- **缓存策略**: SWR 数据缓存
- **Bundle 分析**: webpack-bundle-analyzer

### 后端优化
- **数据库查询**: 使用索引和查询优化
- **缓存策略**: Redis 缓存热点数据
- **异步处理**: Celery 任务队列
- **连接池**: 数据库连接池管理

---

## 🔍 调试技巧

### 前端调试
```typescript
// 使用 React DevTools
// 添加调试日志
console.log('Debug:', { state, props });

// 使用断点调试
debugger;

// 性能分析
console.time('render');
// 代码执行
console.timeEnd('render');
```

### 后端调试
```python
# 使用 pdb 调试器
import pdb; pdb.set_trace()

# 日志记录
import logging
logger = logging.getLogger(__name__)
logger.info(f"Processing project: {project.id}")

# 性能分析
import time
start_time = time.time()
# 代码执行
execution_time = time.time() - start_time
logger.info(f"Execution time: {execution_time:.2f}s")
```

---

*最后更新: 2024-12-19*
*开发指南版本: v1.1 - MVP引用检测平台*
