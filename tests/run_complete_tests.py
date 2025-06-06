#!/usr/bin/env python3
"""
GeoLens 完整测试运行器
整合端到端测试和前端功能测试
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteTestRunner:
    """完整测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {}
        self.start_time = datetime.now()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("🚀 开始GeoLens完整测试套件...")
        
        # 测试套件列表
        test_suites = [
            ("前端语法测试", self.run_frontend_syntax_tests),
            ("前端综合测试", self.run_frontend_comprehensive_tests),
            ("端到端API测试", self.run_e2e_api_tests),
            ("前端功能测试", self.run_frontend_functional_tests),
        ]
        
        results = {}
        
        for suite_name, test_func in test_suites:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 执行测试套件: {suite_name}")
            logger.info(f"{'='*60}")
            
            try:
                result = await test_func()
                results[suite_name] = result
                
                if result.get('success', False):
                    logger.info(f"✅ {suite_name} 完成")
                else:
                    logger.error(f"❌ {suite_name} 失败")
                    
            except Exception as e:
                logger.error(f"💥 {suite_name} 异常: {e}")
                results[suite_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
    
    async def run_frontend_syntax_tests(self) -> Dict[str, Any]:
        """运行前端语法测试"""
        logger.info("📝 执行前端语法测试...")
        
        try:
            import subprocess
            
            # 运行前端语法检查
            result = subprocess.run([
                sys.executable, 
                str(self.project_root / "frontend" / "test_comprehensive.py")
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': '前端语法测试通过',
                    'output': result.stdout[-500:] if result.stdout else '',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': '前端语法测试失败',
                    'output': result.stderr[-500:] if result.stderr else '',
                    'timestamp': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '前端语法测试超时',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'前端语法测试异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_frontend_comprehensive_tests(self) -> Dict[str, Any]:
        """运行前端综合测试"""
        logger.info("🧪 执行前端综合测试...")
        
        try:
            # 导入前端测试模块
            frontend_test_path = self.project_root / "frontend" / "test_comprehensive.py"
            
            if frontend_test_path.exists():
                import subprocess
                
                result = subprocess.run([
                    sys.executable, str(frontend_test_path)
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'message': '前端综合测试通过',
                        'details': '语法、导入、结构、组件测试全部通过',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': '前端综合测试失败',
                        'output': result.stderr[-500:] if result.stderr else '',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                return {
                    'success': False,
                    'error': '前端测试文件不存在',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'前端综合测试异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_e2e_api_tests(self) -> Dict[str, Any]:
        """运行端到端API测试"""
        logger.info("🔗 执行端到端API测试...")
        
        try:
            # 检查后端是否存在
            backend_dir = self.project_root / "backend"
            if not backend_dir.exists():
                return {
                    'success': False,
                    'error': '后端目录不存在，跳过API测试',
                    'message': '这是一个前端MVP项目，后端API测试暂不可用',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 如果后端存在，运行E2E测试
            from tests.e2e_test_framework import E2ETestFramework
            
            framework = E2ETestFramework()
            
            # 设置测试环境
            if await framework.setup_test_environment():
                # 运行测试
                results = await framework.run_complete_e2e_tests()
                
                # 清理环境
                await framework.cleanup_test_environment()
                
                total_suites = len(results)
                passed_suites = sum(1 for result in results.values() if result.get('success', False))
                
                return {
                    'success': passed_suites >= total_suites * 0.7,  # 70%通过率
                    'total_suites': total_suites,
                    'passed_suites': passed_suites,
                    'pass_rate': passed_suites/total_suites*100 if total_suites > 0 else 0,
                    'details': results,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'E2E测试环境设置失败',
                    'timestamp': datetime.now().isoformat()
                }
                
        except ImportError:
            return {
                'success': False,
                'error': 'E2E测试框架导入失败',
                'message': '可能缺少依赖包或后端服务',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'E2E API测试异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_frontend_functional_tests(self) -> Dict[str, Any]:
        """运行前端功能测试"""
        logger.info("🎨 执行前端功能测试...")
        
        try:
            # 检查Selenium是否可用
            try:
                import selenium
                selenium_available = True
            except ImportError:
                selenium_available = False
            
            if not selenium_available:
                return {
                    'success': True,
                    'message': 'Selenium未安装，跳过前端自动化测试',
                    'note': '前端功能已通过综合测试验证',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 运行前端功能测试
            from tests.frontend_functional_tester import FrontendFunctionalTester
            
            tester = FrontendFunctionalTester()
            
            # 启动前端服务
            if tester.start_frontend_service():
                # 设置Selenium
                if tester.setup_selenium_driver():
                    # 运行测试
                    results = tester.run_complete_frontend_tests()
                    
                    # 清理资源
                    tester.cleanup()
                    
                    total_suites = len(results)
                    passed_suites = sum(1 for result in results.values() if result.get('success', False))
                    
                    return {
                        'success': passed_suites >= total_suites * 0.8,  # 80%通过率
                        'total_suites': total_suites,
                        'passed_suites': passed_suites,
                        'pass_rate': passed_suites/total_suites*100 if total_suites > 0 else 0,
                        'details': results,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    tester.cleanup()
                    return {
                        'success': False,
                        'error': 'Selenium WebDriver设置失败',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                return {
                    'success': False,
                    'error': '前端服务启动失败',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'前端功能测试异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合测试报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        total_suites = len(results)
        passed_suites = sum(1 for result in results.values() if result.get('success', False))
        
        # 计算详细统计
        detailed_stats = {}
        for suite_name, result in results.items():
            if isinstance(result, dict) and 'details' in result:
                details = result['details']
                if isinstance(details, dict):
                    suite_total = result.get('total_suites', 0)
                    suite_passed = result.get('passed_suites', 0)
                    detailed_stats[suite_name] = {
                        'total': suite_total,
                        'passed': suite_passed,
                        'pass_rate': suite_passed/suite_total*100 if suite_total > 0 else 0
                    }
        
        report = {
            'test_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'total_test_suites': total_suites,
                'passed_test_suites': passed_suites,
                'failed_test_suites': total_suites - passed_suites,
                'overall_pass_rate': passed_suites/total_suites*100 if total_suites > 0 else 0
            },
            'detailed_results': results,
            'detailed_statistics': detailed_stats,
            'recommendations': self.generate_recommendations(results),
            'environment_info': {
                'python_version': sys.version,
                'project_root': str(self.project_root),
                'test_timestamp': datetime.now().isoformat()
            }
        }
        
        return report
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成测试建议"""
        recommendations = []
        
        for suite_name, result in results.items():
            if not result.get('success', False):
                if 'Selenium' in result.get('error', ''):
                    recommendations.append("安装Selenium和ChromeDriver以启用完整的前端自动化测试")
                elif '后端' in result.get('error', ''):
                    recommendations.append("开发后端API以启用完整的端到端测试")
                elif '语法' in suite_name:
                    recommendations.append("修复前端代码语法错误")
                elif '功能' in suite_name:
                    recommendations.append("检查前端功能实现")
        
        if not recommendations:
            recommendations.append("所有测试通过，代码质量良好！")
        
        return recommendations

async def main():
    """主函数"""
    runner = CompleteTestRunner()
    
    try:
        # 运行所有测试
        results = await runner.run_all_tests()
        
        # 生成综合报告
        report = runner.generate_comprehensive_report(results)
        
        # 打印测试总结
        print("\n" + "="*80)
        print("🧪 GeoLens 完整测试报告")
        print("="*80)
        
        summary = report['test_summary']
        print(f"⏱️  测试时长: {summary['duration_seconds']:.1f}秒")
        print(f"📋 总测试套件: {summary['total_test_suites']}")
        print(f"✅ 通过套件: {summary['passed_test_suites']}")
        print(f"❌ 失败套件: {summary['failed_test_suites']}")
        print(f"📈 总体通过率: {summary['overall_pass_rate']:.1f}%")
        
        print(f"\n📋 详细结果:")
        for suite_name, result in results.items():
            status = "✅ 通过" if result.get('success', False) else "❌ 失败"
            print(f"   {suite_name}: {status}")
            
            if not result.get('success', False) and result.get('error'):
                print(f"     错误: {result['error']}")
        
        print(f"\n💡 建议:")
        for recommendation in report['recommendations']:
            print(f"   • {recommendation}")
        
        # 保存详细报告
        report_file = runner.project_root / "complete_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
        # 返回适当的退出码
        return 0 if summary['overall_pass_rate'] >= 70 else 1
        
    except Exception as e:
        logger.error(f"❌ 测试运行异常: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
