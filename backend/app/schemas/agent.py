#!/usr/bin/env python3
"""
Agent 数据模式
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Agent 基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="Agent 名称")
    description: Optional[str] = Field(None, description="Agent 描述")
    type: str = Field(..., description="Agent 类型: summary, training, tool_server")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent 配置")
    prompt_template: Optional[str] = Field(None, description="提示词模板")
    version: str = Field("1.0.0", description="版本号")


class AgentCreate(AgentBase):
    """创建 Agent 的数据模式"""
    pass


class AgentUpdate(BaseModel):
    """更新 Agent 的数据模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    prompt_template: Optional[str] = None
    is_active: Optional[bool] = None
    version: Optional[str] = None


class AgentResponse(AgentBase):
    """Agent 响应数据模式"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentSummary(BaseModel):
    """Agent 摘要信息"""
    id: int
    name: str
    type: str
    is_active: bool
    
    class Config:
        from_attributes = True