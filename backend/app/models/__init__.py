#!/usr/bin/env python3
"""
数据模型模块
"""

from .user import User
from .coding_session import CodingSession
from .code_record import CodeRecord
from .skill_assessment import SkillAssessment
from .learning_task import LearningTask
from .technical_debt import TechnicalDebt

# 新增的数据库模型
from .mcp_session import MCPSession, MCPCodeSnippet
from .learning_progress import TechStackAsset, TechStackDebt, LearningProgressSummary
from .learning_content import LearningArticle, LearningQuestion, QuestionAttempt
from .tech_stack_config import TechStackCategory, TechStackStandard, TechStackMapping

__all__ = [
    "User",
    "CodingSession",
    "CodeRecord",
    "SkillAssessment",
    "LearningTask",
    "TechnicalDebt",
    # MCP会话管理
    "MCPSession",
    "MCPCodeSnippet",
    # 学习进度管理
    "TechStackAsset",
    "TechStackDebt",
    "LearningProgressSummary",
    # 学习内容管理
    "LearningArticle",
    "LearningQuestion",
    "QuestionAttempt",
    # 技术栈配置
    "TechStackCategory",
    "TechStackStandard",
    "TechStackMapping",
]