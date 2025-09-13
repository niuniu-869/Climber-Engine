#!/usr/bin/env python3
"""
MCP会话管理相关的Pydantic模式
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MCPSessionBase(BaseModel):
    """MCP会话基础模式"""
    session_name: Optional[str] = None
    session_description: Optional[str] = None
    project_name: Optional[str] = None
    work_type: str = Field(..., description="工作类型")
    task_description: str = Field(..., description="任务描述")
    technologies: List[str] = Field(..., description="使用的技术栈")
    primary_language: Optional[str] = None
    frameworks: Optional[List[str]] = None
    libraries: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    difficulty_level: str = "intermediate"
    complexity_score: float = 0.0
    estimated_duration: Optional[int] = None


class MCPSessionCreate(MCPSessionBase):
    """创建MCP会话模式"""
    user_id: int


class MCPSessionUpdate(BaseModel):
    """更新MCP会话模式"""
    session_name: Optional[str] = None
    session_description: Optional[str] = None
    work_summary: Optional[str] = None
    achievements: Optional[List[str]] = None
    challenges_faced: Optional[List[str]] = None
    solutions_applied: Optional[List[str]] = None
    lessons_learned: Optional[List[str]] = None
    actual_duration: Optional[int] = None
    files_modified: Optional[int] = None
    lines_added: Optional[int] = None
    lines_deleted: Optional[int] = None
    commits_count: Optional[int] = None
    code_quality_score: Optional[float] = None
    test_coverage: Optional[float] = None
    documentation_quality: Optional[float] = None
    mcp_call_count: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    is_successful: Optional[bool] = None


class MCPSessionResponse(MCPSessionBase):
    """MCP会话响应模式"""
    id: int
    user_id: int
    actual_duration: Optional[int] = None
    work_summary: Optional[str] = None
    achievements: Optional[List[str]] = None
    challenges_faced: Optional[List[str]] = None
    solutions_applied: Optional[List[str]] = None
    lessons_learned: Optional[List[str]] = None
    files_modified: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    commits_count: int = 0
    code_quality_score: float = 0.0
    test_coverage: float = 0.0
    documentation_quality: float = 0.0
    mcp_server_version: Optional[str] = None
    mcp_client_info: Optional[Dict[str, Any]] = None
    mcp_call_count: int = 0
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: str = "active"
    is_successful: bool = True
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MCPCodeSnippetBase(BaseModel):
    """MCP代码片段基础模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    code_content: str = Field(..., description="代码内容")
    language: str = Field(..., description="编程语言")
    framework: Optional[str] = None
    snippet_type: Optional[str] = None
    purpose: Optional[str] = None
    complexity_level: str = "medium"


class MCPCodeSnippetCreate(MCPCodeSnippetBase):
    """创建MCP代码片段模式"""
    mcp_session_id: int
    related_technologies: Optional[List[str]] = None
    concepts_demonstrated: Optional[List[str]] = None
    patterns_used: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class MCPCodeSnippetUpdate(BaseModel):
    """更新MCP代码片段模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    code_content: Optional[str] = None
    quality_score: Optional[float] = None
    readability_score: Optional[float] = None
    maintainability_score: Optional[float] = None
    learning_value: Optional[float] = None
    difficulty_rating: Optional[int] = None
    educational_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class MCPCodeSnippetResponse(MCPCodeSnippetBase):
    """MCP代码片段响应模式"""
    id: int
    mcp_session_id: int
    related_technologies: Optional[List[str]] = None
    concepts_demonstrated: Optional[List[str]] = None
    patterns_used: Optional[List[str]] = None
    quality_score: float = 0.0
    readability_score: float = 0.0
    maintainability_score: float = 0.0
    learning_value: float = 0.0
    difficulty_rating: int = 3
    educational_notes: Optional[str] = None
    reference_count: int = 0
    last_referenced: Optional[datetime] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MCPSessionSummary(BaseModel):
    """MCP会话总结模式"""
    id: int
    session_name: Optional[str] = None
    project_name: Optional[str] = None
    work_type: str
    technologies: List[str]
    primary_language: Optional[str] = None
    difficulty_level: str
    duration_minutes: Optional[int] = None
    code_quality_score: float
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MCPSessionStats(BaseModel):
    """MCP会话统计模式"""
    total_sessions: int
    total_duration: int  # 总时长（分钟）
    average_quality_score: float
    most_used_technologies: List[Dict[str, Any]]
    work_type_distribution: Dict[str, int]
    monthly_activity: List[Dict[str, Any]]
    

class MCPTechnologyUsage(BaseModel):
    """MCP技术栈使用统计模式"""
    technology_name: str
    usage_count: int
    total_duration: int
    average_quality_score: float
    projects: List[str]
    last_used: Optional[datetime] = None


class MCPSessionFilter(BaseModel):
    """MCP会话过滤模式"""
    user_id: Optional[int] = None
    project_name: Optional[str] = None
    work_type: Optional[str] = None
    technologies: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_quality_score: Optional[float] = None
    max_quality_score: Optional[float] = None


class MCPSessionListResponse(BaseModel):
    """MCP会话列表响应模式"""
    sessions: List[MCPSessionSummary]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool