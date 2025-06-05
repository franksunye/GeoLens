"""
引用检测算法准确率测试

验证NER+关键词匹配算法的准确率是否达到≥95%的要求。
"""

import pytest
from app.services.mention_detection import MentionDetectionService


class TestMentionAlgorithmAccuracy:
    """引用检测算法准确率测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.service = MentionDetectionService()
        
        # 准确率测试数据集
        self.test_cases = [
            # 精确匹配测试
            {
                "text": "我推荐使用Notion作为团队协作工具",
                "brands": ["Notion", "Obsidian"],
                "expected": {"Notion": True, "Obsidian": False}
            },
            {
                "text": "Obsidian是一个很好的笔记软件",
                "brands": ["Notion", "Obsidian"],
                "expected": {"Notion": False, "Obsidian": True}
            },
            
            # 大小写不敏感测试
            {
                "text": "我觉得notion是个不错的选择",
                "brands": ["Notion"],
                "expected": {"Notion": True}
            },
            {
                "text": "OBSIDIAN功能很强大",
                "brands": ["Obsidian"],
                "expected": {"Obsidian": True}
            },
            
            # 多品牌提及测试
            {
                "text": "对比Notion、Obsidian和Roam Research这三个工具",
                "brands": ["Notion", "Obsidian", "Roam Research"],
                "expected": {"Notion": True, "Obsidian": True, "Roam Research": True}
            },
            
            # 否定测试
            {
                "text": "我从来没有使用过任何笔记软件",
                "brands": ["Notion", "Obsidian"],
                "expected": {"Notion": False, "Obsidian": False}
            },
            {
                "text": "这个工具很好用，推荐给大家",
                "brands": ["Notion"],
                "expected": {"Notion": False}
            },
            
            # 空文本测试
            {
                "text": "",
                "brands": ["Notion"],
                "expected": {"Notion": False}
            }
        ]
    
    def test_algorithm_accuracy(self):
        """测试算法整体准确率"""
        correct_predictions = 0
        total_predictions = 0
        failed_cases = []
        
        for i, case in enumerate(self.test_cases):
            try:
                # 执行引用检测
                mentions = self.service._analyze_mentions(case["text"], case["brands"])
                
                # 检查每个品牌的预测结果
                for mention in mentions:
                    brand = mention.brand
                    expected = case["expected"][brand]
                    actual = mention.mentioned
                    
                    if expected == actual:
                        correct_predictions += 1
                    else:
                        failed_cases.append({
                            "case_index": i,
                            "text": case["text"],
                            "brand": brand,
                            "expected": expected,
                            "actual": actual,
                            "confidence": mention.confidence_score
                        })
                    
                    total_predictions += 1
                    
            except Exception as e:
                # 记录异常情况
                failed_cases.append({
                    "case_index": i,
                    "text": case["text"],
                    "error": str(e)
                })
                total_predictions += len(case["brands"])
        
        # 计算准确率
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        # 输出详细结果
        print(f"\n=== 算法准确率测试结果 ===")
        print(f"总预测数: {total_predictions}")
        print(f"正确预测数: {correct_predictions}")
        print(f"准确率: {accuracy:.2%}")
        print(f"目标准确率: 95%")
        
        if failed_cases:
            print(f"\n失败案例 ({len(failed_cases)}个):")
            for case in failed_cases[:5]:  # 只显示前5个失败案例
                if "error" in case:
                    print(f"  案例{case['case_index']}: 异常 - {case['error']}")
                else:
                    print(f"  案例{case['case_index']}: {case['brand']} - 期望:{case['expected']}, 实际:{case['actual']}, 置信度:{case.get('confidence', 'N/A')}")
                    print(f"    文本: {case['text'][:50]}...")
        
        # 验证准确率要求
        assert accuracy >= 0.95, f"算法准确率{accuracy:.2%}低于95%要求。失败案例数: {len(failed_cases)}"
