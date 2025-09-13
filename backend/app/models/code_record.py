#!/usr/bin/env python3
"""
代码记录数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class CodeRecord(Base):
    """代码记录模型"""
    
    __tablename__ = "code_records"
    
    id = Column(Integer, primary_key=True, index=True)
    coding_session_id = Column(Integer, ForeignKey("coding_sessions.id"), nullable=False)
    
    # 代码基本信息
    file_path = Column(String(500), nullable=False)  # 文件路径
    file_name = Column(String(200), nullable=False)  # 文件名
    file_extension = Column(String(20))  # 文件扩展名
    language = Column(String(50))  # 编程语言
    
    # 代码内容
    code_before = Column(Text)  # 修改前的代码
    code_after = Column(Text)  # 修改后的代码
    diff_content = Column(Text)  # 差异内容
    
    # 变更信息
    change_type = Column(String(20), nullable=False)  # create, modify, delete, rename
    lines_added = Column(Integer, default=0)  # 新增行数
    lines_deleted = Column(Integer, default=0)  # 删除行数
    lines_modified = Column(Integer, default=0)  # 修改行数
    
    # 代码分析
    complexity_score = Column(Float, default=0.0)  # 复杂度评分
    maintainability_score = Column(Float, default=0.0)  # 可维护性评分
    readability_score = Column(Float, default=0.0)  # 可读性评分
    
    # 技术债务分析
    tech_debt_score = Column(Float, default=0.0)  # 技术债务评分
    code_smells = Column(JSON)  # 代码异味列表
    security_issues = Column(JSON)  # 安全问题列表
    performance_issues = Column(JSON)  # 性能问题列表
    
    # 功能分析
    functions_added = Column(JSON)  # 新增函数列表
    functions_modified = Column(JSON)  # 修改函数列表
    functions_deleted = Column(JSON)  # 删除函数列表
    classes_added = Column(JSON)  # 新增类列表
    classes_modified = Column(JSON)  # 修改类列表
    
    # 依赖分析
    imports_added = Column(JSON)  # 新增导入
    imports_removed = Column(JSON)  # 删除导入
    dependencies_added = Column(JSON)  # 新增依赖
    dependencies_removed = Column(JSON)  # 删除依赖
    
    # 测试相关
    test_coverage_before = Column(Float, default=0.0)  # 修改前测试覆盖率
    test_coverage_after = Column(Float, default=0.0)  # 修改后测试覆盖率
    tests_added = Column(Integer, default=0)  # 新增测试数量
    tests_modified = Column(Integer, default=0)  # 修改测试数量
    
    # 提交信息
    commit_hash = Column(String(40))  # Git提交哈希
    commit_message = Column(Text)  # 提交信息
    branch_name = Column(String(100))  # 分支名称
    
    # 学习标记
    learning_tags = Column(JSON)  # 学习标签
    difficulty_level = Column(Integer, default=3)  # 难度级别 1-5
    concepts_applied = Column(JSON)  # 应用的概念
    patterns_used = Column(JSON)  # 使用的设计模式
    
    # AI分析结果
    ai_summary = Column(Text)  # AI生成的代码总结
    ai_suggestions = Column(JSON)  # AI建议列表
    ai_learning_points = Column(JSON)  # AI识别的学习要点
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    coding_session = relationship("CodingSession", back_populates="code_records")
    technical_debts = relationship("TechnicalDebt", back_populates="code_record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CodeRecord(id={self.id}, file_path='{self.file_path}', change_type='{self.change_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "coding_session_id": self.coding_session_id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "language": self.language,
            "change_type": self.change_type,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
            "lines_modified": self.lines_modified,
            "complexity_score": self.complexity_score,
            "maintainability_score": self.maintainability_score,
            "tech_debt_score": self.tech_debt_score,
            "test_coverage_after": self.test_coverage_after,
            "difficulty_level": self.difficulty_level,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def get_net_lines_changed(self):
        """获取净代码行数变化"""
        return self.lines_added - self.lines_deleted
    
    def get_code_quality_summary(self):
        """获取代码质量总结"""
        return {
            "complexity_score": self.complexity_score,
            "maintainability_score": self.maintainability_score,
            "readability_score": self.readability_score,
            "tech_debt_score": self.tech_debt_score,
            "code_smells": self.code_smells or [],
            "security_issues": self.security_issues or [],
            "performance_issues": self.performance_issues or []
        }
    
    def get_learning_insights(self):
        """获取学习洞察"""
        return {
            "concepts_applied": self.concepts_applied or [],
            "patterns_used": self.patterns_used or [],
            "learning_tags": self.learning_tags or [],
            "difficulty_level": self.difficulty_level,
            "ai_learning_points": self.ai_learning_points or [],
            "ai_suggestions": self.ai_suggestions or []
        }