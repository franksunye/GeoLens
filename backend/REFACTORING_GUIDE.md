# 🔧 GeoLens 重构迁移指南

## 📋 重构概述

本重构旨在解决代码重复、架构不一致和维护困难等问题，建立统一、可扩展的服务架构。

## 🎯 重构目标

### 已解决的问题
1. ✅ **服务层重复**: 统一 `mention_detection.py` 和 `mention_detection_service.py`
2. ✅ **架构不一致**: 采用统一的异步架构模式
3. ✅ **品牌检测分散**: 创建统一的品牌检测服务
4. ✅ **配置管理混乱**: 扩展配置管理支持多AI模型

### 新增功能
1. ✅ **服务基类**: 提供统一的服务架构和依赖注入
2. ✅ **策略模式**: 支持多种品牌检测策略
3. ✅ **并行/串行执行**: 灵活的AI模型调用方式
4. ✅ **批量处理**: 支持批量引用检测
5. ✅ **策略比较**: 比较不同检测策略的效果

## 🔄 迁移步骤

### 第一阶段: 新服务集成 (推荐)

#### 1. 使用新的统一服务

**旧代码**:
```python
from app.services.mention_detection import MentionDetectionService

service = MentionDetectionService()
result = await service.check_mentions(prompt, brands, models, project_id)
```

**新代码**:
```python
from app.services.mention_detection_unified import (
    UnifiedMentionDetectionService, 
    MentionDetectionConfig
)

config = MentionDetectionConfig(
    models=["doubao", "deepseek"],
    api_keys={"DOUBAO_API_KEY": "xxx", "DEEPSEEK_API_KEY": "yyy"},
    parallel_execution=True
)

async with UnifiedMentionDetectionService() as service:
    result = await service.execute_detection(
        project_id=project_id,
        user_id=user_id,
        prompt=prompt,
        brands=brands,
        config=config
    )
```

#### 2. 使用新的品牌检测服务

**旧代码**:
```python
from app.services.brand_detection import analyze_brand_mentions

results = analyze_brand_mentions(text, brands)
```

**新代码**:
```python
from app.services.brand_detection_service import (
    BrandDetectionService, 
    DetectionStrategy
)

service = BrandDetectionService()
results = service.detect_brands(
    text=text, 
    brands=brands, 
    strategy=DetectionStrategy.IMPROVED
)
```

#### 3. 使用新的API端点

**旧端点**: `POST /api/check-mention`
**新端点**: `POST /api/v1/mention-detection/detect`

**新功能端点**:
- `POST /api/v1/mention-detection/detect-brands` - 仅品牌检测
- `POST /api/v1/mention-detection/compare-strategies` - 策略比较
- `POST /api/v1/mention-detection/batch-detect` - 批量检测

### 第二阶段: 逐步替换 (可选)

#### 1. 更新导入语句

创建兼容性导入文件:
```python
# app/services/mention_detection_compat.py
from app.services.mention_detection_unified import UnifiedMentionDetectionService

# 向后兼容的别名
MentionDetectionService = UnifiedMentionDetectionService
```

#### 2. 更新测试文件

```python
# 旧测试
from app.services.mention_detection import MentionDetectionService

# 新测试
from app.services.mention_detection_unified import UnifiedMentionDetectionService
from app.services.mention_detection_unified import MentionDetectionConfig
```

#### 3. 更新配置使用

```python
# 旧配置
from app.core.config import settings
api_key = settings.doubao_api_key

# 新配置
from app.core.config import settings
config = settings.get_ai_model_config("doubao")
api_key = config["api_key"]
```

## 📁 文件映射关系

### 重构前 → 重构后

| 旧文件 | 新文件 | 状态 | 说明 |
|--------|--------|------|------|
| `mention_detection.py` | `mention_detection_unified.py` | ✅ 替换 | 统一的引用检测服务 |
| `mention_detection_service.py` | `mention_detection_unified.py` | ✅ 合并 | 功能已整合 |
| `brand_detection.py` | `brand_detection_service.py` | ✅ 扩展 | 新增策略模式 |
| - | `base.py` | ✅ 新增 | 服务基类 |
| - | `mention_detection_unified.py` | ✅ 新增 | 统一API |

### 保留文件 (向后兼容)

