#!/usr/bin/env python3
"""
学习任务相关 API 端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.learning_task import LearningTask
from app.schemas.learning_task import LearningTaskCreate, LearningTaskUpdate, LearningTaskResponse
from app.services.learning_task_service import LearningTaskService

router = APIRouter()


@router.get("/", response_model=List[LearningTaskResponse])
async def list_learning_tasks(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    status: str = None,
    priority: str = None,
    db: Session = Depends(get_db)
):
    """获取学习任务列表"""
    service = LearningTaskService(db)
    return service.get_learning_tasks(
        skip=skip, 
        limit=limit, 
        user_id=user_id,
        status=status,
        priority=priority
    )


@router.post("/", response_model=LearningTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_task(
    task_data: LearningTaskCreate,
    db: Session = Depends(get_db)
):
    """创建新的学习任务"""
    service = LearningTaskService(db)
    return service.create_learning_task(task_data)


@router.get("/{task_id}", response_model=LearningTaskResponse)
async def get_learning_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取指定学习任务"""
    service = LearningTaskService(db)
    task = service.get_learning_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning task not found"
        )
    return task


@router.put("/{task_id}", response_model=LearningTaskResponse)
async def update_learning_task(
    task_id: int,
    task_data: LearningTaskUpdate,
    db: Session = Depends(get_db)
):
    """更新学习任务"""
    service = LearningTaskService(db)
    task = service.update_learning_task(task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning task not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_learning_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """删除学习任务"""
    service = LearningTaskService(db)
    success = service.delete_learning_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning task not found"
        )


@router.post("/{task_id}/start")
async def start_learning_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """开始学习任务"""
    service = LearningTaskService(db)
    success = service.start_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning task not found"
        )
    return {"message": "Learning task started successfully"}


@router.post("/{task_id}/complete")
async def complete_learning_task(
    task_id: int,
    completion_notes: str = None,
    db: Session = Depends(get_db)
):
    """完成学习任务"""
    service = LearningTaskService(db)
    success = service.complete_task(task_id, completion_notes)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning task not found"
        )
    return {"message": "Learning task completed successfully"}


@router.post("/{task_id}/pause")
async def pause_learning_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """暂停学习任务"""
    service = LearningTaskService(db)
    success = service.pause_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning task not found"
        )
    return {"message": "Learning task paused successfully"}


@router.post("/generate")
async def generate_learning_tasks(
    user_id: int,
    skill_gaps: List[str] = None,
    learning_goals: List[str] = None,
    db: Session = Depends(get_db)
):
    """基于用户技能缺口生成学习任务"""
    service = LearningTaskService(db)
    tasks = await service.generate_learning_tasks(user_id, skill_gaps, learning_goals)
    return tasks


@router.get("/user/{user_id}/recommendations")
async def get_task_recommendations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取个性化学习任务推荐"""
    service = LearningTaskService(db)
    recommendations = await service.get_task_recommendations(user_id)
    return recommendations


@router.get("/user/{user_id}/progress")
async def get_learning_progress(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取学习进度统计"""
    service = LearningTaskService(db)
    progress = service.get_learning_progress(user_id, days)
    return progress