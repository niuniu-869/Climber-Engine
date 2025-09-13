#!/usr/bin/env python3
"""
API v1 主路由
"""

from fastapi import APIRouter
from datetime import datetime

from app.api.v1.endpoints import (
    agents, conversations, knowledge, tools,
    users, coding_sessions, skill_assessments, 
    learning_tasks, technical_debt, mcp, climber_recorder,
    tech_stack_agent, tech_stack_scheduler, coding_tutor_agent
)

api_router = APIRouter()

# 健康检查端点
@api_router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Climber Engine API",
        "version": "1.0.0"
    }

# 注册各模块路由
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(coding_sessions.router, prefix="/coding-sessions", tags=["coding-sessions"])
api_router.include_router(skill_assessments.router, prefix="/skill-assessments", tags=["skill-assessments"])
api_router.include_router(learning_tasks.router, prefix="/learning-tasks", tags=["learning-tasks"])
api_router.include_router(technical_debt.router, prefix="/technical-debt", tags=["technical-debt"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(climber_recorder.router, prefix="/climber-recorder", tags=["climber-recorder"])
api_router.include_router(tech_stack_agent.router, prefix="/tech-stack-agent", tags=["tech-stack-agent"])
api_router.include_router(tech_stack_scheduler.router, prefix="/tech-stack-scheduler", tags=["tech-stack-scheduler"])
api_router.include_router(coding_tutor_agent.router, prefix="/coding-tutor-agent", tags=["coding-tutor-agent"])