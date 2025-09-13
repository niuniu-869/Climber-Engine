#!/usr/bin/env python3
"""
学习内容管理相关的Pydantic模式
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LearningArticleBase(BaseModel):
    """学习文章基础模式"""
    title: str = Field(..., max_length=300, description="文章标题")
    subtitle: Optional[str] = Field(None, max_length=500, description="副标题")
    summary: Optional[str] = Field(None, description="文章摘要")
    content: str = Field(..., description="文章内容")
    article_type: str = Field(..., description="文章类型")
    category: str = Field(..., description="技术分类")
    subcategory: Optional[str] = None
    target_technologies: List[str] = Field(..., description="目标技术栈")
    difficulty_level: str = Field(..., description="难度级别")
    target_audience: Optional[str] = None


class LearningArticleCreate(LearningArticleBase):
    """创建学习文章模式"""
    user_id: int
    related_concepts: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    key_takeaways: Optional[List[str]] = None
    practical_applications: Optional[List[str]] = None
    sections: Optional[List[Dict[str, Any]]] = None
    code_examples: Optional[List[Dict[str, Any]]] = None
    external_resources: Optional[List[Dict[str, str]]] = None
    personalization_factors: Optional[Dict[str, Any]] = None
    ai_model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class LearningArticleUpdate(BaseModel):
    """更新学习文章模式"""
    title: Optional[str] = Field(None, max_length=300)
    subtitle: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = None
    content: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    key_takeaways: Optional[List[str]] = None
    content_quality_score: Optional[float] = Field(None, ge=0, le=10)
    readability_score: Optional[float] = Field(None, ge=0, le=10)
    educational_value: Optional[float] = Field(None, ge=0, le=10)
    accuracy_score: Optional[float] = Field(None, ge=0, le=10)
    user_rating: Optional[float] = Field(None, ge=0, le=5)
    estimated_reading_time: Optional[int] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    version: Optional[str] = None
    revision_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class LearningArticleResponse(LearningArticleBase):
    """学习文章响应模式"""
    id: int
    user_id: int
    skill_level_required: Optional[str] = None
    related_concepts: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    key_takeaways: Optional[List[str]] = None
    practical_applications: Optional[List[str]] = None
    sections: Optional[List[Dict[str, Any]]] = None
    code_examples: Optional[List[Dict[str, Any]]] = None
    diagrams: Optional[List[Dict[str, Any]]] = None
    external_resources: Optional[List[Dict[str, str]]] = None
    personalization_factors: Optional[Dict[str, Any]] = None
    user_interests: Optional[List[str]] = None
    learning_style_match: float = 0.0
    content_quality_score: float = 0.0
    readability_score: float = 0.0
    educational_value: float = 0.0
    accuracy_score: float = 0.0
    view_count: int = 0
    completion_rate: float = 0.0
    user_rating: float = 0.0
    bookmark_count: int = 0
    estimated_reading_time: int = 0
    actual_reading_time: int = 0
    comprehension_score: float = 0.0
    retention_score: float = 0.0
    ai_model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    generation_parameters: Optional[Dict[str, Any]] = None
    ai_confidence_score: float = 0.0
    status: str = "draft"
    is_featured: bool = False
    is_public: bool = False
    version: str = "1.0"
    revision_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    last_viewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningQuestionBase(BaseModel):
    """学习题目基础模式"""
    title: str = Field(..., max_length=300, description="题目标题")
    question_text: str = Field(..., description="题目内容")
    question_type: str = Field(..., description="题目类型")
    target_technologies: List[str] = Field(..., description="目标技术栈")
    difficulty_level: str = Field(..., description="难度级别")
    complexity_score: float = Field(0.0, ge=0, le=10, description="复杂度评分")
    estimated_time: int = Field(0, ge=0, description="预计完成时间（分钟）")


class LearningQuestionCreate(LearningQuestionBase):
    """创建学习题目模式"""
    user_id: int
    related_article_id: Optional[int] = None
    concepts_tested: Optional[List[str]] = None
    skills_assessed: Optional[List[str]] = None
    options: Optional[Any] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    starter_code: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    expected_output: Optional[str] = None
    solution_code: Optional[str] = None
    scoring_criteria: Optional[List[Dict[str, Any]]] = None
    learning_objectives: Optional[List[str]] = None
    knowledge_points: Optional[List[str]] = None
    ai_model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class LearningQuestionUpdate(BaseModel):
    """更新学习题目模式"""
    title: Optional[str] = Field(None, max_length=300)
    question_text: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    max_score: Optional[float] = Field(None, ge=0)
    passing_score: Optional[float] = Field(None, ge=0)
    question_quality_score: Optional[float] = Field(None, ge=0, le=10)
    clarity_score: Optional[float] = Field(None, ge=0, le=10)
    educational_value: Optional[float] = Field(None, ge=0, le=10)
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class LearningQuestionResponse(LearningQuestionBase):
    """学习题目响应模式"""
    id: int
    user_id: int
    related_article_id: Optional[int] = None
    concepts_tested: Optional[List[str]] = None
    skills_assessed: Optional[List[str]] = None
    options: Optional[Any] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    starter_code: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    expected_output: Optional[str] = None
    solution_code: Optional[str] = None
    scoring_criteria: Optional[List[Dict[str, Any]]] = None
    max_score: float = 100.0
    passing_score: float = 60.0
    learning_objectives: Optional[List[str]] = None
    knowledge_points: Optional[List[str]] = None
    skill_requirements: Optional[List[str]] = None
    personalization_factors: Optional[Dict[str, Any]] = None
    adaptive_difficulty: bool = True
    user_preference_match: float = 0.0
    question_quality_score: float = 0.0
    clarity_score: float = 0.0
    educational_value: float = 0.0
    discrimination_index: float = 0.0
    attempt_count: int = 0
    correct_count: int = 0
    average_score: float = 0.0
    average_time: float = 0.0
    ai_model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    generation_parameters: Optional[Dict[str, Any]] = None
    ai_confidence_score: float = 0.0
    status: str = "draft"
    is_featured: bool = False
    is_public: bool = False
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_attempted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuestionAttemptBase(BaseModel):
    """题目尝试基础模式"""
    user_answer: Optional[str] = None
    submitted_code: Optional[str] = None
    is_correct: bool = False
    score: float = Field(0.0, ge=0, description="得分")


class QuestionAttemptCreate(QuestionAttemptBase):
    """创建题目尝试模式"""
    user_id: int
    question_id: int
    time_spent: int = Field(0, ge=0, description="花费时间（秒）")
    hint_used_count: int = 0
    help_requested: bool = False
    confidence_level: float = Field(0.0, ge=0, le=1)
    understanding_level: float = Field(0.0, ge=0, le=1)
    satisfaction_rating: int = Field(3, ge=1, le=5)


class QuestionAttemptUpdate(BaseModel):
    """更新题目尝试模式"""
    user_answer: Optional[str] = None
    submitted_code: Optional[str] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = Field(None, ge=0)
    automated_feedback: Optional[Dict[str, Any]] = None
    detailed_analysis: Optional[Dict[str, Any]] = None
    improvement_suggestions: Optional[List[str]] = None
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    understanding_level: Optional[float] = Field(None, ge=0, le=1)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)


class QuestionAttemptResponse(QuestionAttemptBase):
    """题目尝试响应模式"""
    id: int
    user_id: int
    question_id: int
    time_spent: int = 0
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    hint_used_count: int = 0
    attempts_before_correct: int = 0
    help_requested: bool = False
    automated_feedback: Optional[Dict[str, Any]] = None
    detailed_analysis: Optional[Dict[str, Any]] = None
    improvement_suggestions: Optional[List[str]] = None
    confidence_level: float = 0.0
    understanding_level: float = 0.0
    satisfaction_rating: int = 3
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningArticleSummary(BaseModel):
    """学习文章摘要模式"""
    id: int
    title: str
    subtitle: Optional[str] = None
    article_type: str
    category: str
    target_technologies: List[str]
    difficulty_level: str
    estimated_reading_time: int
    content_quality_score: float
    educational_value: float
    view_count: int
    user_rating: float
    status: str
    is_featured: bool
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningQuestionSummary(BaseModel):
    """学习题目摘要模式"""
    id: int
    title: str
    question_type: str
    target_technologies: List[str]
    difficulty_level: str
    complexity_score: float
    estimated_time: int
    attempt_count: int
    average_score: float
    question_quality_score: float
    status: str
    is_featured: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningContentDashboard(BaseModel):
    """学习内容仪表板模式"""
    user_id: int
    total_articles: int
    total_questions: int
    published_articles: int
    active_questions: int
    total_views: int
    total_attempts: int
    average_article_rating: float
    average_question_score: float
    featured_content_count: int
    recent_articles: List[LearningArticleSummary]
    recent_questions: List[LearningQuestionSummary]
    popular_technologies: List[Dict[str, Any]]
    content_quality_trends: List[Dict[str, Any]]


class LearningContentFilter(BaseModel):
    """学习内容过滤模式"""
    user_id: Optional[int] = None
    content_type: Optional[str] = None  # "article" or "question"
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    technologies: Optional[List[str]] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    min_quality_score: Optional[float] = None
    max_quality_score: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_query: Optional[str] = None


class LearningContentStats(BaseModel):
    """学习内容统计模式"""
    total_articles: int
    total_questions: int
    total_attempts: int
    average_article_quality: float
    average_question_quality: float
    content_by_difficulty: Dict[str, int]
    content_by_category: Dict[str, int]
    content_by_technology: Dict[str, int]
    monthly_creation_trend: List[Dict[str, Any]]
    engagement_metrics: Dict[str, float]
    top_performing_content: List[Dict[str, Any]]


class ContentGenerationRequest(BaseModel):
    """内容生成请求模式"""
    content_type: str = Field(..., description="内容类型：article 或 question")
    user_id: int
    target_technologies: List[str] = Field(..., description="目标技术栈")
    difficulty_level: str = Field(..., description="难度级别")
    category: str = Field(..., description="技术分类")
    specific_topic: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    ai_model: str = "GPT-4"
    generation_parameters: Optional[Dict[str, Any]] = None


class ContentGenerationResponse(BaseModel):
    """内容生成响应模式"""
    success: bool
    content_id: Optional[int] = None
    content_type: str
    generation_time: float
    ai_confidence_score: float
    quality_estimate: float
    suggestions: Optional[List[str]] = None
    error_message: Optional[str] = None