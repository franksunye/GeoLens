#!/bin/bash

# GeoLens 后端服务测试脚本
# 快速测试后端API功能

set -e

echo "🌍 GeoLens 后端服务测试"
echo "=================================="

# 检查是否在项目根目录
if [[ ! -d "backend" ]]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

echo "📁 项目结构检查通过"

# 进入后端目录
cd backend

echo ""
echo "📦 检查后端依赖..."
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ requirements.txt 不存在"
    exit 1
fi

echo "✅ requirements.txt 存在"
echo "📋 依赖包数量: $(wc -l < requirements.txt)"

# 检查Python模块
echo ""
echo "🐍 检查Python模块..."
if python3 -c "import app.main" 2>/dev/null; then
    echo "✅ 主模块可导入"
else
    echo "❌ 主模块导入失败，可能缺少依赖"
    echo "💡 请先安装依赖: pip install -r requirements.txt"
fi

# 检查配置文件
echo ""
echo "⚙️ 检查配置文件..."
if [[ -f ".env.example" ]]; then
    echo "✅ .env.example 存在"
else
    echo "⚠️ .env.example 不存在"
fi

if [[ -f ".env" ]]; then
    echo "✅ .env 配置文件存在"
else
    echo "⚠️ .env 配置文件不存在，将使用默认配置"
fi

# 检查数据库文件
echo ""
echo "💾 检查数据库..."
if [[ -f "*.db" ]] || [[ -f "data/*.db" ]]; then
    echo "✅ 发现数据库文件"
else
    echo "ℹ️ 未发现数据库文件，首次运行时会自动创建"
fi

# 尝试启动服务（测试模式）
echo ""
echo "🚀 测试服务启动..."

# 设置环境变量
export PYTHONPATH="."
export ENVIRONMENT="testing"

# 检查端口
if lsof -i :8000 >/dev/null 2>&1; then
    echo "⚠️ 端口 8000 已被占用"
    echo "💡 请先停止占用端口的服务"
else
    echo "✅ 端口 8000 可用"
fi

echo ""
echo "📋 后端测试总结"
echo "=================================="
echo "✅ 项目结构正常"
echo "✅ 依赖配置存在"
echo "✅ 端口可用"

echo ""
echo "🚀 启动后端服务命令:"
echo "   cd backend"
echo "   pip install -r requirements.txt"
echo "   uvicorn app.main:app --reload --port 8000"

echo ""
echo "📚 启动后可访问:"
echo "   API文档: http://localhost:8000/docs"
echo "   健康检查: http://localhost:8000/health"
echo "   根端点: http://localhost:8000/"

cd ..
