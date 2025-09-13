#!/usr/bin/env python3
"""
技能评估相关 API 端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.skill_assessment import SkillAssessment
from app.schemas.skill_assessment import SkillAssessmentCreate, SkillAssessmentUpdate, SkillAssessmentResponse
from app.services.skill_assessment_service import SkillAssessmentService

router = APIRouter()


@router.get("/", response_model=List[SkillAssessmentResponse])
async def list_skill_assessments(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    skill_category: str = None,
    db: Session = Depends(get_db)
):
    """获取技能评估列表"""
    service = SkillAssessmentService(db)
    return service.get_skill_assessments(
        skip=skip, 
        limit=limit, 
        user_id=user_id,
        skill_category=skill_category
    )


@router.post("/", response_model=SkillAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_skill_assessment(
    assessment_data: SkillAssessmentCreate,
    db: Session = Depends(get_db)
):
    """创建新的技能评估"""
    service = SkillAssessmentService(db)
    return service.create_skill_assessment(assessment_data)


@router.get("/{assessment_id}", response_model=SkillAssessmentResponse)
async def get_skill_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """获取指定技能评估"""
    service = SkillAssessmentService(db)
    assessment = service.get_skill_assessment(assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill assessment not found"
        )
    return assessment


@router.put("/{assessment_id}", response_model=SkillAssessmentResponse)
async def update_skill_assessment(
    assessment_id: int,
    assessment_data: SkillAssessmentUpdate,
    db: Session = Depends(get_db)
):
    """更新技能评估"""
    service = SkillAssessmentService(db)
    assessment = service.update_skill_assessment(assessment_id, assessment_data)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill assessment not found"
        )
    return assessment


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """删除技能评估"""
    service = SkillAssessmentService(db)
    success = service.delete_skill_assessment(assessment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill assessment not found"
        )


@router.post("/analyze")
async def analyze_user_skills(
    user_id: int,
    db: Session = Depends(get_db)
):
    """分析用户技能并生成评估报告"""
    service = SkillAssessmentService(db)
    analysis = await service.analyze_user_skills(user_id)
    return analysis


@router.get("/user/{user_id}/radar")
async def get_user_skill_radar(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户技能雷达图数据"""
    service = SkillAssessmentService(db)
    radar_data = service.get_user_skill_radar(user_id)
    return radar_data


@router.get("/user/{user_id}/progress")
async def get_user_skill_progress(
    user_id: int,
    skill_name: str = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取用户技能进步趋势"""
    service = SkillAssessmentService(db)
    progress = service.get_user_skill_progress(user_id, skill_name, days)
    return progress


@router.post("/user/{user_id}/recommendations")
async def get_skill_recommendations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取技能提升建议"""
    service = SkillAssessmentService(db)
    recommendations = await service.get_skill_recommendations(user_id)
    return recommendations