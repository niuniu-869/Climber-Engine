#!/usr/bin/env python3
"""
运行技术栈总结Agent和编程教学Agent测试
使用DeepSeek API生成真实数据
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, get_db
from app.services.tech_stack_summary_agent import TechStackSummaryAgent
from app.services.coding_tutor_agent import CodingTutorAgent
from app.services.ai_service import AIService
from app.models.user import User
from app.models.mcp_session import MCPSession, MCPCodeSnippet
from app.models.learning_progress import TechStackAsset, TechStackDebt
from app.models.learning_content import LearningArticle, LearningQuestion


def create_test_users(db) -> List[User]:
    """创建测试用户"""
    print("\n=== 创建测试用户 ===")
    
    test_users = [
        {
            "username": "agent_test_user_1",
            "email": "agent1@test.com",
            "full_name": "Agent Test User 1",
            "skill_level": "intermediate",
            "primary_languages": ["python", "javascript"]
        },
        {
            "username": "agent_test_user_2", 
            "email": "agent2@test.com",
            "full_name": "Agent Test User 2",
            "skill_level": "beginner",
            "primary_languages": ["python", "java"]
        },
        {
            "username": "agent_test_user_3",
            "email": "agent3@test.com", 
            "full_name": "Agent Test User 3",
            "skill_level": "advanced",
            "primary_languages": ["javascript", "typescript", "react"]
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        
        if existing_user:
            print(f"✅ 用户已存在: {existing_user.username}")
            created_users.append(existing_user)
        else:
            # 创建新用户
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                skill_level=user_data["skill_level"],
                primary_languages=user_data["primary_languages"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ 创建新用户: {user.username}")
            created_users.append(user)
    
    return created_users


def create_test_mcp_sessions(db, users: List[User]) -> List[MCPSession]:
    """创建测试MCP会话数据"""
    print("\n=== 创建测试MCP会话数据 ===")
    
    sessions_data = [
        {
            "user_id": users[0].id,
            "session_id": "test_session_1",
            "project_name": "Web开发项目",
            "work_type": "development",
            "task_description": "开发用户认证系统",
            "primary_language": "python",
            "technologies": ["python", "django", "postgresql"],
            "frameworks": ["django", "django-rest-framework"],
            "libraries": ["requests", "pandas"],
            "tools": ["git", "docker"],
            "actual_duration": 120,  # 2小时
            "complexity_score": 7.5,
            "code_quality_score": 85.0,
            "status": "completed"
        },
        {
            "user_id": users[0].id,
            "session_id": "test_session_2",
            "project_name": "数据分析项目",
            "work_type": "analysis",
            "task_description": "用户行为数据分析",
            "primary_language": "python",
            "technologies": ["python", "pandas", "numpy"],
            "frameworks": ["jupyter"],
            "libraries": ["pandas", "numpy", "matplotlib", "seaborn"],
            "tools": ["jupyter", "git"],
            "actual_duration": 180,  # 3小时
            "complexity_score": 6.0,
            "code_quality_score": 78.0,
            "status": "completed"
        },
        {
            "user_id": users[1].id,
            "session_id": "test_session_3",
            "project_name": "Java学习项目",
            "work_type": "learning",
            "task_description": "学习Java基础语法",
            "primary_language": "java",
            "technologies": ["java"],
            "frameworks": [],
            "libraries": [],
            "tools": ["intellij", "maven"],
            "actual_duration": 90,  # 1.5小时
            "complexity_score": 3.0,
            "code_quality_score": 65.0,
            "status": "completed"
        },
        {
            "user_id": users[2].id,
            "session_id": "test_session_4",
            "project_name": "React应用开发",
            "work_type": "development",
            "task_description": "构建响应式前端界面",
            "primary_language": "javascript",
            "technologies": ["javascript", "typescript", "react"],
            "frameworks": ["react", "next.js"],
            "libraries": ["axios", "lodash", "moment"],
            "tools": ["vscode", "npm", "webpack"],
            "actual_duration": 240,  # 4小时
            "complexity_score": 8.5,
            "code_quality_score": 92.0,
            "status": "completed"
        }
    ]
    
    created_sessions = []
    
    for session_data in sessions_data:
        # 检查会话是否已存在
        existing_session = db.query(MCPSession).filter(
            MCPSession.session_name == session_data["session_id"]
        ).first()
        
        if existing_session:
            print(f"✅ 会话已存在: {existing_session.session_name}")
            created_sessions.append(existing_session)
        else:
            # 创建新会话
            session = MCPSession(
                user_id=session_data["user_id"],
                session_name=session_data["session_id"],
                project_name=session_data["project_name"],
                work_type=session_data["work_type"],
                task_description=session_data["task_description"],
                primary_language=session_data["primary_language"],
                technologies=session_data["technologies"],
                frameworks=session_data["frameworks"],
                libraries=session_data["libraries"],
                tools=session_data["tools"],
                actual_duration=session_data["actual_duration"],
                complexity_score=session_data["complexity_score"],
                code_quality_score=session_data["code_quality_score"],
                status=session_data["status"],
                created_at=datetime.utcnow() - timedelta(days=1),  # 1天前创建
                updated_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            print(f"✅ 创建新会话: {session.session_name}")
            created_sessions.append(session)
    
    return created_sessions


async def test_tech_stack_summary_agent(users: List[User]):
    """测试技术栈总结Agent"""
    print("\n=== 测试技术栈总结Agent ===")
    
    try:
        # 初始化Agent
        agent = TechStackSummaryAgent()
        
        print(f"Agent状态: {'启用' if agent.is_enabled() else '禁用'}")
        print(f"应该运行分析: {'是' if agent.should_run_analysis() else '否'}")
        
        # 运行分析
        print("\n开始运行技术栈分析...")
        
        # 为每个用户运行分析
        for user in users:
            print(f"\n分析用户: {user.username}")
            result = agent.run_analysis(user_id=user.id)
            
            if result['status'] == 'completed':
                print(f"✅ 分析完成")
                print(f"   处理会话数: {result.get('total_sessions_processed', 0)}")
                print(f"   更新资产数: {result.get('total_assets_updated', 0)}")
                print(f"   识别负债数: {result.get('total_debts_identified', 0)}")
                
                # 显示用户结果详情
                user_results = result.get('user_results', [])
                for user_result in user_results:
                    if user_result.get('user_id') == user.id:
                        print(f"   技术栈分析数: {user_result.get('technologies_analyzed', 0)}")
            else:
                print(f"❌ 分析失败: {result.get('message', 'Unknown error')}")
        
        # 获取Agent状态
        status = agent.get_analysis_status()
        print(f"\n最后分析时间: {status.get('last_analysis_time', 'Never')}")
        
    except Exception as e:
        print(f"❌ 技术栈总结Agent测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_coding_tutor_agent_with_deepseek(users: List[User]):
    """测试编程教学Agent（使用DeepSeek API）"""
    print("\n=== 测试编程教学Agent（使用DeepSeek API）===")
    
    try:
        # 初始化Agent
        agent = CodingTutorAgent()
        
        print(f"Agent状态: {'启用' if agent.is_enabled() else '禁用'}")
        
        # 测试内容生成
        for user in users:
            print(f"\n为用户 {user.username} 生成学习内容...")
            
            # 生成混合内容
            result = agent.generate_learning_content(
                user_id=user.id,
                content_type='mixed',
                count=3
            )
            
            if result['status'] == 'success':
                print(f"✅ 内容生成成功")
                print(f"   生成内容数: {result.get('content_count', 0)}")
                print(f"   推荐技术栈: {', '.join(result.get('technologies', []))}")
                
                # 显示生成的内容
                content_list = result.get('content', [])
                for i, content in enumerate(content_list[:2]):  # 只显示前2个
                    print(f"   内容 {i+1}: {content.get('type')} - {content.get('title', 'N/A')}")
                    if content.get('type') == 'article':
                        print(f"     预计阅读时间: {content.get('estimated_reading_time', 0)} 分钟")
                    elif content.get('type') == 'quiz':
                        print(f"     题目数量: {content.get('total_questions', 0)}")
            
            elif result['status'] == 'no_content':
                print(f"⚠️  没有找到合适的学习内容: {result.get('message', '')}")
            else:
                print(f"❌ 内容生成失败: {result.get('message', 'Unknown error')}")
        
        # 测试学习推荐
        print("\n测试学习推荐功能...")
        for user in users[:2]:  # 只测试前2个用户
            recommendations = agent.get_learning_recommendations(user.id, limit=5)
            
            if recommendations['status'] == 'success':
                print(f"✅ 用户 {user.username} 的学习推荐:")
                recs = recommendations.get('recommendations', [])
                for i, rec in enumerate(recs[:3]):  # 只显示前3个推荐
                    print(f"   {i+1}. {rec.get('technology', 'N/A')} - {rec.get('reason', 'N/A')}")
                    if 'recommended_difficulty' in rec:
                        print(f"      推荐难度: {rec['recommended_difficulty']}")
            else:
                print(f"❌ 推荐生成失败: {recommendations.get('message', 'Unknown error')}")
        
        # 获取Agent状态
        status = agent.get_agent_status()
        print(f"\n支持的技术栈数量: {len(status.get('supported_technologies', []))}")
        print(f"AI生成启用: {'是' if status.get('config', {}).get('ai_generation_enabled', False) else '否'}")
        
    except Exception as e:
        print(f"❌ 编程教学Agent测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_ai_service_with_deepseek():
    """测试AI服务（专门使用DeepSeek）"""
    print("\n=== 测试AI服务（DeepSeek API）===")
    
    try:
        db = SessionLocal()
        ai_service = AIService(db)
        
        # 检查DeepSeek客户端是否可用
        if 'deepseek' not in ai_service.clients:
            print("❌ DeepSeek客户端未初始化，请检查API密钥配置")
            return
        
        print("✅ DeepSeek客户端已初始化")
        
        # 测试代码分析（使用DeepSeek）
        print("\n1. 测试技术债务分析（DeepSeek）...")
        test_code = """
