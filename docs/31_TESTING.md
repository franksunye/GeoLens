# 🧪 GEO Insight - 测试策略文档

## 📋 测试概述

GEO Insight 采用多层次的测试策略，确保产品质量和用户体验。测试覆盖单元测试、集成测试、端到端测试和性能测试等多个维度。

---

## 🎯 测试目标

### 质量目标
- **代码覆盖率**: 前端 ≥ 80%，后端 ≥ 90%
- **缺陷密度**: < 1 缺陷/KLOC
- **性能指标**: 页面加载 < 3s，API响应 < 2s
- **可用性**: 99.9% 系统可用性

### 测试原则
- **左移测试**: 在开发早期发现问题
- **自动化优先**: 减少手动测试工作量
- **持续测试**: 集成到CI/CD流水线
- **风险驱动**: 重点测试高风险功能

---

## 🏗️ 测试金字塔

```
                    E2E Tests (10%)
                   ┌─────────────────┐
                   │   用户场景测试    │
                   └─────────────────┘
                 
              Integration Tests (20%)
            ┌─────────────────────────────┐
            │      API集成测试             │
            │    组件集成测试              │
            └─────────────────────────────┘
          
        Unit Tests (70%)
    ┌─────────────────────────────────────────┐
    │           单元测试                       │
    │    函数测试 | 组件测试 | 服务测试         │
    └─────────────────────────────────────────┘
```

---

## 🔬 单元测试

### 前端单元测试 (Jest + React Testing Library)

#### 组件测试
```typescript
// frontend/src/__tests__/components/ProjectCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProjectCard } from '@/components/ProjectCard';
import { mockProject } from '@/tests/mocks/project';

describe('ProjectCard Component', () => {
  it('should render project information correctly', () => {
    render(<ProjectCard project={mockProject} />);
    
    expect(screen.getByText(mockProject.name)).toBeInTheDocument();
    expect(screen.getByText(mockProject.domain)).toBeInTheDocument();
    expect(screen.getByText('活跃')).toBeInTheDocument();
  });
  
  it('should call onEdit when edit button is clicked', () => {
    const onEdit = jest.fn();
    render(<ProjectCard project={mockProject} onEdit={onEdit} />);
    
    const editButton = screen.getByRole('button', { name: /编辑/i });
    fireEvent.click(editButton);
    
    expect(onEdit).toHaveBeenCalledWith(mockProject);
  });
  
  it('should display keywords as badges', () => {
    render(<ProjectCard project={mockProject} />);
    
    mockProject.targetKeywords.forEach(keyword => {
      expect(screen.getByText(keyword)).toBeInTheDocument();
    });
  });
});
```

#### Hook测试
```typescript
// frontend/src/__tests__/hooks/useProject.test.ts
import { renderHook, act } from '@testing-library/react';
import { useProject } from '@/hooks/useProject';
import { projectApi } from '@/lib/api';

jest.mock('@/lib/api');

describe('useProject Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('should fetch project data on mount', async () => {
    const mockProject = { id: '1', name: 'Test Project' };
    (projectApi.getProject as jest.Mock).mockResolvedValue(mockProject);
    
    const { result } = renderHook(() => useProject('1'));
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    expect(result.current.project).toEqual(mockProject);
    expect(result.current.loading).toBe(false);
  });
});
```

### 后端单元测试 (pytest)

#### 服务层测试
```python
# backend/tests/services/test_project_service.py
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.project import ProjectService
from app.schemas.project import ProjectCreate
from app.models.project import Project

@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def project_service(mock_db):
    return ProjectService(mock_db)

@pytest.fixture
def sample_project_data():
    return ProjectCreate(
        name="测试项目",
        domain="example.com",
        description="测试描述",
        target_keywords=["关键词1", "关键词2"]
    )

class TestProjectService:
    async def test_create_project_success(self, project_service, sample_project_data):
        """测试成功创建项目"""
        user_id = "user-123"
        
        with patch.object(project_service.db, 'add') as mock_add, \
             patch.object(project_service.db, 'commit') as mock_commit, \
             patch.object(project_service.db, 'refresh') as mock_refresh:
            
            result = await project_service.create_project(sample_project_data, user_id)
            
            assert result.name == sample_project_data.name
            assert result.user_id == user_id
            mock_add.assert_called_once()
            mock_commit.assert_called_once()
    
    async def test_create_project_duplicate_domain(self, project_service, sample_project_data):
        """测试创建重复域名项目"""
        user_id = "user-123"
        
        with patch.object(project_service, '_check_domain_exists', return_value=True):
            with pytest.raises(ValueError, match="域名已存在"):
                await project_service.create_project(sample_project_data, user_id)
```

