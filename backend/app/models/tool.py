#!/usr/bin/env python3
"""
工具数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tool(Base):
    """工具模型"""
    
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # 工具配置
    tool_type = Column(String(50), nullable=False)  # mcp, builtin, external
    config = Column(JSON)  # 工具的配置信息
    schema = Column(JSON)  # 工具的输入输出模式
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0.0")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    executions = relationship("ToolExecution", back_populates="tool")
    
    def __repr__(self):
        return f"<Tool(id={self.id}, name='{self.name}', type='{self.tool_type}')>"


class ToolExecution(Base):
    """工具执行记录模型"""
    
    __tablename__ = "tool_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    
    # 执行信息
    input_data = Column(JSON)  # 输入参数
    output_data = Column(JSON)  # 输出结果
    status = Column(String(20), default="pending")  # pending, running, success, failed
    error_message = Column(Text)  # 错误信息
    
    # 执行时间
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)  # 执行时长（毫秒）
    
    # 关系
    tool = relationship("Tool", back_populates="executions")
    agent = relationship("Agent", back_populates="tool_executions")
    
    def __repr__(self):
        return f"<ToolExecution(id={self.id}, tool_id={self.tool_id}, status='{self.status}')>"