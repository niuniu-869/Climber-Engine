#!/usr/bin/env python3
"""
技术栈总结Agent服务
负责分析MCP会话数据并更新学习进度
"""

import yaml
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.database import get_db
from app.models.mcp_session import MCPSession, MCPCodeSnippet
from app.models.learning_progress import TechStackAsset, TechStackDebt, LearningProgressSummary
from app.models.user import User
from app.schemas.learning_progress import (
    TechStackAssetCreate, TechStackAssetUpdate,
    TechStackDebtCreate, TechStackDebtUpdate,
    LearningProgressSummaryCreate
)


class TechStackSummaryAgent:
    """
    技术栈总结Agent
    
    主要功能：
    1. 分析MCP会话数据
    2. 识别新技术栈和技能提升
    3. 更新学习进度数据库
    4. 生成学习建议和报告
    """
    
    def __init__(self, config_path: str = "app/config/tech_stack_agent_config.yaml"):
        """初始化Agent"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.last_analysis_time = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # 使用默认配置
            return {
                'basic': {'enabled': True},
                'schedule': {'analysis_interval_hours': 24},
                'data_processing': {'max_sessions_per_batch': 100},
                'analysis': {
                    'tech_stack_weights': {
                        'programming_language': 1.0,
                        'framework': 0.8,
                        'library': 0.6,
                        'tool': 0.4,
                        'database': 0.7
                    },
                    'proficiency_scoring': {
                        'base_score': 10.0,
                        'duration_weight': 0.3,
                        'complexity_weight': 0.4,
                        'quality_weight': 0.3,
                        'max_single_increment': 5.0
                    }
                }
            }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('TechStackSummaryAgent')
        logger.setLevel(getattr(logging, self.config.get('logging', {}).get('level', 'INFO')))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def is_enabled(self) -> bool:
        """检查Agent是否启用"""
        return self.config.get('basic', {}).get('enabled', True)
    
    def should_run_analysis(self) -> bool:
        """检查是否应该运行分析"""
        if not self.is_enabled():
            return False
        
        if self.last_analysis_time is None:
            return True
        
        interval_hours = self.config.get('schedule', {}).get('analysis_interval_hours', 24)
        time_since_last = datetime.utcnow() - self.last_analysis_time
        
        return time_since_last >= timedelta(hours=interval_hours)
    
    def run_analysis(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """运行技术栈分析"""
        if not self.is_enabled():
            self.logger.warning("TechStackSummaryAgent is disabled")
            return {'status': 'disabled', 'message': 'Agent is disabled'}
        
        self.logger.info(f"Starting tech stack analysis for user_id: {user_id}")
        
        try:
            db = next(get_db())
            
            # 获取需要分析的用户列表
            users_to_analyze = self._get_users_to_analyze(db, user_id)
            
            results = []
            for user in users_to_analyze:
                user_result = self._analyze_user_sessions(db, user.id)
                results.append(user_result)
            
            self.last_analysis_time = datetime.utcnow()
            
            summary = {
                'status': 'completed',
                'analyzed_users': len(users_to_analyze),
                'total_sessions_processed': sum(r.get('sessions_processed', 0) for r in results),
                'total_assets_updated': sum(r.get('assets_updated', 0) for r in results),
                'total_debts_identified': sum(r.get('debts_identified', 0) for r in results),
                'analysis_time': self.last_analysis_time.isoformat(),
                'user_results': results
            }
            
            self.logger.info(f"Analysis completed: {summary}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        finally:
            db.close()
    
    def _get_users_to_analyze(self, db: Session, user_id: Optional[int] = None) -> List[User]:
        """获取需要分析的用户列表"""
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            return [user] if user else []
        else:
            # 获取有活跃MCP会话的用户
            return db.query(User).join(MCPSession).filter(
                MCPSession.created_at >= datetime.utcnow() - timedelta(days=7)
            ).distinct().all()
    
    def _analyze_user_sessions(self, db: Session, user_id: int) -> Dict[str, Any]:
        """分析单个用户的会话数据"""
        self.logger.info(f"Analyzing sessions for user {user_id}")
        
        # 获取最近的会话数据
        cutoff_time = self._get_analysis_cutoff_time(db, user_id)
        sessions = self._get_recent_sessions(db, user_id, cutoff_time)
        
        if not sessions:
            self.logger.info(f"No new sessions found for user {user_id}")
            return {
                'user_id': user_id,
                'sessions_processed': 0,
                'assets_updated': 0,
                'debts_identified': 0
            }
        
        # 分析技术栈使用情况
        tech_usage = self._analyze_technology_usage(sessions)
        
        # 更新技术栈资产
        assets_updated = self._update_tech_stack_assets(db, user_id, tech_usage)
        
        # 识别技术栈负债
        debts_identified = self._identify_tech_stack_debts(db, user_id, tech_usage)
        
        # 生成学习进度总结
        self._generate_progress_summary(db, user_id, sessions, tech_usage)
        
        db.commit()
        
        return {
            'user_id': user_id,
            'sessions_processed': len(sessions),
            'assets_updated': assets_updated,
            'debts_identified': debts_identified,
            'technologies_analyzed': len(tech_usage)
        }
    
    def _get_analysis_cutoff_time(self, db: Session, user_id: int) -> datetime:
        """获取分析的截止时间"""
        # 查找最后一次分析时间
        last_summary = db.query(LearningProgressSummary).filter(
            LearningProgressSummary.user_id == user_id
        ).order_by(LearningProgressSummary.generated_at.desc()).first()
        
        if last_summary:
            return last_summary.period_end
        else:
            # 如果没有历史记录，分析最近30天的数据
            return datetime.utcnow() - timedelta(days=30)
    
    def _get_recent_sessions(self, db: Session, user_id: int, cutoff_time: datetime) -> List[MCPSession]:
        """获取最近的会话数据"""
        max_sessions = self.config.get('data_processing', {}).get('max_sessions_per_batch', 100)
        min_duration = self.config.get('data_processing', {}).get('min_session_duration_minutes', 5)
        
        return db.query(MCPSession).filter(
            and_(
                MCPSession.user_id == user_id,
                MCPSession.created_at > cutoff_time,
                MCPSession.status == 'completed',
                or_(
                    MCPSession.actual_duration >= min_duration,
                    MCPSession.actual_duration.is_(None)
                )
            )
        ).order_by(MCPSession.created_at.desc()).limit(max_sessions).all()
    
    def _analyze_technology_usage(self, sessions: List[MCPSession]) -> Dict[str, Dict[str, Any]]:
        """分析技术栈使用情况"""
        tech_usage = {}
        
        for session in sessions:
            # 分析主要技术栈
            technologies = session.technologies or []
            if session.primary_language:
                technologies.append(session.primary_language)
            
            frameworks = session.frameworks or []
            libraries = session.libraries or []
            tools = session.tools or []
            
            # 合并所有技术栈
            all_techs = {
                'programming_language': [session.primary_language] if session.primary_language else [],
                'framework': frameworks,
                'library': libraries,
                'tool': tools,
                'general': [t for t in technologies if t not in frameworks + libraries + tools]
            }
            
            for category, tech_list in all_techs.items():
                for tech in tech_list:
                    if not tech:
                        continue
                    
                    tech_key = tech.lower().strip()
                    if tech_key not in tech_usage:
                        tech_usage[tech_key] = {
                            'name': tech,
                            'category': category,
                            'usage_count': 0,
                            'total_duration': 0,
                            'total_complexity': 0,
                            'total_quality': 0,
                            'sessions': [],
                            'projects': set()
                        }
                    
                    usage = tech_usage[tech_key]
                    usage['usage_count'] += 1
                    usage['total_duration'] += session.actual_duration or 0
                    usage['total_complexity'] += session.complexity_score or 0
                    usage['total_quality'] += session.code_quality_score or 0
                    usage['sessions'].append(session.id)
                    
                    if session.project_name:
                        usage['projects'].add(session.project_name)
        
        # 计算平均值
        for tech_key, usage in tech_usage.items():
            count = usage['usage_count']
            if count > 0:
                usage['avg_duration'] = usage['total_duration'] / count
                usage['avg_complexity'] = usage['total_complexity'] / count
                usage['avg_quality'] = usage['total_quality'] / count
                usage['project_count'] = len(usage['projects'])
                usage['projects'] = list(usage['projects'])
        
        return tech_usage
    
    def _update_tech_stack_assets(self, db: Session, user_id: int, tech_usage: Dict[str, Dict[str, Any]]) -> int:
        """更新技术栈资产"""
        updated_count = 0
        weights = self.config.get('analysis', {}).get('tech_stack_weights', {})
        scoring = self.config.get('analysis', {}).get('proficiency_scoring', {})
        
        for tech_key, usage in tech_usage.items():
            # 查找现有资产
            existing_asset = db.query(TechStackAsset).filter(
                and_(
                    TechStackAsset.user_id == user_id,
                    func.lower(TechStackAsset.technology_name) == tech_key
                )
            ).first()
            
            if existing_asset:
                # 更新现有资产
                self._update_existing_asset(existing_asset, usage, scoring)
                updated_count += 1
            else:
                # 创建新资产
                new_asset = self._create_new_asset(db, user_id, usage, weights, scoring)
                if new_asset:
                    updated_count += 1
        
        return updated_count
    
    def _update_existing_asset(self, asset: TechStackAsset, usage: Dict[str, Any], scoring: Dict[str, Any]):
        """更新现有技术栈资产"""
        # 计算新的熟练度分数
        score_increment = self._calculate_proficiency_increment(usage, scoring)
        
        # 更新分数，但不超过最大增长限制
        max_increment = scoring.get('max_single_increment', 5.0)
        actual_increment = min(score_increment, max_increment)
        
        asset.proficiency_score = min(100.0, asset.proficiency_score + actual_increment)
        asset.total_practice_hours += usage.get('total_duration', 0) / 60.0  # 转换为小时
        asset.project_count += usage.get('project_count', 0)
        asset.last_practiced_date = datetime.utcnow()
        asset.is_active = True
        
        # 更新熟练度级别
        asset.proficiency_level = self._determine_proficiency_level(asset.proficiency_score)
        
        # 更新技能维度
        self._update_skill_dimensions(asset, usage)
        
        asset.updated_at = datetime.utcnow()
    
    def _create_new_asset(self, db: Session, user_id: int, usage: Dict[str, Any], 
                         weights: Dict[str, float], scoring: Dict[str, Any]) -> Optional[TechStackAsset]:
        """创建新的技术栈资产"""
        category = usage.get('category', 'general')
        weight = weights.get(category, 0.5)
        
        # 计算初始熟练度分数
        initial_score = self._calculate_initial_proficiency_score(usage, scoring, weight)
        
        new_asset = TechStackAsset(
            user_id=user_id,
            technology_name=usage['name'],
            category=category,
            proficiency_level=self._determine_proficiency_level(initial_score),
            proficiency_score=initial_score,
            confidence_level=min(1.0, initial_score / 100.0),
            first_learned_date=datetime.utcnow(),
            last_practiced_date=datetime.utcnow(),
            total_practice_hours=usage.get('total_duration', 0) / 60.0,
            project_count=usage.get('project_count', 0),
            is_active=True
        )
        
        # 设置技能维度
        self._update_skill_dimensions(new_asset, usage)
        
        db.add(new_asset)
        return new_asset
    
    def _calculate_proficiency_increment(self, usage: Dict[str, Any], scoring: Dict[str, Any]) -> float:
        """计算熟练度增长"""
        base_score = scoring.get('base_score', 10.0)
        duration_weight = scoring.get('duration_weight', 0.3)
        complexity_weight = scoring.get('complexity_weight', 0.4)
        quality_weight = scoring.get('quality_weight', 0.3)
        
        # 基于使用时长的分数
        duration_score = min(20.0, (usage.get('avg_duration', 0) / 60.0) * 2)  # 每小时2分
        
        # 基于复杂度的分数
        complexity_score = usage.get('avg_complexity', 0) * 2  # 复杂度 * 2
        
        # 基于质量的分数
        quality_score = usage.get('avg_quality', 0) / 10  # 质量分数 / 10
        
        total_score = (
            base_score +
            duration_score * duration_weight +
            complexity_score * complexity_weight +
            quality_score * quality_weight
        )
        
        return total_score
    
    def _calculate_initial_proficiency_score(self, usage: Dict[str, Any], 
                                           scoring: Dict[str, Any], weight: float) -> float:
        """计算初始熟练度分数"""
        increment = self._calculate_proficiency_increment(usage, scoring)
        return min(100.0, increment * weight)
    
    def _determine_proficiency_level(self, score: float) -> str:
        """根据分数确定熟练度级别"""
        if score >= 80:
            return "expert"
        elif score >= 60:
            return "advanced"
        elif score >= 30:
            return "intermediate"
        else:
            return "beginner"
    
    def _update_skill_dimensions(self, asset: TechStackAsset, usage: Dict[str, Any]):
        """更新技能维度评分"""
        # 基于使用情况更新各个维度
        usage_factor = min(1.0, usage.get('usage_count', 1) / 10.0)
        quality_factor = usage.get('avg_quality', 50) / 100.0
        complexity_factor = usage.get('avg_complexity', 5) / 10.0
        
        # 确保asset的属性不为None，如果为None则初始化为0
        if asset.practical_skills is None:
            asset.practical_skills = 0.0
        if asset.problem_solving is None:
            asset.problem_solving = 0.0
        if asset.theoretical_knowledge is None:
            asset.theoretical_knowledge = 0.0
        
        # 实践技能基于使用频率和质量
        asset.practical_skills = min(100.0, asset.practical_skills + usage_factor * quality_factor * 10)
        
        # 问题解决能力基于复杂度
        asset.problem_solving = min(100.0, asset.problem_solving + complexity_factor * 8)
        
        # 理论知识基于项目多样性
        project_diversity = min(1.0, usage.get('project_count', 1) / 5.0)
        asset.theoretical_knowledge = min(100.0, asset.theoretical_knowledge + project_diversity * 6)
    
    def _identify_tech_stack_debts(self, db: Session, user_id: int, tech_usage: Dict[str, Dict[str, Any]]) -> int:
        """识别技术栈负债"""
        # 这里可以实现更复杂的负债识别逻辑
        # 例如：分析项目需求但用户缺乏的技术栈
        identified_count = 0
        
        # 示例：如果用户使用了某个框架但没有掌握相关的核心技术
        for tech_key, usage in tech_usage.items():
            related_techs = self._get_related_technologies(usage['name'], usage['category'])
            
            for related_tech in related_techs:
                # 检查用户是否已经掌握相关技术
                existing_asset = db.query(TechStackAsset).filter(
                    and_(
                        TechStackAsset.user_id == user_id,
                        func.lower(TechStackAsset.technology_name) == related_tech.lower()
                    )
                ).first()
                
                existing_debt = db.query(TechStackDebt).filter(
                    and_(
                        TechStackDebt.user_id == user_id,
                        func.lower(TechStackDebt.technology_name) == related_tech.lower()
                    )
                ).first()
                
                if not existing_asset and not existing_debt:
                    # 创建新的技术栈负债
                    new_debt = TechStackDebt(
                        user_id=user_id,
                        technology_name=related_tech,
                        category=self._determine_tech_category(related_tech),
                        urgency_level="medium",
                        importance_score=70.0,
                        career_impact=60.0,
                        project_relevance=80.0,
                        target_proficiency_level="intermediate",
                        estimated_learning_hours=20.0,
                        learning_priority=3,
                        auto_generated=True,
                        status="identified"
                    )
                    
                    db.add(new_debt)
                    identified_count += 1
        
        return identified_count
    
    def _get_related_technologies(self, tech_name: str, category: str) -> List[str]:
        """获取相关技术栈"""
        # 这里可以实现更智能的相关技术推荐逻辑
        related_map = {
            'React': ['JavaScript', 'HTML', 'CSS', 'Node.js'],
            'Vue.js': ['JavaScript', 'HTML', 'CSS'],
            'Django': ['Python', 'HTML', 'CSS', 'SQL'],
            'Flask': ['Python', 'HTML', 'CSS'],
            'Spring Boot': ['Java', 'SQL', 'Maven'],
            'Express.js': ['Node.js', 'JavaScript'],
        }
        
        return related_map.get(tech_name, [])
    
    def _determine_tech_category(self, tech_name: str) -> str:
        """确定技术分类"""
        category_map = {
            'JavaScript': 'programming_language',
            'Python': 'programming_language',
            'Java': 'programming_language',
            'HTML': 'markup_language',
            'CSS': 'stylesheet_language',
            'SQL': 'query_language',
            'Node.js': 'runtime',
            'Maven': 'build_tool',
        }
        
        return category_map.get(tech_name, 'general')
    
    def _generate_progress_summary(self, db: Session, user_id: int, 
                                 sessions: List[MCPSession], tech_usage: Dict[str, Dict[str, Any]]):
        """生成学习进度总结"""
        period_start = min(session.created_at for session in sessions) if sessions else datetime.utcnow()
        period_end = datetime.utcnow()
        
        # 统计资产和负债数量
        total_assets = db.query(TechStackAsset).filter(TechStackAsset.user_id == user_id).count()
        total_debts = db.query(TechStackDebt).filter(
            and_(TechStackDebt.user_id == user_id, TechStackDebt.is_active == True)
        ).count()
        
        # 计算学习时间
        total_learning_hours = sum(session.actual_duration or 0 for session in sessions) / 60.0
        
        summary = LearningProgressSummary(
            user_id=user_id,
            report_period="analysis_cycle",
            period_start=period_start,
            period_end=period_end,
            total_assets=total_assets,
            new_assets_acquired=len([u for u in tech_usage.values() if u.get('usage_count', 0) == 1]),
            total_debts=total_debts,
            total_learning_hours=total_learning_hours,
            practice_sessions=len(sessions),
            projects_completed=len(set(s.project_name for s in sessions if s.project_name)),
            generated_at=datetime.utcnow()
        )
        
        db.add(summary)
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """获取分析状态"""
        return {
            'enabled': self.is_enabled(),
            'last_analysis_time': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'should_run': self.should_run_analysis(),
            'config': {
                'analysis_interval_hours': self.config.get('schedule', {}).get('analysis_interval_hours', 24),
                'max_sessions_per_batch': self.config.get('data_processing', {}).get('max_sessions_per_batch', 100)
            }
        }