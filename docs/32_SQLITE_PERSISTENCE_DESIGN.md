# 🗄️ SQLite本地持久化设计文档

## 📋 设计概述

### 🎯 设计目标
采用SQLite作为本地数据库，实现引用检测功能的数据持久化，确保开发和测试的敏捷性，避免过早引入云数据库的复杂性。

### 🔄 迁移策略
```
Phase 1: 内存存储 (当前) ✅
    ↓
Phase 2: SQLite本地存储 (Sprint 4) 🔥
    ↓  
Phase 3: Supabase云存储 (Sprint 5) 🚀
```

---

## 🏗️ 数据库设计

### 📊 表结构设计

#### 1. mention_checks (引用检测记录)
```sql
CREATE TABLE mention_checks (
    id TEXT PRIMARY KEY,                    -- UUID
    project_id TEXT NOT NULL,               -- 项目ID
    user_id TEXT NOT NULL,                  -- 用户ID
    prompt TEXT NOT NULL,                   -- 检测Prompt
    brands_checked TEXT NOT NULL,           -- JSON数组: ["Notion", "Obsidian"]
    models_used TEXT NOT NULL,              -- JSON数组: ["doubao", "deepseek"]
    status TEXT NOT NULL DEFAULT 'pending', -- pending/running/completed/failed
    total_mentions INTEGER DEFAULT 0,       -- 总提及次数
    mention_rate REAL DEFAULT 0.0,         -- 提及率
    avg_confidence REAL DEFAULT 0.0,       -- 平均置信度
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata TEXT                           -- JSON: 额外元数据
);

-- 索引
CREATE INDEX idx_mention_checks_project_id ON mention_checks(project_id);
CREATE INDEX idx_mention_checks_user_id ON mention_checks(user_id);
CREATE INDEX idx_mention_checks_created_at ON mention_checks(created_at);
CREATE INDEX idx_mention_checks_status ON mention_checks(status);
```

#### 2. mention_results (模型检测结果)
```sql
CREATE TABLE mention_results (
    id TEXT PRIMARY KEY,                    -- UUID
    check_id TEXT NOT NULL,                 -- 关联mention_checks.id
    model TEXT NOT NULL,                    -- 模型名称: doubao/deepseek/chatgpt
    response_text TEXT NOT NULL,            -- AI回答原文
    processing_time_ms INTEGER,             -- 处理时间(毫秒)
    error_message TEXT,                     -- 错误信息(如果有)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (check_id) REFERENCES mention_checks(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_mention_results_check_id ON mention_results(check_id);
CREATE INDEX idx_mention_results_model ON mention_results(model);
```

#### 3. brand_mentions (品牌提及详情)
```sql
CREATE TABLE brand_mentions (
    id TEXT PRIMARY KEY,                    -- UUID
    result_id TEXT NOT NULL,                -- 关联mention_results.id
    brand TEXT NOT NULL,                    -- 品牌名称
    mentioned BOOLEAN NOT NULL,             -- 是否被提及
    confidence_score REAL NOT NULL,         -- 置信度分数
    context_snippet TEXT,                   -- 上下文片段
    position INTEGER,                       -- 提及位置(第几个)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (result_id) REFERENCES mention_results(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_brand_mentions_result_id ON brand_mentions(result_id);
CREATE INDEX idx_brand_mentions_brand ON brand_mentions(brand);
CREATE INDEX idx_brand_mentions_mentioned ON brand_mentions(mentioned);
```

#### 4. prompt_templates (Prompt模板)
```sql
CREATE TABLE prompt_templates (
    id TEXT PRIMARY KEY,                    -- UUID
    user_id TEXT NOT NULL,                  -- 创建用户ID
    name TEXT NOT NULL,                     -- 模板名称
    category TEXT NOT NULL,                 -- 分类: productivity/comparison/recommendation
    template TEXT NOT NULL,                 -- 模板内容
    variables TEXT,                         -- JSON: 变量定义
    description TEXT,                       -- 描述
    usage_count INTEGER DEFAULT 0,          -- 使用次数
    is_public BOOLEAN DEFAULT FALSE,        -- 是否公开
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_prompt_templates_user_id ON prompt_templates(user_id);
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX idx_prompt_templates_is_public ON prompt_templates(is_public);
```

