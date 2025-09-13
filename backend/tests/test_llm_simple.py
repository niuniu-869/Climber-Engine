#!/usr/bin/env python3
"""
简单的LLM测试 - 测试AI服务基础功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.ai_service import AIService


async def test_ai_service_simple():
    """简单测试AI服务"""
    print("\n=== 简单AI服务测试 ===")
    
    db = SessionLocal()
    try:
        ai_service = AIService(db)
        
        # 检查可用模型
        print("\n1. 检查可用模型...")
        available_models = ai_service.get_available_models()
        print(f"可用提供商: {list(available_models.keys())}")
        
        for provider, models in available_models.items():
            print(f"   {provider}: {models}")
        
        # 测试简单的LLM调用
        if available_models:
            provider = list(available_models.keys())[0]
            model = available_models[provider][0]
            
            print(f"\n2. 测试 {provider}/{model} 调用...")
            
            simple_messages = [
                {"role": "user", "content": "请简单回复'测试成功'"}
            ]
            
            try:
                result = await ai_service.call_llm(
                    messages=simple_messages,
                    model_provider=provider,
                    model_name=model,
                    max_tokens=50,
                    temperature=0.1
                )
                
                if result["success"]:
                    print("✅ LLM调用成功")
                    print(f"   响应: {result['content'][:100]}...")
                    print(f"   Token使用: {result['usage']}")
                else:
                    print(f"❌ LLM调用失败: {result['error']}")
            
            except Exception as e:
                print(f"❌ LLM调用异常: {str(e)}")
        else:
            print("❌ 没有可用的LLM提供商")
        
    finally:
        db.close()


async def test_ai_health_check():
    """测试AI服务健康检查"""
    print("\n=== AI服务健康检查 ===")
    
    db = SessionLocal()
    try:
        ai_service = AIService(db)
        
        print("\n检查AI服务健康状态...")
        health = await ai_service.health_check()
        
        print(f"整体状态: {health['status']}")
        print(f"检查时间: {health['timestamp']}")
        
        for provider, status in health['providers'].items():
            if status['status'] == 'healthy':
                print(f"✅ {provider}: 健康")
            else:
                print(f"❌ {provider}: {status['error']}")
        
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
    finally:
        db.close()


async def main():
    """主测试函数"""
    print("开始简单LLM功能测试...")
    
    try:
        await test_ai_service_simple()
        await test_ai_health_check()
        print("\n🎉 LLM功能测试完成！")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())