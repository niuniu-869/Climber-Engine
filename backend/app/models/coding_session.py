#!/usr/bin/env python3
"""
编程会话数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class CodingSession(Base):
    """编程会话模型"""
    
    __tablename__ = "coding_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 会话基本信息
    title = Column(String(200))  # 会话标题
    description = Column(Text)  # 会话描述
    session_type = Column(String(50), default="practice")  # practice, project, learning, debugging
    
    # 技术栈信息
    primary_language = Column(String(50))  # 主要编程语言
    frameworks = Column(JSON)  # 使用的框架
    tools = Column(JSON)  # 使用的工具
    libraries = Column(JSON)  # 使用的库
    
    # 项目信息
    project_name = Column(String(100))  # 项目名称
    project_type = Column(String(50))  # web, mobile, desktop, cli, library, etc.
    repository_url = Column(String(500))  # 代码仓库URL
    
    # 会话统计
    duration_minutes = Column(Integer, default=0)  # 会话时长（分钟）
    lines_of_code = Column(Integer, default=0)  # 代码行数
    files_modified = Column(Integer, default=0)  # 修改的文件数
    commits_count = Column(Integer, default=0)  # 提交次数
    
    # 学习成果
    concepts_learned = Column(JSON)  # 学到的概念
    skills_practiced = Column(JSON)  # 练习的技能
    challenges_faced = Column(JSON)  # 遇到的挑战
    solutions_found = Column(JSON)  # 找到的解决方案
    
    # 质量指标
    code_quality_score = Column(Float, default=0.0)  # 代码质量评分
    test_coverage = Column(Float, default=0.0)  # 测试覆盖率
    performance_score = Column(Float, default=0.0)  # 性能评分
    
    # 技术债务分析
    tech_debt_added = Column(Float, default=0.0)  # 新增技术债务
    tech_debt_resolved = Column(Float, default=0.0)  # 解决的技术债务
    refactoring_time = Column(Integer, default=0)  # 重构时间（分钟）
    
    # 学习效果评估
    difficulty_rating = Column(Integer, default=3)  # 难度评级 1-5
    satisfaction_rating = Column(Integer, default=3)  # 满意度评级 1-5
    learning_effectiveness = Column(Float, default=0.0)  # 学习效果评分
    
    # 会话状态
    status = Column(String(20), default="active")  # active, paused, completed, abandoned
    is_public = Column(Boolean, default=False)  # 是否公开
    
    # 时间戳
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="coding_sessions")
    code_records = relationship("CodeRecord", back_populates="coding_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CodingSession(id={self.id}, user_id={self.user_id}, title='{self.title}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "session_type": self.session_type,
            "primary_language": self.primary_language,
            "duration_minutes": self.duration_minutes,
            "lines_of_code": self.lines_of_code,
            "code_quality_score": self.code_quality_score,
            "tech_debt_added": self.tech_debt_added,
            "tech_debt_resolved": self.tech_debt_resolved,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def calculate_net_tech_debt(self):
        """计算净技术债务变化"""
        return self.tech_debt_added - self.tech_debt_resolved
    
    def get_learning_summary(self):
        """获取学习总结"""
        return {
            "concepts_learned": self.concepts_learned or [],
            "skills_practiced": self.skills_practiced or [],
            "challenges_faced": self.challenges_faced or [],
            "solutions_found": self.solutions_found or [],
            "difficulty_rating": self.difficulty_rating,
            "satisfaction_rating": self.satisfaction_rating,
            "learning_effectiveness": self.learning_effectiveness
        }