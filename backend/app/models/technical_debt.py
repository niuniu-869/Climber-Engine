#!/usr/bin/env python3
"""
技术债务数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class TechnicalDebt(Base):
    """技术债务模型"""
    
    __tablename__ = "technical_debts"
    
    id = Column(Integer, primary_key=True, index=True)
    code_record_id = Column(Integer, ForeignKey("code_records.id"), nullable=False)
    
    # 债务基本信息
    title = Column(String(200), nullable=False)  # 债务标题
    description = Column(Text)  # 债务描述
    debt_type = Column(String(50), nullable=False)  # code_smell, design_debt, documentation_debt, test_debt, performance_debt
    category = Column(String(50))  # 债务分类
    
    # 位置信息
    file_path = Column(String(500))  # 文件路径
    line_start = Column(Integer)  # 起始行号
    line_end = Column(Integer)  # 结束行号
    function_name = Column(String(200))  # 函数名
    class_name = Column(String(200))  # 类名
    
    # 严重程度
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    priority = Column(Integer, default=3)  # 优先级 1-5
    impact_score = Column(Float, default=0.0)  # 影响分数 0-10
    effort_estimate = Column(Float, default=0.0)  # 修复工作量估计（小时）
    
    # 债务详情
    code_snippet = Column(Text)  # 问题代码片段
    suggested_fix = Column(Text)  # 建议修复方案
    alternative_solutions = Column(JSON)  # 替代解决方案
    
    # 影响分析
    maintainability_impact = Column(Float, default=0.0)  # 可维护性影响
    performance_impact = Column(Float, default=0.0)  # 性能影响
    security_impact = Column(Float, default=0.0)  # 安全性影响
    readability_impact = Column(Float, default=0.0)  # 可读性影响
    testability_impact = Column(Float, default=0.0)  # 可测试性影响
    
    # 检测信息
    detection_method = Column(String(50))  # manual, static_analysis, ai_analysis, code_review
    detection_tool = Column(String(100))  # 检测工具
    detection_confidence = Column(Float, default=0.0)  # 检测置信度
    
    # 状态管理
    status = Column(String(20), default="open")  # open, in_progress, resolved, ignored, wont_fix
    resolution_notes = Column(Text)  # 解决说明
    resolution_commit = Column(String(100))  # 解决提交ID
    
    # 历史追踪
    first_detected = Column(DateTime, default=datetime.utcnow)  # 首次检测时间
    last_seen = Column(DateTime, default=datetime.utcnow)  # 最后发现时间
    resolved_at = Column(DateTime)  # 解决时间
    age_days = Column(Integer, default=0)  # 债务年龄（天）
    
    # 关联信息
    related_debts = Column(JSON)  # 相关债务ID列表
    blocking_debts = Column(JSON)  # 阻塞的债务ID列表
    caused_by_debt_id = Column(Integer)  # 由哪个债务引起
    
    # 业务影响
    business_impact = Column(Text)  # 业务影响描述
    user_impact = Column(Text)  # 用户影响描述
    technical_risk = Column(Text)  # 技术风险描述
    
    # 修复计划
    planned_fix_version = Column(String(50))  # 计划修复版本
    assigned_to = Column(String(100))  # 分配给谁
    estimated_fix_date = Column(DateTime)  # 预计修复日期
    
    # 统计信息
    occurrence_count = Column(Integer, default=1)  # 出现次数
    false_positive_reports = Column(Integer, default=0)  # 误报次数
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    code_record = relationship("CodeRecord", back_populates="technical_debts")
    
    def __repr__(self):
        return f"<TechnicalDebt(id={self.id}, title='{self.title}', severity='{self.severity}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "code_record_id": self.code_record_id,
            "title": self.title,
            "description": self.description,
            "debt_type": self.debt_type,
            "category": self.category,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "severity": self.severity,
            "priority": self.priority,
            "impact_score": self.impact_score,
            "effort_estimate": self.effort_estimate,
            "status": self.status,
            "age_days": self.age_days,
            "occurrence_count": self.occurrence_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "first_detected": self.first_detected.isoformat() if self.first_detected else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    def calculate_debt_score(self):
        """计算技术债务综合评分"""
        # 基础分数基于严重程度
        severity_scores = {
            "critical": 10.0,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5
        }
        base_score = severity_scores.get(self.severity, 5.0)
        
        # 影响因子
        impact_factor = (
            self.maintainability_impact * 0.3 +
            self.performance_impact * 0.2 +
            self.security_impact * 0.25 +
            self.readability_impact * 0.15 +
            self.testability_impact * 0.1
        ) / 10.0
        
        # 年龄因子（债务越老，影响越大）
        age_factor = min(1.0 + (self.age_days / 365.0) * 0.5, 2.0)
        
        # 出现频率因子
        frequency_factor = min(1.0 + (self.occurrence_count - 1) * 0.1, 1.5)
        
        return base_score * (1 + impact_factor) * age_factor * frequency_factor
    
    def get_fix_urgency(self):
        """获取修复紧急程度"""
        debt_score = self.calculate_debt_score()
        
        if debt_score >= 15.0 or self.severity == "critical":
            return "immediate"
        elif debt_score >= 10.0 or self.severity == "high":
            return "urgent"
        elif debt_score >= 6.0 or self.severity == "medium":
            return "normal"
        else:
            return "low"
    
    def update_age(self):
        """更新债务年龄"""
        if self.first_detected:
            self.age_days = (datetime.utcnow() - self.first_detected).days
    
    def mark_resolved(self, resolution_notes=None, commit_id=None):
        """标记为已解决"""
        self.status = "resolved"
        self.resolved_at = datetime.utcnow()
        if resolution_notes:
            self.resolution_notes = resolution_notes
        if commit_id:
            self.resolution_commit = commit_id
    
    def increment_occurrence(self):
        """增加出现次数"""
        self.occurrence_count += 1
        self.last_seen = datetime.utcnow()
    
    def get_impact_summary(self):
        """获取影响摘要"""
        impacts = {
            "maintainability": self.maintainability_impact,
            "performance": self.performance_impact,
            "security": self.security_impact,
            "readability": self.readability_impact,
            "testability": self.testability_impact
        }
        
        # 找出主要影响领域
        max_impact = max(impacts.values()) if impacts.values() else 0
        primary_impacts = [k for k, v in impacts.items() if v == max_impact and v > 0]
        
        return {
            "total_score": sum(impacts.values()),
            "primary_impacts": primary_impacts,
            "impact_details": impacts
        }
    
    def get_fix_recommendation(self):
        """获取修复建议"""
        urgency = self.get_fix_urgency()
        debt_score = self.calculate_debt_score()
        
        recommendation = {
            "urgency": urgency,
            "debt_score": debt_score,
            "suggested_fix": self.suggested_fix,
            "effort_estimate": self.effort_estimate,
            "priority_reason": ""
        }
        
        if self.severity == "critical":
            recommendation["priority_reason"] = "Critical severity requires immediate attention"
        elif self.security_impact > 7.0:
            recommendation["priority_reason"] = "High security impact"
        elif self.age_days > 180:
            recommendation["priority_reason"] = "Long-standing debt affecting maintainability"
        elif self.occurrence_count > 5:
            recommendation["priority_reason"] = "Frequently occurring issue"
        else:
            recommendation["priority_reason"] = "Standard priority based on impact assessment"
        
        return recommendation