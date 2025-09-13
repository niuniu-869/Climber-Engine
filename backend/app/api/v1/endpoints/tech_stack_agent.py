#!/usr/bin/env python3
"""
技术栈总结Agent API端点
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.services.tech_stack_summary_agent import TechStackSummaryAgent
from app.services.tech_stack_data_service import TechStackDataService
from app.schemas.learning_progress import (
    TechStackAssetResponse, TechStackDebtResponse, 
    LearningProgressSummaryResponse, LearningProgressDashboard
)
from pydantic import BaseModel

router = APIRouter()

# 创建全局Agent实例
tech_stack_agent = TechStackSummaryAgent()


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    user_id: Optional[int] = None
    force_run: bool = False


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    status: str
    message: Optional[str] = None
    analyzed_users: Optional[int] = None
    total_sessions_processed: Optional[int] = None
    total_assets_updated: Optional[int] = None
    total_debts_identified: Optional[int] = None
    analysis_time: Optional[str] = None
    user_results: Optional[List[Dict[str, Any]]] = None


class AgentStatusResponse(BaseModel):
    """Agent状态响应模型"""
    enabled: bool
    last_analysis_time: Optional[str] = None
    should_run: bool
    config: Dict[str, Any]


class TechStackStatistics(BaseModel):
    """技术栈统计模型"""
    total_technologies: int
    assets_count: int
    debts_count: int
    average_proficiency: float
    total_learning_hours: float
    category_breakdown: Dict[str, Dict[str, int]]
    top_skills: List[Dict[str, Any]]


@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """
    获取技术栈总结Agent状态
    
    Returns:
        Agent状态信息
    """
    try:
        status_info = tech_stack_agent.get_analysis_status()
        return AgentStatusResponse(**status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def run_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    手动触发技术栈分析
    
    Args:
        request: 分析请求参数
        background_tasks: 后台任务
        db: 数据库会话
    
    Returns:
        分析结果
    """
    try:
        # 检查是否应该运行分析
        if not request.force_run and not tech_stack_agent.should_run_analysis():
            return AnalysisResponse(
                status="skipped",
                message="Analysis not needed at this time. Use force_run=true to override."
            )
        
        # 如果指定了用户ID，验证用户是否存在
        if request.user_id:
            data_service = TechStackDataService(db)
            user = data_service.get_user_by_id(request.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {request.user_id} not found"
                )
        
        # 运行分析
        result = tech_stack_agent.run_analysis(user_id=request.user_id)
        
        return AnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze/async", response_model=Dict[str, str])
async def run_analysis_async(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    异步运行技术栈分析
    
    Args:
        request: 分析请求参数
        background_tasks: 后台任务
    
    Returns:
        任务状态信息
    """
    try:
        # 添加后台任务
        background_tasks.add_task(
            tech_stack_agent.run_analysis,
            user_id=request.user_id
        )
        
        return {
            "status": "started",
            "message": "Analysis started in background",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start async analysis: {str(e)}"
        )


@router.get("/users/{user_id}/assets", response_model=List[TechStackAssetResponse])
async def get_user_tech_assets(
    user_id: int,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取用户的技术栈资产
    
    Args:
        user_id: 用户ID
        category: 技术分类过滤
        is_active: 是否活跃过滤
        db: 数据库会话
    
    Returns:
        技术栈资产列表
    """
    try:
        data_service = TechStackDataService(db)
        
        # 验证用户是否存在
        user = data_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        assets = data_service.get_tech_stack_assets(
            user_id=user_id,
            category=category,
            is_active=is_active
        )
        
        return [TechStackAssetResponse.from_orm(asset) for asset in assets]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tech assets: {str(e)}"
        )


