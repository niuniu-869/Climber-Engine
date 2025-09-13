#!/usr/bin/env python3
"""
技术债务相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TechnicalDebtBase(BaseModel):
    """技术债务基础模式"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    debt_type: str = Field(..., pattern="^(code_smell|design_debt|documentation_debt|test_debt|architecture_debt|performance_debt|security_debt)$")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    category: str = Field(..., max_length=100)  # 债务类别
    file_path: Optional[str] = Field(None, max_length=500)  # 相关文件路径
    line_number: Optional[int] = Field(None, ge=1)  # 行号
    function_name: Optional[str] = Field(None, max_length=100)  # 函数名
    class_name: Optional[str] = Field(None, max_length=100)  # 类名
    estimated_effort: Optional[int] = Field(None, ge=1)  # 预估修复工作量（小时）
    business_impact: Optional[str] = Field(None, max_length=500)  # 业务影响
    technical_impact: Optional[str] = Field(None, max_length=500)  # 技术影响
    root_cause: Optional[str] = Field(None, max_length=500)  # 根本原因
    suggested_solution: Optional[str] = Field(None, max_length=1000)  # 建议解决方案
    tags: Optional[str] = Field(None, max_length=200)  # 标签


class TechnicalDebtCreate(TechnicalDebtBase):
    """创建技术债务模式"""
    user_id: int
    coding_session_id: Optional[int] = None
    detection_method: str = Field("manual", max_length=50)  # 检测方法


class TechnicalDebtUpdate(BaseModel):
    """更新技术债务模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    debt_type: Optional[str] = Field(None, pattern="^(code_smell|design_debt|documentation_debt|test_debt|architecture_debt|performance_debt|security_debt)$")
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    category: Optional[str] = Field(None, max_length=100)
    file_path: Optional[str] = Field(None, max_length=500)
    line_number: Optional[int] = Field(None, ge=1)
    function_name: Optional[str] = Field(None, max_length=100)
    class_name: Optional[str] = Field(None, max_length=100)
    estimated_effort: Optional[int] = Field(None, ge=1)
    business_impact: Optional[str] = Field(None, max_length=500)
    technical_impact: Optional[str] = Field(None, max_length=500)
    root_cause: Optional[str] = Field(None, max_length=500)
    suggested_solution: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern="^(open|in_progress|resolved|deferred|wont_fix)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")


class TechnicalDebtResponse(TechnicalDebtBase):
    """技术债务响应模式"""
    id: int
    user_id: int
    coding_session_id: Optional[int] = None
    status: str
    priority: str
    detection_method: str
    interest_rate: float = 0.0  # 利息率（债务增长速度）
    principal_amount: float = 0.0  # 本金（初始修复成本）
    current_cost: float = 0.0  # 当前成本
    resolution_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    assignee_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TechnicalDebtAnalysis(BaseModel):
    """技术债务分析模式"""
    file_path: str
    code_content: str
    analysis_results: List[Dict[str, Any]]  # 分析结果
    debt_score: float  # 债务评分
    complexity_metrics: Dict[str, float]  # 复杂度指标
    maintainability_index: float  # 可维护性指数
    code_smells: List[Dict[str, Any]]  # 代码异味
    security_issues: List[Dict[str, Any]]  # 安全问题
    performance_issues: List[Dict[str, Any]]  # 性能问题
    documentation_gaps: List[str]  # 文档缺失
    test_coverage_gaps: List[str]  # 测试覆盖缺失
    recommendations: List[str]  # 推荐修复


class TechnicalDebtSummary(BaseModel):
    """技术债务汇总模式"""
    user_id: int
    total_debt_items: int
    total_estimated_effort: int  # 总预估工作量（小时）
    total_current_cost: float  # 总当前成本
    debt_by_severity: Dict[str, int]  # 按严重程度分组
    debt_by_type: Dict[str, int]  # 按类型分组
    debt_by_status: Dict[str, int]  # 按状态分组
    average_resolution_time: float  # 平均解决时间（天）
    debt_trend: List[Dict[str, Any]]  # 债务趋势
    top_debt_files: List[Dict[str, Any]]  # 债务最多的文件
    resolution_rate: float  # 解决率
    new_debt_rate: float  # 新增债务率


class TechnicalDebtTrend(BaseModel):
    """技术债务趋势模式"""
    period: str  # 时间周期
    new_debt_count: int  # 新增债务数量
    resolved_debt_count: int  # 解决债务数量
    total_debt_count: int  # 总债务数量
    debt_score_change: float  # 债务评分变化
    effort_invested: int  # 投入工作量（小时）
    cost_saved: float  # 节省成本
    productivity_impact: float  # 生产力影响


class TechnicalDebtRecommendation(BaseModel):
    """技术债务解决推荐模式"""
    debt_id: int
    priority_score: float  # 优先级评分
    impact_analysis: Dict[str, Any]  # 影响分析
    effort_estimation: Dict[str, Any]  # 工作量估算
    risk_assessment: Dict[str, Any]  # 风险评估
    solution_approaches: List[Dict[str, Any]]  # 解决方案
    dependencies: List[int]  # 依赖的其他债务项
    prerequisites: List[str]  # 前置条件
    expected_benefits: List[str]  # 预期收益
    implementation_steps: List[str]  # 实施步骤
    testing_strategy: str  # 测试策略
    rollback_plan: str  # 回滚计划


class TechnicalDebtMetrics(BaseModel):
    """技术债务指标模式"""
    debt_ratio: float  # 债务比率
    debt_index: float  # 债务指数
    maintainability_score: float  # 可维护性评分
    code_quality_score: float  # 代码质量评分
    technical_debt_per_kloc: float  # 每千行代码的技术债务
    average_debt_age: float  # 平均债务年龄（天）
    debt_velocity: float  # 债务处理速度
    debt_accumulation_rate: float  # 债务累积率
    cost_of_delay: float  # 延迟成本
    roi_of_debt_reduction: float  # 债务减少的投资回报率


class TechnicalDebtReport(BaseModel):
    """技术债务报告模式"""
    user_id: int
    report_period: Dict[str, datetime]  # 报告周期
    summary: TechnicalDebtSummary
    trends: List[TechnicalDebtTrend]
    metrics: TechnicalDebtMetrics
    top_priority_items: List[TechnicalDebtResponse]
    recommendations: List[TechnicalDebtRecommendation]
    action_plan: List[Dict[str, Any]]  # 行动计划
    risk_analysis: Dict[str, Any]  # 风险分析
    cost_benefit_analysis: Dict[str, Any]  # 成本效益分析
    export_formats: List[str] = ["pdf", "html", "json"]


class TechnicalDebtFilter(BaseModel):
    """技术债务过滤模式"""
    user_id: Optional[int] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    debt_type: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    file_path: Optional[str] = None
    assignee_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_effort: Optional[int] = None
    max_effort: Optional[int] = None
    tags: Optional[List[str]] = None
    sort_by: str = Field("created_at", pattern="^(created_at|severity|priority|estimated_effort|current_cost)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)