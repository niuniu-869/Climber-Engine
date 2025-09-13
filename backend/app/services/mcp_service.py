#!/usr/bin/env python3
"""
MCP协议服务层
处理Model Context Protocol相关的业务逻辑
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
import json
import uuid
import asyncio
from enum import Enum

from ..models.user import User
from ..models.agent import Agent
from ..schemas.mcp import (
    MCPMessage, MCPError, MCPCapabilities, MCPClientInfo, MCPServerInfo,
    MCPInitializeRequest, MCPInitializeResponse, MCPListToolsRequest, MCPListToolsResponse,
    MCPCallToolRequest, MCPCallToolResponse, MCPListResourcesRequest, MCPListResourcesResponse,
    MCPReadResourceRequest, MCPReadResourceResponse, MCPGetPromptRequest, MCPGetPromptResponse,
    MCPCompleteRequest, MCPCompleteResponse, MCPSamplingRequest, MCPSamplingResponse,
    MCPNotification, MCPSessionInfo
)
from ..core.exceptions import MCPError as MCPException, InvalidOperationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class MCPSessionStatus(Enum):
    """MCP会话状态"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ERROR = "error"


class MCPSession:
    """MCP会话管理"""
    
    def __init__(self, session_id: str, user_id: int, agent_id: Optional[int] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.status = MCPSessionStatus.INITIALIZING
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.capabilities = None
        self.client_info = None
        self.server_info = None
        self.context = {}
        self.message_history = []
    
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = datetime.utcnow()
    
    def add_message(self, message: Dict[str, Any]):
        """添加消息到历史记录"""
        self.message_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'message': message
        })
        self.update_activity()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'agent_id': self.agent_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'capabilities': self.capabilities.dict() if self.capabilities else None,
            'client_info': self.client_info.dict() if self.client_info else None,
            'server_info': self.server_info.dict() if self.server_info else None,
            'context': self.context,
            'message_count': len(self.message_history)
        }


