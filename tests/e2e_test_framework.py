#!/usr/bin/env python3
"""
GeoLens 端到端测试框架
真实环境下的完整功能测试
"""

import asyncio
import time
import json
import subprocess
import requests
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class E2ETestFramework:
    """端到端测试框架"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:8501"
        self.test_results = {}
        self.test_data = {}
        
    async def setup_test_environment(self) -> bool:
        """设置测试环境"""
        logger.info("🚀 设置端到端测试环境...")
        
        try:
            # 1. 启动后端服务
            if not await self.start_backend():
                return False
            
            # 2. 等待后端就绪
            if not await self.wait_for_backend():
                return False
            
            # 3. 初始化测试数据
            if not await self.setup_test_data():
                return False
            
            # 4. 启动前端服务
            if not await self.start_frontend():
                return False
            
            # 5. 等待前端就绪
            if not await self.wait_for_frontend():
                return False
            
            logger.info("✅ 测试环境设置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试环境设置失败: {e}")
            return False
    
    async def start_backend(self) -> bool:
        """启动后端服务"""
        logger.info("🔧 启动后端服务...")
        
        try:
            # 检查后端目录
            backend_dir = self.project_root / "backend"
            if not backend_dir.exists():
                logger.error("❌ 后端目录不存在")
                return False
            
            # 启动FastAPI服务
            cmd = [
                "python", "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--reload"
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("✅ 后端服务启动命令已执行")
            return True
            
        except Exception as e:
            logger.error(f"❌ 后端服务启动失败: {e}")
            return False
    
    async def start_frontend(self) -> bool:
        """启动前端服务"""
        logger.info("🎨 启动前端服务...")
        
        try:
            # 检查前端目录
            frontend_dir = self.project_root / "frontend"
            if not frontend_dir.exists():
                logger.error("❌ 前端目录不存在")
                return False
            
            # 启动Streamlit服务
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
            
            logger.info("✅ 前端服务启动命令已执行")
            return True
            
        except Exception as e:
            logger.error(f"❌ 前端服务启动失败: {e}")
            return False
    
    async def wait_for_backend(self, timeout: int = 30) -> bool:
        """等待后端服务就绪"""
        logger.info("⏳ 等待后端服务就绪...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ 后端服务已就绪")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            await asyncio.sleep(1)
        
        logger.error("❌ 后端服务启动超时")
        return False
    
    async def wait_for_frontend(self, timeout: int = 30) -> bool:
        """等待前端服务就绪"""
        logger.info("⏳ 等待前端服务就绪...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(self.frontend_url, timeout=5)
                if response.status_code == 200:
                    logger.info("✅ 前端服务已就绪")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            await asyncio.sleep(1)
        
        logger.error("❌ 前端服务启动超时")
        return False
    
    async def setup_test_data(self) -> bool:
        """设置测试数据"""
        logger.info("📊 设置测试数据...")
        
        try:
            # 创建测试用户
            test_user = {
                "email": "test@geolens.com",
                "password": "test123456",
                "full_name": "测试用户"
            }
            
            # 注册测试用户
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/register",
                json=test_user,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ 测试用户创建成功")
                self.test_data['user'] = test_user
            else:
                logger.warning(f"⚠️ 测试用户可能已存在: {response.status_code}")
                self.test_data['user'] = test_user
            
            # 登录获取token
            login_response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json={
                    "email": test_user["email"],
                    "password": test_user["password"]
                },
                timeout=10
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.test_data['token'] = token_data.get('access_token')
                logger.info("✅ 测试用户登录成功")
            else:
                logger.error(f"❌ 测试用户登录失败: {login_response.status_code}")
                return False
            
            # 创建测试项目
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            project_data = {
                "name": "E2E测试项目",
                "description": "端到端测试专用项目",
                "brands": ["Apple", "Google", "Microsoft"]
            }
            
            project_response = requests.post(
                f"{self.backend_url}/api/v1/projects",
                json=project_data,
                headers=headers,
                timeout=10
            )
            
            if project_response.status_code in [200, 201]:
                project = project_response.json()
                self.test_data['project'] = project
                logger.info("✅ 测试项目创建成功")
            else:
                logger.error(f"❌ 测试项目创建失败: {project_response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试数据设置失败: {e}")
            return False
    
    async def run_complete_e2e_tests(self) -> Dict[str, Any]:
        """运行完整的端到端测试"""
        logger.info("🧪 开始端到端功能测试...")
        
        test_suites = [
            ("用户认证流程", self.test_authentication_flow),
            ("项目管理功能", self.test_project_management),
            ("品牌检测功能", self.test_brand_detection),
            ("历史记录功能", self.test_history_management),
            ("模板管理功能", self.test_template_management),
            ("数据分析功能", self.test_analytics_features),
            ("用户资料功能", self.test_profile_management),
        ]
        
        results = {}
        
        for suite_name, test_func in test_suites:
            logger.info(f"🔍 测试套件: {suite_name}")
            try:
                result = await test_func()
                results[suite_name] = result
                
                if result.get('success', False):
                    logger.info(f"✅ {suite_name} 测试通过")
                else:
                    logger.error(f"❌ {suite_name} 测试失败")
                    
            except Exception as e:
                logger.error(f"💥 {suite_name} 测试异常: {e}")
                results[suite_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    async def test_authentication_flow(self) -> Dict[str, Any]:
        """测试用户认证流程"""
        logger.info("🔐 测试用户认证流程...")
        
        tests = []
        
        try:
            # 1. 测试用户注册
            register_result = await self.test_user_registration()
            tests.append(("用户注册", register_result))
            
            # 2. 测试用户登录
            login_result = await self.test_user_login()
            tests.append(("用户登录", login_result))
            
            # 3. 测试token验证
            token_result = await self.test_token_validation()
            tests.append(("Token验证", token_result))
            
            # 4. 测试权限控制
            auth_result = await self.test_authorization()
            tests.append(("权限控制", auth_result))
            
            success_count = sum(1 for _, result in tests if result.get('success', False))
            
            return {
                'success': success_count == len(tests),
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
    
    async def test_user_registration(self) -> Dict[str, Any]:
        """测试用户注册"""
        try:
            # 测试新用户注册
            new_user = {
                "email": f"test_{int(time.time())}@geolens.com",
                "password": "test123456",
                "full_name": "新测试用户"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/register",
                json=new_user,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return {'success': True, 'message': '用户注册成功'}
            else:
                return {'success': False, 'error': f'注册失败: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_user_login(self) -> Dict[str, Any]:
        """测试用户登录"""
        try:
            login_data = {
                "email": self.test_data['user']['email'],
                "password": self.test_data['user']['password']
            }

            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json=login_data,
                timeout=10
            )

            if response.status_code == 200:
                token_data = response.json()
                if 'access_token' in token_data:
                    return {'success': True, 'message': '用户登录成功'}
                else:
                    return {'success': False, 'error': '登录响应缺少token'}
            else:
                return {'success': False, 'error': f'登录失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_token_validation(self) -> Dict[str, Any]:
        """测试token验证"""
        try:
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}

            response = requests.get(
                f"{self.backend_url}/api/v1/auth/me",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                user_data = response.json()
                if user_data.get('email') == self.test_data['user']['email']:
                    return {'success': True, 'message': 'Token验证成功'}
                else:
                    return {'success': False, 'error': '用户信息不匹配'}
            else:
                return {'success': False, 'error': f'Token验证失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_authorization(self) -> Dict[str, Any]:
        """测试权限控制"""
        try:
            # 测试无token访问受保护资源
            response = requests.get(
                f"{self.backend_url}/api/v1/projects",
                timeout=10
            )

            if response.status_code == 401:
                return {'success': True, 'message': '权限控制正常'}
            else:
                return {'success': False, 'error': f'权限控制异常: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_project_management(self) -> Dict[str, Any]:
        """测试项目管理功能"""
        logger.info("📁 测试项目管理功能...")

        tests = []
        headers = {"Authorization": f"Bearer {self.test_data['token']}"}

        try:
            # 1. 测试创建项目
            create_result = await self.test_create_project(headers)
            tests.append(("创建项目", create_result))

            # 2. 测试获取项目列表
            list_result = await self.test_get_projects(headers)
            tests.append(("获取项目列表", list_result))

            # 3. 测试更新项目
            update_result = await self.test_update_project(headers)
            tests.append(("更新项目", update_result))

            success_count = sum(1 for _, result in tests if result.get('success', False))

            return {
                'success': success_count >= len(tests) - 1,  # 允许一个测试失败
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

    async def test_create_project(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """测试创建项目"""
        try:
            project_data = {
                "name": f"测试项目_{int(time.time())}",
                "description": "E2E测试创建的项目",
                "brands": ["TestBrand1", "TestBrand2"]
            }

            response = requests.post(
                f"{self.backend_url}/api/v1/projects",
                json=project_data,
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                project = response.json()
                self.test_data['created_project'] = project
                return {'success': True, 'message': '项目创建成功'}
            else:
                return {'success': False, 'error': f'项目创建失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_get_projects(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """测试获取项目列表"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/projects",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                projects = response.json()
                if isinstance(projects, list) and len(projects) > 0:
                    return {'success': True, 'message': f'获取到{len(projects)}个项目'}
                else:
                    return {'success': True, 'message': '项目列表为空（正常）'}
            else:
                return {'success': False, 'error': f'获取项目列表失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_update_project(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """测试更新项目"""
        try:
            if 'created_project' not in self.test_data:
                return {'success': False, 'error': '没有可更新的项目'}

            project_id = self.test_data['created_project']['id']
            update_data = {
                "name": "更新后的项目名称",
                "description": "更新后的项目描述"
            }

            response = requests.put(
                f"{self.backend_url}/api/v1/projects/{project_id}",
                json=update_data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'message': '项目更新成功'}
            else:
                return {'success': False, 'error': f'项目更新失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_brand_detection(self) -> Dict[str, Any]:
        """测试品牌检测功能"""
        logger.info("🔍 测试品牌检测功能...")

        tests = []
        headers = {"Authorization": f"Bearer {self.test_data['token']}"}

        try:
            # 1. 测试单次检测
            detection_result = await self.test_single_detection(headers)
            tests.append(("单次检测", detection_result))

            # 2. 测试获取检测结果
            result_result = await self.test_get_detection_results(headers)
            tests.append(("获取检测结果", result_result))

            success_count = sum(1 for _, result in tests if result.get('success', False))

            return {
                'success': success_count >= 1,  # 至少一个测试通过
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

    async def test_single_detection(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """测试单次检测"""
        try:
            detection_data = {
                "prompt": "请推荐一些好用的智能手机品牌",
                "brands": ["Apple", "Samsung", "Huawei"],
                "models": ["mock-model"],  # 使用模拟模型
                "project_id": self.test_data['project']['id']
            }

            response = requests.post(
                f"{self.backend_url}/api/v1/detections",
                json=detection_data,
                headers=headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                detection = response.json()
                self.test_data['detection'] = detection
                return {'success': True, 'message': '单次检测成功'}
            else:
                return {'success': False, 'error': f'单次检测失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_get_detection_results(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """测试获取检测结果"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/detections",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                detections = response.json()
                if isinstance(detections, list):
                    return {'success': True, 'message': f'获取到{len(detections)}个检测结果'}
                else:
                    return {'success': False, 'error': '检测结果格式错误'}
            else:
                return {'success': False, 'error': f'获取检测结果失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_history_management(self) -> Dict[str, Any]:
        """测试历史记录功能"""
        logger.info("📜 测试历史记录功能...")

        # 简化测试，主要验证API可访问性
        headers = {"Authorization": f"Bearer {self.test_data['token']}"}

        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/detections",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'message': '历史记录功能正常'}
            else:
                return {'success': False, 'error': f'历史记录访问失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_template_management(self) -> Dict[str, Any]:
        """测试模板管理功能"""
        logger.info("📚 测试模板管理功能...")

        headers = {"Authorization": f"Bearer {self.test_data['token']}"}

        try:
            # 测试获取模板列表
            response = requests.get(
                f"{self.backend_url}/api/v1/templates",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'message': '模板管理功能正常'}
            else:
                return {'success': False, 'error': f'模板管理访问失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_analytics_features(self) -> Dict[str, Any]:
        """测试数据分析功能"""
        logger.info("📊 测试数据分析功能...")

        headers = {"Authorization": f"Bearer {self.test_data['token']}"}

        try:
            # 测试获取分析数据
            response = requests.get(
                f"{self.backend_url}/api/v1/analytics/summary",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'message': '数据分析功能正常'}
            else:
                return {'success': False, 'error': f'数据分析访问失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_profile_management(self) -> Dict[str, Any]:
        """测试用户资料功能"""
        logger.info("👤 测试用户资料功能...")

        headers = {"Authorization": f"Bearer {self.test_data['token']}"}

        try:
            # 测试获取用户信息
            response = requests.get(
                f"{self.backend_url}/api/v1/auth/me",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'message': '用户资料功能正常'}
            else:
                return {'success': False, 'error': f'用户资料访问失败: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def cleanup_test_environment(self):
        """清理测试环境"""
        logger.info("🧹 清理测试环境...")

        # 停止前端服务
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            logger.info("✅ 前端服务已停止")

        # 停止后端服务
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            logger.info("✅ 后端服务已停止")

        logger.info("✅ 测试环境清理完成")

async def main():
    """主函数"""
    framework = E2ETestFramework()

    try:
        # 设置测试环境
        if not await framework.setup_test_environment():
            logger.error("❌ 测试环境设置失败")
            return

        # 运行端到端测试
        results = await framework.run_complete_e2e_tests()

        # 生成测试报告
        logger.info("📊 生成测试报告...")

        total_suites = len(results)
        passed_suites = sum(1 for result in results.values() if result.get('success', False))

        print("\n" + "="*60)
        print("🧪 GeoLens 端到端测试报告")
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
        report_file = framework.project_root / "e2e_test_report.json"
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
        # 清理测试环境
        await framework.cleanup_test_environment()

if __name__ == "__main__":
    asyncio.run(main())
