# 🧪 GeoLens 引用检测功能全面测试计划

## 📊 当前测试状态
- **单元测试**: 20/20 通过 ✅ (100%)
- **API集成测试**: 16/21 通过 ✅ (76%)
- **总体通过率**: 36/41 = 88%

## 🎯 测试目标
确保引用检测MVP功能100%稳定可靠，为Sprint 4做好准备。

---

## Phase 1: 修复现有测试问题 (优先级：高)

### 1.1 修复JSON序列化问题
**问题**: datetime对象无法JSON序列化
**影响**: 5个API错误处理测试失败
**解决方案**:
```python
# 在main.py中添加自定义JSON编码器
from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 在FastAPI应用中使用
app = FastAPI(
    title="GeoLens API",
    json_encoder=DateTimeEncoder
)
```

### 1.2 完善错误处理测试
**目标**: 确保所有错误场景都能正确处理
**测试用例**:
- [ ] AI服务超时处理
- [ ] 网络连接失败处理
- [ ] 无效输入参数处理
- [ ] 认证失败处理

---

## Phase 2: 核心功能深度测试 (优先级：高)

### 2.1 引用检测算法测试
**目标**: 验证NER+关键词匹配算法准确率≥95%

#### 测试数据集
```python
test_cases = [
    # 精确匹配
    {
        "text": "我推荐使用Notion作为团队协作工具",
        "brands": ["Notion", "Obsidian"],
        "expected": {"Notion": True, "Obsidian": False}
    },
    # 大小写不敏感
    {
        "text": "notion是个不错的选择",
        "brands": ["Notion"],
        "expected": {"Notion": True}
    },
    # 多品牌提及
    {
        "text": "对比Notion、Obsidian和Roam Research",
        "brands": ["Notion", "Obsidian", "Roam Research"],
        "expected": {"Notion": True, "Obsidian": True, "Roam Research": True}
    },
    # 上下文干扰
    {
        "text": "我不推荐使用Notion，因为有bug",
        "brands": ["Notion"],
        "expected": {"Notion": True}  # 仍然被提及，但置信度应该较低
    }
]
```

#### 准确率测试
```python
def test_algorithm_accuracy():
    """测试算法准确率"""
    correct_predictions = 0
    total_predictions = 0
    
    for case in test_cases:
        result = mention_service._analyze_mentions(
            case["text"], 
            case["brands"]
        )
        
        for mention in result:
            expected = case["expected"][mention.brand]
            actual = mention.mentioned
            
            if expected == actual:
                correct_predictions += 1
            total_predictions += 1
    
    accuracy = correct_predictions / total_predictions
    assert accuracy >= 0.95, f"算法准确率{accuracy:.2%}低于95%要求"
```

### 2.2 置信度评分测试
**目标**: 验证置信度评分的合理性

```python
def test_confidence_scoring():
    """测试置信度评分"""
    # 正面上下文应该有高置信度
    positive_text = "我强烈推荐Notion，它是优秀的工具"
    positive_score = service._calculate_confidence(positive_text, "Notion", 6)
    assert positive_score > 0.8
    
    # 负面上下文应该有较低置信度
    negative_text = "我不推荐Notion，因为有问题"
    negative_score = service._calculate_confidence(negative_text, "Notion", 3)
    assert negative_score < 0.8
    
    # 中性上下文应该有中等置信度
    neutral_text = "Notion是一个协作工具"
    neutral_score = service._calculate_confidence(neutral_text, "Notion", 0)
    assert 0.6 <= neutral_score <= 0.9
```

### 2.3 多模型并行测试
**目标**: 验证多模型并行调用的稳定性

```python
@pytest.mark.asyncio
async def test_parallel_model_calls():
    """测试并行模型调用"""
    start_time = time.time()
    
    result = await mention_service.check_mentions(
        prompt="推荐协作工具",
        brands=["Notion", "Obsidian"],
        models=["doubao", "deepseek", "chatgpt"],
        project_id="test"
    )
    
    end_time = time.time()
    
    # 验证结果
    assert len(result.results) == 3
    assert result.status == "completed"
    
    # 验证并行性能（应该比串行快）
    assert end_time - start_time < 10  # 10秒内完成
    
    # 验证每个模型都有结果
    models_tested = [r.model for r in result.results]
    assert "doubao" in models_tested
    assert "deepseek" in models_tested
    assert "chatgpt" in models_tested
```

---

## Phase 3: 边界条件和压力测试 (优先级：中)

### 3.1 边界条件测试
```python
def test_edge_cases():
    """测试边界条件"""
    # 空输入
    result = service._analyze_mentions("", ["Notion"])
    assert len(result) == 1
    assert not result[0].mentioned
    
    # 超长文本
    long_text = "Notion " * 1000
    result = service._analyze_mentions(long_text, ["Notion"])
    assert result[0].mentioned
    
    # 特殊字符
    special_text = "使用Notion！@#$%^&*()工具"
    result = service._analyze_mentions(special_text, ["Notion"])
    assert result[0].mentioned
    
    # 大量品牌
    many_brands = [f"Brand{i}" for i in range(100)]
    result = service._analyze_mentions("test", many_brands)
    assert len(result) == 100
```

