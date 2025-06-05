#!/bin/bash

# 端到端测试运行脚本
# 使用真实的AI API进行完整的业务流程测试

set -e  # 遇到错误立即退出

echo "🚀 GeoLens 端到端测试启动"
echo "=================================="

# 检查当前目录
if [ ! -f "app/main.py" ]; then
    echo "❌ 错误: 请在backend目录下运行此脚本"
    exit 1
fi

# 设置API密钥（如果未设置）
if [ -z "$DOUBAO_API_KEY" ]; then
    export DOUBAO_API_KEY="fb429f70-7037-4e2b-bc44-e98b14685cc0"
    echo "✅ 设置豆包API密钥"
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
    export DEEPSEEK_API_KEY="sk-b3e19280c908402e90ed28b986fbc2f5"
    echo "✅ 设置DeepSeek API密钥"
fi

# 设置测试环境变量
export E2E_TESTING=true
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo ""
echo "🔧 测试环境配置"
echo "   豆包模型: Doubao-1.5-lite-32k"
echo "   DeepSeek模型: DeepSeek-R1"
echo "   测试超时: 30秒"
echo ""

# 检查依赖
echo "📦 检查测试依赖..."
python -c "import pytest, asyncio, sqlalchemy" 2>/dev/null || {
    echo "❌ 缺少必要的依赖，请运行: pip install -r requirements.txt"
    exit 1
}
echo "✅ 依赖检查通过"

# 创建测试数据库目录
mkdir -p data
echo "✅ 测试数据库目录准备完成"

echo ""
echo "🧪 开始端到端测试"
echo "=================================="

# 运行不同阶段的测试
echo ""
echo "📡 Phase 1: AI连通性测试"
echo "------------------------"
pytest tests/e2e/test_real_ai_connectivity.py -v --tb=short -s || {
    echo "❌ AI连通性测试失败"
    exit 1
}

echo ""
echo "🔄 Phase 2: 完整业务流程测试"
echo "----------------------------"
pytest tests/e2e/test_full_mention_detection.py -v --tb=short -s || {
    echo "❌ 业务流程测试失败"
    exit 1
}

echo ""
echo "💾 Phase 2: 数据持久化测试"
echo "-------------------------"
pytest tests/e2e/test_data_persistence.py -v --tb=short -s || {
    echo "❌ 数据持久化测试失败"
    exit 1
}

echo ""
echo "🏢 Phase 3: 业务场景测试"
echo "------------------------"
pytest tests/e2e/test_business_scenarios.py -v --tb=short -s || {
    echo "❌ 业务场景测试失败"
    exit 1
}

echo ""
echo "🎉 端到端测试完成！"
echo "=================================="

# 生成测试报告
echo ""
echo "📊 生成测试报告..."
mkdir -p reports

# 运行完整的E2E测试套件并生成HTML报告
pytest tests/e2e/ --html=reports/e2e_report.html --self-contained-html -v --tb=short || {
    echo "⚠️ 测试报告生成失败，但测试已完成"
}

if [ -f "reports/e2e_report.html" ]; then
    echo "✅ 测试报告已生成: reports/e2e_report.html"
else
    echo "⚠️ 测试报告生成失败"
fi

echo ""
echo "✨ 端到端测试全部完成！"
echo ""
echo "📋 测试总结:"
echo "   ✅ AI连通性测试 - 验证豆包和DeepSeek API连接"
echo "   ✅ 完整业务流程测试 - 端到端引用检测流程"
echo "   ✅ 数据持久化测试 - 真实场景下的数据库操作"
echo "   ✅ 业务场景测试 - 品牌监控、竞品分析等实际应用场景"
echo ""
echo "🎯 所有真实AI模型集成测试通过！"