@router.get("/users/{user_id}/debts", response_model=List[TechStackDebtResponse])
async def get_user_tech_debts(
    user_id: int,
    status_filter: Optional[str] = None,
    urgency_level: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取用户的技术栈负债
    
    Args:
        user_id: 用户ID
        status_filter: 状态过滤
        urgency_level: 紧急程度过滤
        is_active: 是否活跃过滤
        db: 数据库会话
    
    Returns:
        技术栈负债列表
    """
    try:
        data_service = TechStackDataService(db)
        
        # 验证用户是否存在
        user = data_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        debts = data_service.get_tech_stack_debts(
            user_id=user_id,
            status=status_filter,
            urgency_level=urgency_level,
            is_active=is_active
        )
        
        return [TechStackDebtResponse.from_orm(debt) for debt in debts]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tech debts: {str(e)}"
        )


@router.get("/users/{user_id}/high-priority-debts", response_model=List[TechStackDebtResponse])
async def get_user_high_priority_debts(
    user_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取用户的高优先级技术栈负债
    
    Args:
        user_id: 用户ID
        limit: 最大返回数量
        db: 数据库会话
    
    Returns:
        高优先级技术栈负债列表
    """
    try:
        data_service = TechStackDataService(db)
        
        # 验证用户是否存在
        user = data_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        debts = data_service.get_high_priority_debts(user_id=user_id, limit=limit)
        
        return [TechStackDebtResponse.from_orm(debt) for debt in debts]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get high priority debts: {str(e)}"
        )


@router.get("/users/{user_id}/progress-summaries", response_model=List[LearningProgressSummaryResponse])
async def get_user_progress_summaries(
    user_id: int,
    report_period: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取用户的学习进度总结
    
    Args:
        user_id: 用户ID
        report_period: 报告周期过滤
        limit: 最大返回数量
        db: 数据库会话
    
    Returns:
        学习进度总结列表
    """
    try:
        data_service = TechStackDataService(db)
        
        # 验证用户是否存在
        user = data_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        summaries = data_service.get_learning_progress_summaries(
            user_id=user_id,
            report_period=report_period,
            limit=limit
        )
        
        return [LearningProgressSummaryResponse.from_orm(summary) for summary in summaries]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress summaries: {str(e)}"
        )


@router.get("/users/{user_id}/statistics", response_model=TechStackStatistics)
async def get_user_tech_statistics(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户的技术栈统计信息
    
    Args:
        user_id: 用户ID
        db: 数据库会话
    
    Returns:
        技术栈统计信息
    """
    try:
        data_service = TechStackDataService(db)
        
        # 验证用户是否存在
        user = data_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # 获取资产统计
        asset_stats = data_service.get_tech_stack_asset_statistics(user_id)
        
        # 获取负债统计
        debts = data_service.get_tech_stack_debts(user_id, is_active=True)
        
        # 获取MCP会话统计
        mcp_stats = data_service.get_mcp_session_statistics(user_id)
        
        return TechStackStatistics(
            total_technologies=asset_stats['total_assets'] + len(debts),
            assets_count=asset_stats['total_assets'],
            debts_count=len(debts),
            average_proficiency=asset_stats['average_proficiency'],
            total_learning_hours=mcp_stats['total_duration_hours'],
            category_breakdown={
                'assets': asset_stats['category_distribution'],
                'debts': {}
            },
            top_skills=asset_stats['top_skills']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tech statistics: {str(e)}"
        )


@router.get("/users/{user_id}/mcp-sessions-stats")
async def get_user_mcp_sessions_stats(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    获取用户的MCP会话统计信息
    
    Args:
        user_id: 用户ID
        days: 统计天数
        db: 数据库会话
    
    Returns:
        MCP会话统计信息
    """
    try:
        data_service = TechStackDataService(db)
        
        # 验证用户是否存在
        user = data_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        since = datetime.utcnow() - timedelta(days=days) if days > 0 else None
        stats = data_service.get_mcp_session_statistics(user_id, since=since)
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get MCP session stats: {str(e)}"
        )


@router.get("/config")
async def get_agent_config():
    """
    获取Agent配置信息
    
    Returns:
        Agent配置
    """
    try:
        return tech_stack_agent.config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent config: {str(e)}"
        )


@router.post("/reload-config")
async def reload_agent_config():
    """
    重新加载Agent配置
    
    Returns:
        操作结果
    """
    try:
        # 重新创建Agent实例以加载新配置
        global tech_stack_agent
        tech_stack_agent = TechStackSummaryAgent()
        
        return {
            "status": "success",
            "message": "Agent configuration reloaded successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload agent config: {str(e)}"
        )