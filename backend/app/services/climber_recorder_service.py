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
from ..models.mcp_session import MCPSession, MCPCodeSnippet
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
                        "project_name": {
                            "type": "string",
                            "description": "项目名称"
                        },
                        "session_name": {
                            "type": "string",
                            "description": "会话名称"
                        },
                        "frameworks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "使用的框架列表"
                        },
                        "libraries": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "使用的库列表"
                        },
                        "tools": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "使用的工具列表"
                        },
                        "achievements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "完成的成就列表"
                        },
                        "challenges_faced": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "遇到的挑战列表"
                        },
                        "solutions_applied": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "应用的解决方案列表"
                        },
                        "lessons_learned": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "学到的经验列表"
                        },
                        "code_snippet": {
                            "type": "string",
                            "description": "相关代码片段"
                        },
                        "estimated_duration": {
                            "type": "integer",
                            "description": "预计时长（分钟）"
                        },
                        "files_modified": {
                            "type": "integer",
                            "description": "修改的文件数"
                        },
                        "lines_added": {
                            "type": "integer",
                            "description": "新增代码行数"
                        },
                        "lines_deleted": {
                            "type": "integer",
                            "description": "删除代码行数"
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
            
            # 保存到数据库
            await self._save_tech_stack_record(record, session)
            
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
    
    async def _save_tech_stack_record(self, record: Dict[str, Any], session: RecorderSession) -> None:
        """保存技术栈记录到数据库"""
        try:
            # 查找或创建MCP会话记录
            mcp_session = self.db.query(MCPSession).filter(
                MCPSession.user_id == session.user_id,
                MCPSession.status == "active"
            ).first()
            
            if not mcp_session:
                # 创建新的MCP会话
                mcp_session = MCPSession(
                    user_id=session.user_id,
                    session_name=record.get('session_name', f"MCP Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"),
                    session_description="Climber-Recorder MCP会话",
                    project_name=record.get('project_name', "Unknown Project"),
                    work_type=record['work_type'],
                    task_description=record['task_description'],
                    technologies=record['technologies'],
                    primary_language=record['technologies'][0] if record['technologies'] else None,
                    frameworks=record.get('frameworks', []),
                    libraries=record.get('libraries', []),
                    tools=record.get('tools', []),
                    difficulty_level=record['difficulty_level'],
                    complexity_score=self._calculate_complexity_score(record),
                    estimated_duration=record.get('estimated_duration'),
                    work_summary=record.get('notes', ''),
                    achievements=record.get('achievements', []),
                    challenges_faced=record.get('challenges_faced', []),
                    solutions_applied=record.get('solutions_applied', []),
                    lessons_learned=record.get('lessons_learned', []),
                    files_modified=record.get('files_modified', 0),
                    lines_added=record.get('lines_added', 0),
                    lines_deleted=record.get('lines_deleted', 0),
                    mcp_server_version="1.0.0",
                    mcp_client_info=session.client_info.model_dump() if session.client_info else {},
                    mcp_call_count=len(session.tech_stack_records),
                    notes=record.get('notes', ''),
                    tags=record['technologies'],
                    status="active"
                )
                self.db.add(mcp_session)
                self.db.flush()  # 获取ID
                logger.info(f"Created new MCP session {mcp_session.id} for user {session.user_id}")
            else:
                # 更新现有会话
                mcp_session.technologies = list(set(mcp_session.technologies + record['technologies']))
                mcp_session.mcp_call_count = len(session.tech_stack_records)
                mcp_session.updated_at = datetime.utcnow()
                if record.get('notes'):
                    mcp_session.notes = (mcp_session.notes or '') + '\n' + record['notes']
                logger.info(f"Updated MCP session {mcp_session.id} with new tech stack record")
            
            # 如果有代码相关的记录，可以创建代码片段
            if record.get('code_snippet'):
                code_snippet = MCPCodeSnippet(
                    mcp_session_id=mcp_session.id,
                    title=f"Code for {record['task_description'][:50]}...",
                    description=record['task_description'],
                    code_content=record['code_snippet'],
                    language=record['technologies'][0] if record['technologies'] else 'unknown',
                    snippet_type='function',
                    purpose=record['task_description'],
                    related_technologies=record['technologies'],
                    difficulty_rating=self._get_difficulty_rating(record['difficulty_level'])
                )
                self.db.add(code_snippet)
            
            self.db.commit()
            logger.info(f"Successfully saved tech stack record to database")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save tech stack record to database: {e}")
            raise
    
    def _calculate_complexity_score(self, record: Dict[str, Any]) -> float:
        """计算复杂度评分"""
        base_score = 5.0
        tech_count = len(record.get('technologies', []))
        
        # 根据技术栈数量调整
        if tech_count > 5:
            base_score += 2.0
        elif tech_count > 3:
            base_score += 1.0
        
        # 根据难度级别调整
        difficulty_multiplier = {
            'beginner': 0.8,
            'intermediate': 1.0,
            'advanced': 1.3,
            'expert': 1.5
        }
        
        return min(10.0, base_score * difficulty_multiplier.get(record.get('difficulty_level', 'intermediate'), 1.0))
    
    def _get_difficulty_rating(self, difficulty_level: str) -> int:
        """获取难度评级"""
        mapping = {
            'beginner': 2,
            'intermediate': 3,
            'advanced': 4,
            'expert': 5
        }
        return mapping.get(difficulty_level, 3)
    
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