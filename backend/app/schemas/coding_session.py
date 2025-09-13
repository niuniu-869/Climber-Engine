#!/usr/bin/env python3
"""
编程会话相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CodingSessionBase(BaseModel):
    """编程会话基础模式"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    primary_language: str = Field(..., max_length=50)
    frameworks: Optional[str] = Field(None, max_length=200)
    tools: Optional[str] = Field(None, max_length=200)
    project_type: Optional[str] = Field(None, max_length=100)
    difficulty_level: Optional[str] = Field("medium", pattern="^(easy|medium|hard|expert)$")
    estimated_duration: Optional[int] = Field(None, ge=1)  # 预估时长（分钟）
    learning_objectives: Optional[str] = Field(None, max_length=500)
    tags: Optional[str] = Field(None, max_length=200)  # 逗号分隔的标签


class CodingSessionCreate(CodingSessionBase):
    """创建编程会话模式"""
    user_id: int


class CodingSessionUpdate(BaseModel):
    """更新编程会话模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    primary_language: Optional[str] = Field(None, max_length=50)
    frameworks: Optional[str] = Field(None, max_length=200)
    tools: Optional[str] = Field(None, max_length=200)
    project_type: Optional[str] = Field(None, max_length=100)
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard|expert)$")
    estimated_duration: Optional[int] = Field(None, ge=1)
    learning_objectives: Optional[str] = Field(None, max_length=500)
    tags: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern="^(planning|active|paused|completed|cancelled)$")


class CodingSessionResponse(CodingSessionBase):
    """编程会话响应模式"""
    id: int
    user_id: int
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    actual_duration: Optional[int] = None  # 实际时长（分钟）
    lines_added: int = 0
    lines_deleted: int = 0
    lines_modified: int = 0
    files_created: int = 0
    files_modified: int = 0
    files_deleted: int = 0
    commits_count: int = 0
    code_quality_score: Optional[float] = None
    maintainability_score: Optional[float] = None
    complexity_score: Optional[float] = None
    test_coverage: Optional[float] = None
    performance_score: Optional[float] = None
    security_score: Optional[float] = None
    documentation_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CodingSessionStart(BaseModel):
    """开始编程会话模式"""
    session_id: int
    initial_notes: Optional[str] = Field(None, max_length=500)
    environment_info: Optional[Dict[str, Any]] = None


class CodingSessionEnd(BaseModel):
    """结束编程会话模式"""
    session_id: int
    completion_notes: Optional[str] = Field(None, max_length=1000)
    achievements: Optional[List[str]] = None
    challenges_faced: Optional[str] = Field(None, max_length=500)
    lessons_learned: Optional[str] = Field(None, max_length=500)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)


class CodingSessionStats(BaseModel):
    """编程会话统计模式"""
    total_sessions: int
    total_duration: int  # 总时长（分钟）
    average_duration: float  # 平均时长（分钟）
    total_lines_of_code: int
    languages_distribution: Dict[str, int]
    frameworks_distribution: Dict[str, int]
    difficulty_distribution: Dict[str, int]
    completion_rate: float
    average_quality_score: float
    productivity_trend: List[Dict[str, Any]]  # 生产力趋势
    recent_sessions: List[CodingSessionResponse]


class CodingSessionAnalysis(BaseModel):
    """编程会话分析模式"""
    session_id: int
    productivity_score: float
    focus_score: float
    learning_score: float
    code_quality_analysis: Dict[str, Any]
    time_distribution: Dict[str, float]  # 时间分布
    activity_patterns: Dict[str, Any]  # 活动模式
    improvement_suggestions: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]
    next_steps: List[str]


class CodingSessionReport(BaseModel):
    """编程会话报告模式"""
    session: CodingSessionResponse
    analysis: CodingSessionAnalysis
    code_records: List[Dict[str, Any]]  # 代码记录
    technical_debt_items: List[Dict[str, Any]]  # 技术债务项
    skill_improvements: List[Dict[str, Any]]  # 技能提升
    recommendations: List[str]
    export_formats: List[str] = ["pdf", "html", "json"]


class CodingSessionFilter(BaseModel):
    """编程会话过滤模式"""
    user_id: Optional[int] = None
    status: Optional[str] = None
    primary_language: Optional[str] = None
    difficulty_level: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    tags: Optional[List[str]] = None
    sort_by: str = Field("created_at", pattern="^(created_at|updated_at|duration|quality_score)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)