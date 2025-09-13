#!/usr/bin/env python3
"""
工具业务逻辑服务
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.tool import Tool, ToolExecution
from app.schemas.tool import ToolCreate, ToolUpdate, ToolExecutionCreate


class ToolService:
    """工具服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_tools(
        self, 
        skip: int = 0, 
        limit: int = 100,
        tool_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Tool]:
        """获取工具列表"""
        query = self.db.query(Tool)
        
        if tool_type:
            query = query.filter(Tool.tool_type == tool_type)
        
        if is_active is not None:
            query = query.filter(Tool.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def get_tool(self, tool_id: int) -> Optional[Tool]:
        """获取指定工具"""
        return self.db.query(Tool).filter(Tool.id == tool_id).first()
    
    def create_tool(self, tool_data: ToolCreate) -> Tool:
        """创建新工具"""
        tool = Tool(
            name=tool_data.name,
            description=tool_data.description,
            tool_type=tool_data.tool_type,
            config=tool_data.config,
            tool_schema=tool_data.tool_schema,
            version=tool_data.version
        )
        
        self.db.add(tool)
        self.db.commit()
        self.db.refresh(tool)
        
        return tool
    
    def update_tool(self, tool_id: int, tool_data: ToolUpdate) -> Optional[Tool]:
        """更新工具"""
        tool = self.get_tool(tool_id)
        if not tool:
            return None
        
        update_data = tool_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tool, field, value)
        
        self.db.commit()
        self.db.refresh(tool)
        
        return tool
    
    def delete_tool(self, tool_id: int) -> bool:
        """删除工具"""
        tool = self.get_tool(tool_id)
        if not tool:
            return False
        
        self.db.delete(tool)
        self.db.commit()
        
        return True
    
    async def execute_tool(self, tool_id: int, execution_data: ToolExecutionCreate) -> Optional[ToolExecution]:
        """执行工具"""
        tool = self.get_tool(tool_id)
        if not tool:
            return None
        
        execution = ToolExecution(
            tool_id=tool_id,
            agent_id=execution_data.agent_id,
            input_data=execution_data.input_data,
            status="running"
        )
        
        self.db.add(execution)
        self.db.commit()
        
        # TODO: 实现实际的工具执行逻辑
        execution.output_data = {"result": "执行成功"}
        execution.status = "success"
        execution.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(execution)
        
        return execution
    
    def get_tool_executions(
        self, 
        tool_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> List[ToolExecution]:
        """获取工具执行历史"""
        query = self.db.query(ToolExecution).filter(ToolExecution.tool_id == tool_id)
        
        if status_filter:
            query = query.filter(ToolExecution.status == status_filter)
        
        return query.offset(skip).limit(limit).all()
    
    def get_execution(self, execution_id: int) -> Optional[ToolExecution]:
        """获取指定执行记录"""
        return self.db.query(ToolExecution).filter(ToolExecution.id == execution_id).first()