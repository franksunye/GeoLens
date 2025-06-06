# 🎨 GeoLens 前端开发指南

## 📋 概述

GeoLens 前端采用 **Streamlit** 构建，专注于快速 MVP 开发和数据可视化。本文档涵盖前端架构、开发规范、测试体系和最佳实践。

**技术栈**: Python + Streamlit + Plotly  
**设计风格**: 企业级 B2B 应用  
**开发模式**: 敏捷迭代，快速交付  

---

## 🏗️ 架构设计

### **应用结构**
```
📦 frontend/
├── 📄 main.py                 # 应用入口 + 认证
├── 📁 pages/                  # 多页面应用
│   ├── 2_📁_Projects.py       # 项目管理
│   ├── 3_🔍_Detection.py      # 引用检测（核心）
│   ├── 4_📜_History.py        # 检测历史
│   ├── 5_📚_Templates.py      # Prompt模板
│   ├── 6_📊_Analytics.py      # 数据分析
│   └── 7_👤_Profile.py        # 用户信息
├── 📁 components/             # 可复用组件
│   ├── auth.py               # 认证组件
│   ├── charts.py             # 图表组件
│   ├── sidebar.py            # 侧边栏组件
│   └── ui_components.py      # UI组件库
├── 📁 services/              # API服务封装
│   ├── api_client.py         # HTTP客户端
│   └── detection_service.py  # 检测服务
├── 📁 styles/                # 样式和主题
│   └── enterprise_theme.py   # 企业级主题
└── 📁 utils/                 # 工具函数
    ├── config.py             # 配置管理
    ├── cache_manager.py      # 缓存工具
    └── session.py            # 会话管理
```

### **核心页面功能**

#### 🔍 **引用检测页（核心功能）**
- **Prompt输入**: `st.text_area` + Markdown预览
- **品牌选择**: `st.multiselect` 动态品牌列表
- **模型选择**: `st.selectbox` 支持豆包、DeepSeek、ChatGPT
- **模板应用**: `st.selectbox` 选择Prompt模板
- **实时检测**: `st.button` + `st.progress` 进度显示
- **结果展示**: `st.json` + `st.dataframe` + 可视化图表

#### 📊 **数据分析页**
- **品牌提及率对比**: Plotly柱状图
- **置信度雷达图**: Plotly雷达图
- **时间趋势分析**: Plotly折线图
- **模型性能对比**: 响应时间 + 准确率对比

#### 📜 **检测历史页**
- **历史记录表格**: `st.dataframe` + 分页
- **筛选功能**: 项目、时间、品牌筛选
- **导出功能**: `st.download_button` CSV导出
- **详情查看**: 展开查看完整检测结果

---

## 🎨 企业级UI设计

### **设计原则**
1. **专业性**: 去除emoji装饰，使用简洁文字
2. **一致性**: 统一的颜色、字体、布局
3. **可用性**: 清晰的导航和操作流程
4. **响应式**: 适配不同屏幕尺寸

### **主题系统**
```python
# 企业级主题应用
from styles.enterprise_theme import apply_enterprise_theme, render_enterprise_header

# 页面配置（必须在最前面）
st.set_page_config(
    page_title="页面标题 - GeoLens",
    page_icon="📊",
    layout="wide"
)

# 应用企业级主题
apply_enterprise_theme()

# 渲染企业级标题
render_enterprise_header("页面标题", "页面描述")
```

### **组件规范**
- **按钮**: 使用 `type="primary"` 突出主要操作
- **表格**: 使用 `use_container_width=True` 自适应宽度
- **图表**: 统一使用 Plotly，保持视觉一致性
- **状态**: 使用 `render_status_badge()` 显示状态

---

## 🔧 开发规范

### **页面结构模板**
```python
"""
页面说明
功能描述
"""

import streamlit as st
# ... 其他导入
from styles.enterprise_theme import apply_enterprise_theme, render_enterprise_header
from components.auth import require_auth

# 页面配置
st.set_page_config(
    page_title="页面标题 - GeoLens",
    page_icon="📊",
    layout="wide"
)

# 应用企业级主题
apply_enterprise_theme()

@require_auth
def main():
    """主函数"""
    render_sidebar()
    render_enterprise_header("页面标题", "页面描述")
    
    # 页面内容
    # ...

if __name__ == "__main__":
    main()
```

