#!/usr/bin/env python3
"""
知识库数据模式
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class KnowledgeBaseBase(BaseModel):
    """知识库基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    kb_type: str = Field("general", description="知识库类型: general, domain_specific, personal")
    config: Optional[Dict[str, Any]] = Field(None, description="知识库配置")


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """创建知识库的数据模式"""
    pass


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库的数据模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class KnowledgeBaseResponse(KnowledgeBaseBase):
    """知识库响应数据模式"""
    id: int
    is_active: bool
    item_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeItemBase(BaseModel):
    """知识条目基础模式"""
    title: Optional[str] = Field(None, max_length=200, description="条目标题")
    content: str = Field(..., min_length=1, description="条目内容")
    content_type: str = Field("text", description="内容类型: text, markdown, code, json")
    source: Optional[str] = Field(None, max_length=500, description="来源信息")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class KnowledgeItemCreate(KnowledgeItemBase):
    """创建知识条目的数据模式"""
    pass


class KnowledgeItemUpdate(BaseModel):
    """更新知识条目的数据模式"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[str] = None
    source: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class KnowledgeItemResponse(KnowledgeItemBase):
    """知识条目响应数据模式"""
    id: int
    knowledge_base_id: int
    embedding_model: Optional[str] = None
    quality_score: float
    relevance_score: float
    access_count: int
    last_accessed: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeSearchResult(BaseModel):
    """知识搜索结果"""
    item: KnowledgeItemResponse
    score: float = Field(..., description="相关性评分")
    highlights: Optional[List[str]] = Field(None, description="高亮片段")


class KnowledgeBaseSummary(BaseModel):
    """知识库摘要信息"""
    id: int
    name: str
    kb_type: str
    item_count: int
    is_active: bool
    
    class Config:
        from_attributes = True