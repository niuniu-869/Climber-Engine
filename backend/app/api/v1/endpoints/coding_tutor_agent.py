#!/usr/bin/env python3
"""
Coding教学Agent API端点
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.services.coding_tutor_agent import CodingTutorAgent
from app.services.learning_content_data_service import LearningContentDataService
from app.schemas.learning_content import (
    LearningArticleResponse, LearningQuestionResponse, QuestionAttemptResponse
)
from pydantic import BaseModel

router = APIRouter()

# 创建全局Agent实例
coding_tutor_agent = CodingTutorAgent()


class ContentGenerationRequest(BaseModel):
    """内容生成请求模型"""
    user_id: int
    technology: Optional[str] = None
    content_type: str = 'mixed'  # article, quiz, exercise, mixed
    difficulty: Optional[str] = None
    count: int = 5


class ContentGenerationResponse(BaseModel):
    """内容生成响应模型"""
    status: str
    content_count: Optional[int] = None
    technologies: Optional[List[str]] = None
    content: Optional[List[Dict[str, Any]]] = None
    saved_ids: Optional[List[int]] = None
    generated_at: Optional[str] = None
    message: Optional[str] = None


class LearningAttemptRequest(BaseModel):
    """学习尝试请求模型"""
    user_id: int
    content_id: int
    content_type: str  # quiz, article, exercise
    attempt_data: Dict[str, Any]


class LearningAttemptResponse(BaseModel):
    """学习尝试响应模型"""
    status: str
    message: str
    recorded_at: Optional[str] = None


class RecommendationRequest(BaseModel):
    """推荐请求模型"""
    user_id: int
    limit: int = 10


class RecommendationResponse(BaseModel):
    """推荐响应模型"""
    status: str
    recommendations: Optional[List[Dict[str, Any]]] = None
    total_count: Optional[int] = None
    generated_at: Optional[str] = None
    message: Optional[str] = None


class AgentStatusResponse(BaseModel):
    """Agent状态响应模型"""
    enabled: bool
    config: Dict[str, Any]
    tech_knowledge_base_size: int
    supported_technologies: List[str]


class QuizSubmissionRequest(BaseModel):
    """测验提交请求模型"""
    user_id: int
    quiz_answers: List[Dict[str, Any]]  # [{'question_id': int, 'selected_answer': int, 'time_spent': int}]


class QuizSubmissionResponse(BaseModel):
    """测验提交响应模型"""
    status: str
    total_questions: int
    correct_answers: int
    accuracy_rate: float
    total_time_spent: int
    detailed_results: List[Dict[str, Any]]
    learning_progress_updated: bool


@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """
    获取Coding教学Agent状态
    
    Returns:
        Agent状态信息
    """
    try:
        status_info = coding_tutor_agent.get_agent_status()
        return AgentStatusResponse(**status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_learning_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    生成学习内容
    
    Args:
        request: 内容生成请求参数
        background_tasks: 后台任务
        db: 数据库会话
    
    Returns:
        生成的学习内容
    """
    try:
        # 验证用户是否存在
        data_service = LearningContentDataService(db)
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        user = tech_service.get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        
        # 生成内容
        result = coding_tutor_agent.generate_learning_content(
            user_id=request.user_id,
            technology=request.technology,
            content_type=request.content_type,
            difficulty=request.difficulty,
            count=request.count
        )
        
        return ContentGenerationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.post("/generate-content/async")
