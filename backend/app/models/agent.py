#!/usr/bin/env python3
"""
Agent 数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Agent(Base):
    """Agent 模型"""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    type = Column(String(50), nullable=False)  # summary, training, tool_server
    
    # Agent 配置
    config = Column(JSON)  # 存储 Agent 的配置信息
    prompt_template = Column(Text)  # Agent 的提示词模板
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0.0")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    conversations = relationship("Conversation", back_populates="agent")
    tool_executions = relationship("ToolExecution", back_populates="agent")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}')>"