"""
端到端测试配置文件
"""

import pytest
import os
import asyncio
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.services.ai import AIServiceFactory
from app.services.mention_detection import MentionDetectionService


@pytest.fixture(scope="session")
def e2e_config() -> Dict[str, Any]:
    """端到端测试配置"""
    return {
        "doubao_api_key": "fb429f70-7037-4e2b-bc44-e98b14685cc0",
        "deepseek_api_key": "sk-b3e19280c908402e90ed28b986fbc2f5",
        "doubao_model": "Doubao-1.5-lite-32k",
        "deepseek_model": "DeepSeek-R1",
        "test_timeout": 30,  # 真实API调用超时时间
        "retry_attempts": 2   # 重试次数
    }


@pytest.fixture
def skip_if_no_api_keys(e2e_config):
    """如果没有API密钥则跳过测试"""
    # API密钥已经在配置中硬编码，所以不需要跳过
    pass


@pytest.fixture
async def e2e_db_session() -> AsyncSession:
    """端到端测试专用数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
def ai_factory() -> AIServiceFactory:
    """AI服务工厂"""
    return AIServiceFactory()


@pytest.fixture
def mention_service() -> MentionDetectionService:
    """引用检测服务"""
    return MentionDetectionService()


@pytest.fixture
def test_brands() -> list:
    """测试用品牌列表"""
    return ["Notion", "Obsidian", "Roam Research"]


@pytest.fixture
def test_prompts() -> Dict[str, str]:
    """测试用Prompt"""
    return {
        "collaboration_tools": "推荐几个适合团队协作的知识管理工具",
        "note_taking": "有哪些好用的笔记软件？",
        "productivity": "提高工作效率的工具有哪些推荐？",
        "project_management": "推荐一些项目管理和任务跟踪的工具"
    }


@pytest.fixture
def test_project_data() -> Dict[str, Any]:
    """测试项目数据"""
    return {
        "project_id": "e2e-test-project",
        "user_id": "e2e-test-user"
    }


# 设置环境变量以确保AI服务能够正确初始化
@pytest.fixture(scope="session", autouse=True)
def setup_e2e_environment(e2e_config):
    """设置端到端测试环境变量"""
    os.environ["DOUBAO_API_KEY"] = e2e_config["doubao_api_key"]
    os.environ["DEEPSEEK_API_KEY"] = e2e_config["deepseek_api_key"]
    
    # 设置测试标志
    os.environ["E2E_TESTING"] = "true"
    
    yield
    
    # 清理环境变量
    os.environ.pop("E2E_TESTING", None)


@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# pytest标记
pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]