| 文件 | 状态 | 说明 |
|------|------|------|
| `mention_detection.py` | 🔄 保留 | 暂时保留，标记为废弃 |
| `mention_detection_service.py` | 🔄 保留 | 暂时保留，标记为废弃 |
| `brand_detection.py` | ✅ 保留 | 继续使用，被新服务包装 |

## 🧪 测试迁移

### 1. 单元测试更新

```python
# 新的测试结构
import pytest
from app.services.mention_detection_unified import UnifiedMentionDetectionService
from app.services.brand_detection_service import BrandDetectionService

@pytest.mark.asyncio
async def test_unified_mention_detection():
    async with UnifiedMentionDetectionService() as service:
        # 测试逻辑
        pass

def test_brand_detection_strategies():
    service = BrandDetectionService()
    # 测试不同策略
    pass
```

### 2. 集成测试更新

```python
# 测试新的API端点
async def test_new_api_endpoints():
    # 测试 /api/v1/mention-detection/detect
    # 测试 /api/v1/mention-detection/batch-detect
    pass
```

## 🔧 配置更新

### 环境变量新增

```bash
# .env 文件新增
DEFAULT_DETECTION_STRATEGY=improved
MAX_CONCURRENT_DETECTIONS=5
DETECTION_TIMEOUT=60
BRAND_DETECTION_CACHE_TTL=3600

# 新增AI模型支持
OPENAI_API_KEY=your_openai_key
CLAUDE_API_KEY=your_claude_key
```

### 配置使用示例

```python
from app.core.config import settings

# 获取AI模型配置
doubao_config = settings.get_ai_model_config("doubao")

# 检查可用的AI提供商
available_providers = settings.get_available_ai_providers()

# 环境检查
if settings.is_development():
    # 开发环境特定逻辑
    pass
```

## 📈 性能优化

### 1. 并行执行

```python
# 启用并行执行以提高性能
config = MentionDetectionConfig(
    models=["doubao", "deepseek", "openai"],
    api_keys=api_keys,
    parallel_execution=True  # 并行调用AI模型
)
```

### 2. 批量处理

```python
# 批量处理多个检测请求
batch_request = BatchDetectionRequest(
    requests=[req1, req2, req3],
    max_concurrent=3
)
result = await batch_detect_mentions(batch_request)
```

### 3. 策略选择

```python
# 根据需求选择检测策略
# 简单快速: DetectionStrategy.SIMPLE
# 准确全面: DetectionStrategy.IMPROVED  
# 最佳效果: DetectionStrategy.HYBRID
```

## 🚨 注意事项

### 1. 向后兼容性

- 旧的API端点暂时保留，但建议迁移到新端点
- 旧的服务类暂时可用，但会在未来版本中移除
- 数据库结构保持不变，无需迁移数据

### 2. 性能影响

- 新架构可能在初始化时稍慢（依赖注入开销）
- 并行执行可显著提高多模型检测性能
- 策略模式可能增加内存使用

### 3. 错误处理

- 新服务提供更详细的错误信息
- 支持部分失败的批量操作
- 改进的超时和重试机制

## 📅 迁移时间表

### 立即可用 (已完成)
- ✅ 新服务类和API端点
- ✅ 向后兼容的配置
- ✅ 基础测试覆盖

### 1-2周内
- 🔄 更新现有测试用例
- 🔄 添加新功能的测试
- 🔄 性能基准测试

### 1个月内
- 📋 标记旧服务为废弃
- 📋 完整的文档更新
- 📋 生产环境验证

### 2个月内
- 📋 移除旧服务代码
- 📋 清理向后兼容代码
- 📋 最终性能优化

## 🆘 故障排除

### 常见问题

1. **导入错误**: 确保新的依赖已安装
2. **配置错误**: 检查环境变量设置
3. **性能问题**: 调整并发设置和超时参数
4. **测试失败**: 更新测试用例以匹配新的API

### 获取帮助

- 查看新的API文档: `/docs`
- 运行健康检查: `GET /api/v1/mention-detection/health`
- 查看可用策略: `GET /api/v1/mention-detection/strategies`

---

**重构完成后，GeoLens将拥有更清晰的架构、更好的性能和更强的可扩展性！** 🚀
