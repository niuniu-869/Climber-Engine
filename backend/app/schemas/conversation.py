#!/usr/bin/env python3
"""
对话数据模式
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from .agent import AgentSummary


class MessageBase(BaseModel):
    """消息基础模式"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., min_length=1, description="消息内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")


class MessageCreate(MessageBase):
    """创建消息的数据模式"""
    pass


class MessageResponse(MessageBase):
    """消息响应数据模式"""
    id: int
    conversation_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """对话基础模式"""
    title: Optional[str] = Field(None, max_length=200, description="对话标题")
    agent_id: int = Field(..., description="关联的 Agent ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="对话元数据")


class ConversationCreate(ConversationBase):
    """创建对话的数据模式"""
    session_id: Optional[str] = Field(None, description="会话 ID")


class ConversationUpdate(BaseModel):
    """更新对话的数据模式"""
    title: Optional[str] = Field(None, max_length=200)
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(ConversationBase):
    """对话响应数据模式"""
    id: int
    session_id: str
    created_at: datetime
    updated_at: datetime
    agent: Optional[AgentSummary] = None
    messages: Optional[List[MessageResponse]] = None
    
    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    """对话摘要信息"""
    id: int
    title: Optional[str]
    session_id: str
    agent_id: int
    message_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True