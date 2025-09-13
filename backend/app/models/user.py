#!/usr/bin/env python3
"""
用户数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    
    # 用户档案
    bio = Column(Text)  # 个人简介
    avatar_url = Column(String(500))  # 头像URL
    github_username = Column(String(100))  # GitHub用户名
    
    # 技能档案
    skill_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced, expert
    primary_languages = Column(JSON)  # 主要编程语言列表
    frameworks = Column(JSON)  # 熟悉的框架列表
    tools = Column(JSON)  # 使用的工具列表
    
    # 学习偏好
    learning_style = Column(String(20), default="balanced")  # visual, auditory, kinesthetic, balanced
    preferred_difficulty = Column(String(20), default="medium")  # easy, medium, hard, adaptive
    daily_goal_minutes = Column(Integer, default=30)  # 每日学习目标（分钟）
    
    # 统计数据
    total_coding_time = Column(Integer, default=0)  # 总编程时间（分钟）
    total_sessions = Column(Integer, default=0)  # 总会话数
    current_streak = Column(Integer, default=0)  # 当前连续学习天数
    longest_streak = Column(Integer, default=0)  # 最长连续学习天数
    
    # 技术债务分析
    tech_debt_score = Column(Float, default=0.0)  # 技术债务评分
    knowledge_gaps = Column(JSON)  # 知识缺口分析
    strength_areas = Column(JSON)  # 优势领域
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    coding_sessions = relationship("CodingSession", back_populates="user", cascade="all, delete-orphan")
    skill_assessments = relationship("SkillAssessment", back_populates="user", cascade="all, delete-orphan")
    learning_tasks = relationship("LearningTask", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', skill_level='{self.skill_level}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "skill_level": self.skill_level,
            "total_coding_time": self.total_coding_time,
            "total_sessions": self.total_sessions,
            "current_streak": self.current_streak,
            "tech_debt_score": self.tech_debt_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }