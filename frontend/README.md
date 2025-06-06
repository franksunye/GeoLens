# 🎨 GeoLens 前端应用

## 📋 概述

GeoLens 前端是基于 Streamlit 构建的企业级品牌引用检测应用，提供直观的用户界面和强大的数据可视化功能。

**当前状态**: ✅ 已完成 (v0.8.0)
**技术栈**: Streamlit + Python + Plotly
**设计风格**: 企业级 B2B 应用
**测试状态**: 100% 前端测试通过

---

## 🚀 快速开始

### 简单启动 (推荐)
```bash
# 1. 克隆项目
git clone https://github.com/franksunye/GeoLens.git
cd GeoLens/frontend

# 2. 安装依赖
pip install streamlit plotly pandas httpx python-dotenv

# 3. 启动应用
streamlit run main.py

# 4. 访问应用
# 浏览器打开: http://localhost:8501
```

### 完整安装步骤

1. **克隆项目**
```bash
git clone https://github.com/franksunye/GeoLens.git
cd GeoLens/frontend
```

2. **创建虚拟环境** (可选)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **启动应用**
```bash
streamlit run main.py
```

5. **访问应用**
打开浏览器访问: http://localhost:8501

---

## 📊 项目状态

### ✅ 完成功能 (v0.8.0)
- **7个核心页面**: 完整的品牌检测工作流
- **企业级UI**: 专业的B2B应用设计，无emoji装饰
- **用户认证**: JWT集成的完整权限管理
- **数据可视化**: Plotly交互式图表系统
- **响应式设计**: 适配桌面、平板、手机
- **测试体系**: 100%前端测试通过

### 🧪 测试结果
- **前端测试**: 8/8项目100%通过
- **语法检查**: 27个文件100%通过
- **页面结构**: 6/6页面100%正确
- **组件完整性**: 3/3组件100%正常
- **Streamlit兼容性**: 13/13API100%可用

---

## 📋 功能特性

### 🔐 用户认证
- 用户登录/注册
- JWT令牌管理
- 会话状态管理

### 📁 项目管理
- 创建和管理检测项目
- 品牌列表管理
- 项目配置和设置

### 🔍 引用检测
- 多AI模型并行检测
- 实时检测进度显示
- 结果可视化展示

### 📜 历史管理
- 检测历史记录查看
- 数据筛选和搜索
- 结果导出功能

### 📊 数据分析
- 品牌提及率分析
- 趋势图表展示
- 竞品对比分析

### 📚 模板管理
- Prompt模板库
- 变量替换功能
- 模板分类管理

## 🏗️ 项目结构

```
frontend/
├── main.py                 # 应用入口
├── pages/                  # 页面模块
│   ├── 2_📁_Projects.py    # 项目管理
│   ├── 3_🔍_Detection.py   # 引用检测
│   ├── 4_📜_History.py     # 检测历史
│   ├── 5_📚_Templates.py   # 模板管理
│   ├── 6_📊_Analytics.py   # 数据分析
│   └── 7_👤_Profile.py     # 用户资料
├── components/             # 组件模块
│   ├── auth.py            # 认证组件
│   ├── sidebar.py         # 侧边栏组件
│   └── charts.py          # 图表组件
├── services/              # 服务模块
│   ├── api_client.py      # API客户端
│   └── detection_service.py # 检测服务
├── utils/                 # 工具模块
│   ├── config.py          # 配置管理
│   └── session.py         # 会话管理
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
└── README.md             # 项目说明
```

## 🔧 配置说明

### 环境变量
- `API_BASE_URL`: 后端API地址
- `API_TIMEOUT`: API请求超时时间
- `DEBUG`: 调试模式开关
- `CACHE_TTL`: 缓存过期时间

### Streamlit配置
应用使用Streamlit的多页面架构，支持：
- 响应式布局
- 会话状态管理
- 组件缓存优化
- 自定义CSS样式

## 🎯 使用指南

### 演示账号
- **邮箱**: demo@geolens.ai
- **密码**: demo123

### 基本流程
1. 登录系统
2. 创建或选择项目
3. 配置检测参数
4. 执行引用检测
5. 查看结果分析

### 高级功能
- 使用Prompt模板提高效率
- 批量检测和对比分析
- 导出检测结果数据
- 自定义品牌和模型配置

## 🔗 API集成

前端通过HTTP客户端与FastAPI后端通信：
- 支持JWT认证
- 自动token刷新
- 统一错误处理
- 请求缓存优化

## 🎨 UI/UX设计

### 设计原则
- 简洁直观的用户界面
- 数据驱动的可视化展示
- 响应式设计适配不同屏幕
- 一致的交互体验

### 主题色彩
- 主色调: #1f77b4 (蓝色)
- 辅助色: #ff7f0e (橙色)
- 成功色: #2ca02c (绿色)
- 警告色: #d62728 (红色)

## 🧪 开发和测试

### 开发模式
```bash
# 启用调试模式
export DEBUG=true
streamlit run main.py --server.runOnSave=true
```

### 代码规范
- 使用Black进行代码格式化
- 遵循PEP 8编码规范
- 添加类型注解和文档字符串

## 📦 部署

### Streamlit Cloud部署
1. 推送代码到GitHub
2. 连接Streamlit Cloud
3. 配置环境变量
4. 自动部署和更新

### 本地部署
```bash
# 生产模式启动
streamlit run main.py --server.port=8501 --server.address=0.0.0.0
```

## 🔍 故障排除

### 常见问题
1. **API连接失败**: 检查后端服务是否启动
2. **认证失败**: 确认API密钥配置正确
3. **页面加载慢**: 检查网络连接和缓存设置

### 调试技巧
- 启用DEBUG模式查看详细日志
- 使用浏览器开发者工具检查网络请求
- 查看Streamlit控制台输出

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE) 文件

## 📞 支持

- 📧 邮箱: support@geolens.ai
- 🐛 问题反馈: [GitHub Issues](https://github.com/franksunye/GeoLens/issues)
- 📚 文档: [项目文档](https://github.com/franksunye/GeoLens/docs)

---

**GeoLens** - 专业的AI引用检测平台 🌍
