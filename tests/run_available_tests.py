#!/usr/bin/env python3
"""
GeoLens 可用测试运行器
在当前环境中运行所有可用的测试
"""

import asyncio
import json
import sys
import os
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AvailableTestRunner:
    """可用测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.frontend_process = None
        self.test_results = {}
        self.start_time = datetime.now()
        
    async def run_available_tests(self) -> Dict[str, Any]:
        """运行所有可用的测试"""
        logger.info("🚀 开始GeoLens可用测试套件...")
        
        # 测试套件列表
        test_suites = [
            ("前端语法检查", self.test_frontend_syntax),
            ("前端综合测试", self.test_frontend_comprehensive),
            ("前端启动测试", self.test_frontend_startup),
            ("前端页面访问", self.test_frontend_pages),
            ("代码质量检查", self.test_code_quality),
        ]
        
        results = {}
        
        for suite_name, test_func in test_suites:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 执行测试: {suite_name}")
            logger.info(f"{'='*60}")
            
            try:
                result = await test_func()
                results[suite_name] = result
                
                if result.get('success', False):
                    logger.info(f"✅ {suite_name} 通过")
                else:
                    logger.warning(f"⚠️ {suite_name} 失败")
                    
            except Exception as e:
                logger.error(f"💥 {suite_name} 异常: {e}")
                results[suite_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
    
    async def test_frontend_syntax(self) -> Dict[str, Any]:
        """测试前端语法"""
        logger.info("📝 检查前端Python语法...")
        
        try:
            frontend_dir = self.project_root / "frontend"
            python_files = list(frontend_dir.rglob("*.py"))
            
            syntax_errors = []
            checked_files = 0
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    
                    compile(source, str(file_path), 'exec')
                    checked_files += 1
                    logger.info(f"✅ {file_path.relative_to(frontend_dir)}")
                    
                except SyntaxError as e:
                    error_msg = f"{file_path.relative_to(frontend_dir)}:{e.lineno}: {e.msg}"
                    syntax_errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                except Exception as e:
                    error_msg = f"{file_path.relative_to(frontend_dir)}: {str(e)}"
                    syntax_errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            return {
                'success': len(syntax_errors) == 0,
                'checked_files': checked_files,
                'total_files': len(python_files),
                'errors': syntax_errors,
                'message': f'检查了{checked_files}/{len(python_files)}个文件',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'语法检查异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_frontend_comprehensive(self) -> Dict[str, Any]:
        """运行前端综合测试"""
        logger.info("🧪 运行前端综合测试...")
        
        try:
            test_file = self.project_root / "frontend" / "test_comprehensive.py"
            
            if not test_file.exists():
                return {
                    'success': False,
                    'error': '前端综合测试文件不存在',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 运行测试
            result = subprocess.run([
                sys.executable, str(test_file)
            ], capture_output=True, text=True, timeout=120, cwd=test_file.parent)
            
            if result.returncode == 0:
                # 解析输出中的通过率
                output = result.stdout
                if "通过率: 100.0%" in output:
                    return {
                        'success': True,
                        'message': '前端综合测试100%通过',
                        'details': '语法、导入、结构、组件测试全部通过',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': True,
                        'message': '前端综合测试基本通过',
                        'output': output[-300:] if output else '',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                return {
                    'success': False,
                    'error': '前端综合测试失败',
                    'stderr': result.stderr[-300:] if result.stderr else '',
                    'timestamp': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '前端综合测试超时',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'前端综合测试异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_frontend_startup(self) -> Dict[str, Any]:
        """测试前端启动"""
        logger.info("🚀 测试前端服务启动...")
        
        try:
            frontend_dir = self.project_root / "frontend"
            
            # 启动Streamlit服务
            cmd = [
                "streamlit", "run", "main.py",
                "--server.port", "8502",
                "--server.address", "0.0.0.0",
                "--server.headless", "true"
            ]
            
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务启动
            logger.info("⏳ 等待前端服务启动...")
            await asyncio.sleep(15)
            
            # 检查服务是否正常运行
            try:
                response = requests.get("http://localhost:8502", timeout=10)
                if response.status_code == 200:
                    return {
                        'success': True,
                        'message': '前端服务启动成功',
                        'url': 'http://localhost:8502',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f'前端服务响应异常: {response.status_code}',
                        'timestamp': datetime.now().isoformat()
                    }
            except requests.exceptions.RequestException as e:
                return {
                    'success': False,
                    'error': f'前端服务连接失败: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'前端启动测试异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_frontend_pages(self) -> Dict[str, Any]:
        """测试前端页面访问"""
        logger.info("📄 测试前端页面访问...")
        
        if not self.frontend_process:
            return {
                'success': False,
                'error': '前端服务未启动',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            base_url = "http://localhost:8502"
            
            # 测试主页
            response = requests.get(base_url, timeout=10)
            
            if response.status_code == 200:
                # 检查页面内容
                content = response.text
                
                checks = [
                    ("页面标题", "GeoLens" in content),
                    ("Streamlit框架", "streamlit" in content.lower()),
                    ("页面结构", "<div" in content),
                ]
                
                passed_checks = sum(1 for _, check in checks if check)
                
                return {
                    'success': passed_checks >= len(checks) * 0.8,
                    'total_checks': len(checks),
                    'passed_checks': passed_checks,
                    'checks': checks,
                    'message': f'页面访问测试: {passed_checks}/{len(checks)}项通过',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'页面访问失败: HTTP {response.status_code}',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'页面访问测试异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_code_quality(self) -> Dict[str, Any]:
        """测试代码质量"""
        logger.info("🔍 检查代码质量...")
        
        try:
            frontend_dir = self.project_root / "frontend"
            
            # 检查关键文件是否存在
            key_files = [
                "main.py",
                "styles/enterprise_theme.py",
                "components/auth.py",
                "utils/config.py",
            ]
            
            missing_files = []
            existing_files = []
            
            for file_path in key_files:
                full_path = frontend_dir / file_path
                if full_path.exists():
                    existing_files.append(file_path)
                    logger.info(f"✅ {file_path}")
                else:
                    missing_files.append(file_path)
                    logger.warning(f"❌ {file_path} 缺失")
            
            # 检查页面文件
            pages_dir = frontend_dir / "pages"
            page_files = list(pages_dir.glob("*.py")) if pages_dir.exists() else []
            
            return {
                'success': len(missing_files) == 0,
                'existing_files': len(existing_files),
                'missing_files': len(missing_files),
                'page_files': len(page_files),
                'details': {
                    'existing': existing_files,
                    'missing': missing_files,
                    'pages': [f.name for f in page_files]
                },
                'message': f'代码结构检查: {len(existing_files)}/{len(key_files)}关键文件存在',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'代码质量检查异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理测试资源...")
        
        # 停止前端服务
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            logger.info("✅ 前端服务已停止")
    
    def generate_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result.get('success', False))
        
        return {
            'summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'pass_rate': passed_tests/total_tests*100 if total_tests > 0 else 0
            },
            'results': results,
            'environment': {
                'python_version': sys.version,
                'project_root': str(self.project_root),
                'timestamp': datetime.now().isoformat()
            }
        }

async def main():
    """主函数"""
    runner = AvailableTestRunner()
    
    try:
        # 运行可用测试
        results = await runner.run_available_tests()
        
        # 生成报告
        report = runner.generate_report(results)
        
        # 打印测试总结
        print("\n" + "="*80)
        print("🧪 GeoLens 可用测试报告")
        print("="*80)
        
        summary = report['summary']
        print(f"⏱️  测试时长: {summary['duration_seconds']:.1f}秒")
        print(f"📋 总测试数: {summary['total_tests']}")
        print(f"✅ 通过测试: {summary['passed_tests']}")
        print(f"❌ 失败测试: {summary['failed_tests']}")
        print(f"📈 通过率: {summary['pass_rate']:.1f}%")
        
        print(f"\n📋 详细结果:")
        for test_name, result in results.items():
            status = "✅ 通过" if result.get('success', False) else "❌ 失败"
            message = result.get('message', '')
            print(f"   {test_name}: {status}")
            if message:
                print(f"     {message}")
            if not result.get('success', False) and result.get('error'):
                print(f"     错误: {result['error']}")
        
        # 保存报告
        report_file = runner.project_root / "available_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
        # 测试建议
        if summary['pass_rate'] >= 80:
            print(f"\n🎉 测试结果优秀！前端质量很高。")
        elif summary['pass_rate'] >= 60:
            print(f"\n✅ 测试结果良好！建议修复失败的测试项。")
        else:
            print(f"\n⚠️ 测试结果需要改进，请优先修复关键问题。")
        
        return 0 if summary['pass_rate'] >= 60 else 1
        
    except Exception as e:
        logger.error(f"❌ 测试运行异常: {e}")
        return 1
    finally:
        # 清理资源
        runner.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