#### 5. analytics_cache (统计分析缓存)
```sql
CREATE TABLE analytics_cache (
    id TEXT PRIMARY KEY,                    -- UUID
    cache_key TEXT UNIQUE NOT NULL,         -- 缓存键
    project_id TEXT,                        -- 项目ID
    brand TEXT,                             -- 品牌名称
    timeframe TEXT,                         -- 时间范围: 7d/30d/90d
    data TEXT NOT NULL,                     -- JSON: 统计数据
    expires_at TIMESTAMP NOT NULL,          -- 过期时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_analytics_cache_key ON analytics_cache(cache_key);
CREATE INDEX idx_analytics_cache_expires_at ON analytics_cache(expires_at);
```

---

## 🔧 技术实现

### 📦 依赖配置

#### requirements.txt 更新
```txt
# 现有依赖...
sqlalchemy>=2.0.0
alembic>=1.12.0
aiosqlite>=0.19.0
```

#### 数据库配置
```python
# app/core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库URL配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./data/geolens.db"
)

# 异步引擎
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True if os.getenv("DEBUG") else False,
    future=True
)

# 会话工厂
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 🏗️ 数据模型

#### SQLAlchemy模型定义
```python
# app/models/mention.py
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MentionCheck(Base):
    __tablename__ = "mention_checks"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    brands_checked = Column(Text, nullable=False)  # JSON
    models_used = Column(Text, nullable=False)     # JSON
    status = Column(String, nullable=False, default="pending", index=True)
    total_mentions = Column(Integer, default=0)
    mention_rate = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now(), index=True)
    completed_at = Column(DateTime)
    metadata = Column(Text)  # JSON
    
    # 关系
    results = relationship("MentionResult", back_populates="check", cascade="all, delete-orphan")

