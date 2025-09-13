#!/usr/bin/env python3
"""
学习进度管理数据模型
分为技术栈资产（已掌握）和负债（未掌握）两部分
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class TechStackAsset(Base):
    """技术栈资产模型 - 用户已掌握的技术栈"""
    
    __tablename__ = "tech_stack_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 技术栈基本信息
    technology_name = Column(String(100), nullable=False, index=True)  # 技术名称
    category = Column(String(50), nullable=False)  # programming_language, framework, library, tool, database, etc.
    subcategory = Column(String(50))  # 子分类，如web_framework, mobile_framework
    
    # 掌握程度
    proficiency_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    proficiency_score = Column(Float, default=0.0)  # 熟练度评分 0-100
    confidence_level = Column(Float, default=0.0)  # 信心水平 0-1
    
    # 学习历程
    first_learned_date = Column(DateTime)  # 首次学习日期
    last_practiced_date = Column(DateTime)  # 最后练习日期
    total_practice_hours = Column(Float, default=0.0)  # 总练习时间（小时）
    project_count = Column(Integer, default=0)  # 使用该技术的项目数量
    
    # 技能维度评估
    theoretical_knowledge = Column(Float, default=0.0)  # 理论知识 0-100
    practical_skills = Column(Float, default=0.0)  # 实践技能 0-100
    problem_solving = Column(Float, default=0.0)  # 问题解决能力 0-100
    best_practices = Column(Float, default=0.0)  # 最佳实践掌握 0-100
    advanced_features = Column(Float, default=0.0)  # 高级特性掌握 0-100
    
    # 应用场景
    use_cases = Column(JSON)  # 应用场景列表
    project_types = Column(JSON)  # 适用项目类型
    industry_applications = Column(JSON)  # 行业应用
    
    # 相关技术
    related_technologies = Column(JSON)  # 相关技术栈
    complementary_skills = Column(JSON)  # 互补技能
    prerequisite_skills = Column(JSON)  # 前置技能
    
    # 学习成果
    achievements = Column(JSON)  # 学习成就
    certifications = Column(JSON)  # 相关认证
    notable_projects = Column(JSON)  # 重要项目
    
    # 市场价值
    market_demand = Column(Float, default=0.0)  # 市场需求度 0-100
    salary_impact = Column(Float, default=0.0)  # 薪资影响 0-100
    career_relevance = Column(Float, default=0.0)  # 职业相关性 0-100
    
    # 维护状态
    is_active = Column(Boolean, default=True)  # 是否活跃使用
    decay_rate = Column(Float, default=0.0)  # 技能衰减率
    refresh_needed = Column(Boolean, default=False)  # 是否需要刷新
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_assessed_at = Column(DateTime)  # 最后评估时间
    
    # 关系
    user = relationship("User", back_populates="tech_stack_assets")
    
    def __repr__(self):
        return f"<TechStackAsset(id={self.id}, user_id={self.user_id}, tech='{self.technology_name}', level='{self.proficiency_level}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "technology_name": self.technology_name,
            "category": self.category,
            "subcategory": self.subcategory,
            "proficiency_level": self.proficiency_level,
            "proficiency_score": self.proficiency_score,
            "confidence_level": self.confidence_level,
            "total_practice_hours": self.total_practice_hours,
            "project_count": self.project_count,
            "theoretical_knowledge": self.theoretical_knowledge,
            "practical_skills": self.practical_skills,
            "problem_solving": self.problem_solving,
            "best_practices": self.best_practices,
            "advanced_features": self.advanced_features,
            "market_demand": self.market_demand,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_practiced_date": self.last_practiced_date.isoformat() if self.last_practiced_date else None
        }
    
    def get_overall_score(self):
        """计算综合评分"""
        dimensions = [
            self.theoretical_knowledge,
            self.practical_skills,
            self.problem_solving,
            self.best_practices,
            self.advanced_features
        ]
        valid_scores = [score for score in dimensions if score > 0]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
    
    def update_practice_record(self, hours_spent):
        """更新练习记录"""
        self.total_practice_hours += hours_spent
        self.last_practiced_date = datetime.utcnow()
        self.is_active = True


class TechStackDebt(Base):
    """技术栈负债模型 - 用户未掌握但需要学习的技术栈"""
    
    __tablename__ = "tech_stack_debts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 技术栈基本信息
    technology_name = Column(String(100), nullable=False, index=True)  # 技术名称
    category = Column(String(50), nullable=False)  # programming_language, framework, library, tool, database, etc.
    subcategory = Column(String(50))  # 子分类
    
    # 需求分析
    urgency_level = Column(String(20), default="medium")  # low, medium, high, critical
    importance_score = Column(Float, default=0.0)  # 重要性评分 0-100
    career_impact = Column(Float, default=0.0)  # 职业影响 0-100
    project_relevance = Column(Float, default=0.0)  # 项目相关性 0-100
    
    # 学习计划
    target_proficiency_level = Column(String(20), default="intermediate")  # 目标熟练度
    estimated_learning_hours = Column(Float, default=0.0)  # 预计学习时间（小时）
    learning_priority = Column(Integer, default=3)  # 学习优先级 1-5
    planned_start_date = Column(DateTime)  # 计划开始日期
    target_completion_date = Column(DateTime)  # 目标完成日期
    
    # 学习路径
    prerequisites = Column(JSON)  # 前置技能要求
    learning_path = Column(JSON)  # 学习路径
    recommended_resources = Column(JSON)  # 推荐学习资源
    practice_projects = Column(JSON)  # 练习项目建议
    
    # 障碍分析
    learning_barriers = Column(JSON)  # 学习障碍
    difficulty_factors = Column(JSON)  # 难度因素
    risk_assessment = Column(JSON)  # 风险评估
    mitigation_strategies = Column(JSON)  # 缓解策略
    
    # 动机和目标
    learning_motivation = Column(Text)  # 学习动机
    specific_goals = Column(JSON)  # 具体目标
    success_metrics = Column(JSON)  # 成功指标
    
    # 市场和职业因素
    market_demand = Column(Float, default=0.0)  # 市场需求度 0-100
    salary_potential = Column(Float, default=0.0)  # 薪资潜力 0-100
    job_opportunities = Column(Float, default=0.0)  # 就业机会 0-100
    industry_trends = Column(JSON)  # 行业趋势
    
    # 学习进度跟踪
    learning_progress = Column(Float, default=0.0)  # 学习进度 0-100
    time_invested = Column(Float, default=0.0)  # 已投入时间（小时）
    milestones_achieved = Column(JSON)  # 已达成里程碑
    current_challenges = Column(JSON)  # 当前挑战
    
    # 状态管理
    status = Column(String(20), default="identified")  # identified, planned, learning, paused, completed, cancelled
    is_active = Column(Boolean, default=True)  # 是否活跃
    auto_generated = Column(Boolean, default=False)  # 是否自动生成
    
    # AI分析
    ai_recommendations = Column(JSON)  # AI推荐
    personalized_tips = Column(JSON)  # 个性化建议
    adaptive_adjustments = Column(JSON)  # 自适应调整
    
    # 时间戳
    identified_at = Column(DateTime, default=datetime.utcnow)  # 识别时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="tech_stack_debts")
    
    def __repr__(self):
        return f"<TechStackDebt(id={self.id}, user_id={self.user_id}, tech='{self.technology_name}', urgency='{self.urgency_level}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "technology_name": self.technology_name,
            "category": self.category,
            "subcategory": self.subcategory,
            "urgency_level": self.urgency_level,
            "importance_score": self.importance_score,
            "career_impact": self.career_impact,
            "project_relevance": self.project_relevance,
            "target_proficiency_level": self.target_proficiency_level,
            "estimated_learning_hours": self.estimated_learning_hours,
            "learning_priority": self.learning_priority,
            "learning_progress": self.learning_progress,
            "time_invested": self.time_invested,
            "status": self.status,
            "is_active": self.is_active,
            "market_demand": self.market_demand,
            "salary_potential": self.salary_potential,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "planned_start_date": self.planned_start_date.isoformat() if self.planned_start_date else None,
            "target_completion_date": self.target_completion_date.isoformat() if self.target_completion_date else None
        }
    
    def start_learning(self):
        """开始学习"""
        self.status = "learning"
        if not self.planned_start_date:
            self.planned_start_date = datetime.utcnow()
    
    def update_progress(self, progress_percentage, hours_spent=0):
        """更新学习进度"""
        self.learning_progress = max(0.0, min(100.0, progress_percentage))
        self.time_invested += hours_spent
        
        if self.learning_progress >= 100.0:
            self.status = "completed"
    
    def get_learning_efficiency(self):
        """获取学习效率"""
        if not self.estimated_learning_hours or not self.time_invested:
            return None
        return self.learning_progress / (self.time_invested / self.estimated_learning_hours * 100)
    
    def get_priority_score(self):
        """计算优先级评分"""
        weights = {
            "importance": 0.3,
            "career_impact": 0.25,
            "project_relevance": 0.2,
            "market_demand": 0.15,
            "urgency": 0.1
        }
        
        urgency_scores = {"low": 25, "medium": 50, "high": 75, "critical": 100}
        urgency_score = urgency_scores.get(self.urgency_level, 50)
        
        total_score = (
            self.importance_score * weights["importance"] +
            self.career_impact * weights["career_impact"] +
            self.project_relevance * weights["project_relevance"] +
            self.market_demand * weights["market_demand"] +
            urgency_score * weights["urgency"]
        )
        
        return total_score


class LearningProgressSummary(Base):
    """学习进度总结模型 - 定期生成的学习进度报告"""
    
    __tablename__ = "learning_progress_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 报告基本信息
    report_period = Column(String(20), nullable=False)  # weekly, monthly, quarterly, yearly
    period_start = Column(DateTime, nullable=False)  # 报告期开始
    period_end = Column(DateTime, nullable=False)  # 报告期结束
    
    # 资产统计
    total_assets = Column(Integer, default=0)  # 总资产数量
    new_assets_acquired = Column(Integer, default=0)  # 新获得资产
    assets_improved = Column(Integer, default=0)  # 改进的资产
    average_asset_score = Column(Float, default=0.0)  # 平均资产评分
    
    # 负债统计
    total_debts = Column(Integer, default=0)  # 总负债数量
    new_debts_identified = Column(Integer, default=0)  # 新识别负债
    debts_resolved = Column(Integer, default=0)  # 解决的负债
    average_debt_priority = Column(Float, default=0.0)  # 平均负债优先级
    
    # 学习活动
    total_learning_hours = Column(Float, default=0.0)  # 总学习时间
    practice_sessions = Column(Integer, default=0)  # 练习会话数
    projects_completed = Column(Integer, default=0)  # 完成项目数
    
    # 进度指标
    skill_growth_rate = Column(Float, default=0.0)  # 技能增长率
    learning_velocity = Column(Float, default=0.0)  # 学习速度
    consistency_score = Column(Float, default=0.0)  # 学习一致性
    
    # 详细分析
    top_performing_areas = Column(JSON)  # 表现最佳领域
    improvement_areas = Column(JSON)  # 需要改进的领域
    learning_patterns = Column(JSON)  # 学习模式分析
    recommendations = Column(JSON)  # 推荐建议
    
    # 目标达成
    goals_set = Column(Integer, default=0)  # 设定目标数
    goals_achieved = Column(Integer, default=0)  # 达成目标数
    goal_achievement_rate = Column(Float, default=0.0)  # 目标达成率
    
    # 时间戳
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="learning_progress_summaries")
    
    def __repr__(self):
        return f"<LearningProgressSummary(id={self.id}, user_id={self.user_id}, period='{self.report_period}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "report_period": self.report_period,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "total_assets": self.total_assets,
            "new_assets_acquired": self.new_assets_acquired,
            "total_debts": self.total_debts,
            "debts_resolved": self.debts_resolved,
            "total_learning_hours": self.total_learning_hours,
            "skill_growth_rate": self.skill_growth_rate,
            "learning_velocity": self.learning_velocity,
            "goal_achievement_rate": self.goal_achievement_rate,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }
    
    def get_overall_progress_score(self):
        """计算总体进度评分"""
        factors = [
            self.skill_growth_rate,
            self.learning_velocity,
            self.consistency_score,
            self.goal_achievement_rate * 100
        ]
        valid_factors = [f for f in factors if f > 0]
        return sum(valid_factors) / len(valid_factors) if valid_factors else 0.0