#!/usr/bin/env python3
"""
自定义异常类
"""

from typing import Any, Dict, Optional


class ClimberEngineException(Exception):
    """登攀引擎基础异常类"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details
        }


class ValidationError(ClimberEngineException):
    """数据验证异常"""
    pass


class NotFoundError(ClimberEngineException):
    """资源未找到异常"""
    pass


class AuthenticationError(ClimberEngineException):
    """认证异常"""
    pass


class AuthorizationError(ClimberEngineException):
    """授权异常"""
    pass


class InvalidOperationError(ClimberEngineException):
    """无效操作异常"""
    pass


class ExternalServiceError(ClimberEngineException):
    """外部服务异常"""
    pass


class MCPError(ClimberEngineException):
    """MCP协议异常"""
    
    def __init__(self, message: str, code: int = -32000, data: Optional[Dict[str, Any]] = None):
        self.mcp_code = code
        self.data = data or {}
        super().__init__(message, str(code), data)
    
    def to_mcp_error(self) -> Dict[str, Any]:
        """转换为MCP错误格式"""
        return {
            "code": self.mcp_code,
            "message": self.message,
            "data": self.data
        }


class LLMServiceError(ExternalServiceError):
    """LLM服务异常"""
    pass


class DatabaseError(ClimberEngineException):
    """数据库异常"""
    pass


class ConfigurationError(ClimberEngineException):
    """配置异常"""
    pass


class UserNotFoundError(NotFoundError):
    """用户未找到异常"""
    pass


class UserAlreadyExistsError(ValidationError):
    """用户已存在异常"""
    pass


class CodingSessionNotFoundError(NotFoundError):
    """编程会话未找到异常"""
    pass


class InvalidOperationError(ValidationError):
    """无效操作异常"""
    pass


class SkillAssessmentNotFoundError(NotFoundError):
    """技能评估未找到异常"""
    pass


class LearningTaskNotFoundError(NotFoundError):
    """学习任务未找到异常"""
    pass


class TechnicalDebtNotFoundError(NotFoundError):
    """技术债务未找到异常"""
    pass