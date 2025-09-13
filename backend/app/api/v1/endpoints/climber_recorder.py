#!/usr/bin/env python3
"""
Climber-Recorder MCP相关 API 端点
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.mcp import (
    MCPInitializeRequest, MCPInitializeResponse, MCPListToolsRequest, MCPListToolsResponse,
    MCPCallToolRequest, MCPCallToolResponse
)
from app.services.climber_recorder_service import ClimberRecorderService

router = APIRouter()


@router.post("/initialize")
async def initialize_recorder_session(
    request: MCPInitializeRequest,
    db: Session = Depends(get_db)
) -> MCPInitializeResponse:
    """初始化 Climber-Recorder 会话"""
    service = ClimberRecorderService(db)
    response = service.initialize_session(request)
    return response


@router.get("/capabilities")
async def get_recorder_capabilities(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取 Climber-Recorder 服务器能力"""
    service = ClimberRecorderService(db)
    capabilities = service._get_server_capabilities()
    return capabilities.model_dump()


@router.post("/tools/list")
async def list_recorder_tools(
    request: MCPListToolsRequest,
    session_id: str,
    db: Session = Depends(get_db)
) -> MCPListToolsResponse:
    """获取可用的 Climber-Recorder 工具列表"""
    service = ClimberRecorderService(db)
    try:
        tools = service.list_tools(request, session_id)
        return tools
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found or error: {str(e)}"
        )


@router.post("/tools/call")
async def call_recorder_tool(
    request: MCPCallToolRequest,
    session_id: str,
    db: Session = Depends(get_db)
) -> MCPCallToolResponse:
    """调用 Climber-Recorder 工具"""
    service = ClimberRecorderService(db)
    try:
        result = await service.call_tool(request, session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool execution failed: {str(e)}"
        )


@router.get("/sessions")
async def list_recorder_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """获取 Climber-Recorder 会话列表"""
    service = ClimberRecorderService(db)
    sessions = service.get_sessions(skip=skip, limit=limit)
    return sessions


@router.get("/sessions/{session_id}/records")
async def get_session_tech_stack_records(
    session_id: str,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """获取指定会话的技术栈记录"""
    service = ClimberRecorderService(db)
    try:
        records = service.get_tech_stack_records(session_id)
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def close_recorder_session(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """关闭 Climber-Recorder 会话"""
    service = ClimberRecorderService(db)
    success = service.close_session(session_id)
    if success:
        return {"message": "Session closed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.get("/health")
async def recorder_health_check(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Climber-Recorder 健康检查"""
    service = ClimberRecorderService(db)
    return service.health_check()