#### API路由测试
```python
# backend/tests/api/test_projects.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.deps import get_db, get_current_user
from tests.utils import create_test_user, create_test_project

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def authenticated_client(client, test_user):
    # 模拟认证用户
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides.clear()

class TestProjectsAPI:
    def test_create_project_success(self, authenticated_client):
        """测试成功创建项目"""
        project_data = {
            "name": "新项目",
            "domain": "newproject.com",
            "description": "项目描述"
        }
        
        response = authenticated_client.post("/api/v1/projects", json=project_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == project_data["name"]
    
    def test_create_project_validation_error(self, authenticated_client):
        """测试创建项目参数验证"""
        invalid_data = {
            "name": "",  # 空名称
            "domain": "invalid-domain"  # 无效域名
        }
        
        response = authenticated_client.post("/api/v1/projects", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
```

---

## 🔗 集成测试

### API集成测试
```python
# backend/tests/integration/test_mention_check_flow.py
import pytest
from unittest.mock import patch, AsyncMock

class TestMentionCheckFlow:
    @patch('app.services.ai.openai_client.chat.completions.create')
    async def test_complete_mention_check_flow(self, mock_openai, authenticated_client, test_project):
        """测试完整的引用检测流程"""
        # 模拟OpenAI API响应
        mock_openai.return_value = AsyncMock()
        mock_openai.return_value.choices = [
            AsyncMock(message=AsyncMock(content="Notion是一个很好的协作工具..."))
        ]
        
        # 1. 创建检测请求
        check_data = {
            "project_id": test_project.id,
            "prompt": "推荐协作工具",
            "platforms": ["chatgpt"]
        }
        
        response = authenticated_client.post("/api/v1/mentions/check", json=check_data)
        assert response.status_code == 202
        
        check_id = response.json()["data"]["check_id"]
        
        # 2. 等待处理完成
        import asyncio
        await asyncio.sleep(1)
        
        # 3. 获取检测结果
        response = authenticated_client.get(f"/api/v1/mentions/check/{check_id}")
        assert response.status_code == 200
        
        data = response.json()["data"]
        assert data["status"] == "completed"
        assert len(data["results"]) == 1
        assert data["results"][0]["mentioned"] is True
```

### 前端集成测试
```typescript
// frontend/src/__tests__/integration/ProjectWorkflow.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProjectDashboard } from '@/pages/projects';
import { server } from '@/tests/mocks/server';

describe('Project Workflow Integration', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());
  
  it('should complete project creation and check workflow', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } }
    });
    
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDashboard />
      </QueryClientProvider>
    );
    
    // 1. 创建项目
    fireEvent.click(screen.getByText('创建项目'));
    
    fireEvent.change(screen.getByLabelText('项目名称'), {
      target: { value: '测试项目' }
    });
    fireEvent.change(screen.getByLabelText('域名'), {
      target: { value: 'test.com' }
    });
    
    fireEvent.click(screen.getByText('确认创建'));
    
    // 2. 等待项目创建完成
    await waitFor(() => {
      expect(screen.getByText('测试项目')).toBeInTheDocument();
    });
    
    // 3. 执行引用检测
    fireEvent.click(screen.getByText('开始检测'));
    
    await waitFor(() => {
      expect(screen.getByText('检测完成')).toBeInTheDocument();
    });
  });
});
```

---

## 🌐 端到端测试 (E2E)

### Playwright E2E测试
```typescript
// e2e/tests/user-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Journey', () => {
  test('complete user registration and project creation flow', async ({ page }) => {
    // 1. 访问首页
    await page.goto('/');
    
    // 2. 用户注册
    await page.click('text=注册');
    await page.fill('[data-testid=email-input]', 'test@example.com');
    await page.fill('[data-testid=password-input]', 'password123');
    await page.fill('[data-testid=name-input]', '测试用户');
    await page.click('[data-testid=register-button]');
    
    // 3. 验证登录成功
    await expect(page.locator('text=欢迎，测试用户')).toBeVisible();
    
    // 4. 创建项目
    await page.click('text=创建项目');
    await page.fill('[data-testid=project-name]', 'E2E测试项目');
    await page.fill('[data-testid=project-domain]', 'e2etest.com');
    await page.click('[data-testid=create-project-button]');
    
    // 5. 验证项目创建成功
    await expect(page.locator('text=E2E测试项目')).toBeVisible();
    
    // 6. 执行AI检测
    await page.click('[data-testid=start-check-button]');
    await page.fill('[data-testid=prompt-input]', '推荐项目管理工具');
    await page.click('[data-testid=run-check-button]');
    
    // 7. 等待检测完成
    await expect(page.locator('text=检测完成')).toBeVisible({ timeout: 30000 });
    
    // 8. 查看检测结果
    await expect(page.locator('[data-testid=check-results]')).toBeVisible();
  });
  
  test('mobile responsive design', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/projects');
    
    // 验证移动端布局
    await expect(page.locator('[data-testid=mobile-menu]')).toBeVisible();
    await expect(page.locator('[data-testid=project-grid]')).toHaveCSS('grid-template-columns', '1fr');
  });
});
```

---

## ⚡ 性能测试

### 前端性能测试
```typescript
// frontend/src/__tests__/performance/PageLoad.test.ts
import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('page load performance', async ({ page }) => {
    // 开始性能监控
    await page.goto('/', { waitUntil: 'networkidle' });
    
    // 获取性能指标
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime
      };
    });
    
    // 性能断言
    expect(metrics.domContentLoaded).toBeLessThan(2000); // < 2s
    expect(metrics.firstContentfulPaint).toBeLessThan(1500); // < 1.5s
  });
});
```

### 后端性能测试
```python
# backend/tests/performance/test_api_performance.py
import pytest
import asyncio
import time
from fastapi.testclient import TestClient

class TestAPIPerformance:
    def test_concurrent_requests(self, authenticated_client):
        """测试并发请求性能"""
        async def make_request():
            response = authenticated_client.get("/api/v1/projects")
            return response.status_code
        
        async def run_concurrent_requests():
            tasks = [make_request() for _ in range(100)]
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            return results, end_time - start_time
        
        results, duration = asyncio.run(run_concurrent_requests())
        
        # 验证所有请求成功
        assert all(status == 200 for status in results)
        # 验证响应时间
        assert duration < 5.0  # 100个并发请求在5秒内完成
    
    def test_large_dataset_query(self, authenticated_client, large_dataset):
        """测试大数据集查询性能"""
        start_time = time.time()
        response = authenticated_client.get("/api/v1/mentions/history?limit=1000")
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 2.0  # 查询1000条记录在2秒内完成
```

---

## 🔒 安全测试

### 认证授权测试
```python
# backend/tests/security/test_auth_security.py
class TestAuthSecurity:
    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get("/api/v1/projects")
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """测试无效令牌"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/projects", headers=headers)
        assert response.status_code == 401
    
    def test_sql_injection_protection(self, authenticated_client):
        """测试SQL注入防护"""
        malicious_input = "'; DROP TABLE projects; --"
        response = authenticated_client.get(f"/api/v1/projects?search={malicious_input}")
        
        # 应该正常返回，不会执行恶意SQL
        assert response.status_code == 200
```

---

## 📊 测试报告

### 覆盖率报告
```bash
# 前端覆盖率
npm run test:coverage

# 后端覆盖率
pytest --cov=app --cov-report=html

# 生成合并报告
npm run test:report
```

### 测试指标监控
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Tests
        run: |
          npm run test:ci
          pytest --cov=app --cov-report=xml
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml,./frontend/coverage/lcov.info
      
      - name: Performance Budget
        run: |
          npm run lighthouse:ci
```

---

## 🚀 CI/CD集成

### 测试流水线
```yaml
# 测试阶段
test:
  stage: test
  parallel:
    matrix:
      - TEST_TYPE: [unit, integration, e2e]
  script:
    - npm run test:$TEST_TYPE
  coverage: '/Coverage: \d+\.\d+%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
```

---

*最后更新: 2024-05-30*
*测试策略版本: v1.0*