class MentionResult(Base):
    __tablename__ = "mention_results"
    
    id = Column(String, primary_key=True)
    check_id = Column(String, ForeignKey("mention_checks.id"), nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    response_text = Column(Text, nullable=False)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # 关系
    check = relationship("MentionCheck", back_populates="results")
    mentions = relationship("BrandMention", back_populates="result", cascade="all, delete-orphan")

class BrandMention(Base):
    __tablename__ = "brand_mentions"
    
    id = Column(String, primary_key=True)
    result_id = Column(String, ForeignKey("mention_results.id"), nullable=False, index=True)
    brand = Column(String, nullable=False, index=True)
    mentioned = Column(Boolean, nullable=False, index=True)
    confidence_score = Column(Float, nullable=False)
    context_snippet = Column(Text)
    position = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    # 关系
    result = relationship("MentionResult", back_populates="mentions")
```

### 🔄 数据迁移

#### Alembic配置
```python
# alembic/env.py
from app.core.database import Base
from app.models.mention import MentionCheck, MentionResult, BrandMention
from app.models.template import PromptTemplate
from app.models.analytics import AnalyticsCache

target_metadata = Base.metadata
```

#### 初始迁移脚本
```bash
# 初始化Alembic
cd backend
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "Initial migration: mention detection tables"

# 执行迁移
alembic upgrade head
```

---

## 🔄 服务层重构

### 📊 数据访问层 (Repository Pattern)

#### 引用检测Repository
```python
# app/repositories/mention_repository.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from app.models.mention import MentionCheck, MentionResult, BrandMention

class MentionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_check(self, check_data: dict) -> MentionCheck:
        """创建检测记录"""
        check = MentionCheck(**check_data)
        self.db.add(check)
        await self.db.commit()
        await self.db.refresh(check)
        return check
    
    async def get_check_by_id(self, check_id: str) -> Optional[MentionCheck]:
        """根据ID获取检测记录"""
        result = await self.db.execute(
            select(MentionCheck).where(MentionCheck.id == check_id)
        )
        return result.scalar_one_or_none()
    
    async def get_checks_by_project(
        self, 
        project_id: str, 
        page: int = 1, 
        limit: int = 20,
        brand_filter: Optional[str] = None,
        model_filter: Optional[str] = None
    ) -> List[MentionCheck]:
        """获取项目的检测记录"""
        query = select(MentionCheck).where(MentionCheck.project_id == project_id)
        
        if brand_filter:
            query = query.where(MentionCheck.brands_checked.contains(brand_filter))
        
        if model_filter:
            query = query.where(MentionCheck.models_used.contains(model_filter))
        
        query = query.order_by(desc(MentionCheck.created_at))
        query = query.offset((page - 1) * limit).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def save_result(self, result_data: dict) -> MentionResult:
        """保存模型检测结果"""
        result = MentionResult(**result_data)
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result
    
    async def save_mentions(self, mentions_data: List[dict]) -> List[BrandMention]:
        """批量保存品牌提及"""
        mentions = [BrandMention(**data) for data in mentions_data]
        self.db.add_all(mentions)
        await self.db.commit()
        return mentions
```

### 🔄 服务层更新

#### 引用检测服务重构
```python
# app/services/mention_detection.py (更新)
from app.repositories.mention_repository import MentionRepository
from app.core.database import get_db

class MentionDetectionService:
    def __init__(self):
        self.ai_factory = AIServiceFactory()
    
    async def check_mentions(
        self, 
        prompt: str, 
        brands: List[str], 
        models: List[str], 
        project_id: str,
        user_id: str
    ) -> MentionCheckResponse:
        """执行引用检测 - 使用数据库持久化"""
        
        # 获取数据库会话
        async with AsyncSessionLocal() as db:
            repo = MentionRepository(db)
            
            # 创建检测记录
            check_data = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "user_id": user_id,
                "prompt": prompt,
                "brands_checked": json.dumps(brands),
                "models_used": json.dumps(models),
                "status": "running"
            }
            
            check = await repo.create_check(check_data)
            
            try:
                # 并行调用AI模型
                tasks = [
                    self._check_single_model(prompt, brands, model, check.id, repo)
                    for model in models
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 更新检测状态
                check.status = "completed"
                check.completed_at = datetime.utcnow()
                
                # 计算统计信息
                total_mentions = sum(
                    len([m for m in r.mentions if m.mentioned]) 
                    for r in results if isinstance(r, ModelResult)
                )
                
                check.total_mentions = total_mentions
                check.mention_rate = total_mentions / (len(brands) * len(models))
                
                await db.commit()
                
                return MentionCheckResponse(
                    check_id=check.id,
                    status=check.status,
                    results=results,
                    # ... 其他字段
                )
                
            except Exception as e:
                check.status = "failed"
                await db.commit()
                raise
```

---

## 🧪 测试策略

### 📊 数据库测试

#### 测试数据库配置
```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

@pytest.fixture
async def test_db():
    """测试数据库会话"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()
```

#### Repository测试
```python
# tests/unit/test_mention_repository.py
import pytest
from app.repositories.mention_repository import MentionRepository

@pytest.mark.asyncio
async def test_create_check(test_db):
    """测试创建检测记录"""
    repo = MentionRepository(test_db)
    
    check_data = {
        "id": "test-check-id",
        "project_id": "test-project",
        "user_id": "test-user",
        "prompt": "推荐协作工具",
        "brands_checked": '["Notion", "Obsidian"]',
        "models_used": '["doubao", "deepseek"]'
    }
    
    check = await repo.create_check(check_data)
    
    assert check.id == "test-check-id"
    assert check.project_id == "test-project"
    assert check.status == "pending"
```

---

## 🚀 部署和运维

### 📁 目录结构
```
backend/
├── data/                   # SQLite数据库文件
│   ├── geolens.db         # 主数据库
│   └── backups/           # 备份文件
├── alembic/               # 数据库迁移
│   ├── versions/          # 迁移脚本
│   └── env.py            # Alembic配置
├── app/
│   ├── models/           # SQLAlchemy模型
│   ├── repositories/     # 数据访问层
│   └── services/         # 业务逻辑层
└── tests/
    ├── unit/             # 单元测试
    └── integration/      # 集成测试
```

### 🔄 数据备份策略
```python
# scripts/backup_database.py
import shutil
import os
from datetime import datetime

def backup_database():
    """备份SQLite数据库"""
    source = "data/geolens.db"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/backups/geolens_backup_{timestamp}.db"
    
    os.makedirs("data/backups", exist_ok=True)
    shutil.copy2(source, backup_path)
    
    print(f"数据库备份完成: {backup_path}")

if __name__ == "__main__":
    backup_database()
```

---

## 📈 性能优化

### 🔍 查询优化
- 合理使用索引
- 分页查询避免全表扫描
- 使用连接查询减少N+1问题
- 统计数据缓存

### 💾 存储优化
- JSON字段压缩存储
- 定期清理过期数据
- 数据库文件压缩

---

*设计文档版本: v1.0*
*创建时间: 2024-06-05*
*下次更新: Sprint 4 完成后*
