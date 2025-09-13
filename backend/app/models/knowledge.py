#!/usr/bin/env python3
"""
知识库数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class KnowledgeBase(Base):
    """知识库模型"""
    
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # 知识库配置
    kb_type = Column(String(50), default="general")  # general, domain_specific, personal
    config = Column(JSON)  # 知识库配置信息
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    item_count = Column(Integer, default=0)  # 知识条目数量
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    items = relationship("KnowledgeItem", back_populates="knowledge_base", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name='{self.name}', type='{self.kb_type}')>"


class KnowledgeItem(Base):
    """知识条目模型"""
    
    __tablename__ = "knowledge_items"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    
    # 内容信息
    title = Column(String(200))
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, markdown, code, json
    
    # 元数据
    source = Column(String(500))  # 来源信息
    tags = Column(JSON)  # 标签列表
    extra_metadata = Column(JSON)  # 额外元数据
    
    # 向量化信息（用于语义搜索）
    embedding = Column(JSON)  # 向量表示
    embedding_model = Column(String(100))  # 使用的嵌入模型
    
    # 质量评分
    quality_score = Column(Float, default=0.0)  # 内容质量评分
    relevance_score = Column(Float, default=0.0)  # 相关性评分
    
    # 使用统计
    access_count = Column(Integer, default=0)  # 访问次数
    last_accessed = Column(DateTime)  # 最后访问时间
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="items")
    
    def __repr__(self):
        return f"<KnowledgeItem(id={self.id}, title='{self.title}', kb_id={self.knowledge_base_id})>"