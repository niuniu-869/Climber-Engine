#!/usr/bin/env python3
"""
Climber-Recorder MCP服务
专门用于记录Agent工作过程中涉及的技术栈
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
import json
import uuid
import asyncio
from enum import Enum

from ..models.user import User
from ..schemas.mcp import (
    MCPMessage, MCPError, MCPCapabilities, MCPClientInfo, MCPServerInfo,
    MCPInitializeRequest, MCPInitializeResponse, MCPListToolsRequest, MCPListToolsResponse,
    MCPCallToolRequest, MCPCallToolResponse, MCPTool
)
from ..core.exceptions import MCPError as MCPException
from ..core.logger import get_logger

logger = get_logger(__name__)


class RecorderSessionStatus(Enum):
    """记录器会话状态"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"


class RecorderSession:
    """记录器会话类"""
    
    def __init__(self, session_id: str, user_id: int):
        self.session_id = session_id
        self.user_id = user_id
        self.status = RecorderSessionStatus.INITIALIZING
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.client_info: Optional[MCPClientInfo] = None
        self.capabilities: Optional[MCPCapabilities] = None
        self.server_info: Optional[MCPServerInfo] = None
        self.tech_stack_records: List[Dict[str, Any]] = []
    
    def update_activity(self):
        """更新活动时间"""
        self.last_activity = datetime.utcnow()
    
    def add_tech_stack_record(self, record: Dict[str, Any]):
        """添加技术栈记录"""
        record['timestamp'] = datetime.utcnow().isoformat()
        record['session_id'] = self.session_id
        self.tech_stack_records.append(record)
        self.update_activity()
        logger.info(f"Added tech stack record to session {self.session_id}: {record['technologies']}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'client_info': self.client_info.model_dump() if self.client_info else None,
            'tech_stack_count': len(self.tech_stack_records)
        }


class ClimberRecorderService:
    """Climber-Recorder MCP协议服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.sessions: Dict[str, RecorderSession] = {}
        self.server_info = MCPServerInfo(
            name="Climber-Recorder",
            version="1.0.0",
            description="MCP server for recording technology stacks used during Agent work sessions",
            author="Climber Engine Team",
            homepage="https://github.com/climber-engine/climber-engine"
        )
    
    def initialize_session(self, request: MCPInitializeRequest, user_id: int = 1) -> MCPInitializeResponse:
        """初始化MCP会话"""
        session_id = str(uuid.uuid4())
        
        # 验证用户存在（如果用户表存在的话）
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found, using default user")
        except Exception as e:
            logger.warning(f"Could not query user table: {e}, using default user")
        
        # 创建会话
        session = RecorderSession(session_id, user_id)
        session.client_info = request.client_info
        session.capabilities = self._get_server_capabilities()
        session.server_info = self.server_info
        session.status = RecorderSessionStatus.ACTIVE
        
        self.sessions[session_id] = session
        
        logger.info(f"Initialized Climber-Recorder session {session_id} for user {user_id}")
        
        return MCPInitializeResponse(
            protocol_version=request.protocol_version,
            server_info=self.server_info,
            capabilities=session.capabilities
        )
    
    def _get_server_capabilities(self) -> MCPCapabilities:
        """获取服务器能力"""
        return MCPCapabilities(
            tools={
                "list_tools": True,
                "call_tool": True
            },
            resources={},
            prompts={},
            logging={},
            sampling={},
            experimental={}
        )
    
    def get_session(self, session_id: str) -> RecorderSession:
        """获取会话"""
        session = self.sessions.get(session_id)
        if not session:
            raise MCPException(f"Session {session_id} not found", code=-32001)
        return session
    
    def list_tools(self, request: MCPListToolsRequest, session_id: str) -> MCPListToolsResponse:
        """列出可用工具"""
        session = self.get_session(session_id)
        session.update_activity()
        
        tools = [
            MCPTool(
                name="record_tech_stack",
                description="记录Agent工作过程中使用的技术栈",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "technologies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "使用的技术栈列表，如: ['Python', 'FastAPI', 'SQLAlchemy', 'React', 'TypeScript']"
                        },
                        "task_description": {
                            "type": "string",
                            "description": "任务描述"
                        },
                        "work_type": {
                            "type": "string",
                            "enum": ["development", "debugging", "refactoring", "testing", "documentation", "analysis"],
                            "description": "工作类型"
                        },
                        "difficulty_level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced", "expert"],
                            "description": "难度级别"
                        },
                        "notes": {
                            "type": "string",
                            "description": "额外备注"
                        }
                    },
                    "required": ["technologies", "task_description", "work_type"]
                }
            )
        ]
        
        return MCPListToolsResponse(tools=tools)
    
    async def call_tool(self, request: MCPCallToolRequest, session_id: str) -> MCPCallToolResponse:
        """调用工具"""
        session = self.get_session(session_id)
        session.update_activity()
        
        if request.name == "record_tech_stack":
            return await self._record_tech_stack_tool(request.arguments, session)
        else:
            raise MCPException(f"Unknown tool: {request.name}", code=-32601)
    
    async def _record_tech_stack_tool(self, arguments: Dict[str, Any], session: RecorderSession) -> MCPCallToolResponse:
        """记录技术栈工具"""
        try:
            # 验证必需参数
            technologies = arguments.get('technologies', [])
            task_description = arguments.get('task_description', '')
            work_type = arguments.get('work_type', 'development')
            
            if not technologies:
                raise MCPException("Technologies list cannot be empty", code=-32602)
            
            if not task_description:
                raise MCPException("Task description is required", code=-32602)
            
            # 创建技术栈记录
            record = {
                'technologies': technologies,
                'task_description': task_description,
                'work_type': work_type,
                'difficulty_level': arguments.get('difficulty_level', 'intermediate'),
                'notes': arguments.get('notes', ''),
                'user_id': session.user_id
            }
            
            # 添加到会话记录中
            session.add_tech_stack_record(record)
            
            # 这里可以添加持久化到数据库的逻辑
            # await self._save_tech_stack_record(record)
            
            return MCPCallToolResponse(
                content=[
                    {
                        "type": "text",
                        "text": f"✅ 技术栈记录已保存！\n\n" +
                               f"📋 任务: {task_description}\n" +
                               f"🔧 技术栈: {', '.join(technologies)}\n" +
                               f"📝 工作类型: {work_type}\n" +
                               f"⭐ 难度级别: {arguments.get('difficulty_level', 'intermediate')}\n" +
                               f"📊 会话总记录数: {len(session.tech_stack_records)}"
                    }
                ],
                is_error=False
            )
            
        except Exception as e:
            logger.error(f"Error in record_tech_stack_tool: {e}")
            return MCPCallToolResponse(
                content=[
                    {
                        "type": "text",
                        "text": f"❌ 记录技术栈时发生错误: {str(e)}"
                    }
                ],
                is_error=True
            )
    
    def get_sessions(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取会话列表"""
        sessions = list(self.sessions.values())[skip:skip + limit]
        return [session.to_dict() for session in sessions]
    
    def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.status = RecorderSessionStatus.CLOSED
            logger.info(f"Closed Climber-Recorder session {session_id}")
            return True
        return False
    
    def get_tech_stack_records(self, session_id: str) -> List[Dict[str, Any]]:
        """获取技术栈记录"""
        session = self.get_session(session_id)
        return session.tech_stack_records
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "server_name": self.server_info.name,
            "version": self.server_info.version,
            "active_sessions": len([s for s in self.sessions.values() if s.status == RecorderSessionStatus.ACTIVE]),
            "total_sessions": len(self.sessions),
            "total_records": sum(len(s.tech_stack_records) for s in self.sessions.values()),
            "timestamp": datetime.utcnow().isoformat()
        }