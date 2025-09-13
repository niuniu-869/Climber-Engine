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
from app.models import User, CodingSession, CodeRecord, SkillAssessment, LearningTask, TechnicalDebt


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