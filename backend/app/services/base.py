"""
服务层基类
提供统一的服务架构和依赖注入
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

# 延迟导入避免循环依赖
if TYPE_CHECKING:
    from app.repositories.mention_repository import MentionRepository
    from app.services.ai import AIServiceFactory


class BaseService(ABC):
    """服务基类"""
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self._db = db
        self._ai_factory = None
        self._repository = None
    
    @property
    def db(self) -> AsyncSession:
        """获取数据库会话"""
        if self._db is None:
            raise RuntimeError("Database session not initialized")
        return self._db
    
    @property
    def ai_factory(self) -> "AIServiceFactory":
        """获取AI服务工厂"""
        if self._ai_factory is None:
            from app.services.ai import AIServiceFactory
            self._ai_factory = AIServiceFactory()
        return self._ai_factory

    @property
    def repository(self) -> "MentionRepository":
        """获取数据仓库"""
        if self._repository is None:
            from app.repositories.mention_repository import MentionRepository
            self._repository = MentionRepository(self.db)
        return self._repository
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        if self._db is None:
            from app.core.database import AsyncSessionLocal
            self._db = AsyncSessionLocal()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self._db:
            if exc_type:
                await self._db.rollback()
            else:
                await self._db.commit()
            await self._db.close()


class BusinessService(BaseService):
    """业务服务基类"""
    
    def __init__(self, db: Optional[AsyncSession] = None):
        super().__init__(db)
        self._config = {}
    
    def configure(self, **kwargs) -> 'BusinessService':
        """配置服务参数"""
        self._config.update(kwargs)
        return self
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置参数"""
        return self._config.get(key, default)
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """执行业务逻辑"""
        pass


class ServiceFactory:
    """服务工厂"""
    
    _services = {}
    
    @classmethod
    def register_service(cls, name: str, service_class):
        """注册服务"""
        cls._services[name] = service_class
    
    @classmethod
    def create_service(cls, name: str, **kwargs):
        """创建服务实例"""
        if name not in cls._services:
            raise ValueError(f"Unknown service: {name}")
        return cls._services[name](**kwargs)
    
    @classmethod
    def get_available_services(cls) -> list:
        """获取可用服务列表"""
        return list(cls._services.keys())
