#!/usr/bin/env python3
"""
MCP (Model Context Protocol) 相关 API 端点
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.mcp import (
    MCPRequest, MCPResponse, MCPToolCall, MCPToolResult,
    MCPResourceRequest, MCPResourceResponse
)
from app.services.mcp_service import MCPService
from app.utils.mcp_client import MCPClient

router = APIRouter()


@router.post("/initialize")
async def initialize_mcp_session(
    client_info: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """初始化 MCP 会话"""
    service = MCPService(db)
    session = await service.initialize_session(client_info)
    return session


@router.get("/capabilities")
async def get_mcp_capabilities(
    db: Session = Depends(get_db)
):
    """获取 MCP 服务器能力"""
    service = MCPService(db)
    capabilities = service._get_server_capabilities()
    return capabilities


@router.get("/tools")
async def list_mcp_tools(
    db: Session = Depends(get_db)
):
    """获取可用的 MCP 工具列表"""
    from app.schemas.mcp import MCPListToolsRequest
    service = MCPService(db)
    # 创建一个临时会话用于工具列表
    temp_session_id = "temp_tools_session"
    from app.services.mcp_service import MCPSession, MCPSessionStatus
    temp_session = MCPSession(temp_session_id, 1)  # 使用默认用户ID
    temp_session.status = MCPSessionStatus.ACTIVE
    service.sessions[temp_session_id] = temp_session
    
    tools_request = MCPListToolsRequest()
    tools_response = service.list_tools(tools_request, temp_session_id)
    return tools_response


@router.post("/tools/call")
async def call_mcp_tool(
    tool_call: MCPToolCall,
    db: Session = Depends(get_db)
) -> MCPToolResult:
    """调用 MCP 工具"""
    service = MCPService(db)
    result = await service.call_tool(tool_call)
    return result


@router.get("/resources")
async def list_mcp_resources(
    db: Session = Depends(get_db)
):
    """获取可用的 MCP 资源列表"""
    service = MCPService(db)
    resources = service.get_available_resources()
    return resources


@router.post("/resources/read")
async def read_mcp_resource(
    resource_request: MCPResourceRequest,
    db: Session = Depends(get_db)
) -> MCPResourceResponse:
    """读取 MCP 资源"""
    service = MCPService(db)
    resource = await service.read_resource(resource_request)
    return resource


@router.post("/prompts/get")
async def get_mcp_prompt(
    prompt_name: str,
    arguments: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """获取 MCP 提示模板"""
    service = MCPService(db)
    prompt = await service.get_prompt(prompt_name, arguments or {})
    return prompt


@router.get("/prompts")
async def list_mcp_prompts(
    db: Session = Depends(get_db)
):
    """获取可用的 MCP 提示模板列表"""
    service = MCPService(db)
    prompts = service.get_available_prompts()
    return prompts


@router.post("/completion")
async def mcp_completion(
    request: MCPRequest,
    db: Session = Depends(get_db)
) -> MCPResponse:
    """处理 MCP 完成请求"""
    service = MCPService(db)
    response = await service.handle_completion(request)
    return response


@router.post("/sampling")
async def mcp_sampling(
    request: MCPRequest,
    db: Session = Depends(get_db)
) -> MCPResponse:
    """处理 MCP 采样请求"""
    service = MCPService(db)
    response = await service.handle_sampling(request)
    return response


@router.get("/sessions")
async def list_mcp_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取 MCP 会话列表"""
    service = MCPService(db)
    sessions = service.get_sessions(skip=skip, limit=limit)
    return sessions


@router.get("/sessions/{session_id}")
async def get_mcp_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """获取指定 MCP 会话"""
    service = MCPService(db)
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP session not found"
        )
    return session


@router.delete("/sessions/{session_id}")
async def close_mcp_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """关闭 MCP 会话"""
    service = MCPService(db)
    success = await service.close_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP session not found"
        )
    return {"message": "MCP session closed successfully"}


@router.post("/notifications")
async def handle_mcp_notification(
    notification: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """处理 MCP 通知"""
    service = MCPService(db)
    await service.handle_notification(notification)
    return {"message": "Notification processed successfully"}


@router.get("/health")
async def mcp_health_check(
    db: Session = Depends(get_db)
):
    """MCP 服务健康检查"""
    service = MCPService(db)
    health = await service.health_check()
    return health