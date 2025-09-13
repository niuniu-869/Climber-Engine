#!/usr/bin/env python3
"""
学习进度管理相关的Pydantic模式
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TechStackAssetBase(BaseModel):
    """技术栈资产基础模式"""
    technology_name: str = Field(..., description="技术名称")
    category: str = Field(..., description="技术分类")
    subcategory: Optional[str] = None
    proficiency_level: str = Field(..., description="熟练度级别")
    proficiency_score: float = Field(0.0, ge=0, le=100, description="熟练度评分")
    confidence_level: float = Field(0.0, ge=0, le=1, description="信心水平")


class TechStackAssetCreate(TechStackAssetBase):
    """创建技术栈资产模式"""
    user_id: int
    first_learned_date: Optional[datetime] = None
    use_cases: Optional[List[str]] = None
    project_types: Optional[List[str]] = None
    related_technologies: Optional[List[str]] = None


class TechStackAssetUpdate(BaseModel):
    """更新技术栈资产模式"""
    proficiency_level: Optional[str] = None
    proficiency_score: Optional[float] = Field(None, ge=0, le=100)
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    theoretical_knowledge: Optional[float] = Field(None, ge=0, le=100)
    practical_skills: Optional[float] = Field(None, ge=0, le=100)
    problem_solving: Optional[float] = Field(None, ge=0, le=100)
    best_practices: Optional[float] = Field(None, ge=0, le=100)
    advanced_features: Optional[float] = Field(None, ge=0, le=100)
    use_cases: Optional[List[str]] = None
    project_types: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    notable_projects: Optional[List[str]] = None
    is_active: Optional[bool] = None
    refresh_needed: Optional[bool] = None


class TechStackAssetResponse(TechStackAssetBase):
    """技术栈资产响应模式"""
    id: int
    user_id: int
    first_learned_date: Optional[datetime] = None
    last_practiced_date: Optional[datetime] = None
    total_practice_hours: float = 0.0
    project_count: int = 0
    theoretical_knowledge: float = 0.0
    practical_skills: float = 0.0
    problem_solving: float = 0.0
    best_practices: float = 0.0
    advanced_features: float = 0.0
    use_cases: Optional[List[str]] = None
    project_types: Optional[List[str]] = None
    industry_applications: Optional[List[str]] = None
    related_technologies: Optional[List[str]] = None
    complementary_skills: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    notable_projects: Optional[List[str]] = None
    market_demand: float = 0.0
    salary_impact: float = 0.0
    career_relevance: float = 0.0
    is_active: bool = True
    decay_rate: float = 0.0
    refresh_needed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_assessed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechStackDebtBase(BaseModel):
    """技术栈负债基础模式"""
    technology_name: str = Field(..., description="技术名称")
    category: str = Field(..., description="技术分类")
    subcategory: Optional[str] = None
    urgency_level: str = Field("medium", description="紧急程度")
    importance_score: float = Field(0.0, ge=0, le=100, description="重要性评分")
    career_impact: float = Field(0.0, ge=0, le=100, description="职业影响")
    project_relevance: float = Field(0.0, ge=0, le=100, description="项目相关性")
    target_proficiency_level: str = Field("intermediate", description="目标熟练度")


class TechStackDebtCreate(TechStackDebtBase):
    """创建技术栈负债模式"""
    user_id: int
    estimated_learning_hours: Optional[float] = None
    learning_priority: int = Field(3, ge=1, le=5)
    planned_start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    learning_motivation: Optional[str] = None
    specific_goals: Optional[List[str]] = None


class TechStackDebtUpdate(BaseModel):
    """更新技术栈负债模式"""
    urgency_level: Optional[str] = None
    importance_score: Optional[float] = Field(None, ge=0, le=100)
    career_impact: Optional[float] = Field(None, ge=0, le=100)
    project_relevance: Optional[float] = Field(None, ge=0, le=100)
    target_proficiency_level: Optional[str] = None
    estimated_learning_hours: Optional[float] = None
    learning_priority: Optional[int] = Field(None, ge=1, le=5)
    planned_start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    learning_progress: Optional[float] = Field(None, ge=0, le=100)
    time_invested: Optional[float] = None
    status: Optional[str] = None
    learning_motivation: Optional[str] = None
    specific_goals: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TechStackDebtResponse(TechStackDebtBase):
    """技术栈负债响应模式"""
    id: int
    user_id: int
    estimated_learning_hours: Optional[float] = None
    learning_priority: int = 3
    planned_start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    prerequisites: Optional[List[str]] = None
    learning_path: Optional[List[str]] = None
    recommended_resources: Optional[List[str]] = None
    practice_projects: Optional[List[str]] = None
    learning_barriers: Optional[List[str]] = None
    difficulty_factors: Optional[List[str]] = None
    learning_motivation: Optional[str] = None
    specific_goals: Optional[List[str]] = None
    success_metrics: Optional[List[str]] = None
    market_demand: float = 0.0
    salary_potential: float = 0.0
    job_opportunities: float = 0.0
    learning_progress: float = 0.0
    time_invested: float = 0.0
    milestones_achieved: Optional[List[str]] = None
    current_challenges: Optional[List[str]] = None
    status: str = "identified"
    is_active: bool = True
    auto_generated: bool = False
    ai_recommendations: Optional[List[str]] = None
    personalized_tips: Optional[List[str]] = None
    identified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningProgressSummaryBase(BaseModel):
    """学习进度总结基础模式"""
    report_period: str = Field(..., description="报告周期")
    period_start: datetime = Field(..., description="报告期开始")
    period_end: datetime = Field(..., description="报告期结束")


class LearningProgressSummaryCreate(LearningProgressSummaryBase):
    """创建学习进度总结模式"""
    user_id: int
    total_assets: int = 0
    new_assets_acquired: int = 0
    assets_improved: int = 0
    total_debts: int = 0
    new_debts_identified: int = 0
    debts_resolved: int = 0
    total_learning_hours: float = 0.0
    practice_sessions: int = 0
    projects_completed: int = 0


class LearningProgressSummaryResponse(LearningProgressSummaryBase):
    """学习进度总结响应模式"""
    id: int
    user_id: int
    total_assets: int = 0
    new_assets_acquired: int = 0
    assets_improved: int = 0
    average_asset_score: float = 0.0
    total_debts: int = 0
    new_debts_identified: int = 0
    debts_resolved: int = 0
    average_debt_priority: float = 0.0
    total_learning_hours: float = 0.0
    practice_sessions: int = 0
    projects_completed: int = 0
    skill_growth_rate: float = 0.0
    learning_velocity: float = 0.0
    consistency_score: float = 0.0
    top_performing_areas: Optional[List[str]] = None
    improvement_areas: Optional[List[str]] = None
    learning_patterns: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    goals_set: int = 0
    goals_achieved: int = 0
    goal_achievement_rate: float = 0.0
    generated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechStackAssetSummary(BaseModel):
    """技术栈资产摘要模式"""
    id: int
    technology_name: str
    category: str
    proficiency_level: str
    proficiency_score: float
    confidence_level: float
    total_practice_hours: float
    project_count: int
    is_active: bool
    last_practiced_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechStackDebtSummary(BaseModel):
    """技术栈负债摘要模式"""
    id: int
    technology_name: str
    category: str
    urgency_level: str
    importance_score: float
    learning_priority: int
    learning_progress: float
    status: str
    target_completion_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningProgressDashboard(BaseModel):
    """学习进度仪表板模式"""
    user_id: int
    total_assets: int
    total_debts: int
    active_learning_tasks: int
    this_month_hours: float
    skill_growth_rate: float
    top_assets: List[TechStackAssetSummary]
    urgent_debts: List[TechStackDebtSummary]
    recent_achievements: List[str]
    upcoming_milestones: List[Dict[str, Any]]
    learning_streak: int
    progress_trends: Dict[str, List[float]]


class TechStackRecommendation(BaseModel):
    """技术栈推荐模式"""
    technology_name: str
    category: str
    recommendation_type: str  # "learn_next", "improve_existing", "market_trending"
    priority_score: float
    reasoning: str
    estimated_learning_time: Optional[float] = None
    market_demand: float
    career_impact: float
    prerequisites: List[str]
    learning_resources: List[Dict[str, str]]


class LearningProgressFilter(BaseModel):
    """学习进度过滤模式"""
    user_id: Optional[int] = None
    category: Optional[str] = None
    proficiency_level: Optional[str] = None
    urgency_level: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    technologies: Optional[List[str]] = None


class LearningProgressStats(BaseModel):
    """学习进度统计模式"""
    total_technologies: int
    assets_count: int
    debts_count: int
    average_proficiency: float
    total_learning_hours: float
    active_learning_rate: float
    skill_distribution: Dict[str, int]
    category_breakdown: Dict[str, Dict[str, int]]
    monthly_progress: List[Dict[str, Any]]
    learning_velocity_trend: List[float]