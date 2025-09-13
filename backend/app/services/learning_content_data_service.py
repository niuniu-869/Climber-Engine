#!/usr/bin/env python3
"""
学习内容数据访问服务
负责学习内容和题目的CRUD操作
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from app.models.learning_content import LearningArticle, LearningQuestion, QuestionAttempt
from app.models.learning_progress import TechStackAsset, TechStackDebt
from app.models.user import User
from app.schemas.learning_content import (
    LearningArticleCreate, LearningArticleUpdate, LearningArticleResponse,
    LearningQuestionCreate, LearningQuestionUpdate, LearningQuestionResponse,
    QuestionAttemptCreate, QuestionAttemptResponse
)


class LearningContentDataService:
    """
    学习内容数据访问服务
    
    提供学习内容和题目相关的所有数据访问方法
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== 学习文章数据访问 ====================
    
    def get_learning_articles(
        self, 
        user_id: Optional[int] = None,
        technology: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        is_ai_generated: Optional[bool] = None,
        limit: int = 50
    ) -> List[LearningArticle]:
        """
        获取学习文章列表
        
        Args:
            user_id: 用户ID过滤
            technology: 技术栈过滤
            difficulty_level: 难度级别过滤
            is_ai_generated: 是否AI生成过滤
            limit: 最大返回数量
        
        Returns:
            学习文章列表
        """
        query = self.db.query(LearningArticle)
        
        if user_id:
            query = query.filter(LearningArticle.user_id == user_id)
        
        if technology:
            # 使用JSON查询来匹配技术栈
            query = query.filter(func.json_extract(LearningArticle.target_technologies, '$[0]') == technology)
        
        if difficulty_level:
            query = query.filter(LearningArticle.difficulty_level == difficulty_level)
        
        if is_ai_generated is not None:
            query = query.filter(LearningArticle.is_ai_generated == is_ai_generated)
        
        return query.order_by(desc(LearningArticle.created_at)).limit(limit).all()
    
    def get_learning_article_by_id(self, article_id: int) -> Optional[LearningArticle]:
        """
        根据ID获取学习文章
        
        Args:
            article_id: 文章ID
        
        Returns:
            学习文章或None
        """
        return self.db.query(LearningArticle).filter(LearningArticle.id == article_id).first()
    
    def create_learning_article(self, article_data: LearningArticleCreate) -> LearningArticle:
        """
        创建学习文章
        
        Args:
            article_data: 文章创建数据
        
        Returns:
            创建的学习文章
        """
        article = LearningArticle(**article_data.dict())
        self.db.add(article)
        self.db.flush()  # 获取ID但不提交事务
        return article
    
    def update_learning_article(
        self, 
        article: LearningArticle, 
        update_data: LearningArticleUpdate
    ) -> LearningArticle:
        """
        更新学习文章
        
        Args:
            article: 要更新的文章
            update_data: 更新数据
        
        Returns:
            更新后的学习文章
        """
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(article, field, value)
        
        article.updated_at = datetime.utcnow()
        return article
    
    def delete_learning_article(self, article_id: int) -> bool:
        """
        删除学习文章
        
        Args:
            article_id: 文章ID
        
        Returns:
            是否删除成功
        """
        article = self.get_learning_article_by_id(article_id)
        if article:
            self.db.delete(article)
            return True
        return False
    
    def get_articles_by_technology(
        self, 
        technology: str,
        user_id: Optional[int] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 20
    ) -> List[LearningArticle]:
        """
        根据技术栈获取文章
        
        Args:
            technology: 技术名称
            user_id: 用户ID
            difficulty_level: 难度级别
            limit: 最大返回数量
        
        Returns:
            学习文章列表
        """
        query = self.db.query(LearningArticle).filter(
            func.json_extract(LearningArticle.target_technologies, '$[0]') == technology
        )
        
        if user_id:
            query = query.filter(LearningArticle.user_id == user_id)
        
        if difficulty_level:
            query = query.filter(LearningArticle.difficulty_level == difficulty_level)
        
        return query.order_by(desc(LearningArticle.created_at)).limit(limit).all()
    
    def get_article_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取文章统计信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            统计信息字典
        """
        query = self.db.query(LearningArticle)
        
        if user_id:
            query = query.filter(LearningArticle.user_id == user_id)
        
        articles = query.all()
        
        if not articles:
            return {
                'total_articles': 0,
                'ai_generated_count': 0,
                'technology_distribution': {},
                'difficulty_distribution': {},
                'average_reading_time': 0
            }
        
        # 统计各种分布
        tech_dist = {}
        difficulty_dist = {}
        ai_generated_count = 0
        total_reading_time = 0
        
        for article in articles:
            # 技术分布
            techs = article.target_technologies or ['Unknown']
            for tech in techs:
                tech_dist[tech] = tech_dist.get(tech, 0) + 1
            
            # 难度分布
            difficulty = article.difficulty_level or 'Unknown'
            difficulty_dist[difficulty] = difficulty_dist.get(difficulty, 0) + 1
            
            # AI生成统计
            if article.ai_model_used:
                ai_generated_count += 1
            
            # 阅读时间统计
            total_reading_time += article.estimated_reading_time or 0
        
        return {
            'total_articles': len(articles),
            'ai_generated_count': ai_generated_count,
            'technology_distribution': tech_dist,
            'difficulty_distribution': difficulty_dist,
            'average_reading_time': total_reading_time / len(articles) if articles else 0
        }
    
    # ==================== 学习问题数据访问 ====================
    
    def get_learning_questions(
        self, 
        user_id: Optional[int] = None,
        technology: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        question_type: Optional[str] = None,
        limit: int = 50
    ) -> List[LearningQuestion]:
        """
        获取学习问题列表
        
        Args:
            user_id: 用户ID过滤
            technology: 技术栈过滤
            difficulty_level: 难度级别过滤
            question_type: 问题类型过滤
            limit: 最大返回数量
        
        Returns:
            学习问题列表
        """
        query = self.db.query(LearningQuestion)
        
        if user_id:
            query = query.filter(LearningQuestion.user_id == user_id)
        
        if technology:
            # 使用JSON查询来匹配技术栈
            query = query.filter(func.json_extract(LearningQuestion.target_technologies, '$[0]') == technology)
        
        if difficulty_level:
            query = query.filter(LearningQuestion.difficulty_level == difficulty_level)
        
        if question_type:
            query = query.filter(LearningQuestion.question_type == question_type)
        
        return query.order_by(desc(LearningQuestion.created_at)).limit(limit).all()
    
    def get_learning_question_by_id(self, question_id: int) -> Optional[LearningQuestion]:
        """
        根据ID获取学习问题
        
        Args:
            question_id: 问题ID
        
        Returns:
            学习问题或None
        """
        return self.db.query(LearningQuestion).filter(LearningQuestion.id == question_id).first()
    
    def create_learning_question(self, question_data: LearningQuestionCreate) -> LearningQuestion:
        """
        创建学习问题
        
        Args:
            question_data: 问题创建数据
        
        Returns:
            创建的学习问题
        """
        question = LearningQuestion(**question_data.dict())
        self.db.add(question)
        self.db.flush()  # 获取ID但不提交事务
        return question
    
    def update_learning_question(
        self, 
        question: LearningQuestion, 
        update_data: LearningQuestionUpdate
    ) -> LearningQuestion:
        """
        更新学习问题
        
        Args:
            question: 要更新的问题
            update_data: 更新数据
        
        Returns:
            更新后的学习问题
        """
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(question, field, value)
        
        question.updated_at = datetime.utcnow()
        return question
    
    def delete_learning_question(self, question_id: int) -> bool:
        """
        删除学习问题
        
        Args:
            question_id: 问题ID
        
        Returns:
            是否删除成功
        """
        question = self.get_learning_question_by_id(question_id)
        if question:
            self.db.delete(question)
            return True
        return False
    
    def get_questions_by_technology(
        self, 
        technology: str,
        user_id: Optional[int] = None,
        difficulty_level: Optional[str] = None,
        question_type: str = 'multiple_choice',
        limit: int = 20
    ) -> List[LearningQuestion]:
        """
        根据技术栈获取问题
        
        Args:
            technology: 技术名称
            user_id: 用户ID
            difficulty_level: 难度级别
            question_type: 问题类型
            limit: 最大返回数量
        
        Returns:
            学习问题列表
        """
        query = self.db.query(LearningQuestion).filter(
            and_(
                func.json_extract(LearningQuestion.target_technologies, '$[0]') == technology,
                LearningQuestion.question_type == question_type
            )
        )
        
        if user_id:
            query = query.filter(LearningQuestion.user_id == user_id)
        
        if difficulty_level:
            query = query.filter(LearningQuestion.difficulty_level == difficulty_level)
        
        return query.order_by(func.random()).limit(limit).all()  # 随机排序
    
    def get_question_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取问题统计信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            统计信息字典
        """
        query = self.db.query(LearningQuestion)
        
        if user_id:
            query = query.filter(LearningQuestion.user_id == user_id)
        
        questions = query.all()
        
        if not questions:
            return {
                'total_questions': 0,
                'technology_distribution': {},
                'difficulty_distribution': {},
                'type_distribution': {},
                'ai_generated_count': 0
            }
        
        # 统计各种分布
        tech_dist = {}
        difficulty_dist = {}
        type_dist = {}
        ai_generated_count = 0
        
        for question in questions:
            # 技术分布
            techs = question.target_technologies or ['Unknown']
            for tech in techs:
                tech_dist[tech] = tech_dist.get(tech, 0) + 1
            
            # 难度分布
            difficulty = question.difficulty_level or 'Unknown'
            difficulty_dist[difficulty] = difficulty_dist.get(difficulty, 0) + 1
            
            # 类型分布
            q_type = question.question_type or 'Unknown'
            type_dist[q_type] = type_dist.get(q_type, 0) + 1
            
            # AI生成统计
            if question.ai_model_used:
                ai_generated_count += 1
        
        return {
            'total_questions': len(questions),
            'technology_distribution': tech_dist,
            'difficulty_distribution': difficulty_dist,
            'type_distribution': type_dist,
            'ai_generated_count': ai_generated_count
        }
    
    # ==================== 答题尝试数据访问 ====================
    
    def get_question_attempts(
        self, 
        user_id: Optional[int] = None,
        question_id: Optional[int] = None,
        is_correct: Optional[bool] = None,
        limit: int = 100
    ) -> List[QuestionAttempt]:
        """
        获取答题尝试列表
        
        Args:
            user_id: 用户ID过滤
            question_id: 问题ID过滤
            is_correct: 是否正确过滤
            limit: 最大返回数量
        
        Returns:
            答题尝试列表
        """
        query = self.db.query(QuestionAttempt)
        
        if user_id:
            query = query.filter(QuestionAttempt.user_id == user_id)
        
        if question_id:
            query = query.filter(QuestionAttempt.question_id == question_id)
        
        if is_correct is not None:
            query = query.filter(QuestionAttempt.is_correct == is_correct)
        
        return query.order_by(desc(QuestionAttempt.created_at)).limit(limit).all()
    
    def create_question_attempt(self, attempt_data: QuestionAttemptCreate) -> QuestionAttempt:
        """
        创建答题尝试
        
        Args:
            attempt_data: 尝试创建数据
        
        Returns:
            创建的答题尝试
        """
        attempt = QuestionAttempt(**attempt_data.dict())
        self.db.add(attempt)
        self.db.flush()  # 获取ID但不提交事务
        return attempt
    
    def get_user_attempt_statistics(
        self, 
        user_id: int,
        technology: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取用户答题统计
        
        Args:
            user_id: 用户ID
            technology: 技术栈过滤
            days: 统计天数
        
        Returns:
            统计信息字典
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(QuestionAttempt).filter(
            and_(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.created_at >= cutoff_date
            )
        )
        
        if technology:
            query = query.join(LearningQuestion).filter(
                func.json_extract(LearningQuestion.target_technologies, '$[0]') == technology
            )
        
        attempts = query.all()
        
        if not attempts:
            return {
                'total_attempts': 0,
                'correct_attempts': 0,
                'accuracy_rate': 0.0,
                'average_time_spent': 0.0,
                'daily_activity': {},
                'technology_performance': {}
            }
        
        # 基本统计
        total_attempts = len(attempts)
        correct_attempts = sum(1 for attempt in attempts if attempt.is_correct)
        accuracy_rate = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
        
        # 平均用时
        total_time = sum(attempt.time_spent or 0 for attempt in attempts)
        average_time = total_time / total_attempts if total_attempts > 0 else 0
        
        # 每日活动统计
        daily_activity = {}
        for attempt in attempts:
            date_key = attempt.created_at.date().isoformat()
            if date_key not in daily_activity:
                daily_activity[date_key] = {'attempts': 0, 'correct': 0}
            daily_activity[date_key]['attempts'] += 1
            if attempt.is_correct:
                daily_activity[date_key]['correct'] += 1
        
        # 技术栈表现统计
        tech_performance = {}
        for attempt in attempts:
            if hasattr(attempt, 'question') and attempt.question:
                techs = attempt.question.target_technologies or ['Unknown']
                for tech in techs:
                    if tech not in tech_performance:
                        tech_performance[tech] = {'attempts': 0, 'correct': 0}
                    tech_performance[tech]['attempts'] += 1
                    if attempt.is_correct:
                        tech_performance[tech]['correct'] += 1
        
        # 计算各技术的准确率
        for tech, stats in tech_performance.items():
            stats['accuracy_rate'] = (stats['correct'] / stats['attempts']) * 100 if stats['attempts'] > 0 else 0
        
        return {
            'total_attempts': total_attempts,
            'correct_attempts': correct_attempts,
            'accuracy_rate': round(accuracy_rate, 2),
            'average_time_spent': round(average_time, 2),
            'daily_activity': daily_activity,
            'technology_performance': tech_performance
        }
    
    def get_learning_progress_by_technology(
        self, 
        user_id: int,
        technology: str
    ) -> Dict[str, Any]:
        """
        获取用户在特定技术栈的学习进度
        
        Args:
            user_id: 用户ID
            technology: 技术名称
        
        Returns:
            学习进度信息
        """
        # 获取文章阅读情况
        articles = self.get_articles_by_technology(technology, user_id)
        
        # 获取问题练习情况
        questions = self.get_questions_by_technology(technology, user_id)
        
        # 获取答题统计
        attempt_stats = self.get_user_attempt_statistics(user_id, technology)
        
        return {
            'technology': technology,
            'articles_available': len(articles),
            'questions_available': len(questions),
            'attempt_statistics': attempt_stats,
            'learning_materials': {
                'articles': [{
                    'id': article.id,
                    'title': article.title,
                    'difficulty': article.difficulty_level,
                    'reading_time': article.estimated_reading_time
                } for article in articles[:5]],  # 只返回前5篇
                'questions': [{
                    'id': question.id,
                    'difficulty': question.difficulty_level,
                    'type': question.question_type
                } for question in questions[:10]]  # 只返回前10题
            }
        }
    
    def get_recommended_content(
        self, 
        user_id: int,
        technology: str,
        difficulty_level: str,
        content_type: str = 'mixed',
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        获取推荐的学习内容
        
        Args:
            user_id: 用户ID
            technology: 技术名称
            difficulty_level: 难度级别
            content_type: 内容类型 (article, quiz, mixed)
            limit: 最大返回数量
        
        Returns:
            推荐内容
        """
        recommendations = []
        
        if content_type in ['article', 'mixed']:
            articles = self.get_articles_by_technology(
                technology, user_id, difficulty_level, limit
            )
            for article in articles:
                recommendations.append({
                    'type': 'article',
                    'id': article.id,
                    'title': article.title,
                    'difficulty': article.difficulty_level,
                    'estimated_time': article.estimated_reading_time,
                    'created_at': article.created_at.isoformat() if article.created_at else None
                })
        
        if content_type in ['quiz', 'mixed']:
            questions = self.get_questions_by_technology(
                technology, user_id, difficulty_level, 'multiple_choice', limit
            )
            
            # 按问题分组为测验
            if questions:
                quiz_questions = []
                for question in questions:
                    quiz_questions.append({
                        'id': question.id,
                        'question': question.question_text,
                        'options': question.options,
                        'difficulty': question.difficulty_level
                    })
                
                recommendations.append({
                    'type': 'quiz',
                    'title': f'{technology} {difficulty_level.title()} 测验',
                    'questions': quiz_questions,
                    'total_questions': len(quiz_questions),
                    'estimated_time': len(quiz_questions) * 2  # 每题2分钟
                })
        
        return {
            'technology': technology,
            'difficulty_level': difficulty_level,
            'recommendations': recommendations[:limit],
            'total_count': len(recommendations)
        }
    
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