async def generate_learning_content_async(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    异步生成学习内容
    
    Args:
        request: 内容生成请求参数
        background_tasks: 后台任务
    
    Returns:
        任务状态信息
    """
    try:
        # 添加后台任务
        background_tasks.add_task(
            coding_tutor_agent.generate_learning_content,
            user_id=request.user_id,
            technology=request.technology,
            content_type=request.content_type,
            difficulty=request.difficulty,
            count=request.count
        )
        
        return {
            "status": "started",
            "message": "Content generation started in background",
            "user_id": request.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start async content generation: {str(e)}"
        )


@router.post("/record-attempt", response_model=LearningAttemptResponse)
async def record_learning_attempt(
    request: LearningAttemptRequest,
    db: Session = Depends(get_db)
):
    """
    记录学习尝试
    
    Args:
        request: 学习尝试请求参数
        db: 数据库会话
    
    Returns:
        记录结果
    """
    try:
        # 验证用户是否存在
        data_service = LearningContentDataService(db)
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        user = tech_service.get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        
        # 记录学习尝试
        result = coding_tutor_agent.record_learning_attempt(
            user_id=request.user_id,
            content_id=request.content_id,
            content_type=request.content_type,
            attempt_data=request.attempt_data
        )
        
        return LearningAttemptResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record learning attempt: {str(e)}"
        )


@router.post("/submit-quiz", response_model=QuizSubmissionResponse)
async def submit_quiz(
    request: QuizSubmissionRequest,
    db: Session = Depends(get_db)
):
    """
    提交测验答案
    
    Args:
        request: 测验提交请求
        db: 数据库会话
    
    Returns:
        测验结果
    """
    try:
        data_service = LearningContentDataService(db)
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        # 验证用户是否存在
        user = tech_service.get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        
        # 处理测验提交
        total_questions = len(request.quiz_answers)
        correct_answers = 0
        total_time_spent = 0
        detailed_results = []
        
        for answer_data in request.quiz_answers:
            question_id = answer_data['question_id']
            selected_answer = answer_data['selected_answer']
            time_spent = answer_data.get('time_spent', 0)
            
            # 获取问题信息
            question = data_service.get_learning_question_by_id(question_id)
            if not question:
                continue
            
            # 检查答案是否正确
            is_correct = selected_answer == question.correct_answer
            if is_correct:
                correct_answers += 1
            
            total_time_spent += time_spent
            
            # 记录答题尝试
            from app.schemas.learning_content import QuestionAttemptCreate
            attempt_data = QuestionAttemptCreate(
                user_id=request.user_id,
                question_id=question_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                time_spent_seconds=time_spent
            )
            
            attempt = data_service.create_question_attempt(attempt_data)
            
            # 添加到详细结果
            detailed_results.append({
                'question_id': question_id,
                'question_text': question.question_text,
                'selected_answer': selected_answer,
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation,
                'time_spent': time_spent
            })
            
            # 更新学习进度
            coding_tutor_agent._update_learning_progress(
                db, request.user_id, question.technology, 
                question.difficulty_level, is_correct
            )
        
        # 计算准确率
        accuracy_rate = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        data_service.commit()
        
        return QuizSubmissionResponse(
            status="success",
            total_questions=total_questions,
            correct_answers=correct_answers,
            accuracy_rate=round(accuracy_rate, 2),
            total_time_spent=total_time_spent,
            detailed_results=detailed_results,
            learning_progress_updated=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit quiz: {str(e)}"
        )


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_learning_recommendations(
    user_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取学习推荐
    
    Args:
        user_id: 用户ID
        limit: 最大返回数量
        db: 数据库会话
    
    Returns:
        学习推荐列表
    """
    try:
        # 验证用户是否存在
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        user = tech_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # 获取推荐
        result = coding_tutor_agent.get_learning_recommendations(
            user_id=user_id,
            limit=limit
        )
        
        return RecommendationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get learning recommendations: {str(e)}"
        )


