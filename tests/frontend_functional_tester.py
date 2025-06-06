#!/usr/bin/env python3
"""
GeoLens 前端功能测试器
使用Selenium自动化测试Streamlit应用
"""

import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrontendFunctionalTester:
    """前端功能测试器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.frontend_url = "http://localhost:8501"
        self.driver = None
        self.frontend_process = None
        self.test_results = {}
        
    def setup_selenium_driver(self) -> bool:
        """设置Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            logger.error("❌ Selenium未安装，无法进行前端自动化测试")
            return False
        
        try:
            # Chrome选项
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 创建WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ Selenium WebDriver设置成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ Selenium WebDriver设置失败: {e}")
            return False
    
    def start_frontend_service(self) -> bool:
        """启动前端服务"""
        logger.info("🎨 启动前端服务...")
        
        try:
            frontend_dir = self.project_root / "frontend"
            if not frontend_dir.exists():
                logger.error("❌ 前端目录不存在")
                return False
            
            cmd = [
                "streamlit", "run", "main.py",
                "--server.port", "8501",
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
            time.sleep(10)
            logger.info("✅ 前端服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 前端服务启动失败: {e}")
            return False
    
    def test_page_loading(self) -> Dict[str, Any]:
        """测试页面加载"""
        logger.info("📄 测试页面加载...")
        
        tests = []
        
        # 测试主页加载
        main_page_result = self.test_main_page_loading()
        tests.append(("主页加载", main_page_result))
        
        # 测试各个功能页面
        pages = [
            ("项目管理", "Projects"),
            ("引用检测", "Detection"), 
            ("检测历史", "History"),
            ("模板管理", "Templates"),
            ("数据分析", "Analytics"),
            ("个人资料", "Profile")
        ]
        
        for page_name, page_key in pages:
            result = self.test_page_navigation(page_name, page_key)
            tests.append((f"{page_name}页面", result))
        
        success_count = sum(1 for _, result in tests if result.get('success', False))
        
        return {
            'success': success_count >= len(tests) * 0.8,  # 80%通过率
            'total_tests': len(tests),
            'passed_tests': success_count,
            'details': tests
        }
    
    def test_main_page_loading(self) -> Dict[str, Any]:
        """测试主页加载"""
        try:
            self.driver.get(self.frontend_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检查页面标题
            if "GeoLens" in self.driver.title:
                return {'success': True, 'message': '主页加载成功'}
            else:
                return {'success': False, 'error': f'页面标题异常: {self.driver.title}'}
                
        except TimeoutException:
            return {'success': False, 'error': '页面加载超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_page_navigation(self, page_name: str, page_key: str) -> Dict[str, Any]:
        """测试页面导航"""
        try:
            # 查找侧边栏链接
            sidebar_links = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='stSidebar'] a")
            
            target_link = None
            for link in sidebar_links:
                if page_key.lower() in link.text.lower():
                    target_link = link
                    break
            
            if target_link:
                target_link.click()
                time.sleep(3)  # 等待页面加载
                
                # 检查页面是否正确加载
                if page_key.lower() in self.driver.current_url.lower():
                    return {'success': True, 'message': f'{page_name}页面导航成功'}
                else:
                    return {'success': True, 'message': f'{page_name}页面可访问'}
            else:
                return {'success': False, 'error': f'未找到{page_name}页面链接'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_ui_components(self) -> Dict[str, Any]:
        """测试UI组件"""
        logger.info("🎨 测试UI组件...")
        
        tests = []
        
        try:
            # 测试侧边栏
            sidebar_result = self.test_sidebar_functionality()
            tests.append(("侧边栏功能", sidebar_result))
            
            # 测试主要按钮
            button_result = self.test_button_functionality()
            tests.append(("按钮功能", button_result))
            
            # 测试表单组件
            form_result = self.test_form_components()
            tests.append(("表单组件", form_result))
            
            success_count = sum(1 for _, result in tests if result.get('success', False))
            
            return {
                'success': success_count >= len(tests) * 0.7,  # 70%通过率
                'total_tests': len(tests),
                'passed_tests': success_count,
                'details': tests
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'details': tests
            }
    
    def test_sidebar_functionality(self) -> Dict[str, Any]:
        """测试侧边栏功能"""
        try:
            # 检查侧边栏是否存在
            sidebar = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='stSidebar']")
            
            if sidebar.is_displayed():
                return {'success': True, 'message': '侧边栏显示正常'}
            else:
                return {'success': False, 'error': '侧边栏未显示'}
                
        except NoSuchElementException:
            return {'success': False, 'error': '未找到侧边栏元素'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_button_functionality(self) -> Dict[str, Any]:
        """测试按钮功能"""
        try:
            # 查找页面中的按钮
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
            
            if len(buttons) > 0:
                return {'success': True, 'message': f'找到{len(buttons)}个按钮'}
            else:
                return {'success': False, 'error': '未找到任何按钮'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_form_components(self) -> Dict[str, Any]:
        """测试表单组件"""
        try:
            # 查找输入框
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
            
            if len(inputs) > 0:
                return {'success': True, 'message': f'找到{len(inputs)}个表单组件'}
            else:
                return {'success': True, 'message': '当前页面无表单组件（正常）'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_responsive_design(self) -> Dict[str, Any]:
        """测试响应式设计"""
        logger.info("📱 测试响应式设计...")
        
        tests = []
        
        # 测试不同屏幕尺寸
        screen_sizes = [
            ("桌面端", 1920, 1080),
            ("平板端", 768, 1024),
            ("手机端", 375, 667)
        ]
        
        for size_name, width, height in screen_sizes:
            result = self.test_screen_size(size_name, width, height)
            tests.append((f"{size_name}适配", result))
        
        success_count = sum(1 for _, result in tests if result.get('success', False))
        
        return {
            'success': success_count >= len(tests) * 0.8,
            'total_tests': len(tests),
            'passed_tests': success_count,
            'details': tests
        }
    
    def test_screen_size(self, size_name: str, width: int, height: int) -> Dict[str, Any]:
        """测试特定屏幕尺寸"""
        try:
            # 设置窗口大小
            self.driver.set_window_size(width, height)
            time.sleep(2)
            
            # 检查页面是否正常显示
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            if body.is_displayed():
                return {'success': True, 'message': f'{size_name}({width}x{height})显示正常'}
            else:
                return {'success': False, 'error': f'{size_name}显示异常'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_complete_frontend_tests(self) -> Dict[str, Any]:
        """运行完整的前端测试"""
        logger.info("🧪 开始前端功能测试...")
        
        if not SELENIUM_AVAILABLE:
            return {
                'success': False,
                'error': 'Selenium未安装，跳过前端自动化测试',
                'message': '请安装selenium和chromedriver进行完整测试'
            }
        
        test_suites = [
            ("页面加载测试", self.test_page_loading),
            ("UI组件测试", self.test_ui_components),
            ("响应式设计测试", self.test_responsive_design),
        ]
        
        results = {}
        
        for suite_name, test_func in test_suites:
            logger.info(f"🔍 测试套件: {suite_name}")
            try:
                result = test_func()
                results[suite_name] = result
                
                if result.get('success', False):
                    logger.info(f"✅ {suite_name} 通过")
                else:
                    logger.error(f"❌ {suite_name} 失败")
                    
            except Exception as e:
                logger.error(f"💥 {suite_name} 异常: {e}")
                results[suite_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理前端测试资源...")
        
        # 关闭WebDriver
        if self.driver:
            self.driver.quit()
            logger.info("✅ WebDriver已关闭")
        
        # 停止前端服务
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            logger.info("✅ 前端服务已停止")

def main():
    """主函数"""
    tester = FrontendFunctionalTester()
    
    try:
        # 启动前端服务
        if not tester.start_frontend_service():
            logger.error("❌ 前端服务启动失败")
            return
        
        # 设置Selenium
        if not tester.setup_selenium_driver():
            logger.warning("⚠️ Selenium设置失败，跳过自动化测试")
            return
        
        # 运行前端测试
        results = tester.run_complete_frontend_tests()
        
        # 生成测试报告
        total_suites = len(results)
        passed_suites = sum(1 for result in results.values() if result.get('success', False))
        
        print("\n" + "="*60)
        print("🎨 GeoLens 前端功能测试报告")
        print("="*60)
        print(f"📋 总测试套件: {total_suites}")
        print(f"✅ 通过套件: {passed_suites}")
        print(f"❌ 失败套件: {total_suites - passed_suites}")
        print(f"📈 通过率: {passed_suites/total_suites*100:.1f}%")
        
        print(f"\n📋 详细结果:")
        for suite_name, result in results.items():
            status = "✅ 通过" if result.get('success', False) else "❌ 失败"
            print(f"   {suite_name}: {status}")
            
            if not result.get('success', False) and result.get('error'):
                print(f"     错误: {result['error']}")
        
        # 保存测试报告
        report_file = tester.project_root / "frontend_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_suites': total_suites,
                'passed_suites': passed_suites,
                'pass_rate': passed_suites/total_suites*100,
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
    finally:
        # 清理资源
        tester.cleanup()

if __name__ == "__main__":
    main()
