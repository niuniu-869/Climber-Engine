#!/usr/bin/env python3
"""
技能评估相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SkillAssessmentBase(BaseModel):
    """技能评估基础模式"""
    assessment_type: str = Field(..., pattern="^(self|peer|automated|comprehensive)$")
    skill_category: str = Field(..., max_length=100)  # 技能类别
    skill_name: str = Field(..., max_length=100)  # 具体技能名称
    current_level: str = Field(..., pattern="^(novice|beginner|intermediate|advanced|expert)$")
    target_level: Optional[str] = Field(None, pattern="^(novice|beginner|intermediate|advanced|expert)$")
    assessment_method: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


class SkillAssessmentCreate(SkillAssessmentBase):
    """创建技能评估模式"""
    user_id: int


class SkillAssessmentUpdate(BaseModel):
    """更新技能评估模式"""
    assessment_type: Optional[str] = Field(None, pattern="^(self|peer|automated|comprehensive)$")
    skill_category: Optional[str] = Field(None, max_length=100)
    skill_name: Optional[str] = Field(None, max_length=100)
    current_level: Optional[str] = Field(None, pattern="^(novice|beginner|intermediate|advanced|expert)$")
    target_level: Optional[str] = Field(None, pattern="^(novice|beginner|intermediate|advanced|expert)$")
    assessment_method: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    score: Optional[float] = Field(None, ge=0, le=100)
    confidence_level: Optional[float] = Field(None, ge=0, le=1)


class SkillAssessmentResponse(SkillAssessmentBase):
    """技能评估响应模式"""
    id: int
    user_id: int
    score: float = Field(..., ge=0, le=100)
    confidence_level: float = Field(..., ge=0, le=1)
    evidence: Optional[str] = None
    assessor_id: Optional[int] = None
    assessment_date: datetime
    next_assessment_date: Optional[datetime] = None
    improvement_plan: Optional[str] = None
    resources_recommended: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SkillRadarData(BaseModel):
    """技能雷达图数据模式"""
    skill_name: str
    current_level: float  # 0-5 的数值
    target_level: float
    category: str
    last_assessed: datetime
    improvement_rate: float  # 提升速度


class SkillAnalysis(BaseModel):
    """技能分析模式"""
    user_id: int
    overall_score: float
    skill_distribution: Dict[str, float]  # 技能分布
    strengths: List[str]  # 优势技能
    weaknesses: List[str]  # 薄弱技能
    improvement_areas: List[str]  # 需要改进的领域
    recommended_focus: List[str]  # 推荐关注的技能
    skill_gaps: List[Dict[str, Any]]  # 技能差距
    learning_path: List[Dict[str, Any]]  # 学习路径
    estimated_time_to_goals: Dict[str, int]  # 达到目标的预估时间


class SkillProgressTrend(BaseModel):
    """技能进步趋势模式"""
    skill_name: str
    skill_category: str
    progress_data: List[Dict[str, Any]]  # 时间序列数据
    trend_direction: str  # "improving", "stable", "declining"
    improvement_rate: float  # 改进速度
    projected_level: float  # 预测水平
    milestones: List[Dict[str, Any]]  # 里程碑


class SkillRecommendation(BaseModel):
    """技能推荐模式"""
    skill_name: str
    skill_category: str
    priority: str = Field(..., pattern="^(high|medium|low)$")
    reason: str
    learning_resources: List[Dict[str, str]]  # 学习资源
    estimated_time: int  # 预估学习时间（小时）
    prerequisites: List[str]  # 前置技能
    related_skills: List[str]  # 相关技能
    career_impact: str  # 职业影响


class SkillAssessmentBatch(BaseModel):
    """批量技能评估模式"""
    user_id: int
    assessments: List[SkillAssessmentCreate]
    assessment_context: Optional[str] = None
    auto_generate_plan: bool = True


class SkillComparisonData(BaseModel):
    """技能对比数据模式"""
    user_skills: Dict[str, float]
    peer_average: Dict[str, float]
    industry_benchmark: Dict[str, float]
    percentile_ranking: Dict[str, float]
    comparison_insights: List[str]


class SkillCertification(BaseModel):
    """技能认证模式"""
    skill_name: str
    certification_name: str
    issuer: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    verification_url: Optional[str] = None
    skill_level_certified: str


class SkillAssessmentReport(BaseModel):
    """技能评估报告模式"""
    user_id: int
    report_date: datetime
    assessment_period: Dict[str, datetime]  # 评估周期
    overall_analysis: SkillAnalysis
    skill_radar: List[SkillRadarData]
    progress_trends: List[SkillProgressTrend]
    recommendations: List[SkillRecommendation]
    certifications: List[SkillCertification]
    next_assessment_plan: Dict[str, Any]
    export_formats: List[str] = ["pdf", "html", "json"]


class SkillFilter(BaseModel):
    """技能过滤模式"""
    user_id: Optional[int] = None
    skill_category: Optional[str] = None
    assessment_type: Optional[str] = None
    current_level: Optional[str] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=0, le=100)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort_by: str = Field("assessment_date", pattern="^(assessment_date|score|skill_name|current_level)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)