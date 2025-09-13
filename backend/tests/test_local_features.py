#!/usr/bin/env python3
"""
测试本地功能（不依赖外部API）
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.mcp_service import MCPService, MCPSession
from app.models.user import User
from app.schemas.mcp import MCPCallToolRequest


async def test_mcp_service_basic():
    """测试MCP服务基础功能"""
    print("\n=== 测试MCP服务基础功能 ===")
    
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
            print(f"✅ 创建测试用户: {user.username}")
        else:
            print(f"✅ 使用现有测试用户: {user.username}")
        
        mcp_service = MCPService(db)
        
        # 测试会话创建
        print("\n1. 测试MCP会话创建...")
        from app.services.mcp_service import MCPSessionStatus
        session = MCPSession("test_session_456", user.id)
        session.status = MCPSessionStatus.ACTIVE
        mcp_service.sessions["test_session_456"] = session
        print("✅ MCP会话创建成功")
        
        # 测试工具列表
        print("\n2. 测试工具列表获取...")
        from app.schemas.mcp import MCPListToolsRequest
        tools_request = MCPListToolsRequest()
        tools_response = mcp_service.list_tools(tools_request, "test_session_456")
        print(f"✅ 获取到 {len(tools_response.tools)} 个可用工具")
        for tool in tools_response.tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        # 测试资源列表
        print("\n3. 测试资源列表获取...")
        from app.schemas.mcp import MCPListResourcesRequest
        resources_request = MCPListResourcesRequest()
        resources_response = mcp_service.list_resources(resources_request, "test_session_456")
        print(f"✅ 获取到 {len(resources_response.resources)} 个可用资源")
        for resource in resources_response.resources:
            print(f"   - {resource.name}: {resource.description[:50]}...")
        
        # 测试资源读取
        print("\n4. 测试用户档案资源读取...")
        from app.schemas.mcp import MCPReadResourceRequest
        read_request = MCPReadResourceRequest(uri="climber://user/profile")
        read_response = mcp_service.read_resource(read_request, "test_session_456")
        print("✅ 用户档案资源读取成功")
        print(f"   内容长度: {len(read_response.contents[0]['text'])} 字符")
        
        print("\n🎉 MCP服务基础功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


async def test_database_operations():
    """测试数据库操作"""
    print("\n=== 测试数据库操作 ===")
    
    db = SessionLocal()
    try:
        # 测试用户查询
        print("\n1. 测试用户查询...")
        users = db.query(User).all()
        print(f"✅ 数据库中有 {len(users)} 个用户")
        
        # 测试用户创建
        print("\n2. 测试用户创建...")
        test_user_2 = db.query(User).filter(User.username == "test_user_2").first()
        if not test_user_2:
            test_user_2 = User(
                username="test_user_2",
                email="test2@example.com",
                full_name="Test User 2",
                skill_level="beginner"
            )
            db.add(test_user_2)
            db.commit()
            db.refresh(test_user_2)
            print(f"✅ 创建新用户: {test_user_2.username}")
        else:
            print(f"✅ 用户已存在: {test_user_2.username}")
        
        # 测试编程会话创建
        print("\n3. 测试编程会话创建...")
        from app.models.coding_session import CodingSession
        
        session = CodingSession(
            user_id=test_user_2.id,
            title="测试编程会话",
            description="这是一个测试会话",
            session_type="practice",
            primary_language="python"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        print(f"✅ 创建编程会话: {session.title}")
        
        # 测试代码记录创建
        print("\n4. 测试代码记录创建...")
        from app.models.code_record import CodeRecord
        
        code_record = CodeRecord(
            coding_session_id=session.id,
            file_path="/test/example.py",
            file_name="example.py",
            file_extension=".py",
            language="python",
            change_type="create",
            code_after="def hello(): print('Hello, World!')",
            lines_added=1
        )
        db.add(code_record)
        db.commit()
        db.refresh(code_record)
        print(f"✅ 创建代码记录: {code_record.file_name}")
        
        print("\n🎉 数据库操作测试完成！")
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


async def main():
    """主测试函数"""
    print("开始测试登攀引擎本地功能...")
    
    try:
        await test_database_operations()
        await test_mcp_service_basic()
        print("\n🎉 所有本地功能测试完成！")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())