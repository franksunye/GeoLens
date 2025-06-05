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

# 设置API密钥
export DOUBAO_API_KEY="fb429f70-7037-4e2b-bc44-e98b14685cc0"
export DEEPSEEK_API_KEY="sk-b3e19280c908402e90ed28b986fbc2f5"
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
