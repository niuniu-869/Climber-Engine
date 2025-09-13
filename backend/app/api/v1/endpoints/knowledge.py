#!/usr/bin/env python3
"""
知识库相关 API 端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse,
    KnowledgeItemCreate, KnowledgeItemUpdate, KnowledgeItemResponse
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


# 知识库管理
@router.get("/bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 100,
    kb_type: str = None,
    db: Session = Depends(get_db)
):
    """获取知识库列表"""
    service = KnowledgeService(db)
    return service.get_knowledge_bases(skip=skip, limit=limit, kb_type=kb_type)


@router.post("/bases", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    """创建知识库"""
    service = KnowledgeService(db)
    return service.create_knowledge_base(kb_data)


@router.get("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db)
):
    """获取指定知识库"""
    service = KnowledgeService(db)
    kb = service.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    return kb


@router.put("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: int,
    kb_data: KnowledgeBaseUpdate,
    db: Session = Depends(get_db)
):
    """更新知识库"""
    service = KnowledgeService(db)
    kb = service.update_knowledge_base(kb_id, kb_data)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    return kb


@router.delete("/bases/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db)
):
    """删除知识库"""
    service = KnowledgeService(db)
    success = service.delete_knowledge_base(kb_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )


# 知识条目管理
@router.get("/bases/{kb_id}/items", response_model=List[KnowledgeItemResponse])
async def list_knowledge_items(
    kb_id: int,
    skip: int = 0,
    limit: int = 100,
    content_type: str = None,
    db: Session = Depends(get_db)
):
    """获取知识条目列表"""
    service = KnowledgeService(db)
    return service.get_knowledge_items(
        kb_id, 
        skip=skip, 
        limit=limit, 
        content_type=content_type
    )


@router.post("/bases/{kb_id}/items", response_model=KnowledgeItemResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_item(
    kb_id: int,
    item_data: KnowledgeItemCreate,
    db: Session = Depends(get_db)
):
    """创建知识条目"""
    service = KnowledgeService(db)
    return service.create_knowledge_item(kb_id, item_data)


@router.get("/items/{item_id}", response_model=KnowledgeItemResponse)
async def get_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """获取指定知识条目"""
    service = KnowledgeService(db)
    item = service.get_knowledge_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge item not found"
        )
    return item


@router.put("/items/{item_id}", response_model=KnowledgeItemResponse)
async def update_knowledge_item(
    item_id: int,
    item_data: KnowledgeItemUpdate,
    db: Session = Depends(get_db)
):
    """更新知识条目"""
    service = KnowledgeService(db)
    item = service.update_knowledge_item(item_id, item_data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge item not found"
        )
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """删除知识条目"""
    service = KnowledgeService(db)
    success = service.delete_knowledge_item(item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge item not found"
        )


@router.post("/search")
async def search_knowledge(
    query: str,
    kb_id: int = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """搜索知识库"""
    service = KnowledgeService(db)
    results = await service.search_knowledge(query, kb_id=kb_id, limit=limit)
    return {"query": query, "results": results}