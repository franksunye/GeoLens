# 🚀 GeoLens 端到端测试快速启动指南

## 📋 前提条件
- Python 3.11+
- 豆包API密钥
- DeepSeek API密钥
- 网络连接

## ⚡ 快速开始

### 1. 克隆项目并进入后端目录
```bash
git clone https://github.com/franksunye/GeoLens.git
cd GeoLens/backend
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置API密钥
```bash
# 复制配置文件模板
cp .env.e2e.example .env.e2e

# 编辑配置文件
nano .env.e2e
```

在 `.env.e2e` 中填入你的API密钥：
```bash
DOUBAO_API_KEY=your_doubao_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 4. 运行快速测试
```bash
# 快速验证 (推荐首次使用)
./scripts/quick_e2e_test.sh
```

### 5. 运行完整测试
```bash
# 完整端到端测试套件
./scripts/run_e2e_tests.sh
```

## 🔧 高级配置

### 环境变量方式
如果不想使用配置文件，可以直接设置环境变量：
```bash
export DOUBAO_API_KEY=your_doubao_key
export DEEPSEEK_API_KEY=your_deepseek_key
export DOUBAO_MODEL=doubao-1-5-lite-32k-250115
export DEEPSEEK_MODEL=deepseek-reasoner
```

### 运行特定测试
```bash
# 只测试AI连通性
pytest tests/e2e/test_real_ai_connectivity.py -v

# 只测试业务场景
pytest tests/e2e/test_business_scenarios.py -v

# 只测试数据持久化
pytest tests/e2e/test_data_persistence.py -v
```

### 调试模式
```bash
# 运行测试并显示详细输出
pytest tests/e2e/ -v -s

# 运行测试并在失败时停止
pytest tests/e2e/ -x

# 运行测试并生成HTML报告
pytest tests/e2e/ --html=reports/e2e_report.html --self-contained-html
```

## 📊 预期结果

### 成功的测试输出示例
```
🚀 GeoLens 端到端测试启动
==================================

📡 Phase 1: AI连通性测试
------------------------
✅ 豆包连接成功: 豆包连接成功
✅ DeepSeek连接成功: DeepSeek is working

🔄 Phase 2: 完整业务流程测试
----------------------------
✅ 端到端检测流程测试成功
✅ 多品牌检测测试成功

💾 Phase 2: 数据持久化测试
-------------------------
✅ 检测历史持久化测试成功
✅ Prompt模板持久化测试成功

🏢 Phase 3: 业务场景测试
------------------------
✅ 品牌监控场景测试完成
✅ 竞品分析场景测试完成

🎉 端到端测试完成！
```

### 测试指标
- **豆包API**: 连接成功，响应正常
- **DeepSeek API**: 连接成功，响应正常
- **引用检测**: 基础功能验证通过
- **数据持久化**: 数据库操作正常
- **业务场景**: 实际应用场景验证

## 🚨 常见问题

### API密钥问题
```bash
❌ 错误: 缺少API密钥
```
**解决方案**: 确保在 `.env.e2e` 文件中正确设置了API密钥

### 网络连接问题
```bash
❌ 连接超时
```
**解决方案**: 检查网络连接，可能需要VPN或代理

### 模型权限问题
```bash
❌ HTTP 404 Not Found
```
**解决方案**: 确认API密钥有访问指定模型的权限

### 测试跳过
```bash
SKIPPED [1] API keys not provided
```
**解决方案**: 检查环境变量或 `.env.e2e` 文件配置

## 📈 测试覆盖情况

当前端到端测试覆盖：
- ✅ **AI模型集成**: 豆包 + DeepSeek双模型
- ✅ **引用检测核心**: 多品牌、多模型检测
- ✅ **数据持久化**: 检测历史、模板管理
- ✅ **业务场景**: 品牌监控、竞品分析
- ⚠️ **认证授权**: 计划中
- ⚠️ **项目管理**: 计划中

详细覆盖分析: `E2E_COVERAGE_ANALYSIS.md`

## 🎯 下一步

测试成功后，你可以：
1. 开始前端开发
2. 集成云数据库
3. 部署到生产环境
4. 添加更多AI模型支持

## 📞 获取帮助

如果遇到问题：
1. 查看 `E2E_TEST_RESULTS.md` 了解详细测试结果
2. 查看 `E2E_COVERAGE_ANALYSIS.md` 了解测试覆盖情况
3. 查看 `docs/30_DEVELOPMENT.md` 了解完整开发指南
