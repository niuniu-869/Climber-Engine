#!/usr/bin/env python3
"""
数据库配置和初始化
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库表"""
    # 导入所有模型以确保它们被注册到 Base.metadata
    from app.models import (
        agent, conversation, tool, knowledge,
        user, coding_session, skill_assessment, 
        learning_task, technical_debt
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)