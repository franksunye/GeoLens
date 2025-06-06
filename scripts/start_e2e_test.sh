#!/bin/bash

# GeoLens 端到端集成测试启动脚本
# 自动安装依赖、启动服务并进行集成测试

set -e  # 遇到错误立即退出

echo "🌍 GeoLens 端到端集成测试"
echo "=================================================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "🐍 Python版本: $python_version"

if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
    echo "⚠️ 建议使用Python 3.8+，当前版本可能存在兼容性问题"
fi

# 检查项目结构
echo ""
echo "📁 检查项目结构..."
if [[ ! -d "backend" ]] || [[ ! -d "frontend" ]]; then
    echo "❌ 项目结构不正确，请在项目根目录运行此脚本"
    exit 1
fi
echo "✅ 项目结构正常"

# 创建虚拟环境（可选）
echo ""
echo "🔧 准备Python环境..."
if [[ ! -d "venv" ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 安装后端依赖
echo ""
echo "📦 安装后端依赖..."
cd backend
if pip install -r requirements.txt; then
    echo "✅ 后端依赖安装成功"
else
    echo "❌ 后端依赖安装失败"
    exit 1
fi
cd ..

# 安装前端依赖
echo ""
echo "📦 安装前端依赖..."
cd frontend
if pip install -r requirements.txt; then
    echo "✅ 前端依赖安装成功"
else
    echo "❌ 前端依赖安装失败"
    exit 1
fi
cd ..

# 启动后端服务
echo ""
echo "🚀 启动后端服务..."
cd backend

# 设置环境变量
export PYTHONPATH="."
export ENVIRONMENT="testing"

# 启动FastAPI服务（后台运行）
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

cd ..

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端服务启动成功"
        break
    fi
    
    if [[ $i -eq 30 ]]; then
        echo "❌ 后端服务启动超时"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 1
done

# 测试后端API
echo ""
echo "🧪 测试后端API..."

# 测试健康检查
if curl -s http://localhost:8000/health | grep -q "version"; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败"
fi

# 测试API文档
if curl -s http://localhost:8000/docs | grep -q "swagger"; then
    echo "✅ API文档可访问"
else
    echo "❌ API文档访问失败"
fi

# 测试关键端点
echo "🔑 测试关键API端点..."

endpoints=(
    "GET:/:根端点"
    "GET:/api/v1/projects:项目列表"
    "POST:/api/v1/auth/login:用户登录"
    "POST:/api/v1/api/check-mention:引用检测"
)

for endpoint in "${endpoints[@]}"; do
    IFS=':' read -r method path name <<< "$endpoint"
    
    if [[ "$method" == "GET" ]]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000$path)
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{}' http://localhost:8000$path)
    fi
    
    if [[ "$status" != "404" ]]; then
        echo "✅ $name: 端点存在 (HTTP $status)"
    else
        echo "❌ $name: 端点不存在"
    fi
done

# 启动前端服务
echo ""
echo "🖥️ 启动前端服务..."
cd frontend

# 设置环境变量
export API_BASE_URL="http://localhost:8000/api/v1"
export DEBUG="true"

# 启动Streamlit服务（后台运行）
nohup python -m streamlit run main.py --server.port 8501 --server.headless true > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

cd ..

# 等待前端服务启动
echo "⏳ 等待前端服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "✅ 前端服务启动成功"
        break
    fi
    
    if [[ $i -eq 30 ]]; then
        echo "❌ 前端服务启动超时"
        kill $FRONTEND_PID 2>/dev/null || true
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 1
done

# 集成测试
echo ""
echo "🔗 进行集成测试..."

# 测试前端页面访问
if curl -s http://localhost:8501 | grep -q "GeoLens"; then
    echo "✅ 前端页面可访问"
else
    echo "❌ 前端页面访问失败"
fi

# 显示服务状态
echo ""
echo "📊 服务状态总结"
echo "=================================================="
echo "🔗 后端服务: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "🖥️ 前端服务: http://localhost:8501"
echo ""
echo "📋 进程信息:"
echo "   后端PID: $BACKEND_PID"
echo "   前端PID: $FRONTEND_PID"
echo ""
echo "📄 日志文件:"
echo "   后端日志: backend.log"
echo "   前端日志: frontend.log"

# 等待用户操作
echo ""
echo "🎉 集成测试完成！服务正在运行中..."
echo "💡 您现在可以:"
echo "   1. 访问前端: http://localhost:8501"
echo "   2. 查看API文档: http://localhost:8000/docs"
echo "   3. 测试各项功能"
echo ""
echo "⏹️ 按 Ctrl+C 停止所有服务"

# 等待中断信号
cleanup() {
    echo ""
    echo "🧹 正在停止服务..."
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    echo "✅ 所有服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 保持脚本运行
while true; do
    sleep 1
done
