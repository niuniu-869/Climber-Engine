#!/usr/bin/env python3
"""
测试AI服务集成和MCP工具调用
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.ai_service import AIService
from app.services.mcp_service import MCPService, MCPSession
from app.models.user import User


async def test_ai_service():
    """测试AI服务基础功能"""
    print("\n=== 测试AI服务 ===")
    
    db = SessionLocal()
    try:
        ai_service = AIService(db)
        
        # 测试健康检查
        print("\n1. 测试AI服务健康检查...")
        health = await ai_service.health_check()
        print(f"健康状态: {health['status']}")
        print(f"可用提供商: {list(health['providers'].keys())}")
        
        # 测试技术债务分析
        print("\n2. 测试技术债务分析...")
        test_code = """
def calculate_total(items):
    total = 0
    for i in range(len(items)):
        if items[i] > 0:
            total = total + items[i]
    return total
"""
        
        debt_analysis = await ai_service.analyze_technical_debt(
            code_content=test_code,
            file_path="test.py",
            language="python"
        )
        
        if debt_analysis["success"]:
            print("✅ 技术债务分析成功")
            print(f"模型: {debt_analysis['model_info']['provider']}/{debt_analysis['model_info']['model']}")
            print(f"Token使用: {debt_analysis['model_info']['usage']}")
        else:
            print(f"❌ 技术债务分析失败: {debt_analysis['error']}")
        
        # 测试学习任务生成
        print("\n3. 测试学习任务生成...")
        user_skills = {
            "skill_level": "intermediate",
            "primary_languages": ["python", "javascript"],
            "frameworks": ["fastapi", "react"],
            "learning_style": "hands_on"
        }
        
        task_generation = await ai_service.generate_learning_tasks(
            user_skills=user_skills,
            focus_areas=["algorithms", "design_patterns"],
            difficulty_level="intermediate",
            count=3
        )
        
        if task_generation["success"]:
            print("✅ 学习任务生成成功")
            print(f"生成任务数: {len(task_generation['tasks'])}")
            print(f"模型: {task_generation['model_info']['provider']}/{task_generation['model_info']['model']}")
        else:
            print(f"❌ 学习任务生成失败: {task_generation['error']}")
        
        # 测试技能评估
        print("\n4. 测试技能评估...")
        code_samples = [
            "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
            "class Calculator: def add(self, a, b): return a + b"
        ]
        
        skill_assessment = await ai_service.assess_programming_skills(
            code_samples=code_samples,
            skill_type="algorithm_design",
            context="基础算法实现评估"
        )
        
        if skill_assessment["success"]:
            print("✅ 技能评估成功")
            print(f"模型: {skill_assessment['model_info']['provider']}/{skill_assessment['model_info']['model']}")
        else:
            print(f"❌ 技能评估失败: {skill_assessment['error']}")
        
    finally:
        db.close()


async def test_mcp_tools():
    """测试MCP工具调用"""
    print("\n=== 测试MCP工具调用 ===")
    
    db = SessionLocal()
    try:
        # 创建测试用户（如果不存在）
        user = db.query(User).filter(User.username == "test_user").first()
        if not user:
            user = User(
            username="test_user",
            email="test@example.com",
            full_name="Test User",
            skill_level="intermediate",
            primary_languages=["python", "javascript"]
        )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"创建测试用户: {user.username}")
        
        mcp_service = MCPService(db)
        
        # 创建测试会话
        session = MCPSession("test_session_123", user.id)
        session.status = mcp_service.MCPSessionStatus.ACTIVE
        mcp_service.sessions["test_session_123"] = session
        
        print("\n1. 测试代码分析工具...")
        from app.schemas.mcp import MCPCallToolRequest
        
        analyze_request = MCPCallToolRequest(
            name="analyze_code",
            arguments={
                "code": "def bad_function(x): return x*x*x*x*x if x > 0 else None",
                "language": "python",
                "file_path": "test.py"
            }
        )
        
        analyze_result = await mcp_service.call_tool(analyze_request, "test_session_123")
        if not analyze_result.is_error:
            print("✅ 代码分析工具调用成功")
        else:
            print(f"❌ 代码分析工具调用失败: {analyze_result.content}")
        
        print("\n2. 测试学习任务生成工具...")
        task_request = MCPCallToolRequest(
            name="generate_learning_tasks",
            arguments={
                "skill_areas": ["algorithms", "data_structures"],
                "difficulty_level": "intermediate",
                "count": 2
            }
        )
        
        task_result = await mcp_service.call_tool(task_request, "test_session_123")
        if not task_result.is_error:
            print("✅ 学习任务生成工具调用成功")
        else:
            print(f"❌ 学习任务生成工具调用失败: {task_result.content}")
        
        print("\n3. 测试技能评估工具...")
        assess_request = MCPCallToolRequest(
            name="assess_skills",
            arguments={
                "code_samples": [
                    "def quicksort(arr): return arr if len(arr) <= 1 else quicksort([x for x in arr[1:] if x < arr[0]]) + [arr[0]] + quicksort([x for x in arr[1:] if x >= arr[0]])"
                ],
                "skill_type": "algorithm_implementation",
                "context": "快速排序算法实现"
            }
        )
        
        assess_result = await mcp_service.call_tool(assess_request, "test_session_123")
        if not assess_result.is_error:
            print("✅ 技能评估工具调用成功")
        else:
            print(f"❌ 技能评估工具调用失败: {assess_result.content}")
        
    finally:
        db.close()


async def main():
    """主测试函数"""
    print("开始测试登攀引擎AI集成功能...")
    
    try:
        await test_ai_service()
        await test_mcp_tools()
        print("\n🎉 所有测试完成！")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())