#!/usr/bin/env python3
"""
MCP (Model Context Protocol) 相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class MCPMessage(BaseModel):
    """MCP 消息基础模式"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class MCPError(BaseModel):
    """MCP 错误模式"""
    code: int
    message: str
    data: Optional[Any] = None


class MCPCapabilities(BaseModel):
    """MCP 能力模式"""
    experimental: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    tools: Optional[Dict[str, Any]] = None
    sampling: Optional[Dict[str, Any]] = None


class MCPClientInfo(BaseModel):
    """MCP 客户端信息模式"""
    name: str
    version: str


class MCPServerInfo(BaseModel):
    """MCP 服务器信息模式"""
    name: str = "Climber Engine MCP Server"
    version: str = "1.0.0"
    protocol_version: str = "2024-11-05"


class MCPInitializeRequest(BaseModel):
    """MCP 初始化请求模式"""
    protocol_version: str
    capabilities: MCPCapabilities
    client_info: MCPClientInfo


class MCPInitializeResponse(BaseModel):
    """MCP 初始化响应模式"""
    protocol_version: str
    capabilities: MCPCapabilities
    server_info: MCPServerInfo
    instructions: Optional[str] = None


class MCPTool(BaseModel):
    """MCP 工具模式"""
    name: str
    description: str
    input_schema: Dict[str, Any]  # JSON Schema


class MCPToolCall(BaseModel):
    """MCP 工具调用模式"""
    name: str
    arguments: Dict[str, Any]


class MCPCallToolRequest(BaseModel):
    """MCP 调用工具请求模式"""
    name: str
    arguments: Dict[str, Any]


class MCPCallToolResponse(BaseModel):
    """MCP 调用工具响应模式"""
    content: List[Dict[str, Any]]
    is_error: bool = False


class MCPToolResult(BaseModel):
    """MCP 工具结果模式"""
    content: List[Dict[str, Any]]
    is_error: bool = False


class MCPResource(BaseModel):
    """MCP 资源模式"""
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None


class MCPResourceRequest(BaseModel):
    """MCP 资源请求模式"""
    uri: str


class MCPReadResourceRequest(BaseModel):
    """MCP 读取资源请求模式"""
    uri: str


class MCPReadResourceResponse(BaseModel):
    """MCP 读取资源响应模式"""
    contents: List[Dict[str, Any]]


class MCPResourceResponse(BaseModel):
    """MCP 资源响应模式"""
    contents: List[Dict[str, Any]]


class MCPPrompt(BaseModel):
    """MCP 提示模式"""
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None


class MCPGetPromptRequest(BaseModel):
    """MCP 获取提示请求模式"""
    name: str
    arguments: Optional[Dict[str, Any]] = None


class MCPGetPromptResponse(BaseModel):
    """MCP 获取提示响应模式"""
    description: Optional[str] = None
    messages: List[Dict[str, Any]]


class MCPPromptMessage(BaseModel):
    """MCP 提示消息模式"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: Union[str, List[Dict[str, Any]]]


class MCPPromptResponse(BaseModel):
    """MCP 提示响应模式"""
    description: Optional[str] = None
    messages: List[MCPPromptMessage]


class MCPSamplingRequest(BaseModel):
    """MCP 采样请求模式"""
    messages: List[MCPPromptMessage]
    model_preferences: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    include_context: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1)
    stop_sequences: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class MCPSamplingResponse(BaseModel):
    """MCP 采样响应模式"""
    role: str = "assistant"
    content: Union[str, List[Dict[str, Any]]]
    model: Optional[str] = None
    stop_reason: Optional[str] = None


class MCPCompleteRequest(BaseModel):
    """MCP 完成请求模式"""
    ref: str
    argument: Dict[str, Any]


class MCPCompleteResponse(BaseModel):
    """MCP 完成响应模式"""
    completion: Dict[str, Any]


class MCPRequest(BaseModel):
    """MCP 通用请求模式"""
    method: str
    params: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """MCP 通用响应模式"""
    result: Any
    metadata: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None


class MCPSession(BaseModel):
    """MCP 会话模式"""
    session_id: str
    client_info: MCPClientInfo
    capabilities: MCPCapabilities
    status: str = Field("active", pattern="^(active|inactive|closed)$")
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    error_count: int = 0


class MCPSessionInfo(BaseModel):
    """MCP 会话信息模式"""
    session_id: str
    status: str
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    error_count: int = 0


class MCPNotification(BaseModel):
    """MCP 通知模式"""
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPLogEntry(BaseModel):
    """MCP 日志条目模式"""
    level: str = Field(..., pattern="^(debug|info|notice|warning|error|critical|alert|emergency)$")
    data: Any
    logger: Optional[str] = None


class MCPProgress(BaseModel):
    """MCP 进度模式"""
    progress_token: Union[str, int]
    progress: float = Field(..., ge=0, le=1)
    total: Optional[int] = None


class MCPListResourcesRequest(BaseModel):
    """MCP 列出资源请求模式"""
    cursor: Optional[str] = None


class MCPListResourcesResponse(BaseModel):
    """MCP 列出资源响应模式"""
    resources: List[MCPResource]
    next_cursor: Optional[str] = None


class MCPListToolsRequest(BaseModel):
    """MCP 列出工具请求模式"""
    cursor: Optional[str] = None


class MCPListToolsResponse(BaseModel):
    """MCP 列出工具响应模式"""
    tools: List[MCPTool]
    next_cursor: Optional[str] = None


class MCPListPromptsRequest(BaseModel):
    """MCP 列出提示请求模式"""
    cursor: Optional[str] = None


class MCPListPromptsResponse(BaseModel):
    """MCP 列出提示响应模式"""
    prompts: List[MCPPrompt]
    next_cursor: Optional[str] = None


class MCPHealthCheck(BaseModel):
    """MCP 健康检查模式"""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    timestamp: datetime
    version: str
    uptime: int  # 运行时间（秒）
    active_sessions: int
    total_requests: int
    error_rate: float
    response_time_avg: float  # 平均响应时间（毫秒）
    memory_usage: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, str]] = None  # 依赖服务状态


class MCPMetrics(BaseModel):
    """MCP 指标模式"""
    requests_total: int
    requests_per_second: float
    errors_total: int
    error_rate: float
    response_time_percentiles: Dict[str, float]  # 响应时间百分位数
    active_connections: int
    memory_usage_bytes: int
    cpu_usage_percent: float
    uptime_seconds: int
    tool_usage_stats: Dict[str, int]  # 工具使用统计
    resource_access_stats: Dict[str, int]  # 资源访问统计