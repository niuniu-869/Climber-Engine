#!/usr/bin/env python3
"""
Coding教学Agent演示和测试脚本
"""

import sys
import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base
from app.services.coding_tutor_agent import CodingTutorAgent
from app.services.learning_content_data_service import LearningContentDataService
from app.services.tech_stack_data_service import TechStackDataService
from tests.test_data_generator import TestDataGenerator


def create_test_database():
    """
    创建测试数据库
    """
    print("Creating test database for Coding Tutor Agent...")
    engine = create_engine("sqlite:///test_coding_tutor.db", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def generate_test_data(db_session):
    """
    生成测试数据
    """
    print("Generating test data...")
    generator = TestDataGenerator(db_session)
    
    # 生成用户和基础数据
    user_data = generator.generate_complete_test_dataset(
        username="coding_tutor_test_user",
        email="coding_tutor@example.com",
        session_count=20,
        asset_count=8,
        debt_count=6
    )
    
    print(f"  Created user {user_data['username']} with {user_data['total_records']} records")
    print(f"  User ID: {user_data['user_id']}")
    print(f"  Assets: {user_data['assets_created']}, Debts: {user_data['debts_created']}")
    
    return user_data


def test_agent_functionality(db_session, user_data):
    """
    测试Agent功能
    """
    print("\nTesting Coding Tutor Agent functionality...")
    
    # 创建Agent实例
    agent = CodingTutorAgent()
    
    # 测试Agent状态
    print("\n1. Agent Status:")
    status = agent.get_agent_status()
    print(f"  Enabled: {status['enabled']}")
    print(f"  Supported technologies: {status['supported_technologies']}")
    print(f"  Knowledge base size: {status['tech_knowledge_base_size']}")
    
    user_id = user_data['user_id']
    
    # 测试学习推荐
    print("\n2. Learning Recommendations:")
    recommendations = agent.get_learning_recommendations(user_id, limit=5)
    print(f"  Status: {recommendations['status']}")
    if recommendations['status'] == 'success':
        print(f"  Total recommendations: {recommendations['total_count']}")
        for i, rec in enumerate(recommendations['recommendations'][:3]):
            print(f"    {i+1}. {rec['technology']} ({rec['reason']})")
    
    # 测试内容生成 - Java (确保在知识库中)
    print("\n3. Content Generation - Java:")
    try:
        content_result = agent.generate_learning_content(
            user_id=user_id,
            technology="Java",
            content_type="mixed",
            difficulty="intermediate",
            count=3
        )
        print(f"  Status: {content_result['status']}")
        if content_result['status'] == 'success':
            print(f"  Generated content count: {content_result['content_count']}")
            print(f"  Technologies: {content_result['technologies']}")
            
            # 显示生成的内容
            for i, content in enumerate(content_result['content'][:2]):
                print(f"    Content {i+1}: {content['type']} - {content['title']}")
                if content['type'] == 'quiz':
                    print(f"      Questions: {content['total_questions']}")
                elif content['type'] == 'article':
                    print(f"      Reading time: {content['estimated_reading_time']} min")
    
    except Exception as e:
        print(f"  Error: {e}")
    
    # 测试内容生成 - Python
    print("\n3.1 Content Generation - Python:")
    try:
        python_result = agent.generate_learning_content(
            user_id=user_id,
            technology="Python",
            content_type="quiz",
            difficulty="beginner",
            count=2
        )
        print(f"  Status: {python_result['status']}")
        if python_result['status'] == 'success':
            print(f"  Generated content count: {python_result['content_count']}")
            print(f"  Technologies: {python_result['technologies']}")
    
    except Exception as e:
        print(f"  Error: {e}")
    
    # 测试内容生成 - JavaScript
    print("\n4. Content Generation - JavaScript:")
    try:
        js_content = agent.generate_learning_content(
            user_id=user_id,
            technology="JavaScript",
            content_type="quiz",
            difficulty="beginner",
            count=2
        )
        print(f"  Status: {js_content['status']}")
        if js_content['status'] == 'success':
            print(f"  Generated content count: {js_content['content_count']}")
            
            # 显示第一个测验的问题
            if js_content['content']:
                quiz = js_content['content'][0]
                if quiz['type'] == 'quiz' and 'questions' in quiz:
                    print(f"  Sample question: {quiz['questions'][0]['question']}")
                    print(f"  Options: {quiz['questions'][0]['options']}")
    
    except Exception as e:
        print(f"  Error: {e}")
    
    # 测试自动推荐内容生成
    print("\n5. Auto-Recommended Content Generation:")
    try:
        auto_content = agent.generate_learning_content(
            user_id=user_id,
            content_type="mixed",
            count=2
        )
        print(f"  Status: {auto_content['status']}")
        if auto_content['status'] == 'success':
            print(f"  Auto-selected technologies: {auto_content['technologies']}")
            print(f"  Generated content count: {auto_content['content_count']}")
    
    except Exception as e:
        print(f"  Error: {e}")


def test_data_service(db_session, user_data):
    """
    测试数据服务
    """
    print("\n6. Learning Content Data Service Testing:")
    
    data_service = LearningContentDataService(db_session)
    user_id = user_data['user_id']
    
    # 测试获取学习文章
    print("\n  Learning Articles:")
    articles = data_service.get_learning_articles(user_id=user_id, limit=10)
    print(f"    Total articles: {len(articles)}")
    
    if articles:
        print("    Recent articles:")
        for i, article in enumerate(articles[:3]):
            print(f"      {i+1}. {article.title} ({article.technology}, {article.difficulty_level})")
    
    # 测试获取学习问题
    print("\n  Learning Questions:")
    questions = data_service.get_learning_questions(user_id=user_id, limit=10)
    print(f"    Total questions: {len(questions)}")
    
    if questions:
        print("    Sample questions:")
        for i, question in enumerate(questions[:2]):
            print(f"      {i+1}. {question.question_text[:50]}... ({question.technology})")
    
    # 测试文章统计
    print("\n  Article Statistics:")
    article_stats = data_service.get_article_statistics(user_id)
    print(f"    Total articles: {article_stats['total_articles']}")
    print(f"    AI generated: {article_stats['ai_generated_count']}")
    print(f"    Technology distribution: {article_stats['technology_distribution']}")
    print(f"    Average reading time: {article_stats['average_reading_time']:.1f} min")
    
    # 测试问题统计
    print("\n  Question Statistics:")
    question_stats = data_service.get_question_statistics(user_id)
    print(f"    Total questions: {question_stats['total_questions']}")
    print(f"    AI generated: {question_stats['ai_generated_count']}")
    print(f"    Technology distribution: {question_stats['technology_distribution']}")
    print(f"    Difficulty distribution: {question_stats['difficulty_distribution']}")


def test_learning_simulation(db_session, user_data):
    """
    模拟学习过程
    """
    print("\n7. Learning Process Simulation:")
    
    agent = CodingTutorAgent()
    data_service = LearningContentDataService(db_session)
    user_id = user_data['user_id']
    
    # 获取一些问题进行模拟答题
    questions = data_service.get_learning_questions(
        user_id=user_id, 
        question_type='multiple_choice', 
        limit=5
    )
    
    if questions:
        print(f"\n  Simulating quiz with {len(questions)} questions:")
        
        correct_count = 0
        total_time = 0
        
        for i, question in enumerate(questions):
            # 模拟答题（随机选择答案，50%概率选择正确答案）
            import random
            
            if random.random() < 0.7:  # 70%概率答对
                selected_answer = question.correct_answer
                is_correct = True
                correct_count += 1
            else:
                # 随机选择错误答案
                wrong_options = [i for i in range(len(question.options)) if i != question.correct_answer]
                selected_answer = random.choice(wrong_options) if wrong_options else 0
                is_correct = False
            
            time_spent = random.randint(30, 120)  # 30-120秒
            total_time += time_spent
            
            print(f"    Q{i+1}: {question.question_text[:40]}...")
            print(f"         Selected: {question.options[selected_answer]} ({'✓' if is_correct else '✗'})")
            
            # 记录答题尝试
            try:
                attempt_data = {
                    'technology': question.technology,
                    'difficulty': question.difficulty_level,
                    'selected_answer': selected_answer,
                    'is_correct': is_correct,
                    'time_spent': time_spent
                }
                
                result = agent.record_learning_attempt(
                    user_id=user_id,
                    content_id=question.id,
                    content_type='quiz',
                    attempt_data=attempt_data
                )
                
                if result['status'] != 'success':
                    print(f"         Warning: Failed to record attempt - {result.get('message')}")
            
            except Exception as e:
                print(f"         Error recording attempt: {e}")
        
        accuracy = (correct_count / len(questions)) * 100
        avg_time = total_time / len(questions)
        
        print(f"\n  Quiz Results:")
        print(f"    Accuracy: {accuracy:.1f}% ({correct_count}/{len(questions)})")
        print(f"    Average time per question: {avg_time:.1f} seconds")
        print(f"    Total time: {total_time} seconds")
        
        # 获取更新后的学习统计
        print("\n  Updated Learning Statistics:")
        attempt_stats = data_service.get_user_attempt_statistics(user_id)
        print(f"    Total attempts: {attempt_stats['total_attempts']}")
        print(f"    Overall accuracy: {attempt_stats['accuracy_rate']:.1f}%")
        print(f"    Average time spent: {attempt_stats['average_time_spent']:.1f}s")
        
        if attempt_stats['technology_performance']:
            print("    Technology performance:")
            for tech, perf in attempt_stats['technology_performance'].items():
                print(f"      {tech}: {perf['accuracy_rate']:.1f}% ({perf['correct']}/{perf['attempts']})")
    
    else:
        print("  No questions available for simulation")


def test_learning_progress_tracking(db_session, user_data):
    """
    测试学习进度跟踪
    """
    print("\n8. Learning Progress Tracking:")
    
    data_service = LearningContentDataService(db_session)
    tech_service = TechStackDataService(db_session)
    user_id = user_data['user_id']
    
    # 获取用户的技术栈资产（学习前后对比）
    print("\n  Current Tech Stack Assets:")
    assets = tech_service.get_tech_stack_assets(user_id)
    
    if assets:
        print("    Top skills:")
        for i, asset in enumerate(assets[:5]):
            print(f"      {i+1}. {asset.technology_name}: {asset.proficiency_score:.1f} ({asset.proficiency_level})")
            print(f"         Last practiced: {asset.last_practiced_date}")
    
    # 获取技术栈负债
    print("\n  Current Tech Stack Debts:")
    debts = tech_service.get_tech_stack_debts(user_id, is_active=True)
    
    if debts:
        print("    Learning priorities:")
        for i, debt in enumerate(debts[:5]):
            print(f"      {i+1}. {debt.technology_name}: {debt.urgency_level} urgency")
            print(f"         Progress: {debt.learning_progress:.1f}%, Priority: {debt.learning_priority}")
    
    # 测试特定技术的学习进度
    technologies = ['Python', 'JavaScript', 'React']
    
    for tech in technologies:
        print(f"\n  Learning Progress for {tech}:")
        try:
            progress = data_service.get_learning_progress_by_technology(user_id, tech)
            print(f"    Articles available: {progress['articles_available']}")
            print(f"    Questions available: {progress['questions_available']}")
            
            attempt_stats = progress['attempt_statistics']
            if attempt_stats['total_attempts'] > 0:
                print(f"    Practice attempts: {attempt_stats['total_attempts']}")
                print(f"    Accuracy rate: {attempt_stats['accuracy_rate']:.1f}%")
            else:
                print(f"    No practice attempts yet")
        
        except Exception as e:
            print(f"    Error getting progress: {e}")


def test_content_recommendation(db_session, user_data):
    """
    测试内容推荐
    """
    print("\n9. Content Recommendation Testing:")
    
    # 首先生成一些内容用于推荐测试
    agent = CodingTutorAgent()
    user_id = user_data['user_id']
    
    print("\n  Generating content for recommendation testing...")
    
    # 为Python和JavaScript生成一些内容
    test_technologies = [('Python', 'beginner'), ('JavaScript', 'beginner'), ('Java', 'intermediate')]
    
    for tech, difficulty in test_technologies:
        try:
            result = agent.generate_learning_content(
                user_id=user_id,
                technology=tech,
                content_type='mixed',
                difficulty=difficulty,
                count=2
            )
            if result['status'] == 'success':
                print(f"    Generated {result['content_count']} items for {tech} ({difficulty})")
        except Exception as e:
            print(f"    Error generating content for {tech}: {e}")
    
    # 现在测试推荐功能
    data_service = LearningContentDataService(db_session)
    
    technologies = ['Python', 'JavaScript', 'Java']
    difficulties = ['beginner', 'intermediate']
    
    for tech in technologies:
        for difficulty in difficulties:
            print(f"\n  Recommendations for {tech} ({difficulty}):")
            try:
                recommendations = data_service.get_recommended_content(
                    user_id=user_id,
                    technology=tech,
                    difficulty_level=difficulty,
                    content_type='mixed',
                    limit=3
                )
                
                print(f"    Total recommendations: {recommendations['total_count']}")
                
                for i, rec in enumerate(recommendations['recommendations']):
                    print(f"      {i+1}. {rec['type']}: {rec.get('title', 'Quiz')}")
                    if rec['type'] == 'quiz':
                        print(f"         Questions: {rec.get('total_questions', 0)}")
                    elif rec['type'] == 'article':
                        print(f"         Reading time: {rec.get('estimated_time', 0)} min")
            
            except Exception as e:
                print(f"    Error: {e}")


def display_summary(user_data, db_session):
    """
    显示测试总结
    """
    print("\n" + "="*60)
    print("CODING TUTOR AGENT TEST SUMMARY")
    print("="*60)
    
    data_service = LearningContentDataService(db_session)
    user_id = user_data['user_id']
    
    # 统计生成的内容
    articles = data_service.get_learning_articles(user_id=user_id)
    questions = data_service.get_learning_questions(user_id=user_id)
    attempts = data_service.get_question_attempts(user_id=user_id)
    
    print(f"User: {user_data['username']} (ID: {user_id})")
    print(f"Generated articles: {len(articles)}")
    print(f"Generated questions: {len(questions)}")
    print(f"Learning attempts: {len(attempts)}")
    
    # 统计各技术的内容
    tech_content = {}
    for article in articles:
        techs = article.target_technologies or ['Unknown']
        for tech in techs:
            if tech not in tech_content:
                tech_content[tech] = {'articles': 0, 'questions': 0}
            tech_content[tech]['articles'] += 1
    
    for question in questions:
        techs = question.target_technologies or ['Unknown']
        for tech in techs:
            if tech not in tech_content:
                tech_content[tech] = {'articles': 0, 'questions': 0}
            tech_content[tech]['questions'] += 1
    
    print("\nContent by technology:")
    for tech, counts in tech_content.items():
        print(f"  {tech}: {counts['articles']} articles, {counts['questions']} questions")
    
    # 学习统计
    if attempts:
        correct_attempts = sum(1 for attempt in attempts if attempt.is_correct)
        accuracy = (correct_attempts / len(attempts)) * 100
        print(f"\nLearning performance:")
        print(f"  Total attempts: {len(attempts)}")
        print(f"  Correct answers: {correct_attempts}")
        print(f"  Accuracy rate: {accuracy:.1f}%")
    
    print("\nCoding Tutor Agent testing completed successfully!")
    print("Database file: test_coding_tutor.db")


def main():
    """
    主函数
    """
    print("Coding Tutor Agent Demo")
    print("=" * 40)
    
    try:
        # 创建数据库
        db_session = create_test_database()
        
        # 生成测试数据
        user_data = generate_test_data(db_session)
        
        # 测试Agent功能
        test_agent_functionality(db_session, user_data)
        
        # 测试数据服务
        test_data_service(db_session, user_data)
        
        # 模拟学习过程
        test_learning_simulation(db_session, user_data)
        
        # 测试学习进度跟踪
        test_learning_progress_tracking(db_session, user_data)
        
        # 测试内容推荐
        test_content_recommendation(db_session, user_data)
        
        # 显示总结
        display_summary(user_data, db_session)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'db_session' in locals():
            db_session.close()


if __name__ == "__main__":
    main()