### 3.2 性能压力测试
```python
@pytest.mark.asyncio
async def test_performance_stress():
    """性能压力测试"""
    # 并发请求测试
    tasks = []
    for i in range(50):
        task = mention_service.check_mentions(
            prompt=f"测试请求{i}",
            brands=["Notion"],
            models=["doubao"],
            project_id=f"test-{i}"
        )
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # 验证所有请求都成功
    assert len(results) == 50
    for result in results:
        assert result.status == "completed"
    
    # 验证性能（平均每个请求<2秒）
    avg_time = (end_time - start_time) / 50
    assert avg_time < 2.0
```

---

## Phase 4: 集成和端到端测试 (优先级：中)

### 4.1 完整API流程测试
```python
@pytest.mark.asyncio
async def test_complete_api_workflow():
    """测试完整API工作流程"""
    # 1. 健康检查
    health_response = client.get("/api/v1/api/health")
    assert health_response.status_code == 200
    
    # 2. 执行引用检测
    check_response = client.post("/api/v1/api/check-mention", json={
        "project_id": "test-project",
        "prompt": "推荐协作工具",
        "brands": ["Notion", "Obsidian"],
        "models": ["doubao", "deepseek"]
    })
    assert check_response.status_code == 200
    check_data = check_response.json()
    
    # 3. 查询历史记录
    history_response = client.get("/api/v1/api/get-history", params={
        "project_id": "test-project"
    })
    assert history_response.status_code == 200
    
    # 4. 获取统计分析
    analytics_response = client.get("/api/v1/api/analytics/mentions", params={
        "project_id": "test-project",
        "brand": "Notion"
    })
    assert analytics_response.status_code == 200
    
    # 5. 竞品对比
    compare_response = client.get("/api/v1/api/analytics/compare", params={
        "project_id": "test-project",
        "brands": "Notion,Obsidian"
    })
    assert compare_response.status_code == 200
```

### 4.2 数据一致性测试
```python
def test_data_consistency():
    """测试数据一致性"""
    # 执行检测
    result = mention_service.check_mentions(...)
    
    # 验证数据存储
    stored_data = mention_service.checks_storage[result.check_id]
    assert stored_data["prompt"] == result.prompt
    assert len(stored_data["results"]) == len(result.results)
    
    # 验证统计数据更新
    analytics = mention_service.get_mention_analytics(...)
    assert analytics["total_checks"] > 0
```

---

## Phase 5: 安全和可靠性测试 (优先级：低)

### 5.1 安全测试
```python
def test_security():
    """安全测试"""
    # SQL注入测试
    malicious_input = "'; DROP TABLE users; --"
    response = client.post("/api/v1/api/check-mention", json={
        "project_id": malicious_input,
        "prompt": "test",
        "brands": ["test"],
        "models": ["doubao"]
    })
    # 应该被安全处理，不会导致系统错误
    
    # XSS测试
    xss_input = "<script>alert('xss')</script>"
    response = client.post("/api/v1/api/check-mention", json={
        "prompt": xss_input,
        "brands": ["test"],
        "models": ["doubao"]
    })
    # 应该被正确转义
```

### 5.2 容错性测试
```python
@pytest.mark.asyncio
async def test_fault_tolerance():
    """容错性测试"""
    # 模拟AI服务不可用
    with patch('app.services.ai.doubao.DoubaoProvider.chat') as mock_chat:
        mock_chat.side_effect = Exception("Service unavailable")
        
        result = await mention_service.check_mentions(
            prompt="test",
            brands=["Notion"],
            models=["doubao"],
            project_id="test"
        )
        
        # 应该优雅处理错误
        assert result.status == "completed"
        assert "Error" in result.results[0].response_text
```

---

## 📋 测试执行计划

### Week 1: 修复和核心测试
- [ ] 修复JSON序列化问题
- [ ] 完善错误处理测试
- [ ] 深度测试引用检测算法
- [ ] 验证置信度评分准确性

### Week 2: 性能和集成测试
- [ ] 多模型并行测试
- [ ] 边界条件测试
- [ ] 性能压力测试
- [ ] 完整API流程测试

### Week 3: 安全和可靠性
- [ ] 安全测试
- [ ] 容错性测试
- [ ] 数据一致性验证
- [ ] 最终验收测试

## 🎯 验收标准

### 功能验收
- [ ] 所有单元测试100%通过
- [ ] 所有集成测试100%通过
- [ ] 引用检测算法准确率≥95%
- [ ] API响应时间<2秒(95%请求)

### 质量验收
- [ ] 代码覆盖率≥90%
- [ ] 无严重安全漏洞
- [ ] 错误处理完善
- [ ] 文档完整准确

### 性能验收
- [ ] 支持50+并发请求
- [ ] 内存使用稳定
- [ ] 无内存泄漏
- [ ] 优雅降级处理