@router.get("/users/{user_id}/articles", response_model=List[LearningArticleResponse])
async def get_user_articles(
    user_id: int,
    technology: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取用户的学习文章
    
    Args:
        user_id: 用户ID
        technology: 技术栈过滤
        difficulty_level: 难度级别过滤
        limit: 最大返回数量
        db: 数据库会话
    
    Returns:
        学习文章列表
    """
    try:
        data_service = LearningContentDataService(db)
        
        # 验证用户是否存在
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        user = tech_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        articles = data_service.get_learning_articles(
            user_id=user_id,
            technology=technology,
            difficulty_level=difficulty_level,
            limit=limit
        )
        
        return [LearningArticleResponse.from_orm(article) for article in articles]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user articles: {str(e)}"
        )


@router.get("/users/{user_id}/questions", response_model=List[LearningQuestionResponse])
async def get_user_questions(
    user_id: int,
    technology: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    question_type: str = 'multiple_choice',
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取用户的学习问题
    
    Args:
        user_id: 用户ID
        technology: 技术栈过滤
        difficulty_level: 难度级别过滤
        question_type: 问题类型
        limit: 最大返回数量
        db: 数据库会话
    
    Returns:
        学习问题列表
    """
    try:
        data_service = LearningContentDataService(db)
        
        # 验证用户是否存在
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        user = tech_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        questions = data_service.get_learning_questions(
            user_id=user_id,
            technology=technology,
            difficulty_level=difficulty_level,
            question_type=question_type,
            limit=limit
        )
        
        return [LearningQuestionResponse.from_orm(question) for question in questions]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user questions: {str(e)}"
        )


@router.get("/users/{user_id}/progress/{technology}")
async def get_learning_progress(
    user_id: int,
    technology: str,
    db: Session = Depends(get_db)
):
    """
    获取用户在特定技术栈的学习进度
    
    Args:
        user_id: 用户ID
        technology: 技术名称
        db: 数据库会话
    
    Returns:
        学习进度信息
    """
    try:
        data_service = LearningContentDataService(db)
        
        # 验证用户是否存在
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        user = tech_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        progress = data_service.get_learning_progress_by_technology(user_id, technology)
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get learning progress: {str(e)}"
        )


@router.get("/users/{user_id}/statistics")
async def get_user_learning_statistics(
    user_id: int,
    technology: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    获取用户学习统计信息
    
    Args:
        user_id: 用户ID
        technology: 技术栈过滤
        days: 统计天数
        db: 数据库会话
    
    Returns:
        学习统计信息
    """
    try:
        data_service = LearningContentDataService(db)
        
        # 验证用户是否存在
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        user = tech_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # 获取答题统计
        attempt_stats = data_service.get_user_attempt_statistics(
            user_id, technology, days
        )
        
        # 获取内容统计
        article_stats = data_service.get_article_statistics(user_id)
        question_stats = data_service.get_question_statistics(user_id)
        
        return {
            'user_id': user_id,
            'period_days': days,
            'technology_filter': technology,
            'attempt_statistics': attempt_stats,
            'content_statistics': {
                'articles': article_stats,
                'questions': question_stats
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user learning statistics: {str(e)}"
        )


@router.get("/content/recommended")
async def get_recommended_content(
    user_id: int,
    technology: str,
    difficulty_level: str,
    content_type: str = 'mixed',
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    获取推荐的学习内容
    
    Args:
        user_id: 用户ID
        technology: 技术名称
        difficulty_level: 难度级别
        content_type: 内容类型
        limit: 最大返回数量
        db: 数据库会话
    
    Returns:
        推荐内容
    """
    try:
        data_service = LearningContentDataService(db)
        
        # 验证用户是否存在
        from app.services.tech_stack_data_service import TechStackDataService
        tech_service = TechStackDataService(db)
        
        user = tech_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        recommendations = data_service.get_recommended_content(
            user_id, technology, difficulty_level, content_type, limit
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommended content: {str(e)}"
        )


@router.get("/config")
async def get_agent_config():
    """
    获取Agent配置信息
    
    Returns:
        Agent配置
    """
    try:
        return coding_tutor_agent.config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent config: {str(e)}"
        )


@router.post("/reload-config")
async def reload_agent_config():
    """
    重新加载Agent配置
    
    Returns:
        操作结果
    """
    try:
        # 重新创建Agent实例以加载新配置
        global coding_tutor_agent
        coding_tutor_agent = CodingTutorAgent()
        
        return {
            "status": "success",
            "message": "Agent configuration reloaded successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload agent config: {str(e)}"
        )