#!/usr/bin/env python3
"""
技能评估数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class SkillAssessment(Base):
    """技能评估模型"""
    
    __tablename__ = "skill_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 评估基本信息
    assessment_type = Column(String(50), nullable=False)  # initial, periodic, project_based, self_assessment
    skill_category = Column(String(50), nullable=False)  # programming, framework, tool, concept, soft_skill
    skill_name = Column(String(100), nullable=False)  # 具体技能名称
    
    # 评估结果
    current_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    previous_level = Column(String(20))  # 上次评估的级别
    score = Column(Float, nullable=False)  # 评估分数 0-100
    confidence_level = Column(Float, default=0.0)  # 置信度 0-1
    
    # 详细评估
    strengths = Column(JSON)  # 优势领域
    weaknesses = Column(JSON)  # 薄弱环节
    knowledge_gaps = Column(JSON)  # 知识缺口
    improvement_areas = Column(JSON)  # 改进领域
    
    # 评估维度
    theoretical_knowledge = Column(Float, default=0.0)  # 理论知识 0-100
    practical_skills = Column(Float, default=0.0)  # 实践技能 0-100
    problem_solving = Column(Float, default=0.0)  # 问题解决能力 0-100
    code_quality = Column(Float, default=0.0)  # 代码质量 0-100
    best_practices = Column(Float, default=0.0)  # 最佳实践 0-100
    
    # 学习建议
    recommended_resources = Column(JSON)  # 推荐学习资源
    suggested_projects = Column(JSON)  # 建议项目
    learning_path = Column(JSON)  # 学习路径
    estimated_time_to_next_level = Column(Integer)  # 预计达到下一级别的时间（小时）
    
    # 评估方法
    assessment_method = Column(String(50))  # code_analysis, quiz, project_review, peer_review, self_report
    data_sources = Column(JSON)  # 数据来源
    assessment_criteria = Column(JSON)  # 评估标准
    
    # 历史对比
    progress_since_last = Column(Float, default=0.0)  # 自上次评估以来的进步
    learning_velocity = Column(Float, default=0.0)  # 学习速度
    consistency_score = Column(Float, default=0.0)  # 学习一致性评分
    
    # AI分析
    ai_insights = Column(JSON)  # AI洞察
    ai_recommendations = Column(JSON)  # AI推荐
    personalized_tips = Column(JSON)  # 个性化建议
    
    # 验证信息
    is_verified = Column(Boolean, default=False)  # 是否已验证
    verification_method = Column(String(50))  # 验证方法
    verifier_id = Column(String(100))  # 验证者ID
    
    # 时间戳
    assessed_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)  # 评估有效期
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="skill_assessments")
    
    def __repr__(self):
        return f"<SkillAssessment(id={self.id}, user_id={self.user_id}, skill='{self.skill_name}', level='{self.current_level}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "assessment_type": self.assessment_type,
            "skill_category": self.skill_category,
            "skill_name": self.skill_name,
            "current_level": self.current_level,
            "previous_level": self.previous_level,
            "score": self.score,
            "confidence_level": self.confidence_level,
            "theoretical_knowledge": self.theoretical_knowledge,
            "practical_skills": self.practical_skills,
            "problem_solving": self.problem_solving,
            "code_quality": self.code_quality,
            "best_practices": self.best_practices,
            "progress_since_last": self.progress_since_last,
            "learning_velocity": self.learning_velocity,
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None
        }
    
    def get_overall_score(self):
        """计算综合评分"""
        dimensions = [
            self.theoretical_knowledge,
            self.practical_skills,
            self.problem_solving,
            self.code_quality,
            self.best_practices
        ]
        valid_scores = [score for score in dimensions if score > 0]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
    
    def get_skill_radar_data(self):
        """获取技能雷达图数据"""
        return {
            "theoretical_knowledge": self.theoretical_knowledge,
            "practical_skills": self.practical_skills,
            "problem_solving": self.problem_solving,
            "code_quality": self.code_quality,
            "best_practices": self.best_practices
        }
    
    def get_improvement_plan(self):
        """获取改进计划"""
        return {
            "weaknesses": self.weaknesses or [],
            "knowledge_gaps": self.knowledge_gaps or [],
            "improvement_areas": self.improvement_areas or [],
            "recommended_resources": self.recommended_resources or [],
            "suggested_projects": self.suggested_projects or [],
            "learning_path": self.learning_path or [],
            "estimated_time_to_next_level": self.estimated_time_to_next_level,
            "ai_recommendations": self.ai_recommendations or [],
            "personalized_tips": self.personalized_tips or []
        }
    
    def is_assessment_valid(self):
        """检查评估是否仍然有效"""
        if not self.valid_until:
            return True
        return datetime.utcnow() < self.valid_until