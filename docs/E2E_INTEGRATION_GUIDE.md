# 🔗 GeoLens 端到端集成操作指南

## 📋 概述

本指南提供了从演示模式切换到真实API模式的完整操作步骤，以及本地开发环境中进行端到端前后台集成检查的详细流程。

---

## 🎭 演示模式 vs 真实模式

### 当前状态检查
前端默认运行在**演示模式**下，通过以下方式判断：
```python
# 在 frontend/services/api_client.py 中
def _is_demo_mode(self) -> bool:
    return st.session_state.get('access_token') == 'demo-access-token'
```

### 模式特点对比
| 特性 | 演示模式 | 真实模式 |
|------|----------|----------|
| 数据来源 | 模拟数据 | 真实API |
| 后端依赖 | 无需后端 | 需要后端服务 |
| 功能完整性 | 100%演示 | 100%真实 |
| 用户体验 | 快速展示 | 完整功能 |

---

## 🚀 方式1: 自动化端到端测试（推荐）

### 一键启动完整测试
```bash
# 在项目根目录运行
./scripts/start_e2e_test.sh
```

**这个脚本会自动完成**:
1. ✅ 创建虚拟环境
2. ✅ 安装前后端依赖
3. ✅ 启动后端服务 (http://localhost:8000)
4. ✅ 启动前端服务 (http://localhost:8501)
5. ✅ 设置环境变量切换到真实模式
6. ✅ 进行集成测试验证
7. ✅ 提供实时监控和日志

### 测试完成后访问
- 🖥️ **前端应用**: http://localhost:8501
- 📚 **API文档**: http://localhost:8000/docs
- 📄 **日志文件**: `backend.log` 和 `frontend.log`

---

## 🔧 方式2: 手动分步操作

### 步骤1: 准备环境

#### 1.1 克隆项目
```bash
git clone https://github.com/franksunye/GeoLens.git
cd GeoLens
```

#### 1.2 创建虚拟环境（推荐）
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 步骤2: 启动后端服务

#### 2.1 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 2.2 配置后端环境（可选）
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件（可选）
# nano .env
```

#### 2.3 启动后端服务
```bash
# 设置环境变量
export PYTHONPATH="."
export ENVIRONMENT="development"

# 启动FastAPI服务
uvicorn app.main:app --reload --port 8000
```

#### 2.4 验证后端服务
```bash
# 新开终端窗口验证
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### 步骤3: 配置前端切换到真实模式

#### 3.1 进入前端目录
```bash
cd ../frontend  # 从backend目录切换
```

#### 3.2 安装前端依赖
```bash
pip install -r requirements.txt
```

#### 3.3 配置前端环境变量（关键步骤）
```bash
# 方式1: 复制并编辑配置文件
cp .env.example .env

# 编辑 .env 文件，确保以下配置：
echo "API_BASE_URL=http://localhost:8000/api/v1" > .env
echo "DEBUG=true" >> .env
```

```bash
# 方式2: 直接设置环境变量
export API_BASE_URL="http://localhost:8000/api/v1"
export DEBUG="true"
```

#### 3.4 禁用演示模式（可选）
如果需要完全禁用演示模式，可以修改认证逻辑：

编辑 `frontend/components/auth.py`:
```python
def login(self, email: str, password: str) -> bool:
    # 注释掉演示模式检查
    # if email == "demo@geolens.ai" and password == "demo123":
    #     return self._demo_login()
    
    # 强制使用真实API认证
    return self._api_login(email, password)
```

#### 3.5 启动前端服务
```bash
streamlit run main.py --server.port 8501
```

### 步骤4: 验证集成

#### 4.1 访问前端应用
打开浏览器访问: http://localhost:8501

#### 4.2 检查模式状态
在前端应用中，可以通过以下方式确认当前模式：
- 查看浏览器开发者工具的Network标签
- 观察API请求是否指向 `localhost:8000`
- 登录时使用真实账号而非演示账号

#### 4.3 测试核心功能
1. **用户认证**: 尝试登录（可能需要先注册）
2. **项目管理**: 创建、编辑、删除项目
3. **引用检测**: 运行检测任务
4. **历史记录**: 查看检测历史
5. **数据分析**: 查看分析报告

---

## 🔍 故障排除

### 常见问题及解决方案

#### 1. 前端仍在演示模式
**症状**: 登录后显示演示数据，API请求未发送到后端

**解决方案**:
```bash
# 确认环境变量设置
echo $API_BASE_URL  # 应该显示 http://localhost:8000/api/v1

# 重新设置环境变量
export API_BASE_URL="http://localhost:8000/api/v1"

# 重启前端服务
streamlit run main.py --server.port 8501
```

#### 2. API连接失败
**症状**: 前端显示网络错误或连接失败

**解决方案**:
```bash
# 检查后端服务状态
curl http://localhost:8000/health

# 检查端口占用
lsof -i :8000
lsof -i :8501

# 重启服务
pkill -f uvicorn
pkill -f streamlit
```

#### 3. 认证失败
**症状**: 无法登录或token验证失败

**解决方案**:
```bash
# 检查后端认证端点
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# 查看后端日志
tail -f backend.log
```

#### 4. 数据库连接问题
**症状**: 后端启动失败或数据操作错误

**解决方案**:
```bash
# 检查数据库文件
ls -la backend/data/

# 重新初始化数据库
cd backend
python -c "from app.database import init_db; init_db()"
```

---

## 📊 验证检查清单

### ✅ 后端服务验证
- [ ] 后端服务启动成功 (http://localhost:8000)
- [ ] 健康检查通过 (`/health`)
- [ ] API文档可访问 (`/docs`)
- [ ] 数据库连接正常
- [ ] 认证端点响应正常

### ✅ 前端服务验证
- [ ] 前端服务启动成功 (http://localhost:8501)
- [ ] 环境变量配置正确
- [ ] API_BASE_URL指向后端服务
- [ ] 页面正常加载
- [ ] 无JavaScript错误

### ✅ 集成功能验证
- [ ] 用户认证流程正常
- [ ] API请求发送到后端
- [ ] 数据正确显示
- [ ] 错误处理正常
- [ ] 所有核心功能可用

---

## 🎯 快速验证命令

### 一键验证脚本
```bash
# 运行简单集成测试
python scripts/simple_integration_test.py

# 运行后端专项测试
./scripts/test_backend_only.sh

# 检查API连通性
python scripts/quick_api_test.py
```

### 手动验证命令
```bash
# 检查后端
curl http://localhost:8000/health
curl http://localhost:8000/docs

# 检查前端
curl http://localhost:8501

# 检查环境变量
echo $API_BASE_URL
echo $DEBUG
```

---

## 📚 相关文档位置

### 配置信息记录在:
- **前端配置**: `frontend/.env.example` 和 `frontend/utils/config.py`
- **后端配置**: `backend/.env.example` 和 `backend/app/core/config.py`
- **集成测试**: `docs/31_TESTING.md` (第1020-1076行)
- **架构说明**: `docs/10_ARCHITECTURE.md` (第376-407行)

### 自动化脚本位置:
- **完整测试**: `scripts/start_e2e_test.sh`
- **简单测试**: `scripts/simple_integration_test.py`
- **后端测试**: `scripts/test_backend_only.sh`
- **API测试**: `scripts/quick_api_test.py`

---

## 🎉 成功标志

当您看到以下情况时，说明集成成功：

1. ✅ 前端页面正常加载
2. ✅ 浏览器开发者工具显示API请求发送到 `localhost:8000`
3. ✅ 登录功能正常（使用真实账号）
4. ✅ 数据操作正常（项目、检测等）
5. ✅ 后端日志显示前端请求
6. ✅ 所有核心功能可用

**恭喜！您已成功完成GeoLens前后端集成！** 🌍✨
