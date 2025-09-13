#!/usr/bin/env python3
"""
AI 模型客户端工具
"""

from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AIClient:
    """AI 模型客户端"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._init_clients()
    
    def _init_clients(self):
        """初始化 AI 客户端"""
        try:
            if settings.openai_api_key:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI 客户端初始化成功")
        except ImportError:
            logger.warning("OpenAI 库未安装")
        except Exception as e:
            logger.error(f"OpenAI 客户端初始化失败: {e}")
        
        try:
            if settings.anthropic_api_key:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Anthropic 客户端初始化成功")
        except ImportError:
            logger.warning("Anthropic 库未安装")
        except Exception as e:
            logger.error(f"Anthropic 客户端初始化失败: {e}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Optional[str]:
        """聊天完成"""
        try:
            if model.startswith("gpt") and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                return response.choices[0].message.content
            
            elif model.startswith("claude") and self.anthropic_client:
                # 转换消息格式
                anthropic_messages = []
                system_message = None
                
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        anthropic_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                response = self.anthropic_client.messages.create(
                    model=model,
                    messages=anthropic_messages,
                    system=system_message,
                    temperature=temperature,
                    max_tokens=max_tokens or 1000,
                    **kwargs
                )
                return response.content[0].text
            
            else:
                logger.error(f"不支持的模型或客户端未初始化: {model}")
                return None
        
        except Exception as e:
            logger.error(f"AI 聊天完成失败: {e}")
            return None
    
    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> Optional[List[float]]:
        """生成文本嵌入"""
        try:
            if self.openai_client:
                response = self.openai_client.embeddings.create(
                    model=model,
                    input=text
                )
                return response.data[0].embedding
            else:
                logger.error("OpenAI 客户端未初始化")
                return None
        
        except Exception as e:
            logger.error(f"生成嵌入失败: {e}")
            return None
    
    def is_available(self, provider: str = "openai") -> bool:
        """检查 AI 服务是否可用"""
        if provider == "openai":
            return self.openai_client is not None
        elif provider == "anthropic":
            return self.anthropic_client is not None
        else:
            return False