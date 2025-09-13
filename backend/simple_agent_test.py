#!/usr/bin/env python3
"""
简化的Agent测试脚本
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.tech_stack_summary_agent import TechStackSummaryAgent
from app.services.coding_tutor_agent import CodingTutorAgent
from app.services.ai_service import AIService
from app.models.user import User


async def test_ai_service_deepseek():
    """测试AI服务DeepSeek连接"""
    print("\n=== 测试AI服务DeepSeek连接 ===")
    
    try:
        db = SessionLocal()
        ai_service = AIService(db)
        
        # 检查DeepSeek客户端
        if 'deepseek' in ai_service.clients:
            print("✅ DeepSeek客户端已初始化")
            
            # 测试简单的LLM调用
            messages = [
                {"role": "system", "content": "你是一个编程助手。"},
                {"role": "user", "content": "请简单介绍Python的优势，用一句话回答。"}
            ]
            
            result = await ai_service.call_llm(
                messages=messages,
                model_provider="deepseek",
                model_name="deepseek-chat",
                max_tokens=100
            )
            
            if result.get('success'):
                print("✅ DeepSeek API调用成功")
                print(f"   响应内容: {result.get('content', '')[:100]}...")
                print(f"   使用模型: {result.get('model', 'N/A')}")
                print(f"   Token使用: {result.get('usage', {})}")
            else:
                print(f"❌ DeepSeek API调用失败: {result.get('error', 'Unknown error')}")
        else:
            print("❌ DeepSeek客户端未初始化")
            print(f"   可用客户端: {list(ai_service.clients.keys())}")
            
        db.close()
        
    except Exception as e:
        print(f"❌ AI服务测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_tech_stack_agent():
    """测试技术栈总结Agent"""
    print("\n=== 测试技术栈总结Agent ===")
    
    try:
        agent = TechStackSummaryAgent()
        print(f"✅ Agent初始化成功")
        print(f"   启用状态: {'是' if agent.is_enabled() else '否'}")
        print(f"   应该运行分析: {'是' if agent.should_run_analysis() else '否'}")
        
        # 获取状态
        status = agent.get_analysis_status()
        print(f"   配置信息: {status.get('config', {})}")
        
    except Exception as e:
        print(f"❌ 技术栈总结Agent测试失败: {str(e)}")


def test_coding_tutor_agent():
    """测试编程教学Agent"""
    print("\n=== 测试编程教学Agent ===")
    
    try:
        agent = CodingTutorAgent()
        print(f"✅ Agent初始化成功")
        print(f"   启用状态: {'是' if agent.is_enabled() else '否'}")
        
        # 获取状态
        status = agent.get_agent_status()
        print(f"   支持的技术栈数: {len(status.get('supported_technologies', []))}")
        print(f"   支持的内容类型: {status.get('config', {}).get('supported_content_types', [])}")
        
    except Exception as e:
        print(f"❌ 编程教学Agent测试失败: {str(e)}")


def test_database_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    try:
        db = SessionLocal()
        
        # 测试查询用户
        user_count = db.query(User).count()
        print(f"✅ 数据库连接成功")
        print(f"   用户总数: {user_count}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")


async def main():
    """主测试函数"""
    print("🚀 开始简化Agent测试")
    print("=" * 40)
    
    # 检查环境变量
    print("\n=== 环境变量检查 ===")
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    deepseek_url = os.getenv('DEEPSEEK_BASE_URL')
    
    if deepseek_key:
        print(f"✅ DeepSeek API Key: {deepseek_key[:10]}...{deepseek_key[-4:]}")
    else:
        print("❌ DeepSeek API Key未找到")
        
    if deepseek_url:
        print(f"✅ DeepSeek Base URL: {deepseek_url}")
    else:
        print("❌ DeepSeek Base URL未找到")
    
    # 运行测试
    test_database_connection()
    test_tech_stack_agent()
    test_coding_tutor_agent()
    await test_ai_service_deepseek()
    
    print("\n" + "=" * 40)
    print("🎉 简化测试完成！")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())