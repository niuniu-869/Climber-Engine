#!/usr/bin/env python3
"""
技术栈数据访问服务
负责技术栈总结Agent的数据访问操作
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from app.models.mcp_session import MCPSession, MCPCodeSnippet
from app.models.learning_progress import TechStackAsset, TechStackDebt, LearningProgressSummary
from app.models.user import User
from app.schemas.learning_progress import (
    TechStackAssetCreate, TechStackAssetUpdate, TechStackAssetResponse,
    TechStackDebtCreate, TechStackDebtUpdate, TechStackDebtResponse,
    LearningProgressSummaryCreate, LearningProgressSummaryResponse
)


class TechStackDataService:
    """
    技术栈数据访问服务
    
    提供技术栈总结Agent所需的所有数据访问方法
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== MCP会话数据访问 ====================
    
    def get_recent_mcp_sessions(
        self, 
        user_id: Optional[int] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
        min_duration_minutes: int = 5
    ) -> List[MCPSession]:
        """
        获取最近的MCP会话数据
        
        Args:
            user_id: 用户ID，None表示所有用户
            since: 起始时间，None表示最近30天
            limit: 最大返回数量
            min_duration_minutes: 最小会话时长（分钟）
        
        Returns:
            MCP会话列表
        """
        if since is None:
            since = datetime.utcnow() - timedelta(days=30)
        
        query = self.db.query(MCPSession).filter(
            and_(
                MCPSession.created_at >= since,
                MCPSession.status == 'completed',
                or_(
                    MCPSession.actual_duration >= min_duration_minutes,
                    MCPSession.actual_duration.is_(None)
                )
            )
        )
        
        if user_id:
            query = query.filter(MCPSession.user_id == user_id)
        
        return query.order_by(desc(MCPSession.created_at)).limit(limit).all()
    
    def get_mcp_sessions_by_technology(
        self, 
        technology: str,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[MCPSession]:
        """
        根据技术栈获取MCP会话
        
        Args:
            technology: 技术名称
            user_id: 用户ID
            limit: 最大返回数量
        
        Returns:
            MCP会话列表
        """
        query = self.db.query(MCPSession).filter(
            or_(
                MCPSession.technologies.contains([technology]),
                MCPSession.primary_language == technology,
                MCPSession.frameworks.contains([technology]),
                MCPSession.libraries.contains([technology]),
                MCPSession.tools.contains([technology])
            )
        )
        
        if user_id:
            query = query.filter(MCPSession.user_id == user_id)
        
        return query.order_by(desc(MCPSession.created_at)).limit(limit).all()
    
    def get_mcp_session_statistics(
        self, 
        user_id: int,
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取MCP会话统计信息
        
        Args:
            user_id: 用户ID
            since: 起始时间
        
        Returns:
            统计信息字典
        """
        if since is None:
            since = datetime.utcnow() - timedelta(days=30)
        
        query = self.db.query(MCPSession).filter(
            and_(
                MCPSession.user_id == user_id,
                MCPSession.created_at >= since,
                MCPSession.status == 'completed'
            )
        )
        
        sessions = query.all()
        
        if not sessions:
            return {
                'total_sessions': 0,
                'total_duration_hours': 0,
                'average_quality_score': 0,
                'technologies_used': [],
                'projects_worked_on': [],
                'work_types': {}
            }
        
        # 统计技术栈使用情况
        tech_counter = {}
        project_set = set()
        work_type_counter = {}
        total_duration = 0
        total_quality = 0
        quality_count = 0
        
        for session in sessions:
            # 统计时长
            if session.actual_duration:
                total_duration += session.actual_duration
            
            # 统计质量分数
            if session.code_quality_score:
                total_quality += session.code_quality_score
                quality_count += 1
            
            # 统计技术栈
            all_techs = (session.technologies or []) + \
                       (session.frameworks or []) + \
                       (session.libraries or []) + \
                       (session.tools or [])
            
            if session.primary_language:
                all_techs.append(session.primary_language)
            
            for tech in all_techs:
                tech_counter[tech] = tech_counter.get(tech, 0) + 1
            
            # 统计项目
            if session.project_name:
                project_set.add(session.project_name)
            
            # 统计工作类型
            work_type = session.work_type
            work_type_counter[work_type] = work_type_counter.get(work_type, 0) + 1
        
        return {
            'total_sessions': len(sessions),
            'total_duration_hours': total_duration / 60.0,
            'average_quality_score': total_quality / quality_count if quality_count > 0 else 0,
            'technologies_used': sorted(tech_counter.items(), key=lambda x: x[1], reverse=True),
            'projects_worked_on': list(project_set),
            'work_types': work_type_counter
        }
    
    def get_last_analysis_time(self, user_id: int) -> Optional[datetime]:
        """
        获取用户最后一次分析时间
        
        Args:
            user_id: 用户ID
        
        Returns:
            最后分析时间，如果没有则返回None
        """
        last_summary = self.db.query(LearningProgressSummary).filter(
            LearningProgressSummary.user_id == user_id
        ).order_by(desc(LearningProgressSummary.generated_at)).first()
        
        return last_summary.period_end if last_summary else None
    
    # ==================== 技术栈资产数据访问 ====================
    
    def get_tech_stack_assets(
        self, 
        user_id: int,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[TechStackAsset]:
        """
        获取用户的技术栈资产
        
        Args:
            user_id: 用户ID
            category: 技术分类过滤
            is_active: 是否活跃过滤
        
        Returns:
            技术栈资产列表
        """
        query = self.db.query(TechStackAsset).filter(TechStackAsset.user_id == user_id)
        
        if category:
            query = query.filter(TechStackAsset.category == category)
        
        if is_active is not None:
            query = query.filter(TechStackAsset.is_active == is_active)
        
        return query.order_by(desc(TechStackAsset.proficiency_score)).all()
    
    def get_tech_stack_asset_by_name(
        self, 
        user_id: int, 
        technology_name: str
    ) -> Optional[TechStackAsset]:
        """
        根据技术名称获取技术栈资产
        
        Args:
            user_id: 用户ID
            technology_name: 技术名称
        
        Returns:
            技术栈资产或None
        """
        return self.db.query(TechStackAsset).filter(
            and_(
                TechStackAsset.user_id == user_id,
                func.lower(TechStackAsset.technology_name) == technology_name.lower()
            )
        ).first()
    
    def create_tech_stack_asset(self, asset_data: TechStackAssetCreate) -> TechStackAsset:
        """
        创建技术栈资产
        
        Args:
            asset_data: 资产创建数据
        
        Returns:
            创建的技术栈资产
        """
        asset = TechStackAsset(**asset_data.dict())
        self.db.add(asset)
        self.db.flush()  # 获取ID但不提交事务
        return asset
    
    def update_tech_stack_asset(
        self, 
        asset: TechStackAsset, 
        update_data: TechStackAssetUpdate
    ) -> TechStackAsset:
        """
        更新技术栈资产
        
        Args:
            asset: 要更新的资产
            update_data: 更新数据
        
        Returns:
            更新后的技术栈资产
        """
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(asset, field, value)
        
        asset.updated_at = datetime.utcnow()
        return asset
    
    def get_tech_stack_asset_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取技术栈资产统计信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            统计信息字典
        """
        assets = self.get_tech_stack_assets(user_id)
        
        if not assets:
            return {
                'total_assets': 0,
                'active_assets': 0,
                'average_proficiency': 0,
                'category_distribution': {},
                'proficiency_distribution': {},
                'top_skills': []
            }
        
        active_assets = [a for a in assets if a.is_active]
        category_dist = {}
        proficiency_dist = {'beginner': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
        
        total_proficiency = 0
        for asset in assets:
            # 分类分布
            category_dist[asset.category] = category_dist.get(asset.category, 0) + 1
            
            # 熟练度分布
            proficiency_dist[asset.proficiency_level] += 1
            
            # 总熟练度
            total_proficiency += asset.proficiency_score
        
        # 排序获取顶级技能
        top_skills = sorted(assets, key=lambda x: x.proficiency_score, reverse=True)[:10]
        
        return {
            'total_assets': len(assets),
            'active_assets': len(active_assets),
            'average_proficiency': total_proficiency / len(assets),
            'category_distribution': category_dist,
            'proficiency_distribution': proficiency_dist,
            'top_skills': [{
                'name': skill.technology_name,
                'category': skill.category,
                'proficiency_score': skill.proficiency_score,
                'proficiency_level': skill.proficiency_level
            } for skill in top_skills]
        }
    
    # ==================== 技术栈负债数据访问 ====================
    
    def get_tech_stack_debts(
        self, 
        user_id: int,
        status: Optional[str] = None,
        urgency_level: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[TechStackDebt]:
        """
        获取用户的技术栈负债
        
        Args:
            user_id: 用户ID
            status: 状态过滤
            urgency_level: 紧急程度过滤
            is_active: 是否活跃过滤
        
        Returns:
            技术栈负债列表
        """
        query = self.db.query(TechStackDebt).filter(TechStackDebt.user_id == user_id)
        
        if status:
            query = query.filter(TechStackDebt.status == status)
        
        if urgency_level:
            query = query.filter(TechStackDebt.urgency_level == urgency_level)
        
        if is_active is not None:
            query = query.filter(TechStackDebt.is_active == is_active)
        
        return query.order_by(desc(TechStackDebt.importance_score)).all()
    
    def get_tech_stack_debt_by_name(
        self, 
        user_id: int, 
        technology_name: str
    ) -> Optional[TechStackDebt]:
        """
        根据技术名称获取技术栈负债
        
        Args:
            user_id: 用户ID
            technology_name: 技术名称
        
        Returns:
            技术栈负债或None
        """
        return self.db.query(TechStackDebt).filter(
            and_(
                TechStackDebt.user_id == user_id,
                func.lower(TechStackDebt.technology_name) == technology_name.lower()
            )
        ).first()
    
    def create_tech_stack_debt(self, debt_data: TechStackDebtCreate) -> TechStackDebt:
        """
        创建技术栈负债
        
        Args:
            debt_data: 负债创建数据
        
        Returns:
            创建的技术栈负债
        """
        debt = TechStackDebt(**debt_data.dict())
        self.db.add(debt)
        self.db.flush()  # 获取ID但不提交事务
        return debt
    
    def update_tech_stack_debt(
        self, 
        debt: TechStackDebt, 
        update_data: TechStackDebtUpdate
    ) -> TechStackDebt:
        """
        更新技术栈负债
        
        Args:
            debt: 要更新的负债
            update_data: 更新数据
        
        Returns:
            更新后的技术栈负债
        """
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(debt, field, value)
        
        debt.updated_at = datetime.utcnow()
        return debt
    
    def get_high_priority_debts(self, user_id: int, limit: int = 10) -> List[TechStackDebt]:
        """
        获取高优先级技术栈负债
        
        Args:
            user_id: 用户ID
            limit: 最大返回数量
        
        Returns:
            高优先级负债列表
        """
        return self.db.query(TechStackDebt).filter(
            and_(
                TechStackDebt.user_id == user_id,
                TechStackDebt.is_active == True,
                TechStackDebt.status.in_(['identified', 'planned', 'learning'])
            )
        ).order_by(
            desc(TechStackDebt.learning_priority),
            desc(TechStackDebt.importance_score)
        ).limit(limit).all()
    
    # ==================== 学习进度总结数据访问 ====================
    
    def get_learning_progress_summaries(
        self, 
        user_id: int,
        report_period: Optional[str] = None,
        limit: int = 10
    ) -> List[LearningProgressSummary]:
        """
        获取学习进度总结
        
        Args:
            user_id: 用户ID
            report_period: 报告周期过滤
            limit: 最大返回数量
        
        Returns:
            学习进度总结列表
        """
        query = self.db.query(LearningProgressSummary).filter(
            LearningProgressSummary.user_id == user_id
        )
        
        if report_period:
            query = query.filter(LearningProgressSummary.report_period == report_period)
        
        return query.order_by(desc(LearningProgressSummary.generated_at)).limit(limit).all()
    
    def create_learning_progress_summary(
        self, 
        summary_data: LearningProgressSummaryCreate
    ) -> LearningProgressSummary:
        """
        创建学习进度总结
        
        Args:
            summary_data: 总结创建数据
        
        Returns:
            创建的学习进度总结
        """
        summary = LearningProgressSummary(**summary_data.dict())
        self.db.add(summary)
        self.db.flush()  # 获取ID但不提交事务
        return summary
    
    def get_latest_progress_summary(self, user_id: int) -> Optional[LearningProgressSummary]:
        """
        获取最新的学习进度总结
        
        Args:
            user_id: 用户ID
        
        Returns:
            最新的学习进度总结或None
        """
        return self.db.query(LearningProgressSummary).filter(
            LearningProgressSummary.user_id == user_id
        ).order_by(desc(LearningProgressSummary.generated_at)).first()
    
    # ==================== 用户数据访问 ====================
    
    def get_active_users_with_sessions(self, days: int = 7) -> List[User]:
        """
        获取有活跃会话的用户
        
        Args:
            days: 天数范围
        
        Returns:
            用户列表
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(User).join(MCPSession).filter(
            MCPSession.created_at >= cutoff_date
        ).distinct().all()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户对象或None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    # ==================== 事务管理 ====================
    
    def commit(self):
        """提交事务"""
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def rollback(self):
        """回滚事务"""
        self.db.rollback()
    
    def flush(self):
        """刷新会话"""
        self.db.flush()