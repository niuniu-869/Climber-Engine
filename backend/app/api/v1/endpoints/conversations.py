#!/usr/bin/env python3
"""
对话相关 API 端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.conversation import (
    ConversationCreate, ConversationResponse, 
    MessageCreate, MessageResponse
)
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 100,
    agent_id: int = None,
    db: Session = Depends(get_db)
):
    """获取对话列表"""
    service = ConversationService(db)
    return service.get_conversations(skip=skip, limit=limit, agent_id=agent_id)


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db)
):
    """创建新对话"""
    service = ConversationService(db)
    return service.create_conversation(conversation_data)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """获取指定对话"""
    service = ConversationService(db)
    conversation = service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """删除对话"""
    service = ConversationService(db)
    success = service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取对话消息"""
    service = ConversationService(db)
    return service.get_messages(conversation_id, skip=skip, limit=limit)


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """添加消息到对话"""
    service = ConversationService(db)
    return service.add_message(conversation_id, message_data)


@router.post("/{conversation_id}/chat")
async def chat(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """与 Agent 对话"""
    service = ConversationService(db)
    
    # 添加用户消息
    user_message = service.add_message(conversation_id, message_data)
    
    # 获取 Agent 响应
    assistant_response = await service.get_agent_response(conversation_id, message_data.content)
    
    return {
        "user_message": user_message,
        "assistant_response": assistant_response
    }