### **API调用规范**
```python
# 统一使用服务层
from services.detection_service import DetectionService

try:
    service = DetectionService()
    result = service.detect_brands(prompt, brands, models)
    
    if result.get('success'):
        st.success("检测完成")
        # 处理结果
    else:
        st.error(f"检测失败: {result.get('error')}")
        
except Exception as e:
    st.error(f"系统错误: {str(e)}")
```

### **错误处理**
```python
# 防御性编程
available_categories = ["类别1", "类别2", "类别3"]
current_category = data.get('category', '默认类别')

# 安全检查
if current_category not in available_categories:
    current_category = "默认类别"

# 安全使用
index = available_categories.index(current_category)
```

---

## 🧪 测试体系

### **测试架构**

#### **1. 综合测试套件** (`test_comprehensive.py`)
```python
测试维度:
✅ 语法检查 - Python编译验证
✅ 导入测试 - 模块导入验证
✅ 企业级主题 - 主题函数可用性
✅ 页面结构 - 页面结构完整性
✅ 配置系统 - 配置加载验证
✅ 组件完整性 - 组件功能验证
✅ Streamlit兼容性 - API可用性验证
```

#### **2. CI/CD测试管道** (`scripts/ci_frontend_test.py`)
```python
CI步骤:
✅ 环境检查 - Python版本、目录结构
✅ 依赖验证 - 依赖包安装验证
✅ 代码质量 - 代码规范检查
✅ 语法验证 - 语法错误检查
✅ 导入测试 - 模块导入测试
✅ 功能测试 - 核心功能验证
✅ 性能测试 - 性能指标检查
```

### **测试执行**
```bash
# 日常开发测试
cd frontend
python test_comprehensive.py

# CI/CD集成测试
python scripts/ci_frontend_test.py

# 启动测试
streamlit run main.py --server.port 8501
```

### **质量门禁**
- **语法检查**: 100% 通过
- **导入测试**: 100% 成功
- **页面结构**: 100% 正确
- **综合测试**: ≥ 80% 通过率

---

## ⚡ 性能优化

### **缓存策略**
```python
# 数据缓存
@st.cache_data(ttl=300)  # 5分钟缓存
def get_detection_history():
    return api_client.get("/detections")

# 资源缓存
@st.cache_resource
def get_chart_config():
    return plotly_config

# 会话状态
if 'user_data' not in st.session_state:
    st.session_state.user_data = load_user_data()
```

### **加载优化**
- **懒加载**: 按需加载大型组件
- **分页**: 大数据集分页显示
- **异步**: 使用异步API调用
- **压缩**: 图片和资源压缩

---

## 🛠️ 开发工具

### **自动化脚本**
- **`scripts/fix_import_errors.py`** - 导入错误自动修复
- **`scripts/ci_frontend_test.py`** - CI/CD测试管道
- **`frontend/test_comprehensive.py`** - 综合测试套件

### **开发环境**
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
streamlit run main.py --server.port 8501

# 运行测试
python test_comprehensive.py
```

---

## 🚀 部署指南

### **生产部署**
```bash
# 环境变量配置
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 启动应用
streamlit run main.py \
  --server.port $STREAMLIT_SERVER_PORT \
  --server.address $STREAMLIT_SERVER_ADDRESS \
  --server.headless true
```

### **Docker部署**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 📈 监控指标

### **技术指标**
- **页面加载时间**: ≤ 3秒
- **API响应时间**: ≤ 2秒
- **错误率**: ≤ 1%
- **测试通过率**: ≥ 80%

### **用户指标**
- **功能完成率**: ≥ 80%
- **页面跳出率**: ≤ 20%
- **用户满意度**: ≥ 4.0/5.0

---

## 🔮 未来规划

### **短期优化**
- 移动端适配改进
- 性能监控完善
- 用户体验优化

### **长期考虑**
- React迁移评估（用户量 > 1000 DAU）
- 微前端架构
- 国际化支持

---

*文档版本: v1.0*  
*最后更新: 2024-12-19*  
*维护者: 前端开发团队*
