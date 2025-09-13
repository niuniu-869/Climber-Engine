#!/usr/bin/env python3
"""
学习任务相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LearningTaskBase(BaseModel):
    """学习任务基础模式"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    task_type: str = Field(..., pattern="^(tutorial|exercise|project|reading|video|quiz|practice)$")
    difficulty_level: str = Field(..., pattern="^(beginner|intermediate|advanced|expert)$")
    skill_category: str = Field(..., max_length=100)
    target_skills: str = Field(..., max_length=200)  # 逗号分隔的目标技能
    estimated_duration: int = Field(..., ge=1)  # 预估时长（分钟）
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    prerequisites: Optional[str] = Field(None, max_length=200)  # 前置条件
    learning_objectives: Optional[str] = Field(None, max_length=500)
    resources: Optional[str] = Field(None, max_length=1000)  # 学习资源
    tags: Optional[str] = Field(None, max_length=200)  # 标签


class LearningTaskCreate(LearningTaskBase):
    """创建学习任务模式"""
    user_id: int
    source: Optional[str] = Field("manual", max_length=50)  # 任务来源


class LearningTaskUpdate(BaseModel):
    """更新学习任务模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    task_type: Optional[str] = Field(None, pattern="^(tutorial|exercise|project|reading|video|quiz|practice)$")
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced|expert)$")
    skill_category: Optional[str] = Field(None, max_length=100)
    target_skills: Optional[str] = Field(None, max_length=200)
    estimated_duration: Optional[int] = Field(None, ge=1)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    prerequisites: Optional[str] = Field(None, max_length=200)
    learning_objectives: Optional[str] = Field(None, max_length=500)
    resources: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|paused|completed|cancelled|skipped)$")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)


class LearningTaskResponse(LearningTaskBase):
    """学习任务响应模式"""
    id: int
    user_id: int
    status: str
    progress_percentage: float = 0.0
    actual_duration: Optional[int] = None  # 实际花费时长（分钟）
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    source: str  # 任务来源
    difficulty_rating: Optional[float] = None  # 用户评价的难度
    satisfaction_rating: Optional[float] = None  # 满意度评分
    learning_outcome: Optional[str] = None  # 学习成果
    notes: Optional[str] = None  # 用户笔记
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LearningTaskStart(BaseModel):
    """开始学习任务模式"""
    task_id: int
    start_notes: Optional[str] = Field(None, max_length=500)
    environment_setup: Optional[Dict[str, Any]] = None


class LearningTaskProgress(BaseModel):
    """学习任务进度更新模式"""
    task_id: int
    progress_percentage: float = Field(..., ge=0, le=100)
    current_step: Optional[str] = Field(None, max_length=200)
    time_spent: Optional[int] = None  # 本次花费时间（分钟）
    notes: Optional[str] = Field(None, max_length=500)
    challenges_faced: Optional[str] = Field(None, max_length=500)


class LearningTaskComplete(BaseModel):
    """完成学习任务模式"""
    task_id: int
    completion_notes: Optional[str] = Field(None, max_length=1000)
    learning_outcome: Optional[str] = Field(None, max_length=500)
    difficulty_rating: Optional[float] = Field(None, ge=1, le=5)
    satisfaction_rating: Optional[float] = Field(None, ge=1, le=5)
    would_recommend: Optional[bool] = None
    skills_gained: Optional[List[str]] = None
    next_steps: Optional[str] = Field(None, max_length=500)


class LearningTaskGeneration(BaseModel):
    """学习任务生成请求模式"""
    user_id: int
    skill_gaps: List[str]  # 技能差距
    learning_preferences: Dict[str, Any]  # 学习偏好
    available_time: int  # 可用时间（分钟/周）
    difficulty_preference: str = Field("mixed", pattern="^(easy|medium|hard|mixed)$")
    task_types: List[str] = []  # 偏好的任务类型
    focus_areas: List[str] = []  # 重点关注领域
    exclude_topics: List[str] = []  # 排除的主题
    max_tasks: int = Field(10, ge=1, le=50)


class LearningTaskRecommendation(BaseModel):
    """学习任务推荐模式"""
    task: LearningTaskCreate
    relevance_score: float  # 相关性评分
    difficulty_match: float  # 难度匹配度
    time_fit: float  # 时间适配度
    skill_impact: float  # 技能影响度
    recommendation_reason: str  # 推荐理由
    alternative_tasks: List[Dict[str, Any]]  # 替代任务


class LearningTaskStats(BaseModel):
    """学习任务统计模式"""
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    completion_rate: float
    average_completion_time: float  # 平均完成时间（分钟）
    total_learning_time: int  # 总学习时间（分钟）
    skill_categories_covered: List[str]
    difficulty_distribution: Dict[str, int]
    task_type_distribution: Dict[str, int]
    monthly_progress: List[Dict[str, Any]]  # 月度进度
    productivity_trends: List[Dict[str, Any]]  # 生产力趋势


class LearningPath(BaseModel):
    """学习路径模式"""
    name: str
    description: str
    target_role: str  # 目标角色
    estimated_duration: int  # 预估总时长（小时）
    difficulty_progression: str  # 难度递进
    tasks: List[LearningTaskResponse]  # 任务序列
    milestones: List[Dict[str, Any]]  # 里程碑
    prerequisites: List[str]  # 前置条件
    learning_outcomes: List[str]  # 学习成果
    completion_criteria: Dict[str, Any]  # 完成标准


class LearningTaskAnalysis(BaseModel):
    """学习任务分析模式"""
    task_id: int
    effectiveness_score: float  # 有效性评分
    engagement_level: float  # 参与度
    knowledge_retention: float  # 知识保持度
    skill_improvement: Dict[str, float]  # 技能提升
    time_efficiency: float  # 时间效率
    difficulty_accuracy: float  # 难度准确性
    resource_quality: float  # 资源质量
    improvement_suggestions: List[str]  # 改进建议
    similar_tasks: List[Dict[str, Any]]  # 相似任务


class LearningTaskFilter(BaseModel):
    """学习任务过滤模式"""
    user_id: Optional[int] = None
    status: Optional[str] = None
    task_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    skill_category: Optional[str] = None
    priority: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    sort_by: str = Field("created_at", pattern="^(created_at|due_date|priority|difficulty_level|progress_percentage)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)