class MCPService:
    """MCP协议服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.sessions: Dict[str, MCPSession] = {}
        self.server_info = MCPServerInfo(
            name="Climber Engine MCP Server",
            version="1.0.0",
            description="MCP server for Climber Engine - AI-powered programming skill development platform",
            author="Climber Engine Team",
            homepage="https://github.com/climber-engine/climber-engine"
        )
    
    def initialize_session(self, request: MCPInitializeRequest, user_id: int) -> MCPInitializeResponse:
        """初始化MCP会话"""
        session_id = str(uuid.uuid4())
        
        # 验证用户存在
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise MCPException("User not found", code=-32001)
        
        # 创建会话
        session = MCPSession(session_id, user_id)
        session.client_info = request.client_info
        session.capabilities = self._get_server_capabilities()
        session.server_info = self.server_info
        session.status = MCPSessionStatus.ACTIVE
        
        self.sessions[session_id] = session
        
        logger.info(f"Initialized MCP session {session_id} for user {user_id}")
        
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
            resources={
                "list_resources": True,
                "read_resource": True,
                "subscribe": False
            },
            prompts={
                "list_prompts": True,
                "get_prompt": True
            },
            completion={
                "complete": True
            },
            sampling={
                "sample": True
            },
            experimental={}
        )
    
    def get_session(self, session_id: str) -> MCPSession:
        """获取会话"""
        if session_id not in self.sessions:
            raise MCPException(f"Session {session_id} not found", code=-32002)
        
        session = self.sessions[session_id]
        session.update_activity()
        return session
    
    def list_tools(self, request: MCPListToolsRequest, session_id: str) -> MCPListToolsResponse:
        """列出可用工具"""
        session = self.get_session(session_id)
        
        tools = [
            {
                "name": "analyze_code",
                "description": "Analyze code for technical debt, complexity, and quality issues",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code content to analyze"},
                        "language": {"type": "string", "description": "Programming language"},
                        "file_path": {"type": "string", "description": "File path (optional)"}
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "generate_learning_tasks",
                "description": "Generate personalized learning tasks based on skill assessment",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "skill_areas": {"type": "array", "items": {"type": "string"}, "description": "Areas to focus on"},
                        "difficulty_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                        "count": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Number of tasks to generate"}
                    },
                    "required": ["skill_areas"]
                }
            },
            {
                "name": "assess_skills",
                "description": "Assess programming skills based on code samples and performance",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code_samples": {"type": "array", "items": {"type": "string"}, "description": "Code samples to assess"},
                        "skill_type": {"type": "string", "description": "Type of skill to assess"},
                        "context": {"type": "string", "description": "Additional context for assessment"}
                    },
                    "required": ["code_samples", "skill_type"]
                }
            },
            {
                "name": "get_coding_insights",
                "description": "Get insights and recommendations based on coding session data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_data": {"type": "object", "description": "Coding session data"},
                        "analysis_type": {"type": "string", "enum": ["performance", "quality", "learning"], "description": "Type of analysis"}
                    },
                    "required": ["session_data"]
                }
            },
            {
                "name": "suggest_improvements",
                "description": "Suggest code improvements and best practices",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to improve"},
                        "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Areas to focus on"},
                        "language": {"type": "string", "description": "Programming language"}
                    },
                    "required": ["code"]
                }
            }
        ]
        
        session.add_message({"type": "list_tools", "tools_count": len(tools)})
        
        return MCPListToolsResponse(tools=tools)
    
    async def call_tool(self, request: MCPCallToolRequest, session_id: str) -> MCPCallToolResponse:
        """调用工具 - 支持异步LLM调用"""
        session = self.get_session(session_id)
        
        tool_name = request.name
        arguments = request.arguments or {}
        
        session.add_message({
            "type": "call_tool",
            "tool_name": tool_name,
            "arguments": arguments
        })
        
        try:
            if tool_name == "analyze_code":
                result = await self._analyze_code_tool(arguments, session)
            elif tool_name == "generate_learning_tasks":
                result = await self._generate_learning_tasks_tool(arguments, session)
            elif tool_name == "assess_skills":
                result = await self._assess_skills_tool(arguments, session)
            elif tool_name == "get_coding_insights":
                result = await self._get_coding_insights_tool(arguments, session)
            elif tool_name == "suggest_improvements":
                result = await self._suggest_improvements_tool(arguments, session)
            else:
                raise MCPException(f"Unknown tool: {tool_name}", code=-32601)
            
            return MCPCallToolResponse(
                content=[
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, ensure_ascii=False)
                    }
                ],
                is_error=False
            )
        
        except Exception as e:
            logger.error(f"Tool call error: {str(e)}")
            return MCPCallToolResponse(
                content=[
                    {
                        "type": "text",
                        "text": f"Error calling tool {tool_name}: {str(e)}"
                    }
                ],
                is_error=True
            )
    
    async def _analyze_code_tool(self, arguments: Dict[str, Any], session: MCPSession) -> Dict[str, Any]:
        """代码分析工具 - 使用真实LLM分析"""
        from .ai_service import AIService
        
        code = arguments.get("code", "")
        language = arguments.get("language", "python")
        file_path = arguments.get("file_path", "unknown")
        
        if not code:
            raise MCPException("Code content is required", code=-32602)
        
        ai_service = AIService(self.db)
        analysis_result = await ai_service.analyze_technical_debt(
            code_content=code,
            file_path=file_path,
            language=language
        )
        
        if analysis_result["success"]:
            analysis = analysis_result["analysis"]
            return {
                "analysis_type": "code_analysis",
                "language": language,
                "file_path": file_path,
                "ai_analysis": analysis,
                "model_info": analysis_result["model_info"],
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "analysis_type": "code_analysis",
                "language": language,
                "file_path": file_path,
                "error": analysis_result["error"],
                "model_info": analysis_result["model_info"],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _generate_learning_tasks_tool(self, arguments: Dict[str, Any], session: MCPSession) -> Dict[str, Any]:
        """生成学习任务工具 - 使用真实LLM生成"""
        from .ai_service import AIService
        
        skill_areas = arguments.get("skill_areas", [])
        difficulty_level = arguments.get("difficulty_level", "intermediate")
        count = arguments.get("count", 5)
        
        if not skill_areas:
            raise MCPException("Skill areas are required", code=-32602)
        
        # 获取用户技能信息
        user = self.db.query(User).filter(User.id == session.user_id).first()
        if not user:
            raise MCPException("User not found", code=-32001)
        
        user_skills = {
            "skill_level": user.skill_level,
            "primary_languages": user.primary_languages,
            "frameworks": user.frameworks,
            "tools": user.tools,
            "learning_style": user.learning_style
        }
        
        ai_service = AIService(self.db)
        task_result = await ai_service.generate_learning_tasks(
            user_skills=user_skills,
            focus_areas=skill_areas,
            difficulty_level=difficulty_level,
            count=count
        )
        
        return {
            "task_generation": "success" if task_result["success"] else "failed",
            "requested_skills": skill_areas,
            "difficulty_level": difficulty_level,
            "ai_generated_tasks": task_result.get("tasks", []),
            "generation_info": task_result.get("generation_info", {}),
            "model_info": task_result.get("model_info", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _assess_skills_tool(self, arguments: Dict[str, Any], session: MCPSession) -> Dict[str, Any]:
        """技能评估工具 - 使用真实LLM评估"""
        from .ai_service import AIService
        
        code_samples = arguments.get("code_samples", [])
        skill_type = arguments.get("skill_type", "")
        context = arguments.get("context", "")
        
        if not code_samples or not skill_type:
            raise MCPException("Code samples and skill type are required", code=-32602)
        
        ai_service = AIService(self.db)
        assessment_result = await ai_service.assess_programming_skills(
            code_samples=code_samples,
            skill_type=skill_type,
            context=context
        )
        
        if assessment_result["success"]:
            try:
                # 尝试解析AI返回的JSON结果
                ai_assessment = json.loads(assessment_result["content"])
                return {
                    "skill_type": skill_type,
                    "ai_assessment": ai_assessment,
                    "code_samples_analyzed": len(code_samples),
                    "model_info": assessment_result["model_info"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            except json.JSONDecodeError:
                return {
                    "skill_type": skill_type,
                    "raw_assessment": assessment_result["content"],
                    "code_samples_analyzed": len(code_samples),
                    "model_info": assessment_result["model_info"],
                    "note": "AI响应格式需要人工解析",
                    "timestamp": datetime.utcnow().isoformat()
                }
        else:
            return {
                "skill_type": skill_type,
                "error": assessment_result["error"],
                "model_info": assessment_result["model_info"],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_coding_insights_tool(self, arguments: Dict[str, Any], session: MCPSession) -> Dict[str, Any]:
        """编程洞察工具 - 使用真实LLM分析"""
        from .ai_service import AIService
        
        session_data = arguments.get("session_data", {})
        analysis_type = arguments.get("analysis_type", "performance")
        
        ai_service = AIService(self.db)
        insights_result = await ai_service.get_coding_insights(
            session_data=session_data,
            analysis_type=analysis_type
        )
        
        return {
            "analysis_type": analysis_type,
            "session_summary": session_data,
            "ai_insights": insights_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _suggest_improvements_tool(self, arguments: Dict[str, Any], session: MCPSession) -> Dict[str, Any]:
        """代码改进建议工具 - 使用真实LLM分析"""
        from .ai_service import AIService
        
        code = arguments.get("code", "")
        focus_areas = arguments.get("focus_areas", [])
        language = arguments.get("language", "python")
        
        if not code:
            raise MCPException("Code content is required", code=-32602)
        
        ai_service = AIService(self.db)
        improvement_result = await ai_service.suggest_code_improvements(
            code=code,
            language=language,
            focus_areas=focus_areas
        )
        
        return {
            "original_code": code,
            "language": language,
            "focus_areas": focus_areas,
            "ai_suggestions": improvement_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_code_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """基于检测到的问题生成推荐"""
        recommendations = []
        
        issue_types = [issue["type"] for issue in issues]
        
        if "security" in issue_types:
            recommendations.append("Conduct a thorough security review and implement secure coding practices")
        
        if "complexity" in issue_types:
            recommendations.append("Refactor complex functions into smaller, more manageable pieces")
        
        if "performance" in issue_types:
            recommendations.append("Profile the application and optimize performance bottlenecks")
        
        if "duplication" in issue_types:
            recommendations.append("Extract common code into reusable functions or modules")
        
        if not recommendations:
            recommendations.append("Continue following good coding practices and regular code reviews")
        
        return recommendations
    
    def list_resources(self, request: MCPListResourcesRequest, session_id: str) -> MCPListResourcesResponse:
        """列出可用资源"""
        session = self.get_session(session_id)
        
        resources = [
            {
                "uri": "climber://user/profile",
                "name": "User Profile",
                "description": "Current user's profile and preferences",
                "mime_type": "application/json"
            },
            {
                "uri": "climber://user/skills",
                "name": "Skill Assessments",
                "description": "User's skill assessment history and current levels",
                "mime_type": "application/json"
            },
            {
                "uri": "climber://user/sessions",
                "name": "Coding Sessions",
                "description": "Recent coding session data and statistics",
                "mime_type": "application/json"
            },
            {
                "uri": "climber://user/tasks",
                "name": "Learning Tasks",
                "description": "Current and completed learning tasks",
                "mime_type": "application/json"
            },
            {
                "uri": "climber://user/debt",
                "name": "Technical Debt",
                "description": "Technical debt analysis and tracking",
                "mime_type": "application/json"
            }
        ]
        
        session.add_message({"type": "list_resources", "resources_count": len(resources)})
        
        return MCPListResourcesResponse(resources=resources)
    
    def read_resource(self, request: MCPReadResourceRequest, session_id: str) -> MCPReadResourceResponse:
        """读取资源"""
        session = self.get_session(session_id)
        uri = request.uri
        
        session.add_message({"type": "read_resource", "uri": uri})
        
        try:
            if uri == "climber://user/profile":
                content = self._get_user_profile(session.user_id)
            elif uri == "climber://user/skills":
                content = self._get_user_skills(session.user_id)
            elif uri == "climber://user/sessions":
                content = self._get_user_sessions(session.user_id)
            elif uri == "climber://user/tasks":
                content = self._get_user_tasks(session.user_id)
            elif uri == "climber://user/debt":
                content = self._get_user_debt(session.user_id)
            else:
                raise MCPException(f"Resource not found: {uri}", code=-32003)
            
            return MCPReadResourceResponse(
                contents=[
                    {
                        "uri": uri,
                        "mime_type": "application/json",
                        "text": json.dumps(content, indent=2, ensure_ascii=False)
                    }
                ]
            )
        
        except Exception as e:
            logger.error(f"Resource read error: {str(e)}")
            raise MCPException(f"Failed to read resource: {str(e)}", code=-32004)
    
    def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """获取用户档案"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise MCPException("User not found", code=-32001)
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "github_username": user.github_username,
            "skill_level": user.skill_level,
            "primary_languages": user.primary_languages,
            "frameworks": user.frameworks,
            "tools": user.tools,
            "learning_style": user.learning_style,
            "preferred_difficulty": user.preferred_difficulty,
            "daily_goal_minutes": user.daily_goal_minutes,
            "total_coding_time": user.total_coding_time,
            "total_sessions": user.total_sessions,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "tech_debt_score": user.tech_debt_score,
            "knowledge_gaps": user.knowledge_gaps,
            "strength_areas": user.strength_areas,
            "is_active": user.is_active,
            "is_premium": user.is_premium,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    
    def _get_user_skills(self, user_id: int) -> Dict[str, Any]:
        """获取用户技能"""
        from .skill_assessment_service import SkillAssessmentService
        
        skill_service = SkillAssessmentService(self.db)
        assessments = skill_service.get_skill_assessments(user_id=user_id, limit=50)
        
        return {
            "user_id": user_id,
            "total_assessments": len(assessments),
            "assessments": [{
                "id": assessment.id,
                "skill_type": assessment.skill_type,
                "score": assessment.score,
                "max_score": assessment.max_score,
                "percentage": (assessment.score / assessment.max_score) * 100,
                "level": assessment.level,
                "created_at": assessment.created_at.isoformat()
            } for assessment in assessments]
        }
    
    def _get_user_sessions(self, user_id: int) -> Dict[str, Any]:
        """获取用户编程会话"""
        from .coding_session_service import CodingSessionService
        
        session_service = CodingSessionService(self.db)
        sessions = session_service.get_coding_sessions(user_id=user_id, limit=20)
        
        return {
            "user_id": user_id,
            "total_sessions": len(sessions),
            "sessions": [{
                "id": session.id,
                "title": session.title,
                "description": session.description,
                "status": session.status,
                "duration": session.duration,
                "language": session.language,
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            } for session in sessions]
        }
    
    def _get_user_tasks(self, user_id: int) -> Dict[str, Any]:
        """获取用户学习任务"""
        from .learning_task_service import LearningTaskService
        
        task_service = LearningTaskService(self.db)
        tasks = task_service.get_learning_tasks(user_id=user_id, limit=30)
        
        return {
            "user_id": user_id,
            "total_tasks": len(tasks),
            "tasks": [{
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "skill_type": task.skill_type,
                "status": task.status,
                "progress": task.progress,
                "difficulty_level": task.difficulty_level,
                "estimated_duration": task.estimated_duration,
                "created_at": task.created_at.isoformat()
            } for task in tasks]
        }
    
    def _get_user_debt(self, user_id: int) -> Dict[str, Any]:
        """获取用户技术债务"""
        from .technical_debt_service import TechnicalDebtService
        
        debt_service = TechnicalDebtService(self.db)
        summary = debt_service.get_user_debt_summary(user_id)
        metrics = debt_service.get_debt_metrics_overview(user_id)
        
        return {
            "user_id": user_id,
            "summary": summary,
            "metrics": metrics
        }
    
    def get_prompt(self, request: MCPGetPromptRequest, session_id: str) -> MCPGetPromptResponse:
        """获取提示模板"""
        session = self.get_session(session_id)
        prompt_name = request.name
        arguments = request.arguments or {}
        
        session.add_message({"type": "get_prompt", "prompt_name": prompt_name})
        
        # 预定义的提示模板
        prompts = {
            "code_review": {
                "description": "Code review prompt for analyzing code quality",
                "template": "Please review the following code and provide feedback on:\n1. Code quality and best practices\n2. Potential bugs or issues\n3. Performance considerations\n4. Suggestions for improvement\n\nCode:\n{code}"
            },
            "skill_assessment": {
                "description": "Skill assessment prompt for evaluating programming abilities",
                "template": "Assess the programming skills demonstrated in the following code:\n1. Technical competency level\n2. Understanding of concepts\n3. Code organization and structure\n4. Areas for improvement\n\nCode samples:\n{code_samples}"
            },
            "learning_plan": {
                "description": "Learning plan generation prompt",
                "template": "Create a personalized learning plan for a programmer with the following profile:\n- Current skill level: {skill_level}\n- Learning goals: {goals}\n- Available time: {time_commitment}\n- Preferred learning style: {learning_style}\n\nProvide a structured plan with specific tasks and milestones."
            }
        }
        
        if prompt_name not in prompts:
            raise MCPException(f"Prompt not found: {prompt_name}", code=-32005)
        
        prompt_info = prompts[prompt_name]
        
        # 填充模板参数
        try:
            filled_template = prompt_info["template"].format(**arguments)
        except KeyError as e:
            raise MCPException(f"Missing required argument: {e}", code=-32602)
        
        return MCPGetPromptResponse(
            description=prompt_info["description"],
            messages=[
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": filled_template
                    }
                }
            ]
        )
    
    def complete(self, request: MCPCompleteRequest, session_id: str) -> MCPCompleteResponse:
        """处理完成请求"""
        session = self.get_session(session_id)
        
        session.add_message({"type": "complete", "ref": request.ref})
        
        # 基于引用类型提供不同的完成建议
        ref = request.ref
        suggestions = []
        
        if ref.get("type") == "resource":
            # 资源URI完成
            base_uri = ref.get("uri", "")
            if base_uri.startswith("climber://"):
                suggestions = [
                    "climber://user/profile",
                    "climber://user/skills",
                    "climber://user/sessions",
                    "climber://user/tasks",
                    "climber://user/debt"
                ]
        elif ref.get("type") == "tool":
            # 工具名称完成
            suggestions = [
                "analyze_code",
                "generate_learning_tasks",
                "assess_skills",
                "get_coding_insights",
                "suggest_improvements"
            ]
        
        return MCPCompleteResponse(
            completion={
                "values": suggestions,
                "total": len(suggestions),
                "has_more": False
            }
        )
    
    def sample(self, request: MCPSamplingRequest, session_id: str) -> MCPSamplingResponse:
        """处理采样请求"""
        session = self.get_session(session_id)
        
        session.add_message({"type": "sample", "method": request.method})
        
        # 这里应该集成实际的LLM采样逻辑
        # 暂时返回模拟响应
        return MCPSamplingResponse(
            role="assistant",
            content={
                "type": "text",
                "text": "This is a sample response from the Climber Engine MCP server. In a real implementation, this would be generated by an LLM based on the provided prompt and sampling parameters."
            },
            model="climber-engine-v1",
            stop_reason="end_turn"
        )
    
    def list_sessions(self) -> List[MCPSessionInfo]:
        """列出所有会话"""
        return [
            MCPSessionInfo(
                session_id=session.session_id,
                user_id=session.user_id,
                status=session.status.value,
                created_at=session.created_at,
                last_activity=session.last_activity
            )
            for session in self.sessions.values()
        ]
    
    def get_session_info(self, session_id: str) -> MCPSessionInfo:
        """获取会话信息"""
        session = self.get_session(session_id)
        return MCPSessionInfo(
            session_id=session.session_id,
            user_id=session.user_id,
            status=session.status.value,
            created_at=session.created_at,
            last_activity=session.last_activity
        )
    
    def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.status = MCPSessionStatus.CLOSED
            session.add_message({"type": "session_closed"})
            
            # 可以选择立即删除或保留一段时间
            # del self.sessions[session_id]
            
            logger.info(f"Closed MCP session {session_id}")
            return True
        return False
    
    def handle_notification(self, notification: MCPNotification, session_id: str) -> None:
        """处理通知"""
        session = self.get_session(session_id)
        
        session.add_message({
            "type": "notification",
            "method": notification.method,
            "params": notification.params
        })
        
        # 根据通知类型执行相应操作
        if notification.method == "progress":
            # 处理进度通知
            logger.info(f"Progress notification: {notification.params}")
        elif notification.method == "cancelled":
            # 处理取消通知
            logger.info(f"Operation cancelled: {notification.params}")
        
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        active_sessions = len([s for s in self.sessions.values() if s.status == MCPSessionStatus.ACTIVE])
        
        return {
            "status": "healthy",
            "server_info": self.server_info.dict(),
            "active_sessions": active_sessions,
            "total_sessions": len(self.sessions),
            "uptime": "running",
            "capabilities": self._get_server_capabilities().dict()
        }