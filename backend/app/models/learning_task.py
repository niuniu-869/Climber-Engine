#!/usr/bin/env python3
"""
学习任务数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class LearningTask(Base):
    """学习任务模型"""
    
    __tablename__ = "learning_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 任务基本信息
    title = Column(String(200), nullable=False)  # 任务标题
    description = Column(Text)  # 任务描述
    task_type = Column(String(50), nullable=False)  # concept, practice, project, challenge, review
    category = Column(String(50))  # 任务分类
    
    # 技能相关
    target_skill = Column(String(100), nullable=False)  # 目标技能
    skill_level = Column(String(20), nullable=False)  # 技能级别要求
    prerequisites = Column(JSON)  # 前置技能要求
    learning_objectives = Column(JSON)  # 学习目标
    
    # 任务内容
    content = Column(Text)  # 任务内容
    instructions = Column(Text)  # 任务说明
    resources = Column(JSON)  # 学习资源
    examples = Column(JSON)  # 示例代码/项目
    
    # 难度和时间
    difficulty_level = Column(Integer, default=3)  # 难度级别 1-5
    estimated_duration = Column(Integer)  # 预计完成时间（分钟）
    actual_duration = Column(Integer)  # 实际完成时间（分钟）
    
    # 任务状态
    status = Column(String(20), default="pending")  # pending, in_progress, completed, skipped, failed
    progress_percentage = Column(Float, default=0.0)  # 完成进度百分比
    completion_quality = Column(Float, default=0.0)  # 完成质量评分
    
    # 评估标准
    success_criteria = Column(JSON)  # 成功标准
    evaluation_metrics = Column(JSON)  # 评估指标
    auto_evaluation = Column(Boolean, default=True)  # 是否自动评估
    
    # 个性化设置
    personalization_factors = Column(JSON)  # 个性化因素
    adaptive_difficulty = Column(Boolean, default=True)  # 是否自适应难度
    learning_style_match = Column(Float, default=0.0)  # 学习风格匹配度
    
    # 反馈和结果
    user_feedback = Column(JSON)  # 用户反馈
    ai_feedback = Column(JSON)  # AI反馈
    completion_notes = Column(Text)  # 完成笔记
    lessons_learned = Column(JSON)  # 学到的经验
    
    # 关联信息
    related_tasks = Column(JSON)  # 相关任务ID列表
    follow_up_tasks = Column(JSON)  # 后续任务ID列表
    source_assessment_id = Column(Integer)  # 来源评估ID
    
    # 调度信息
    priority = Column(Integer, default=3)  # 优先级 1-5
    scheduled_date = Column(DateTime)  # 计划开始日期
    due_date = Column(DateTime)  # 截止日期
    reminder_sent = Column(Boolean, default=False)  # 是否已发送提醒
    
    # 统计信息
    attempt_count = Column(Integer, default=0)  # 尝试次数
    hint_used_count = Column(Integer, default=0)  # 使用提示次数
    help_requested_count = Column(Integer, default=0)  # 请求帮助次数
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)  # 开始时间
    completed_at = Column(DateTime)  # 完成时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="learning_tasks")
    
    def __repr__(self):
        return f"<LearningTask(id={self.id}, user_id={self.user_id}, title='{self.title}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "category": self.category,
            "target_skill": self.target_skill,
            "skill_level": self.skill_level,
            "difficulty_level": self.difficulty_level,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "completion_quality": self.completion_quality,
            "priority": self.priority,
            "attempt_count": self.attempt_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def start_task(self):
        """开始任务"""
        self.status = "in_progress"
        self.started_at = datetime.utcnow()
        self.attempt_count += 1
    
    def complete_task(self, quality_score=None):
        """完成任务"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100.0
        
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 60
            self.actual_duration = int(duration)
        
        if quality_score is not None:
            self.completion_quality = quality_score
    
    def update_progress(self, percentage):
        """更新进度"""
        self.progress_percentage = max(0.0, min(100.0, percentage))
        if self.progress_percentage >= 100.0:
            self.complete_task()
    
    def get_time_efficiency(self):
        """获取时间效率"""
        if not self.estimated_duration or not self.actual_duration:
            return None
        return self.estimated_duration / self.actual_duration
    
    def get_learning_outcome(self):
        """获取学习成果"""
        return {
            "completion_quality": self.completion_quality,
            "time_efficiency": self.get_time_efficiency(),
            "attempt_count": self.attempt_count,
            "hint_used_count": self.hint_used_count,
            "lessons_learned": self.lessons_learned or [],
            "user_feedback": self.user_feedback or {},
            "ai_feedback": self.ai_feedback or {}
        }
    
    def is_overdue(self):
        """检查是否过期"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status not in ["completed", "skipped"]
    
    def get_difficulty_adjustment_suggestion(self):
        """获取难度调整建议"""
        if self.attempt_count <= 1:
            return None
        
        if self.completion_quality < 0.6 or self.attempt_count > 3:
            return "decrease"  # 降低难度
        elif self.completion_quality > 0.9 and self.get_time_efficiency() and self.get_time_efficiency() > 1.5:
            return "increase"  # 增加难度
        
        return "maintain"  # 保持当前难度