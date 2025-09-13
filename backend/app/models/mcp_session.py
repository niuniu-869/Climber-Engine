#!/usr/bin/env python3
"""
MCP会话管理数据模型
专门用于记录Recorder MCP调用的会话信息
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class MCPSession(Base):
    """MCP会话模型 - 记录每次Recorder MCP调用的会话信息"""
    
    __tablename__ = "mcp_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 会话基本信息
    session_name = Column(String(200))  # 会话名称
    session_description = Column(Text)  # 会话描述
    project_name = Column(String(100))  # 项目名称
    work_type = Column(String(50), nullable=False)  # development, debugging, refactoring, testing, documentation, analysis
    task_description = Column(Text, nullable=False)  # 任务描述
    
    # 技术栈信息
    technologies = Column(JSON, nullable=False)  # 使用的技术栈列表
    primary_language = Column(String(50))  # 主要编程语言
    frameworks = Column(JSON)  # 使用的框架
    libraries = Column(JSON)  # 使用的库
    tools = Column(JSON)  # 使用的工具
    
    # 难度和评估
    difficulty_level = Column(String(20), default="intermediate")  # beginner, intermediate, advanced, expert
    complexity_score = Column(Float, default=0.0)  # 复杂度评分 0-10
    estimated_duration = Column(Integer)  # 预计时长（分钟）
    actual_duration = Column(Integer)  # 实际时长（分钟）
    
    # 工作内容和成果
    work_summary = Column(Text)  # 工作总结
    achievements = Column(JSON)  # 完成的成就
    challenges_faced = Column(JSON)  # 遇到的挑战
    solutions_applied = Column(JSON)  # 应用的解决方案
    lessons_learned = Column(JSON)  # 学到的经验
    
    # 代码相关信息
    files_modified = Column(Integer, default=0)  # 修改的文件数
    lines_added = Column(Integer, default=0)  # 新增代码行数
    lines_deleted = Column(Integer, default=0)  # 删除代码行数
    commits_count = Column(Integer, default=0)  # 提交次数
    
    # 质量指标
    code_quality_score = Column(Float, default=0.0)  # 代码质量评分
    test_coverage = Column(Float, default=0.0)  # 测试覆盖率
    documentation_quality = Column(Float, default=0.0)  # 文档质量
    
    # MCP特定信息
    mcp_server_version = Column(String(50))  # MCP服务器版本
    mcp_client_info = Column(JSON)  # MCP客户端信息
    mcp_call_count = Column(Integer, default=0)  # MCP调用次数
    
    # 备注和扩展信息
    notes = Column(Text)  # 额外备注
    tags = Column(JSON)  # 标签
    extra_metadata = Column(JSON)  # 扩展元数据
    
    # 会话状态
    status = Column(String(20), default="active")  # active, completed, paused, cancelled
    is_successful = Column(Boolean, default=True)  # 是否成功完成
    
    # 时间戳
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="mcp_sessions")
    code_snippets = relationship("MCPCodeSnippet", back_populates="mcp_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MCPSession(id={self.id}, user_id={self.user_id}, project='{self.project_name}', work_type='{self.work_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_name": self.session_name,
            "project_name": self.project_name,
            "work_type": self.work_type,
            "task_description": self.task_description,
            "technologies": self.technologies,
            "primary_language": self.primary_language,
            "difficulty_level": self.difficulty_level,
            "complexity_score": self.complexity_score,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "files_modified": self.files_modified,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
            "code_quality_score": self.code_quality_score,
            "status": self.status,
            "is_successful": self.is_successful,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def complete_session(self, success=True):
        """完成会话"""
        self.status = "completed"
        self.is_successful = success
        self.ended_at = datetime.utcnow()
        
        if self.started_at:
            duration = (self.ended_at - self.started_at).total_seconds() / 60
            self.actual_duration = int(duration)
    
    def get_technology_summary(self):
        """获取技术栈总结"""
        return {
            "technologies": self.technologies or [],
            "primary_language": self.primary_language,
            "frameworks": self.frameworks or [],
            "libraries": self.libraries or [],
            "tools": self.tools or []
        }
    
    def get_work_summary(self):
        """获取工作总结"""
        return {
            "work_type": self.work_type,
            "task_description": self.task_description,
            "work_summary": self.work_summary,
            "achievements": self.achievements or [],
            "challenges_faced": self.challenges_faced or [],
            "solutions_applied": self.solutions_applied or [],
            "lessons_learned": self.lessons_learned or []
        }
    
    def get_code_metrics(self):
        """获取代码指标"""
        return {
            "files_modified": self.files_modified,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
            "commits_count": self.commits_count,
            "code_quality_score": self.code_quality_score,
            "test_coverage": self.test_coverage,
            "documentation_quality": self.documentation_quality
        }


class MCPCodeSnippet(Base):
    """MCP代码片段模型 - 记录与技术栈相关的代码片段"""
    
    __tablename__ = "mcp_code_snippets"
    
    id = Column(Integer, primary_key=True, index=True)
    mcp_session_id = Column(Integer, ForeignKey("mcp_sessions.id"), nullable=False)
    
    # 代码片段基本信息
    title = Column(String(200))  # 代码片段标题
    description = Column(Text)  # 代码片段描述
    file_path = Column(String(500))  # 文件路径
    file_name = Column(String(100))  # 文件名
    
    # 代码内容
    code_content = Column(Text, nullable=False)  # 代码内容
    language = Column(String(50), nullable=False)  # 编程语言
    framework = Column(String(100))  # 相关框架
    
    # 代码分类
    snippet_type = Column(String(50))  # function, class, module, config, test, documentation
    purpose = Column(String(100))  # 代码用途
    complexity_level = Column(String(20), default="medium")  # simple, medium, complex
    
    # 技术栈关联
    related_technologies = Column(JSON)  # 相关技术栈
    concepts_demonstrated = Column(JSON)  # 展示的概念
    patterns_used = Column(JSON)  # 使用的设计模式
    
    # 质量指标
    quality_score = Column(Float, default=0.0)  # 质量评分
    readability_score = Column(Float, default=0.0)  # 可读性评分
    maintainability_score = Column(Float, default=0.0)  # 可维护性评分
    
    # 学习价值
    learning_value = Column(Float, default=0.0)  # 学习价值评分
    difficulty_rating = Column(Integer, default=3)  # 难度评级 1-5
    educational_notes = Column(Text)  # 教育说明
    
    # 使用统计
    reference_count = Column(Integer, default=0)  # 引用次数
    last_referenced = Column(DateTime)  # 最后引用时间
    
    # 标签和分类
    tags = Column(JSON)  # 标签
    categories = Column(JSON)  # 分类
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    mcp_session = relationship("MCPSession", back_populates="code_snippets")
    
    def __repr__(self):
        return f"<MCPCodeSnippet(id={self.id}, session_id={self.mcp_session_id}, title='{self.title}', language='{self.language}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "mcp_session_id": self.mcp_session_id,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "language": self.language,
            "framework": self.framework,
            "snippet_type": self.snippet_type,
            "purpose": self.purpose,
            "complexity_level": self.complexity_level,
            "related_technologies": self.related_technologies,
            "quality_score": self.quality_score,
            "learning_value": self.learning_value,
            "difficulty_rating": self.difficulty_rating,
            "reference_count": self.reference_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def get_technology_context(self):
        """获取技术栈上下文"""
        return {
            "language": self.language,
            "framework": self.framework,
            "related_technologies": self.related_technologies or [],
            "concepts_demonstrated": self.concepts_demonstrated or [],
            "patterns_used": self.patterns_used or []
        }
    
    def get_learning_context(self):
        """获取学习上下文"""
        return {
            "learning_value": self.learning_value,
            "difficulty_rating": self.difficulty_rating,
            "educational_notes": self.educational_notes,
            "complexity_level": self.complexity_level,
            "purpose": self.purpose
        }