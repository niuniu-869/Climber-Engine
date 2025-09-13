#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, SessionLocal, init_db
from app.models import (
    User, CodingSession, CodeRecord, SkillAssessment, LearningTask, TechnicalDebt,
    MCPSession, MCPCodeSnippet, TechStackAsset, TechStackDebt, LearningProgressSummary,
    LearningArticle, LearningQuestion, QuestionAttempt,
    TechStackCategory, TechStackStandard, TechStackMapping
)


def create_sample_data():
    """创建示例数据"""
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_user = db.query(User).first()
        if existing_user:
            print("数据库已有数据，跳过示例数据创建")
            return
        
        print("创建示例数据...")
        
        # 创建示例用户
        user = User(
            username="demo_user",
            email="demo@example.com",
            full_name="演示用户",
            skill_level="intermediate",
            primary_languages=["Python", "JavaScript"],
            frameworks=["FastAPI", "React"],
            tools=["VSCode", "Git", "Docker"],
            learning_style="kinesthetic",
            preferred_difficulty="medium",
            daily_goal_minutes=60
        )
        db.add(user)
        db.flush()  # 获取用户ID
        
        # 创建编程会话
        session = CodingSession(
            user_id=user.id,
            title="FastAPI项目开发",
            description="实现了用户管理和技能评估功能",
            project_name="登攀引擎",
            primary_language="Python",
            frameworks=["FastAPI", "SQLAlchemy"],
            tools=["VSCode", "Git"],
            session_type="project",
            duration_minutes=120,
            lines_of_code=450,
            files_modified=8,
            commits_count=5,
            code_quality_score=8.5,
            difficulty_rating=4,
            satisfaction_rating=5
        )
        db.add(session)
        db.flush()
        
        # 创建代码记录
        code_record = CodeRecord(
            coding_session_id=session.id,
            file_path="/app/models/user.py",
            file_name="user.py",
            file_extension=".py",
            language="Python",
            change_type="create",
            lines_added=65,
            lines_deleted=0,
            complexity_score=6.5,
            maintainability_score=8.2,
            readability_score=7.8,
            tech_debt_score=2.1,
            code_after="class User(Base):\n    __tablename__ = 'users'\n    # ... 用户模型定义",
            commit_message="创建用户数据模型",
            concepts_applied=["ORM", "数据建模"],
            difficulty_level=3
        )
        db.add(code_record)
        db.flush()
        
        # 创建技能评估
        skill_assessment = SkillAssessment(
            user_id=user.id,
            assessment_type="comprehensive",
            skill_category="programming",
            skill_name="Python开发",
            current_level="intermediate",
            score=75.0,
            confidence_level=0.8,
            theoretical_knowledge=78.0,
            practical_skills=72.0,
            problem_solving=80.0,
            code_quality=70.0,
            best_practices=68.0,
            strengths=["Python编程", "问题解决能力", "学习能力强"],
            weaknesses=["测试覆盖率低", "文档编写不足"],
            knowledge_gaps=["高级设计模式", "性能优化"],
            improvement_areas=["单元测试", "代码文档"],
            recommended_resources=["Python测试指南", "代码质量最佳实践"],
            suggested_projects=["开源项目贡献", "个人博客系统"],
            learning_path=["掌握pytest", "学习设计模式", "提高代码质量"],
            estimated_time_to_next_level=120,
            assessment_method="code_analysis",
            progress_since_last=15.0,
            learning_velocity=2.5
        )
        db.add(skill_assessment)
        db.flush()
        
        # 创建学习任务
        learning_task = LearningTask(
            user_id=user.id,
            title="编写单元测试",
            description="为用户模型编写完整的单元测试",
            task_type="practice",
            target_skill="testing",
            skill_level="intermediate",
            difficulty_level=3,
            estimated_duration=90,
            status="pending",
            learning_objectives=[
                "掌握pytest框架使用",
                "理解测试驱动开发",
                "提高代码覆盖率"
            ],
            success_criteria={
                "test_coverage": 90,
                "test_cases": 15,
                "assertions": 30
            },
            priority=4,
            scheduled_date=datetime.utcnow() + timedelta(days=1)
        )
        db.add(learning_task)
        
        # 创建技术债务记录
        technical_debt = TechnicalDebt(
            code_record_id=code_record.id,
            title="缺少输入验证",
            description="用户模型缺少邮箱格式和密码强度验证",
            debt_type="code_smell",
            severity="medium",
            file_path="/app/models/user.py",
            line_start=15,
            line_end=20,
            impact_score=5.5,
            effort_estimate=2.0,
            maintainability_impact=6.0,
            security_impact=7.0,
            detection_method="ai_analysis",
            suggested_fix="添加Pydantic验证器或SQLAlchemy验证约束",
            business_impact="可能导致无效数据入库",
            technical_risk="数据完整性风险"
        )
        db.add(technical_debt)
        
        # 创建技术栈配置数据
        create_tech_stack_config_data(db, user)
        
        # 创建MCP会话数据
        create_mcp_session_data(db, user)
        
        # 创建学习进度数据
        create_learning_progress_data(db, user)
        
        # 创建学习内容数据
        create_learning_content_data(db, user)
        
        db.commit()
        print("示例数据创建完成！")
        
        # 打印创建的数据统计
        print(f"创建用户: {user.username}")
        print(f"创建编程会话: {session.title}")
        print(f"创建代码记录: {code_record.file_path}")
        print(f"创建技能评估: {skill_assessment.skill_name} - 分数: {skill_assessment.score}")
        print(f"创建学习任务: {learning_task.title}")
        print(f"创建技术债务: {technical_debt.title}")
        
    except Exception as e:
        print(f"创建示例数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tech_stack_config_data(db, user):
    """创建技术栈配置示例数据"""
    # 创建技术栈分类
    categories = [
        {"name": "programming_language", "display_name": "编程语言", "description": "各种编程语言", "icon": "code", "color": "#3B82F6"},
        {"name": "web_framework", "display_name": "Web框架", "description": "Web开发框架", "icon": "globe", "color": "#10B981"},
        {"name": "database", "display_name": "数据库", "description": "数据库系统", "icon": "database", "color": "#F59E0B"},
        {"name": "tool", "display_name": "开发工具", "description": "开发和部署工具", "icon": "tool", "color": "#8B5CF6"}
    ]
    
    for cat_data in categories:
        category = TechStackCategory(**cat_data)
        db.add(category)
        db.flush()
        
        # 为每个分类添加一些技术栈
        if cat_data["name"] == "programming_language":
            techs = [
                {"name": "Python", "display_name": "Python", "description": "高级编程语言", "type": "programming_language", "learning_difficulty": "medium", "market_demand": 95.0},
                {"name": "JavaScript", "display_name": "JavaScript", "description": "Web编程语言", "type": "programming_language", "learning_difficulty": "medium", "market_demand": 98.0},
                {"name": "TypeScript", "display_name": "TypeScript", "description": "JavaScript的超集", "type": "programming_language", "learning_difficulty": "medium", "market_demand": 85.0}
            ]
        elif cat_data["name"] == "web_framework":
            techs = [
                {"name": "React", "display_name": "React", "description": "前端框架", "type": "framework", "learning_difficulty": "medium", "market_demand": 92.0},
                {"name": "FastAPI", "display_name": "FastAPI", "description": "Python Web框架", "type": "framework", "learning_difficulty": "medium", "market_demand": 78.0}
            ]
        else:
            techs = []
        
        for tech_data in techs:
            tech_data["category_id"] = category.id
            tech = TechStackStandard(**tech_data)
            db.add(tech)
    
    # 创建一些映射
    mappings = [
        {"input_name": "js", "standard_name": "JavaScript", "mapping_type": "abbreviation"},
        {"input_name": "ts", "standard_name": "TypeScript", "mapping_type": "abbreviation"},
        {"input_name": "reactjs", "standard_name": "React", "mapping_type": "variation"}
    ]
    
    for mapping_data in mappings:
        mapping = TechStackMapping(**mapping_data)
        db.add(mapping)


def create_mcp_session_data(db, user):
    """创建MCP会话示例数据"""
    mcp_session = MCPSession(
        user_id=user.id,
        session_name="登攀引擎开发会话",
        session_description="开发登攀引擎的MCP服务器功能",
        project_name="Climber Engine",
        work_type="development",
        task_description="实现MCP服务器的技术栈记录功能",
        technologies=["Python", "FastAPI", "SQLAlchemy", "MCP"],
        primary_language="Python",
        frameworks=["FastAPI"],
        libraries=["SQLAlchemy", "Pydantic"],
        tools=["VS Code", "Git"],
        difficulty_level="intermediate",
        complexity_score=7.5,
        estimated_duration=120,
        work_summary="成功实现了MCP服务器的基础功能",
        achievements=["完成MCP协议实现", "集成数据库记录"],
        challenges_faced=["MCP协议理解", "异步编程调试"],
        solutions_applied=["查阅MCP文档", "使用调试工具"],
        lessons_learned=["MCP协议设计原理", "异步编程最佳实践"],
        files_modified=5,
        lines_added=200,
        lines_deleted=10,
        code_quality_score=8.5,
        mcp_server_version="1.0.0",
        mcp_call_count=15
    )
    db.add(mcp_session)
    db.flush()
    
    # 创建代码片段
    code_snippet = MCPCodeSnippet(
        mcp_session_id=mcp_session.id,
        title="MCP服务器初始化",
        description="MCP服务器的初始化代码",
        file_path="/backend/climber_recorder_server.py",
        file_name="climber_recorder_server.py",
        code_content="class ClimberRecorderMCPServer:\n    def __init__(self):\n        self.db = SilentSessionLocal()\n        self.service = ClimberRecorderService(self.db)",
        language="Python",
        framework="MCP",
        snippet_type="class",
        purpose="服务器初始化",
        related_technologies=["Python", "MCP", "SQLAlchemy"],
        concepts_demonstrated=["类设计", "依赖注入"],
        quality_score=8.0,
        learning_value=7.5,
        difficulty_rating=3
    )
    db.add(code_snippet)


def create_learning_progress_data(db, user):
    """创建学习进度示例数据"""
    # 创建技术栈资产
    assets = [
        {
            "technology_name": "Python",
            "category": "programming_language",
            "proficiency_level": "advanced",
            "proficiency_score": 85.0,
            "confidence_level": 0.9,
            "total_practice_hours": 500.0,
            "project_count": 15,
            "theoretical_knowledge": 90.0,
            "practical_skills": 85.0,
            "problem_solving": 80.0,
            "best_practices": 75.0,
            "advanced_features": 70.0,
            "market_demand": 95.0
        },
        {
            "technology_name": "FastAPI",
            "category": "framework",
            "proficiency_level": "intermediate",
            "proficiency_score": 70.0,
            "confidence_level": 0.8,
            "total_practice_hours": 100.0,
            "project_count": 3,
            "theoretical_knowledge": 75.0,
            "practical_skills": 70.0,
            "problem_solving": 65.0,
            "best_practices": 60.0,
            "advanced_features": 50.0,
            "market_demand": 78.0
        }
    ]
    
    for asset_data in assets:
        asset_data["user_id"] = user.id
        asset = TechStackAsset(**asset_data)
        db.add(asset)
    
    # 创建技术栈负债
    debts = [
        {
            "technology_name": "React",
            "category": "framework",
            "urgency_level": "high",
            "importance_score": 90.0,
            "career_impact": 85.0,
            "project_relevance": 80.0,
            "target_proficiency_level": "intermediate",
            "estimated_learning_hours": 80.0,
            "learning_priority": 4,
            "learning_motivation": "前端开发必备技能",
            "market_demand": 92.0,
            "salary_potential": 88.0
        },
        {
            "technology_name": "Docker",
            "category": "tool",
            "urgency_level": "medium",
            "importance_score": 75.0,
            "career_impact": 70.0,
            "project_relevance": 85.0,
            "target_proficiency_level": "intermediate",
            "estimated_learning_hours": 40.0,
            "learning_priority": 3,
            "learning_motivation": "容器化部署需求",
            "market_demand": 82.0,
            "salary_potential": 75.0
        }
    ]
    
    for debt_data in debts:
        debt_data["user_id"] = user.id
        debt = TechStackDebt(**debt_data)
        db.add(debt)
    
    # 创建学习进度总结
    summary = LearningProgressSummary(
        user_id=user.id,
        report_period="monthly",
        period_start=datetime.utcnow() - timedelta(days=30),
        period_end=datetime.utcnow(),
        total_assets=2,
        new_assets_acquired=1,
        total_debts=2,
        debts_resolved=0,
        total_learning_hours=25.0,
        skill_growth_rate=15.0,
        learning_velocity=2.5,
        goal_achievement_rate=0.8
    )
    db.add(summary)


def create_learning_content_data(db, user):
    """创建学习内容示例数据"""
    # 创建学习文章
    article = LearningArticle(
        user_id=user.id,
        title="FastAPI入门指南",
        subtitle="从零开始学习FastAPI框架",
        summary="本文介绍FastAPI的基础概念和使用方法",
        content="# FastAPI入门\n\nFastAPI是一个现代、快速的Python Web框架...",
        article_type="tutorial",
        category="framework",
        target_technologies=["FastAPI", "Python"],
        difficulty_level="beginner",
        target_audience="Python开发者",
        learning_objectives=["理解FastAPI基础概念", "掌握基本API开发"],
        content_quality_score=8.5,
        educational_value=9.0,
        estimated_reading_time=15,
        ai_model_used="GPT-4",
        status="published"
    )
    db.add(article)
    db.flush()
    
    # 创建学习题目
    question = LearningQuestion(
        user_id=user.id,
        related_article_id=article.id,
        title="FastAPI路由定义",
        question_text="如何在FastAPI中定义一个GET路由？",
        question_type="multiple_choice",
        target_technologies=["FastAPI"],
        difficulty_level="beginner",
        complexity_score=3.0,
        estimated_time=5,
        options=[
            {"A": "@app.get('/path')"},
            {"B": "@app.route('/path', methods=['GET'])"},
            {"C": "app.add_route('/path', 'GET')"},
            {"D": "app.get_route('/path')"}
        ],
        correct_answer="A",
        explanation="FastAPI使用装饰器@app.get()来定义GET路由",
        max_score=10.0,
        passing_score=6.0,
        ai_model_used="GPT-4",
        status="active"
    )
    db.add(question)
    db.flush()
    
    # 创建答题记录
    attempt = QuestionAttempt(
        user_id=user.id,
        question_id=question.id,
        user_answer="A",
        is_correct=True,
        score=10.0,
        time_spent=120,
        confidence_level=0.9,
        understanding_level=0.8,
        satisfaction_rating=5
    )
    db.add(attempt)


def main():
    """主函数"""
    print("开始初始化数据库...")
    
    try:
        # 创建所有表
        print("创建数据表...")
        init_db()
        print("数据表创建完成！")
        
        # 创建示例数据
        create_sample_data()
        
        print("数据库初始化完成！")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()