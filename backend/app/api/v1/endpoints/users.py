#!/usr/bin/env python3
"""
用户相关 API 端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """创建新用户"""
    service = UserService(db)
    return service.create_user(user_data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取指定用户"""
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    service = UserService(db)
    user = service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """删除用户"""
    service = UserService(db)
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.get("/{user_id}/coding-sessions")
async def get_user_coding_sessions(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的编程会话"""
    service = UserService(db)
    return service.get_user_coding_sessions(user_id, skip=skip, limit=limit)


@router.get("/{user_id}/skill-assessments")
async def get_user_skill_assessments(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的技能评估"""
    service = UserService(db)
    return service.get_user_skill_assessments(user_id, skip=skip, limit=limit)


@router.get("/{user_id}/learning-tasks")
async def get_user_learning_tasks(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的学习任务"""
    service = UserService(db)
    return service.get_user_learning_tasks(user_id, skip=skip, limit=limit)


@router.get("/{user_id}/dashboard")
async def get_user_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户仪表板数据"""
    service = UserService(db)
    return service.get_user_dashboard(user_id)