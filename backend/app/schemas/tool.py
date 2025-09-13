#!/usr/bin/env python3
"""
工具数据模式
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ToolBase(BaseModel):
    """工具基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="工具名称")
    description: Optional[str] = Field(None, description="工具描述")
    tool_type: str = Field(..., description="工具类型: mcp, builtin, external")
    config: Optional[Dict[str, Any]] = Field(None, description="工具配置")
    tool_schema: Optional[Dict[str, Any]] = Field(None, description="工具输入输出模式")
    version: str = Field("1.0.0", description="版本号")


class ToolCreate(ToolBase):
    """创建工具的数据模式"""
    pass


class ToolUpdate(BaseModel):
    """更新工具的数据模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    tool_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    version: Optional[str] = None


class ToolResponse(ToolBase):
    """工具响应数据模式"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ToolExecutionBase(BaseModel):
    """工具执行基础模式"""
    agent_id: int = Field(..., description="执行 Agent ID")
    input_data: Dict[str, Any] = Field(..., description="输入参数")


class ToolExecutionCreate(ToolExecutionBase):
    """创建工具执行的数据模式"""
    pass


class ToolExecutionResponse(ToolExecutionBase):
    """工具执行响应数据模式"""
    id: int
    tool_id: int
    output_data: Optional[Dict[str, Any]] = None
    status: str
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    
    class Config:
        from_attributes = True


class ToolSummary(BaseModel):
    """工具摘要信息"""
    id: int
    name: str
    tool_type: str
    is_active: bool
    
    class Config:
        from_attributes = True