def process_user_data(users):
    result = []
    for user in users:
        if user['age'] > 18:
            if user['status'] == 'active':
                if user['premium'] == True:
                    result.append({
                        'id': user['id'],
                        'name': user['name'],
                        'type': 'premium_adult'
                    })
                else:
                    result.append({
                        'id': user['id'], 
                        'name': user['name'],
                        'type': 'regular_adult'
                    })
    return result
"""
        
        debt_analysis = await ai_service.analyze_technical_debt(
            code_content=test_code,
            file_path="user_processor.py",
            language="python"
        )
        
        if debt_analysis.get('success'):
            print("✅ 技术债务分析成功")
            analysis = debt_analysis.get('analysis', {})
            if isinstance(analysis, dict):
                print(f"   债务评分: {analysis.get('debt_score', 'N/A')}")
                print(f"   发现问题数: {len(analysis.get('issues', []))}")
                print(f"   改进建议数: {len(analysis.get('recommendations', []))}")
            else:
                print(f"   分析结果: {str(analysis)[:100]}...")
        else:
            print(f"❌ 技术债务分析失败: {debt_analysis.get('error', 'Unknown error')}")
        
        # 测试学习任务生成（使用DeepSeek）
        print("\n2. 测试学习任务生成（DeepSeek）...")
        user_skills = {
            "python": {"level": "intermediate", "experience_months": 12},
            "javascript": {"level": "beginner", "experience_months": 3}
        }
        
        task_generation = await ai_service.generate_learning_tasks(
            user_skills=user_skills,
            focus_areas=["algorithms", "data_structures"],
            difficulty_level="intermediate",
            count=3
        )
        
        if task_generation.get('success'):
            print("✅ 学习任务生成成功")
            tasks = task_generation.get('tasks', [])
            print(f"   生成任务数: {len(tasks)}")
            for i, task in enumerate(tasks[:2]):  # 只显示前2个
                if isinstance(task, dict):
                    print(f"   任务 {i+1}: {task.get('title', 'N/A')}")
                    print(f"     难度: {task.get('difficulty', 'N/A')}")
        else:
            print(f"❌ 学习任务生成失败: {task_generation.get('error', 'Unknown error')}")
        
        # 测试代码改进建议（使用DeepSeek）
        print("\n3. 测试代码改进建议（DeepSeek）...")
        improvement_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price'] * item['quantity']
    return total
"""
        
        improvements = await ai_service.suggest_code_improvements(
            code=improvement_code,
            language="python",
            focus_areas=["performance", "readability"]
        )
        
        if improvements.get('success'):
            print("✅ 代码改进建议成功")
            suggestions = improvements.get('suggestions', [])
            print(f"   改进建议数: {len(suggestions)}")
            if suggestions:
                print(f"   第一个建议: {suggestions[0] if isinstance(suggestions[0], str) else 'Complex suggestion'}")
        else:
            print(f"❌ 代码改进建议失败: {improvements.get('error', 'Unknown error')}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ AI服务测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试函数"""
    print("🚀 开始Agent测试（使用DeepSeek API）")
    print("=" * 50)
    
    try:
        # 初始化数据库
        db = SessionLocal()
        
        try:
            # 1. 创建测试数据
            users = create_test_users(db)
            sessions = create_test_mcp_sessions(db, users)
            
            print(f"\n📊 测试数据准备完成:")
            print(f"   用户数: {len(users)}")
            print(f"   会话数: {len(sessions)}")
            
            # 2. 测试AI服务（DeepSeek）
            await test_ai_service_with_deepseek()
            
            # 3. 测试技术栈总结Agent
            await test_tech_stack_summary_agent(users)
            
            # 4. 测试编程教学Agent
            await test_coding_tutor_agent_with_deepseek(users)
            
            print("\n" + "=" * 50)
            print("🎉 Agent测试完成！")
            print("\n📋 测试总结:")
            print("   ✅ 测试数据创建成功")
            print("   ✅ DeepSeek API集成测试")
            print("   ✅ 技术栈总结Agent运行")
            print("   ✅ 编程教学Agent运行")
            print("   ✅ 真实数据生成完成")
            
            # 显示数据库中的数据统计
            print("\n📈 数据库统计:")
            asset_count = db.query(TechStackAsset).count()
            debt_count = db.query(TechStackDebt).count()
            article_count = db.query(LearningArticle).count()
            question_count = db.query(LearningQuestion).count()
            
            print(f"   技术栈资产: {asset_count}")
            print(f"   技术栈负债: {debt_count}")
            print(f"   学习文章: {article_count}")
            print(f"   练习题目: {question_count}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())