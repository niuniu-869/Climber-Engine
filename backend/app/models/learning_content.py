#!/usr/bin/env python3
"""
学习内容管理数据模型
存储AI为用户生成的题目和文章
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class LearningArticle(Base):
    """学习文章模型 - AI生成的学习文章"""
    
    __tablename__ = "learning_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 文章基本信息
    title = Column(String(300), nullable=False, index=True)  # 文章标题
    subtitle = Column(String(500))  # 副标题
    summary = Column(Text)  # 文章摘要
    content = Column(Text, nullable=False)  # 文章内容
    
    # 内容分类
    article_type = Column(String(50), nullable=False)  # tutorial, concept, best_practice, case_study, reference, troubleshooting
    category = Column(String(50), nullable=False)  # 技术分类
    subcategory = Column(String(50))  # 子分类
    
    # 技术栈相关
    target_technologies = Column(JSON, nullable=False)  # 目标技术栈
    related_concepts = Column(JSON)  # 相关概念
    prerequisites = Column(JSON)  # 前置知识
    
    # 难度和受众
    difficulty_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    target_audience = Column(String(100))  # 目标受众
    skill_level_required = Column(String(20))  # 所需技能水平
    
    # 学习目标
    learning_objectives = Column(JSON)  # 学习目标
    key_takeaways = Column(JSON)  # 关键要点
    practical_applications = Column(JSON)  # 实际应用
    
    # 内容结构
    sections = Column(JSON)  # 章节结构
    code_examples = Column(JSON)  # 代码示例
    diagrams = Column(JSON)  # 图表信息
    external_resources = Column(JSON)  # 外部资源链接
    
    # 个性化因素
    personalization_factors = Column(JSON)  # 个性化因素
    user_interests = Column(JSON)  # 用户兴趣匹配
    learning_style_match = Column(Float, default=0.0)  # 学习风格匹配度
    
    # 质量指标
    content_quality_score = Column(Float, default=0.0)  # 内容质量评分
    readability_score = Column(Float, default=0.0)  # 可读性评分
    educational_value = Column(Float, default=0.0)  # 教育价值
    accuracy_score = Column(Float, default=0.0)  # 准确性评分
    
    # 用户交互
    view_count = Column(Integer, default=0)  # 查看次数
    completion_rate = Column(Float, default=0.0)  # 完成率
    user_rating = Column(Float, default=0.0)  # 用户评分
    bookmark_count = Column(Integer, default=0)  # 收藏次数
    
    # 学习效果
    estimated_reading_time = Column(Integer, default=0)  # 预计阅读时间（分钟）
    actual_reading_time = Column(Integer, default=0)  # 实际阅读时间（分钟）
    comprehension_score = Column(Float, default=0.0)  # 理解度评分
    retention_score = Column(Float, default=0.0)  # 记忆保持评分
    
    # AI生成信息
    ai_model_used = Column(String(100))  # 使用的AI模型
    generation_prompt = Column(Text)  # 生成提示
    generation_parameters = Column(JSON)  # 生成参数
    ai_confidence_score = Column(Float, default=0.0)  # AI置信度
    
    # 内容状态
    status = Column(String(20), default="draft")  # draft, published, archived, under_review
    is_featured = Column(Boolean, default=False)  # 是否精选
    is_public = Column(Boolean, default=False)  # 是否公开
    
    # 版本控制
    version = Column(String(20), default="1.0")  # 版本号
    revision_notes = Column(Text)  # 修订说明
    
    # 标签和分类
    tags = Column(JSON)  # 标签
    keywords = Column(JSON)  # 关键词
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)  # 发布时间
    last_viewed_at = Column(DateTime)  # 最后查看时间
    
    # 关系
    user = relationship("User", back_populates="learning_articles")
    questions = relationship("LearningQuestion", back_populates="related_article", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningArticle(id={self.id}, user_id={self.user_id}, title='{self.title[:50]}...', type='{self.article_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary,
            "article_type": self.article_type,
            "category": self.category,
            "subcategory": self.subcategory,
            "target_technologies": self.target_technologies,
            "difficulty_level": self.difficulty_level,
            "target_audience": self.target_audience,
            "learning_objectives": self.learning_objectives,
            "content_quality_score": self.content_quality_score,
            "educational_value": self.educational_value,
            "view_count": self.view_count,
            "user_rating": self.user_rating,
            "estimated_reading_time": self.estimated_reading_time,
            "status": self.status,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None
        }
    
    def publish(self):
        """发布文章"""
        self.status = "published"
        self.published_at = datetime.utcnow()
    
    def record_view(self, reading_time=None):
        """记录查看"""
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()
        if reading_time:
            self.actual_reading_time = reading_time
    
    def get_engagement_score(self):
        """计算参与度评分"""
        if self.view_count == 0:
            return 0.0
        
        factors = {
            "completion_rate": self.completion_rate * 0.4,
            "user_rating": (self.user_rating / 5.0) * 0.3,
            "bookmark_rate": (self.bookmark_count / max(self.view_count, 1)) * 0.2,
            "retention": self.retention_score * 0.1
        }
        
        return sum(factors.values())


class LearningQuestion(Base):
    """学习题目模型 - AI生成的学习题目"""
    
    __tablename__ = "learning_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    related_article_id = Column(Integer, ForeignKey("learning_articles.id"), nullable=True)  # 关联文章
    
    # 题目基本信息
    title = Column(String(300), nullable=False)  # 题目标题
    question_text = Column(Text, nullable=False)  # 题目内容
    question_type = Column(String(50), nullable=False)  # multiple_choice, coding, essay, true_false, fill_blank, practical
    
    # 技术栈相关
    target_technologies = Column(JSON, nullable=False)  # 目标技术栈
    concepts_tested = Column(JSON)  # 测试的概念
    skills_assessed = Column(JSON)  # 评估的技能
    
    # 难度设置
    difficulty_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    complexity_score = Column(Float, default=0.0)  # 复杂度评分 0-10
    estimated_time = Column(Integer, default=0)  # 预计完成时间（分钟）
    
    # 题目内容
    options = Column(JSON)  # 选择题选项
    correct_answer = Column(Text)  # 正确答案
    explanation = Column(Text)  # 答案解释
    hints = Column(JSON)  # 提示信息
    
    # 代码题特有
    starter_code = Column(Text)  # 起始代码
    test_cases = Column(JSON)  # 测试用例
    expected_output = Column(Text)  # 期望输出
    solution_code = Column(Text)  # 解决方案代码
    
    # 评分标准
    scoring_criteria = Column(JSON)  # 评分标准
    max_score = Column(Float, default=100.0)  # 最高分
    passing_score = Column(Float, default=60.0)  # 及格分
    
    # 学习目标
    learning_objectives = Column(JSON)  # 学习目标
    knowledge_points = Column(JSON)  # 知识点
    skill_requirements = Column(JSON)  # 技能要求
    
    # 个性化因素
    personalization_factors = Column(JSON)  # 个性化因素
    adaptive_difficulty = Column(Boolean, default=True)  # 自适应难度
    user_preference_match = Column(Float, default=0.0)  # 用户偏好匹配度
    
    # 质量指标
    question_quality_score = Column(Float, default=0.0)  # 题目质量评分
    clarity_score = Column(Float, default=0.0)  # 清晰度评分
    educational_value = Column(Float, default=0.0)  # 教育价值
    discrimination_index = Column(Float, default=0.0)  # 区分度
    
    # 使用统计
    attempt_count = Column(Integer, default=0)  # 尝试次数
    correct_count = Column(Integer, default=0)  # 正确次数
    average_score = Column(Float, default=0.0)  # 平均得分
    average_time = Column(Float, default=0.0)  # 平均完成时间
    
    # AI生成信息
    ai_model_used = Column(String(100))  # 使用的AI模型
    generation_prompt = Column(Text)  # 生成提示
    generation_parameters = Column(JSON)  # 生成参数
    ai_confidence_score = Column(Float, default=0.0)  # AI置信度
    
    # 题目状态
    status = Column(String(20), default="draft")  # draft, active, archived, under_review
    is_featured = Column(Boolean, default=False)  # 是否精选
    is_public = Column(Boolean, default=False)  # 是否公开
    
    # 标签和分类
    tags = Column(JSON)  # 标签
    categories = Column(JSON)  # 分类
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_attempted_at = Column(DateTime)  # 最后尝试时间
    
    # 关系
    user = relationship("User", back_populates="learning_questions")
    related_article = relationship("LearningArticle", back_populates="questions")
    attempts = relationship("QuestionAttempt", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningQuestion(id={self.id}, user_id={self.user_id}, title='{self.title[:50]}...', type='{self.question_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "related_article_id": self.related_article_id,
            "title": self.title,
            "question_type": self.question_type,
            "target_technologies": self.target_technologies,
            "difficulty_level": self.difficulty_level,
            "complexity_score": self.complexity_score,
            "estimated_time": self.estimated_time,
            "max_score": self.max_score,
            "passing_score": self.passing_score,
            "attempt_count": self.attempt_count,
            "correct_count": self.correct_count,
            "average_score": self.average_score,
            "question_quality_score": self.question_quality_score,
            "status": self.status,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_attempted_at": self.last_attempted_at.isoformat() if self.last_attempted_at else None
        }
    
    def activate(self):
        """激活题目"""
        self.status = "active"
    
    def record_attempt(self, score, time_spent, is_correct):
        """记录答题尝试"""
        self.attempt_count += 1
        if is_correct:
            self.correct_count += 1
        
        # 更新平均分和平均时间
        self.average_score = ((self.average_score * (self.attempt_count - 1)) + score) / self.attempt_count
        self.average_time = ((self.average_time * (self.attempt_count - 1)) + time_spent) / self.attempt_count
        
        self.last_attempted_at = datetime.utcnow()
    
    def get_success_rate(self):
        """获取成功率"""
        if self.attempt_count == 0:
            return 0.0
        return self.correct_count / self.attempt_count
    
    def get_difficulty_adjustment_suggestion(self):
        """获取难度调整建议"""
        success_rate = self.get_success_rate()
        
        if success_rate > 0.9:
            return "increase"  # 太容易，增加难度
        elif success_rate < 0.3:
            return "decrease"  # 太难，降低难度
        else:
            return "maintain"  # 难度适中


class QuestionAttempt(Base):
    """题目尝试记录模型"""
    
    __tablename__ = "question_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("learning_questions.id"), nullable=False)
    
    # 答题信息
    user_answer = Column(Text)  # 用户答案
    submitted_code = Column(Text)  # 提交的代码（代码题）
    is_correct = Column(Boolean, default=False)  # 是否正确
    score = Column(Float, default=0.0)  # 得分
    
    # 时间信息
    time_spent = Column(Integer, default=0)  # 花费时间（秒）
    started_at = Column(DateTime, default=datetime.utcnow)  # 开始时间
    submitted_at = Column(DateTime)  # 提交时间
    
    # 答题过程
    hint_used_count = Column(Integer, default=0)  # 使用提示次数
    attempts_before_correct = Column(Integer, default=0)  # 正确前的尝试次数
    help_requested = Column(Boolean, default=False)  # 是否请求帮助
    
    # 反馈信息
    automated_feedback = Column(JSON)  # 自动反馈
    detailed_analysis = Column(JSON)  # 详细分析
    improvement_suggestions = Column(JSON)  # 改进建议
    
    # 学习效果
    confidence_level = Column(Float, default=0.0)  # 信心水平 0-1
    understanding_level = Column(Float, default=0.0)  # 理解水平 0-1
    satisfaction_rating = Column(Integer, default=3)  # 满意度评级 1-5
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User")
    question = relationship("LearningQuestion", back_populates="attempts")
    
    def __repr__(self):
        return f"<QuestionAttempt(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, score={self.score})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "question_id": self.question_id,
            "is_correct": self.is_correct,
            "score": self.score,
            "time_spent": self.time_spent,
            "hint_used_count": self.hint_used_count,
            "confidence_level": self.confidence_level,
            "understanding_level": self.understanding_level,
            "satisfaction_rating": self.satisfaction_rating,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def submit_answer(self, answer, code=None):
        """提交答案"""
        self.user_answer = answer
        if code:
            self.submitted_code = code
        self.submitted_at = datetime.utcnow()
        
        if self.started_at:
            duration = (self.submitted_at - self.started_at).total_seconds()
            self.time_spent = int(duration)
    
    def get_performance_metrics(self):
        """获取表现指标"""
        return {
            "score": self.score,
            "time_efficiency": self.get_time_efficiency(),
            "hint_dependency": self.hint_used_count,
            "confidence_level": self.confidence_level,
            "understanding_level": self.understanding_level
        }
    
    def get_time_efficiency(self):
        """获取时间效率（相对于预期时间）"""
        if not self.question or not self.question.estimated_time or not self.time_spent:
            return None
        
        expected_seconds = self.question.estimated_time * 60
        return expected_seconds / self.time_spent if self.time_spent > 0 else 0