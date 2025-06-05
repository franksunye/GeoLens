#!/bin/bash

# 快速端到端测试脚本
# 只运行核心的连通性和基础流程测试

set -e

echo "⚡ GeoLens 快速端到端测试"
echo "========================="

# 检查当前目录
if [ ! -f "app/main.py" ]; then
    echo "❌ 错误: 请在backend目录下运行此脚本"
    exit 1
fi

# 加载环境变量配置
if [ -f ".env.e2e" ]; then
    export $(cat .env.e2e | grep -v '^#' | xargs)
    echo "📁 已加载 .env.e2e 配置"
else
    echo "⚠️ 未找到 .env.e2e，请确保已设置环境变量"
fi

# 检查API密钥
if [ -z "$DOUBAO_API_KEY" ] || [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ 缺少API密钥，请设置环境变量或创建 .env.e2e 文件"
    exit 1
fi

export E2E_TESTING=true
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🔧 快速测试配置完成"
echo ""

# 只运行最核心的测试
echo "📡 测试AI连通性..."
pytest tests/e2e/test_real_ai_connectivity.py::TestRealAIConnectivity::test_doubao_connection -v -s

echo ""
echo "📡 测试DeepSeek连通性..."
pytest tests/e2e/test_real_ai_connectivity.py::TestRealAIConnectivity::test_deepseek_connection -v -s

echo ""
echo "🔄 测试基础检测流程..."
pytest tests/e2e/test_full_mention_detection.py::TestFullMentionDetection::test_end_to_end_detection_flow -v -s

echo ""
echo "✅ 快速端到端测试完成！"
echo ""
echo "💡 运行完整测试: ./scripts/run_e2e_tests.sh"
