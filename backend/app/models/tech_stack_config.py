#!/usr/bin/env python3
"""
技术栈配置数据模型
管理标准技术栈名称和分类
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class TechStackCategory(Base):
    """技术栈分类模型"""
    
    __tablename__ = "tech_stack_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 分类基本信息
    name = Column(String(100), nullable=False, unique=True, index=True)  # 分类名称
    display_name = Column(String(100), nullable=False)  # 显示名称
    description = Column(Text)  # 分类描述
    
    # 分类层级
    parent_id = Column(Integer)  # 父分类ID（自引用）
    level = Column(Integer, default=1)  # 分类层级
    sort_order = Column(Integer, default=0)  # 排序顺序
    
    # 分类属性
    icon = Column(String(100))  # 图标
    color = Column(String(20))  # 颜色代码
    is_active = Column(Boolean, default=True)  # 是否活跃
    
    # 统计信息
    technology_count = Column(Integer, default=0)  # 技术数量
    popularity_score = Column(Float, default=0.0)  # 流行度评分
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    technologies = relationship("TechStackStandard", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TechStackCategory(id={self.id}, name='{self.name}', level={self.level})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "parent_id": self.parent_id,
            "level": self.level,
            "sort_order": self.sort_order,
            "icon": self.icon,
            "color": self.color,
            "is_active": self.is_active,
            "technology_count": self.technology_count,
            "popularity_score": self.popularity_score,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TechStackStandard(Base):
    """标准技术栈模型 - 定义标准的技术栈名称和属性"""
    
    __tablename__ = "tech_stack_standards"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("tech_stack_categories.id"), nullable=False)  # 分类ID
    
    # 技术基本信息
    name = Column(String(100), nullable=False, unique=True, index=True)  # 标准名称
    display_name = Column(String(100), nullable=False)  # 显示名称
    description = Column(Text)  # 技术描述
    
    # 别名和变体
    aliases = Column(JSON)  # 别名列表
    common_variations = Column(JSON)  # 常见变体
    official_name = Column(String(100))  # 官方名称
    
    # 技术分类
    type = Column(String(50), nullable=False)  # programming_language, framework, library, tool, database, platform, etc.
    subtype = Column(String(50))  # 子类型
    domain = Column(String(50))  # 应用领域：web, mobile, desktop, data, ai, etc.
    
    # 技术属性
    version_info = Column(JSON)  # 版本信息
    release_year = Column(Integer)  # 发布年份
    current_status = Column(String(20), default="active")  # active, deprecated, legacy, experimental
    
    # 学习难度
    learning_difficulty = Column(String(20), default="medium")  # easy, medium, hard, expert
    complexity_score = Column(Float, default=5.0)  # 复杂度评分 1-10
    learning_curve = Column(String(20), default="moderate")  # gentle, moderate, steep
    
    # 前置要求
    prerequisites = Column(JSON)  # 前置技术要求
    recommended_background = Column(JSON)  # 推荐背景知识
    skill_dependencies = Column(JSON)  # 技能依赖
    
    # 相关技术
    related_technologies = Column(JSON)  # 相关技术
    complementary_skills = Column(JSON)  # 互补技能
    competing_alternatives = Column(JSON)  # 竞争替代品
    
    # 市场信息
    market_demand = Column(Float, default=0.0)  # 市场需求度 0-100
    job_market_score = Column(Float, default=0.0)  # 就业市场评分 0-100
    salary_impact = Column(Float, default=0.0)  # 薪资影响 0-100
    growth_trend = Column(String(20), default="stable")  # growing, stable, declining
    
    # 使用统计
    popularity_rank = Column(Integer)  # 流行度排名
    github_stars = Column(Integer, default=0)  # GitHub星数（如适用）
    stackoverflow_questions = Column(Integer, default=0)  # StackOverflow问题数
    job_postings_count = Column(Integer, default=0)  # 职位发布数
    
    # 学习资源
    official_docs_url = Column(String(500))  # 官方文档URL
    learning_resources = Column(JSON)  # 学习资源链接
    certification_info = Column(JSON)  # 认证信息
    community_resources = Column(JSON)  # 社区资源
    
    # 应用场景
    use_cases = Column(JSON)  # 使用场景
    industry_applications = Column(JSON)  # 行业应用
    project_types = Column(JSON)  # 适用项目类型
    company_usage = Column(JSON)  # 知名公司使用情况
    
    # 技术特征
    key_features = Column(JSON)  # 关键特性
    advantages = Column(JSON)  # 优势
    disadvantages = Column(JSON)  # 劣势
    performance_characteristics = Column(JSON)  # 性能特征
    
    # 生态系统
    ecosystem_maturity = Column(Float, default=0.0)  # 生态系统成熟度 0-100
    community_size = Column(String(20), default="medium")  # small, medium, large, huge
    vendor_support = Column(String(20), default="community")  # community, commercial, enterprise
    
    # 标签和元数据
    tags = Column(JSON)  # 标签
    keywords = Column(JSON)  # 关键词
    extra_metadata = Column(JSON)  # 扩展元数据
    
    # 状态管理
    is_active = Column(Boolean, default=True)  # 是否活跃
    is_featured = Column(Boolean, default=False)  # 是否精选
    is_trending = Column(Boolean, default=False)  # 是否趋势
    
    # 数据来源
    data_sources = Column(JSON)  # 数据来源
    last_market_update = Column(DateTime)  # 最后市场数据更新
    data_quality_score = Column(Float, default=0.0)  # 数据质量评分
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = relationship("TechStackCategory", back_populates="technologies")
    
    def __repr__(self):
        return f"<TechStackStandard(id={self.id}, name='{self.name}', type='{self.type}', status='{self.current_status}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "aliases": self.aliases,
            "type": self.type,
            "subtype": self.subtype,
            "domain": self.domain,
            "current_status": self.current_status,
            "learning_difficulty": self.learning_difficulty,
            "complexity_score": self.complexity_score,
            "market_demand": self.market_demand,
            "job_market_score": self.job_market_score,
            "salary_impact": self.salary_impact,
            "growth_trend": self.growth_trend,
            "popularity_rank": self.popularity_rank,
            "ecosystem_maturity": self.ecosystem_maturity,
            "community_size": self.community_size,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "is_trending": self.is_trending,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_learning_path_info(self):
        """获取学习路径信息"""
        return {
            "learning_difficulty": self.learning_difficulty,
            "complexity_score": self.complexity_score,
            "learning_curve": self.learning_curve,
            "prerequisites": self.prerequisites or [],
            "recommended_background": self.recommended_background or [],
            "related_technologies": self.related_technologies or [],
            "learning_resources": self.learning_resources or []
        }
    
    def get_market_info(self):
        """获取市场信息"""
        return {
            "market_demand": self.market_demand,
            "job_market_score": self.job_market_score,
            "salary_impact": self.salary_impact,
            "growth_trend": self.growth_trend,
            "popularity_rank": self.popularity_rank,
            "job_postings_count": self.job_postings_count
        }
    
    def get_technical_profile(self):
        """获取技术档案"""
        return {
            "type": self.type,
            "subtype": self.subtype,
            "domain": self.domain,
            "key_features": self.key_features or [],
            "advantages": self.advantages or [],
            "disadvantages": self.disadvantages or [],
            "use_cases": self.use_cases or [],
            "ecosystem_maturity": self.ecosystem_maturity,
            "community_size": self.community_size
        }
    
    def is_suitable_for_level(self, user_level):
        """判断是否适合用户水平"""
        level_mapping = {
            "beginner": ["easy"],
            "intermediate": ["easy", "medium"],
            "advanced": ["easy", "medium", "hard"],
            "expert": ["easy", "medium", "hard", "expert"]
        }
        
        suitable_difficulties = level_mapping.get(user_level, ["medium"])
        return self.learning_difficulty in suitable_difficulties
    
    def calculate_learning_priority(self, user_interests=None, career_goals=None):
        """计算学习优先级"""
        base_score = (
            self.market_demand * 0.3 +
            self.job_market_score * 0.25 +
            self.salary_impact * 0.2 +
            self.ecosystem_maturity * 0.15 +
            (100 - self.complexity_score * 10) * 0.1  # 复杂度越低，优先级越高
        )
        
        # 根据用户兴趣调整
        if user_interests and self.domain in user_interests:
            base_score *= 1.2
        
        # 根据职业目标调整
        if career_goals and any(goal in (self.use_cases or []) for goal in career_goals):
            base_score *= 1.15
        
        return min(100.0, base_score)


class TechStackMapping(Base):
    """技术栈映射模型 - 处理非标准名称到标准名称的映射"""
    
    __tablename__ = "tech_stack_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 映射信息
    input_name = Column(String(100), nullable=False, index=True)  # 输入名称（非标准）
    standard_name = Column(String(100), nullable=False, index=True)  # 标准名称
    confidence_score = Column(Float, default=1.0)  # 映射置信度 0-1
    
    # 映射类型
    mapping_type = Column(String(20), default="alias")  # alias, variation, abbreviation, misspelling
    source = Column(String(50), default="manual")  # manual, auto, ai, community
    
    # 使用统计
    usage_count = Column(Integer, default=0)  # 使用次数
    last_used = Column(DateTime)  # 最后使用时间
    
    # 验证信息
    is_verified = Column(Boolean, default=False)  # 是否已验证
    verified_by = Column(String(100))  # 验证者
    verification_date = Column(DateTime)  # 验证日期
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TechStackMapping(id={self.id}, input='{self.input_name}', standard='{self.standard_name}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "input_name": self.input_name,
            "standard_name": self.standard_name,
            "confidence_score": self.confidence_score,
            "mapping_type": self.mapping_type,
            "source": self.source,
            "usage_count": self.usage_count,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def record_usage(self):
        """记录使用"""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
    
    def verify_mapping(self, verifier):
        """验证映射"""
        self.is_verified = True
        self.verified_by = verifier
        self.verification_date = datetime.utcnow()