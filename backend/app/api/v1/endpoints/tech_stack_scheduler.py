#!/usr/bin/env python3
"""
技术栈调度器API端点
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from datetime import datetime
from pydantic import BaseModel

from app.services.tech_stack_scheduler import get_scheduler

router = APIRouter()


class SchedulerStatusResponse(BaseModel):
    """调度器状态响应模型"""
    is_running: bool
    agent_enabled: bool
    job_stats: Dict[str, Any]
    scheduled_jobs: list
    scheduler_state: Optional[str] = None


class ManualTriggerRequest(BaseModel):
    """手动触发请求模型"""
    user_id: Optional[int] = None
    force_run: bool = False


class ManualTriggerResponse(BaseModel):
    """手动触发响应模型"""
    status: str
    message: Optional[str] = None
    analyzed_users: Optional[int] = None
    total_sessions_processed: Optional[int] = None
    total_assets_updated: Optional[int] = None
    total_debts_identified: Optional[int] = None
    analysis_time: Optional[str] = None


@router.get("/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status():
    """
    获取调度器状态
    
    Returns:
        调度器状态信息
    """
    try:
        scheduler = get_scheduler()
        status_info = scheduler.get_scheduler_status()
        return SchedulerStatusResponse(**status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )


@router.post("/start")
async def start_scheduler():
    """
    启动调度器
    
    Returns:
        操作结果
    """
    try:
        scheduler = get_scheduler()
        
        if scheduler.is_running:
            return {
                "status": "already_running",
                "message": "Scheduler is already running",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        await scheduler.start()
        
        return {
            "status": "started",
            "message": "Scheduler started successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/stop")
async def stop_scheduler():
    """
    停止调度器
    
    Returns:
        操作结果
    """
    try:
        scheduler = get_scheduler()
        
        if not scheduler.is_running:
            return {
                "status": "already_stopped",
                "message": "Scheduler is not running",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        await scheduler.stop()
        
        return {
            "status": "stopped",
            "message": "Scheduler stopped successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop scheduler: {str(e)}"
        )


@router.post("/restart")
async def restart_scheduler():
    """
    重启调度器
    
    Returns:
        操作结果
    """
    try:
        scheduler = get_scheduler()
        
        # 停止调度器（如果正在运行）
        if scheduler.is_running:
            await scheduler.stop()
        
        # 启动调度器
        await scheduler.start()
        
        return {
            "status": "restarted",
            "message": "Scheduler restarted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart scheduler: {str(e)}"
        )


@router.post("/trigger", response_model=ManualTriggerResponse)
async def trigger_manual_analysis(
    request: ManualTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    手动触发技术栈分析
    
    Args:
        request: 触发请求参数
        background_tasks: 后台任务
    
    Returns:
        分析结果
    """
    try:
        scheduler = get_scheduler()
        
        # 检查调度器是否运行
        if not scheduler.is_running:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduler is not running. Please start the scheduler first."
            )
        
        # 触发手动分析
        result = await scheduler.trigger_manual_analysis(user_id=request.user_id)
        
        return ManualTriggerResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger manual analysis: {str(e)}"
        )


@router.post("/trigger/async")
async def trigger_manual_analysis_async(
    request: ManualTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    异步手动触发技术栈分析
    
    Args:
        request: 触发请求参数
        background_tasks: 后台任务
    
    Returns:
        任务状态信息
    """
    try:
        scheduler = get_scheduler()
        
        # 检查调度器是否运行
        if not scheduler.is_running:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduler is not running. Please start the scheduler first."
            )
        
        # 添加后台任务
        background_tasks.add_task(
            scheduler.trigger_manual_analysis,
            user_id=request.user_id
        )
        
        return {
            "status": "started",
            "message": "Manual analysis started in background",
            "user_id": request.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start async manual analysis: {str(e)}"
        )


@router.post("/reschedule")
async def reschedule_jobs():
    """
    重新调度任务（重新加载配置）
    
    Returns:
        操作结果
    """
    try:
        scheduler = get_scheduler()
        
        if not scheduler.is_running:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduler is not running. Cannot reschedule jobs."
            )
        
        await scheduler.reschedule_jobs()
        
        return {
            "status": "rescheduled",
            "message": "Jobs rescheduled successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reschedule jobs: {str(e)}"
        )


@router.get("/jobs")
async def get_scheduled_jobs():
    """
    获取所有调度任务信息
    
    Returns:
        调度任务列表
    """
    try:
        scheduler = get_scheduler()
        status_info = scheduler.get_scheduler_status()
        
        return {
            "jobs": status_info['scheduled_jobs'],
            "total_jobs": len(status_info['scheduled_jobs']),
            "scheduler_running": status_info['is_running'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduled jobs: {str(e)}"
        )


@router.get("/stats")
async def get_job_statistics():
    """
    获取任务执行统计信息
    
    Returns:
        任务统计信息
    """
    try:
        scheduler = get_scheduler()
        status_info = scheduler.get_scheduler_status()
        
        job_stats = status_info['job_stats']
        
        # 计算成功率
        total_runs = job_stats.get('total_runs', 0)
        successful_runs = job_stats.get('successful_runs', 0)
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": job_stats.get('failed_runs', 0),
            "success_rate": round(success_rate, 2),
            "last_run_time": job_stats.get('last_run_time'),
            "last_run_status": job_stats.get('last_run_status'),
            "next_run_time": job_stats.get('next_run_time'),
            "scheduler_running": status_info['is_running'],
            "agent_enabled": status_info['agent_enabled'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job statistics: {str(e)}"
        )


@router.get("/health")
async def scheduler_health_check():
    """
    调度器健康检查
    
    Returns:
        健康状态信息
    """
    try:
        scheduler = get_scheduler()
        status_info = scheduler.get_scheduler_status()
        
        # 检查各种健康指标
        health_status = "healthy"
        issues = []
        
        if not status_info['is_running']:
            health_status = "unhealthy"
            issues.append("Scheduler is not running")
        
        if not status_info['agent_enabled']:
            health_status = "warning"
            issues.append("TechStack Agent is disabled")
        
        if not status_info['scheduled_jobs']:
            health_status = "warning"
            issues.append("No scheduled jobs found")
        
        # 检查最近的运行状态
        last_run_status = status_info['job_stats'].get('last_run_status')
        if last_run_status == 'failed' or last_run_status == 'error':
            health_status = "warning"
            issues.append(f"Last run status: {last_run_status}")
        
        return {
            "status": health_status,
            "scheduler_running": status_info['is_running'],
            "agent_enabled": status_info['agent_enabled'],
            "total_jobs": len(status_info['scheduled_jobs']),
            "issues": issues,
            "last_run_status": last_run_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "scheduler_running": False,
            "agent_enabled": False,
            "total_jobs": 0,
            "issues": [f"Health check failed: {str(e)}"],
            "timestamp": datetime.utcnow().isoformat()
        }