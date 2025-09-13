#!/usr/bin/env python3
"""
工具相关 API 端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tool import (
    ToolCreate, ToolUpdate, ToolResponse,
    ToolExecutionCreate, ToolExecutionResponse
)
from app.services.tool_service import ToolService

router = APIRouter()


@router.get("/", response_model=List[ToolResponse])
async def list_tools(
    skip: int = 0,
    limit: int = 100,
    tool_type: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """获取工具列表"""
    service = ToolService(db)
    return service.get_tools(
        skip=skip, 
        limit=limit, 
        tool_type=tool_type, 
        is_active=is_active
    )


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool_data: ToolCreate,
    db: Session = Depends(get_db)
):
    """创建新工具"""
    service = ToolService(db)
    return service.create_tool(tool_data)


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: int,
    db: Session = Depends(get_db)
):
    """获取指定工具"""
    service = ToolService(db)
    tool = service.get_tool(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return tool


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: int,
    tool_data: ToolUpdate,
    db: Session = Depends(get_db)
):
    """更新工具"""
    service = ToolService(db)
    tool = service.update_tool(tool_id, tool_data)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: int,
    db: Session = Depends(get_db)
):
    """删除工具"""
    service = ToolService(db)
    success = service.delete_tool(tool_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )


@router.post("/{tool_id}/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    tool_id: int,
    execution_data: ToolExecutionCreate,
    db: Session = Depends(get_db)
):
    """执行工具"""
    service = ToolService(db)
    execution = await service.execute_tool(tool_id, execution_data)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return execution


@router.get("/{tool_id}/executions", response_model=List[ToolExecutionResponse])
async def get_tool_executions(
    tool_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """获取工具执行历史"""
    service = ToolService(db)
    return service.get_tool_executions(
        tool_id, 
        skip=skip, 
        limit=limit, 
        status_filter=status_filter
    )


@router.get("/executions/{execution_id}", response_model=ToolExecutionResponse)
async def get_execution(
    execution_id: int,
    db: Session = Depends(get_db)
):
    """获取指定执行记录"""
    service = ToolService(db)
    execution = service.get_execution(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    return execution