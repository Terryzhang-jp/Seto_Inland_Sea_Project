import os
import asyncio
from typing import List, Dict, Any
import logging
from dashscope import TextEmbedding
import dashscope

logger = logging.getLogger(__name__)

class EmbeddingService:
    """通义千问 Embedding 3.0 服务"""
    
    def __init__(self):
        # 从环境变量获取API密钥
        self.api_key = os.getenv("QWEN_API_KEY")
        if not self.api_key:
            logger.warning("QWEN_API_KEY not found in environment variables")
        else:
            dashscope.api_key = self.api_key
        
        self.model_name = "text-embedding-v3"
        self.max_batch_size = 10  # 通义千问API的批处理限制
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        获取文本的向量表示
        
        Args:
            texts: 要向量化的文本列表
            
        Returns:
            向量列表
        """
        if not self.api_key:
            logger.error("QWEN_API_KEY not configured")
            raise ValueError("QWEN_API_KEY not configured")
        
        try:
            # 分批处理大量文本
            all_embeddings = []
            
            for i in range(0, len(texts), self.max_batch_size):
                batch = texts[i:i + self.max_batch_size]
                
                # 调用通义千问API
                response = await asyncio.to_thread(
                    TextEmbedding.call,
                    model=self.model_name,
                    input=batch,
                    dimension=1024  # 指定向量维度
                )
                
                if response.status_code == 200:
                    embeddings = response.output['embeddings']
                    # 提取embedding向量
                    batch_embeddings = [item['embedding'] for item in embeddings]
                    all_embeddings.extend(batch_embeddings)
                else:
                    logger.error(f"Embedding API error: {response.message}")
                    raise Exception(f"Embedding API error: {response.message}")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            raise
    
    async def get_single_embedding(self, text: str) -> List[float]:
        """
        获取单个文本的向量表示
        
        Args:
            text: 要向量化的文本
            
        Returns:
            向量
        """
        embeddings = await self.get_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def get_embedding_dimension(self) -> int:
        """获取向量维度"""
        return 1024  # text-embedding-v3 的向量维度

# 全局实例
embedding_service = EmbeddingService()
