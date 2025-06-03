# 🛠️ GEO Insight - 开发指南

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

### 1. 克隆项目
```bash
git clone https://github.com/franksunye/GeoLens.git
cd GeoLens
```

### 2. 环境配置
```bash
# 复制环境变量模板
cp .env.example .env.local

# 编辑环境变量
nano .env.local
```

### 3. 前端开发环境
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

### 4. 后端开发环境
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload --port 8000

# 访问 http://localhost:8000/docs
```

---

## 📁 项目结构

```
GeoLens/
├── frontend/                 # Next.js 前端应用
│   ├── src/
│   │   ├── app/             # App Router 页面
│   │   ├── components/      # 可复用组件
│   │   ├── hooks/           # 自定义 Hooks
│   │   ├── lib/             # 工具函数
│   │   ├── store/           # 状态管理
│   │   └── types/           # TypeScript 类型定义
│   ├── public/              # 静态资源
│   └── package.json
├── backend/                  # FastAPI 后端应用
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具函数
│   ├── tests/               # 测试文件
│   └── requirements.txt
├── docs/                     # 项目文档
├── scripts/                  # 部署脚本
└── docker-compose.yml        # Docker 配置
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

*最后更新: 2024-05-30*
*开发指南版本: v1.0*
