"""
数据访问层 (Repository Pattern)

提供数据库操作的抽象层，封装具体的数据库访问逻辑。
"""

from .mention_repository import MentionRepository

__all__ = ["MentionRepository"]
