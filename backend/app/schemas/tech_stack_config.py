#!/usr/bin/env python3
"""
技术栈配置相关的Pydantic模式
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TechStackCategoryBase(BaseModel):
    """技术栈分类基础模式"""
    name: str = Field(..., max_length=100, description="分类名称")
    display_name: str = Field(..., max_length=100, description="显示名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    level: int = Field(1, ge=1, le=5, description="分类层级")
    sort_order: int = Field(0, description="排序顺序")
    icon: Optional[str] = Field(None, max_length=100, description="图标")
    color: Optional[str] = Field(None, max_length=20, description="颜色代码")


class TechStackCategoryCreate(TechStackCategoryBase):
    """创建技术栈分类模式"""
    pass


class TechStackCategoryUpdate(BaseModel):
    """更新技术栈分类模式"""
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = Field(None, ge=1, le=5)
    sort_order: Optional[int] = None
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    technology_count: Optional[int] = None
    popularity_score: Optional[float] = Field(None, ge=0, le=100)


class TechStackCategoryResponse(TechStackCategoryBase):
    """技术栈分类响应模式"""
    id: int
    is_active: bool = True
    technology_count: int = 0
    popularity_score: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechStackStandardBase(BaseModel):
    """标准技术栈基础模式"""
    name: str = Field(..., max_length=100, description="标准名称")
    display_name: str = Field(..., max_length=100, description="显示名称")
    description: Optional[str] = Field(None, description="技术描述")
    type: str = Field(..., max_length=50, description="技术类型")
    subtype: Optional[str] = Field(None, max_length=50, description="子类型")
    domain: Optional[str] = Field(None, max_length=50, description="应用领域")
    learning_difficulty: str = Field("medium", description="学习难度")
    complexity_score: float = Field(5.0, ge=1, le=10, description="复杂度评分")
    current_status: str = Field("active", description="当前状态")


class TechStackStandardCreate(TechStackStandardBase):
    """创建标准技术栈模式"""
    category_id: int = Field(..., description="分类ID")
    aliases: Optional[List[str]] = None
    common_variations: Optional[List[str]] = None
    official_name: Optional[str] = Field(None, max_length=100)
    version_info: Optional[Dict[str, Any]] = None
    release_year: Optional[int] = None
    learning_curve: str = "moderate"
    prerequisites: Optional[List[str]] = None
    recommended_background: Optional[List[str]] = None
    related_technologies: Optional[List[str]] = None
    complementary_skills: Optional[List[str]] = None
    competing_alternatives: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    industry_applications: Optional[List[str]] = None
    project_types: Optional[List[str]] = None
    key_features: Optional[List[str]] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    official_docs_url: Optional[str] = Field(None, max_length=500)
    learning_resources: Optional[List[Dict[str, str]]] = None
    certification_info: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class TechStackStandardUpdate(BaseModel):
    """更新标准技术栈模式"""
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    learning_difficulty: Optional[str] = None
    complexity_score: Optional[float] = Field(None, ge=1, le=10)
    current_status: Optional[str] = None
    market_demand: Optional[float] = Field(None, ge=0, le=100)
    job_market_score: Optional[float] = Field(None, ge=0, le=100)
    salary_impact: Optional[float] = Field(None, ge=0, le=100)
    growth_trend: Optional[str] = None
    popularity_rank: Optional[int] = None
    github_stars: Optional[int] = None
    stackoverflow_questions: Optional[int] = None
    job_postings_count: Optional[int] = None
    ecosystem_maturity: Optional[float] = Field(None, ge=0, le=100)
    community_size: Optional[str] = None
    vendor_support: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_trending: Optional[bool] = None
    data_quality_score: Optional[float] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class TechStackStandardResponse(TechStackStandardBase):
    """标准技术栈响应模式"""
    id: int
    category_id: int
    aliases: Optional[List[str]] = None
    common_variations: Optional[List[str]] = None
    official_name: Optional[str] = None
    version_info: Optional[Dict[str, Any]] = None
    release_year: Optional[int] = None
    learning_curve: str = "moderate"
    prerequisites: Optional[List[str]] = None
    recommended_background: Optional[List[str]] = None
    skill_dependencies: Optional[List[str]] = None
    related_technologies: Optional[List[str]] = None
    complementary_skills: Optional[List[str]] = None
    competing_alternatives: Optional[List[str]] = None
    market_demand: float = 0.0
    job_market_score: float = 0.0
    salary_impact: float = 0.0
    growth_trend: str = "stable"
    popularity_rank: Optional[int] = None
    github_stars: int = 0
    stackoverflow_questions: int = 0
    job_postings_count: int = 0
    official_docs_url: Optional[str] = None
    learning_resources: Optional[List[Dict[str, str]]] = None
    certification_info: Optional[List[Dict[str, Any]]] = None
    community_resources: Optional[List[Dict[str, str]]] = None
    use_cases: Optional[List[str]] = None
    industry_applications: Optional[List[str]] = None
    project_types: Optional[List[str]] = None
    company_usage: Optional[List[str]] = None
    key_features: Optional[List[str]] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    performance_characteristics: Optional[Dict[str, Any]] = None
    ecosystem_maturity: float = 0.0
    community_size: str = "medium"
    vendor_support: str = "community"
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_featured: bool = False
    is_trending: bool = False
    data_sources: Optional[List[str]] = None
    last_market_update: Optional[datetime] = None
    data_quality_score: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechStackMappingBase(BaseModel):
    """技术栈映射基础模式"""
    input_name: str = Field(..., max_length=100, description="输入名称")
    standard_name: str = Field(..., max_length=100, description="标准名称")
    confidence_score: float = Field(1.0, ge=0, le=1, description="映射置信度")
    mapping_type: str = Field("alias", description="映射类型")
    source: str = Field("manual", description="来源")


class TechStackMappingCreate(TechStackMappingBase):
    """创建技术栈映射模式"""
    pass


class TechStackMappingUpdate(BaseModel):
    """更新技术栈映射模式"""
    standard_name: Optional[str] = Field(None, max_length=100)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    mapping_type: Optional[str] = None
    source: Optional[str] = None
    is_verified: Optional[bool] = None
    verified_by: Optional[str] = Field(None, max_length=100)


class TechStackMappingResponse(TechStackMappingBase):
    """技术栈映射响应模式"""
    id: int
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_verified: bool = False
    verified_by: Optional[str] = None
    verification_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechStackCategorySummary(BaseModel):
    """技术栈分类摘要模式"""
    id: int
    name: str
    display_name: str
    level: int
    technology_count: int
    popularity_score: float
    is_active: bool

    class Config:
        from_attributes = True


class TechStackStandardSummary(BaseModel):
    """标准技术栈摘要模式"""
    id: int
    name: str
    display_name: str
    type: str
    domain: Optional[str] = None
    learning_difficulty: str
    complexity_score: float
    market_demand: float
    current_status: str
    is_featured: bool
    is_trending: bool

    class Config:
        from_attributes = True


class TechStackRecommendation(BaseModel):
    """技术栈推荐模式"""
    technology: TechStackStandardSummary
    recommendation_score: float
    recommendation_reasons: List[str]
    learning_priority: int
    estimated_learning_time: Optional[float] = None
    career_impact: float
    market_relevance: float
    skill_gap_analysis: Dict[str, Any]
    learning_path: List[str]
    resources: List[Dict[str, str]]


class TechStackAnalysis(BaseModel):
    """技术栈分析模式"""
    technology_name: str
    current_market_position: Dict[str, float]
    growth_trajectory: List[Dict[str, Any]]
    skill_demand_forecast: Dict[str, float]
    learning_investment_analysis: Dict[str, Any]
    career_impact_assessment: Dict[str, float]
    competitive_landscape: List[Dict[str, Any]]
    recommendations: List[str]


class TechStackFilter(BaseModel):
    """技术栈过滤模式"""
    category_id: Optional[int] = None
    type: Optional[str] = None
    domain: Optional[str] = None
    learning_difficulty: Optional[str] = None
    current_status: Optional[str] = None
    min_market_demand: Optional[float] = None
    max_complexity_score: Optional[float] = None
    is_featured: Optional[bool] = None
    is_trending: Optional[bool] = None
    search_query: Optional[str] = None
    tags: Optional[List[str]] = None


class TechStackStats(BaseModel):
    """技术栈统计模式"""
    total_technologies: int
    total_categories: int
    active_technologies: int
    featured_technologies: int
    trending_technologies: int
    technologies_by_difficulty: Dict[str, int]
    technologies_by_domain: Dict[str, int]
    technologies_by_status: Dict[str, int]
    average_market_demand: float
    average_complexity_score: float
    top_trending: List[TechStackStandardSummary]
    most_demanded: List[TechStackStandardSummary]
    easiest_to_learn: List[TechStackStandardSummary]


class TechStackSearchRequest(BaseModel):
    """技术栈搜索请求模式"""
    query: str = Field(..., min_length=1, description="搜索查询")
    filters: Optional[TechStackFilter] = None
    sort_by: str = Field("relevance", description="排序方式")
    sort_order: str = Field("desc", description="排序顺序")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")
    include_suggestions: bool = Field(True, description="是否包含搜索建议")


class TechStackSearchResponse(BaseModel):
    """技术栈搜索响应模式"""
    results: List[TechStackStandardSummary]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
    search_time: float
    suggestions: Optional[List[str]] = None
    filters_applied: Optional[TechStackFilter] = None


class TechStackNormalizationRequest(BaseModel):
    """技术栈标准化请求模式"""
    input_technologies: List[str] = Field(..., description="输入的技术栈列表")
    auto_create_mapping: bool = Field(True, description="是否自动创建映射")
    confidence_threshold: float = Field(0.8, ge=0, le=1, description="置信度阈值")


class TechStackNormalizationResponse(BaseModel):
    """技术栈标准化响应模式"""
    normalized_technologies: List[Dict[str, Any]]
    unmapped_technologies: List[str]
    new_mappings_created: int
    confidence_scores: Dict[str, float]
    suggestions: List[Dict[str, Any]]


class TechStackTrendAnalysis(BaseModel):
    """技术栈趋势分析模式"""
    technology_name: str
    trend_period: str  # "monthly", "quarterly", "yearly"
    trend_data: List[Dict[str, Any]]
    growth_rate: float
    market_position: str
    forecast: List[Dict[str, Any]]
    key_insights: List[str]
    recommendations: List[str]


class TechStackComparisonRequest(BaseModel):
    """技术栈对比请求模式"""
    technologies: List[str] = Field(..., min_items=2, max_items=5, description="要对比的技术栈")
    comparison_aspects: List[str] = Field(
        ["market_demand", "learning_difficulty", "salary_impact", "ecosystem_maturity"],
        description="对比维度"
    )


class TechStackComparisonResponse(BaseModel):
    """技术栈对比响应模式"""
    technologies: List[TechStackStandardSummary]
    comparison_matrix: Dict[str, Dict[str, Any]]
    recommendations: Dict[str, str]
    summary: Dict[str, Any]
    detailed_analysis: Dict[str, Dict[str, Any]]