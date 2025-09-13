#!/usr/bin/env python3
"""
知识库业务逻辑服务
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeBase, KnowledgeItem
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate,
    KnowledgeItemCreate, KnowledgeItemUpdate
)


class KnowledgeService:
    """知识库服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_knowledge_bases(
        self, 
        skip: int = 0, 
        limit: int = 100,
        kb_type: Optional[str] = None
    ) -> List[KnowledgeBase]:
        """获取知识库列表"""
        query = self.db.query(KnowledgeBase)
        
        if kb_type:
            query = query.filter(KnowledgeBase.kb_type == kb_type)
        
        return query.offset(skip).limit(limit).all()
    
    def get_knowledge_base(self, kb_id: int) -> Optional[KnowledgeBase]:
        """获取指定知识库"""
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    def create_knowledge_base(self, kb_data: KnowledgeBaseCreate) -> KnowledgeBase:
        """创建知识库"""
        kb = KnowledgeBase(
            name=kb_data.name,
            description=kb_data.description,
            kb_type=kb_data.kb_type,
            config=kb_data.config
        )
        
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        
        return kb
    
    def update_knowledge_base(self, kb_id: int, kb_data: KnowledgeBaseUpdate) -> Optional[KnowledgeBase]:
        """更新知识库"""
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return None
        
        update_data = kb_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(kb, field, value)
        
        self.db.commit()
        self.db.refresh(kb)
        
        return kb
    
    def delete_knowledge_base(self, kb_id: int) -> bool:
        """删除知识库"""
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return False
        
        self.db.delete(kb)
        self.db.commit()
        
        return True
    
    def get_knowledge_items(
        self, 
        kb_id: int, 
        skip: int = 0, 
        limit: int = 100,
        content_type: Optional[str] = None
    ) -> List[KnowledgeItem]:
        """获取知识条目列表"""
        query = self.db.query(KnowledgeItem).filter(KnowledgeItem.knowledge_base_id == kb_id)
        
        if content_type:
            query = query.filter(KnowledgeItem.content_type == content_type)
        
        return query.offset(skip).limit(limit).all()
    
    def get_knowledge_item(self, item_id: int) -> Optional[KnowledgeItem]:
        """获取指定知识条目"""
        return self.db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    
    def create_knowledge_item(self, kb_id: int, item_data: KnowledgeItemCreate) -> KnowledgeItem:
        """创建知识条目"""
        item = KnowledgeItem(
            knowledge_base_id=kb_id,
            title=item_data.title,
            content=item_data.content,
            content_type=item_data.content_type,
            source=item_data.source,
            tags=item_data.tags,
            metadata=item_data.metadata
        )
        
        self.db.add(item)
        
        # 更新知识库条目计数
        kb = self.get_knowledge_base(kb_id)
        if kb:
            kb.item_count += 1
        
        self.db.commit()
        self.db.refresh(item)
        
        return item
    
    def update_knowledge_item(self, item_id: int, item_data: KnowledgeItemUpdate) -> Optional[KnowledgeItem]:
        """更新知识条目"""
        item = self.get_knowledge_item(item_id)
        if not item:
            return None
        
        update_data = item_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        self.db.commit()
        self.db.refresh(item)
        
        return item
    
    def delete_knowledge_item(self, item_id: int) -> bool:
        """删除知识条目"""
        item = self.get_knowledge_item(item_id)
        if not item:
            return False
        
        kb_id = item.knowledge_base_id
        self.db.delete(item)
        
        # 更新知识库条目计数
        kb = self.get_knowledge_base(kb_id)
        if kb and kb.item_count > 0:
            kb.item_count -= 1
        
        self.db.commit()
        
        return True
    
    async def search_knowledge(self, query: str, kb_id: Optional[int] = None, limit: int = 10) -> List[KnowledgeItem]:
        """搜索知识库"""
        # TODO: 实现向量搜索和语义搜索
        db_query = self.db.query(KnowledgeItem)
        
        if kb_id:
            db_query = db_query.filter(KnowledgeItem.knowledge_base_id == kb_id)
        
        # 简单的文本搜索
        db_query = db_query.filter(
            KnowledgeItem.content.contains(query) | 
            KnowledgeItem.title.contains(query)
        )
        
        return db_query.limit(limit).all()