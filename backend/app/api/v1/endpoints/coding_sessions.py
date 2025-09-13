#!/usr/bin/env python3
"""
编程会话相关 API 端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.coding_session import CodingSession
from app.schemas.coding_session import CodingSessionCreate, CodingSessionUpdate, CodingSessionResponse
from app.services.coding_session_service import CodingSessionService

router = APIRouter()


@router.get("/", response_model=List[CodingSessionResponse])
async def list_coding_sessions(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """获取编程会话列表"""
    service = CodingSessionService(db)
    return service.get_coding_sessions(skip=skip, limit=limit, user_id=user_id)


@router.post("/", response_model=CodingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_coding_session(
    session_data: CodingSessionCreate,
    db: Session = Depends(get_db)
):
    """创建新的编程会话"""
    service = CodingSessionService(db)
    return service.create_coding_session(session_data)


@router.get("/{session_id}", response_model=CodingSessionResponse)
async def get_coding_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """获取指定编程会话"""
    service = CodingSessionService(db)
    session = service.get_coding_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding session not found"
        )
    return session


@router.put("/{session_id}", response_model=CodingSessionResponse)
async def update_coding_session(
    session_id: int,
    session_data: CodingSessionUpdate,
    db: Session = Depends(get_db)
):
    """更新编程会话"""
    service = CodingSessionService(db)
    session = service.update_coding_session(session_id, session_data)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding session not found"
        )
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coding_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """删除编程会话"""
    service = CodingSessionService(db)
    success = service.delete_coding_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding session not found"
        )


@router.post("/{session_id}/start")
async def start_coding_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """开始编程会话"""
    service = CodingSessionService(db)
    success = service.start_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding session not found"
        )
    return {"message": "Coding session started successfully"}


@router.post("/{session_id}/end")
async def end_coding_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """结束编程会话"""
    service = CodingSessionService(db)
    success = service.end_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding session not found"
        )
    return {"message": "Coding session ended successfully"}


@router.get("/{session_id}/code-records")
async def get_session_code_records(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取会话的代码记录"""
    service = CodingSessionService(db)
    return service.get_session_code_records(session_id, skip=skip, limit=limit)


@router.get("/{session_id}/analysis")
async def get_session_analysis(
    session_id: int,
    db: Session = Depends(get_db)
):
    """获取会话分析报告"""
    service = CodingSessionService(db)
    analysis = service.get_session_analysis(session_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding session not found"
        )
    return analysis