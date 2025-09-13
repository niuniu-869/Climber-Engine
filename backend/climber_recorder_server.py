#!/usr/bin/env python3
"""
Climber-Recorder MCP 服务器
独立的MCP服务器，专门用于记录技术栈
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, '/Users/mac/Desktop/AccountingLLM/Climber Engine/backend')

# 在导入任何其他模块之前，完全禁用所有日志输出到stdout
logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr, format='')
for logger_name in ['asyncio', 'sqlalchemy', 'sqlalchemy.engine', 'app', 'uvicorn']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).disabled = True

from app.services.climber_recorder_service import ClimberRecorderService
from app.schemas.mcp import (
    MCPInitializeRequest, MCPListToolsRequest, MCPCallToolRequest,
    MCPClientInfo, MCPCapabilities
)
# 创建一个专门的数据库会话，禁用所有日志输出
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建静默的数据库引擎
silent_engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False  # 强制禁用echo
)
SilentSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=silent_engine)

class ClimberRecorderMCPServer:
    """Climber-Recorder MCP服务器"""
    
    def __init__(self):
        self.db = SilentSessionLocal()
        self.service = ClimberRecorderService(self.db)
        self.session_id = None
        
    async def handle_initialize(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        try:
            client_info = MCPClientInfo(
                name=request_data.get('params', {}).get('clientInfo', {}).get('name', 'Unknown Client'),
                version=request_data.get('params', {}).get('clientInfo', {}).get('version', '1.0.0')
            )
            
            init_request = MCPInitializeRequest(
                protocol_version=request_data.get('params', {}).get('protocolVersion', '2024-11-05'),
                capabilities=MCPCapabilities(
                    tools={"list_tools": True, "call_tool": True},
                    resources={},
                    prompts={},
                    completion={},
                    sampling={},
                    experimental={}
                ),
                client_info=client_info
            )
            
            response = self.service.initialize_session(init_request)
            self.session_id = list(self.service.sessions.keys())[-1]  # 获取最新创建的会话ID
            
            return {
                "jsonrpc": "2.0",
                "id": request_data.get('id'),
                "result": {
                    "protocolVersion": response.protocol_version,
                    "serverInfo": response.server_info.model_dump(),
                    "capabilities": response.capabilities.model_dump()
                }
            }
        except Exception as e:
            print(f"Initialize error: {e}", file=sys.stderr, flush=True)
            return {
                "jsonrpc": "2.0",
                "id": request_data.get('id'),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_list_tools(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理列出工具请求"""
        try:
            if not self.session_id:
                raise Exception("Session not initialized")
            
            list_request = MCPListToolsRequest(
                cursor=request_data.get('params', {}).get('cursor')
            )
            
            response = self.service.list_tools(list_request, self.session_id)
            
            return {
                "jsonrpc": "2.0",
                "id": request_data.get('id'),
                "result": {
                    "tools": [tool.model_dump(by_alias=True) for tool in response.tools]
                }
            }
        except Exception as e:
            print(f"List tools error: {e}", file=sys.stderr, flush=True)
            return {
                "jsonrpc": "2.0",
                "id": request_data.get('id'),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_call_tool(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理调用工具请求"""
        try:
            if not self.session_id:
                raise Exception("Session not initialized")
            
            params = request_data.get('params', {})
            call_request = MCPCallToolRequest(
                name=params.get('name'),
                arguments=params.get('arguments', {})
            )
            
            response = await self.service.call_tool(call_request, self.session_id)
            
            return {
                "jsonrpc": "2.0",
                "id": request_data.get('id'),
                "result": {
                    "content": response.content,
                    "isError": response.is_error
                }
            }
        except Exception as e:
            print(f"Call tool error: {e}", file=sys.stderr, flush=True)
            return {
                "jsonrpc": "2.0",
                "id": request_data.get('id'),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request_data.get('method')
        
        if method == 'initialize':
            return await self.handle_initialize(request_data)
        elif method == 'tools/list':
            return await self.handle_list_tools(request_data)
        elif method == 'tools/call':
            return await self.handle_call_tool(request_data)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get('id'),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def run(self):
        """运行MCP服务器"""
        # 将日志输出到stderr，避免干扰stdout的JSON响应
        print("Starting Climber-Recorder MCP Server...", file=sys.stderr, flush=True)
        
        try:
            while True:
                # 从stdin读取请求
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                try:
                    request_data = json.loads(line.strip())
                    response = await self.handle_request(request_data)
                    
                    # 输出响应到stdout
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}", file=sys.stderr, flush=True)
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            print("Shutting down Climber-Recorder MCP Server...", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr, flush=True)
        finally:
            self.db.close()


async def main():
    """主函数"""
    server = ClimberRecorderMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())