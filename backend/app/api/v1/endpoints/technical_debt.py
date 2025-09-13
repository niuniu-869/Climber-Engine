#!/usr/bin/env python3
"""
技术债务相关 API 端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.technical_debt import TechnicalDebt
from app.schemas.technical_debt import TechnicalDebtCreate, TechnicalDebtUpdate, TechnicalDebtResponse
from app.services.technical_debt_service import TechnicalDebtService

router = APIRouter()


@router.get("/", response_model=List[TechnicalDebtResponse])
async def list_technical_debts(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    severity: str = None,
    category: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取技术债务列表"""
    service = TechnicalDebtService(db)
    return service.get_technical_debts(
        skip=skip, 
        limit=limit, 
        user_id=user_id,
        severity=severity,
        category=category,
        status=status
    )


@router.post("/", response_model=TechnicalDebtResponse, status_code=status.HTTP_201_CREATED)
async def create_technical_debt(
    debt_data: TechnicalDebtCreate,
    db: Session = Depends(get_db)
):
    """创建新的技术债务记录"""
    service = TechnicalDebtService(db)
    return service.create_technical_debt(debt_data)


@router.get("/{debt_id}", response_model=TechnicalDebtResponse)
async def get_technical_debt(
    debt_id: int,
    db: Session = Depends(get_db)
):
    """获取指定技术债务"""
    service = TechnicalDebtService(db)
    debt = service.get_technical_debt(debt_id)
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technical debt not found"
        )
    return debt


@router.put("/{debt_id}", response_model=TechnicalDebtResponse)
async def update_technical_debt(
    debt_id: int,
    debt_data: TechnicalDebtUpdate,
    db: Session = Depends(get_db)
):
    """更新技术债务"""
    service = TechnicalDebtService(db)
    debt = service.update_technical_debt(debt_id, debt_data)
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technical debt not found"
        )
    return debt


@router.delete("/{debt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_technical_debt(
    debt_id: int,
    db: Session = Depends(get_db)
):
    """删除技术债务"""
    service = TechnicalDebtService(db)
    success = service.delete_technical_debt(debt_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technical debt not found"
        )


@router.post("/{debt_id}/resolve")
async def resolve_technical_debt(
    debt_id: int,
    resolution_notes: str = None,
    db: Session = Depends(get_db)
):
    """解决技术债务"""
    service = TechnicalDebtService(db)
    success = service.resolve_debt(debt_id, resolution_notes)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technical debt not found"
        )
    return {"message": "Technical debt resolved successfully"}


@router.post("/analyze")
async def analyze_code_for_debt(
    file_path: str,
    code_content: str,
    user_id: int,
    db: Session = Depends(get_db)
):
    """分析代码并识别技术债务"""
    service = TechnicalDebtService(db)
    analysis = await service.analyze_code_for_debt(file_path, code_content, user_id)
    return analysis


@router.get("/user/{user_id}/summary")
async def get_user_debt_summary(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户技术债务汇总"""
    service = TechnicalDebtService(db)
    summary = service.get_user_debt_summary(user_id)
    return summary


@router.get("/user/{user_id}/trends")
async def get_debt_trends(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取技术债务趋势分析"""
    service = TechnicalDebtService(db)
    trends = service.get_debt_trends(user_id, days)
    return trends


@router.post("/user/{user_id}/recommendations")
async def get_debt_resolution_recommendations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取技术债务解决建议"""
    service = TechnicalDebtService(db)
    recommendations = await service.get_debt_resolution_recommendations(user_id)
    return recommendations


@router.get("/metrics/overview")
async def get_debt_metrics_overview(
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """获取技术债务指标概览"""
    service = TechnicalDebtService(db)
    metrics = service.get_debt_metrics_overview(user_id)
    return metrics