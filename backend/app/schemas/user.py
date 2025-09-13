#!/usr/bin/env python3
"""
用户相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    github_username: Optional[str] = Field(None, max_length=50)
    linkedin_profile: Optional[str] = Field(None, max_length=200)
    preferred_language: Optional[str] = Field("Python", max_length=50)
    experience_level: Optional[str] = Field("beginner", pattern="^(beginner|intermediate|advanced|expert)$")
    learning_goals: Optional[str] = Field(None, max_length=1000)
    timezone: Optional[str] = Field("UTC", max_length=50)
    is_active: bool = True


class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """更新用户模式"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    github_username: Optional[str] = Field(None, max_length=50)
    linkedin_profile: Optional[str] = Field(None, max_length=200)
    preferred_language: Optional[str] = Field(None, max_length=50)
    experience_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced|expert)$")
    learning_goals: Optional[str] = Field(None, max_length=1000)
    timezone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    total_coding_sessions: int = 0
    total_learning_tasks: int = 0
    skill_assessment_count: int = 0
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str
    password: str


class UserToken(BaseModel):
    """用户令牌模式"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserPasswordChange(BaseModel):
    """用户密码修改模式"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserStats(BaseModel):
    """用户统计模式"""
    total_coding_time: int  # 总编程时间（分钟）
    total_lines_of_code: int  # 总代码行数
    languages_used: List[str]  # 使用的编程语言
    frameworks_used: List[str]  # 使用的框架
    skill_level_distribution: dict  # 技能水平分布
    learning_progress: dict  # 学习进度
    technical_debt_score: float  # 技术债务评分
    code_quality_average: float  # 平均代码质量
    recent_activity: List[dict]  # 最近活动
    achievements: List[str]  # 成就列表


class UserDashboard(BaseModel):
    """用户仪表板模式"""
    user: UserResponse
    stats: UserStats
    recent_sessions: List[dict]  # 最近的编程会话
    pending_tasks: List[dict]  # 待完成任务
    skill_radar: dict  # 技能雷达图数据
    progress_trends: dict  # 进度趋势数据
    recommendations: List[str]  # 推荐内容


class UserPreferences(BaseModel):
    """用户偏好设置模式"""
    theme: str = Field("light", pattern="^(light|dark|auto)$")
    language: str = Field("en", max_length=10)
    notifications_enabled: bool = True
    email_notifications: bool = True
    weekly_reports: bool = True
    privacy_level: str = Field("public", pattern="^(public|friends|private)$")
    auto_save_interval: int = Field(300, ge=60, le=3600)  # 自动保存间隔（秒）
    code_editor_theme: str = Field("vs-code", max_length=50)
    font_size: int = Field(14, ge=10, le=24)
    show_line_numbers: bool = True
    enable_autocomplete: bool = True