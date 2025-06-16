import os
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class VectorStore:
    """ChromaDB向量数据库服务"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化ChromaDB客户端"""
        try:
            # 确保目录存在
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # 创建持久化客户端
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name="ferry_knowledge",
                metadata={"description": "瀬户内海船班知识库"}
            )
            
            logger.info(f"ChromaDB initialized with {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    async def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文档到向量数据库
        
        Args:
            documents: 文档内容列表
            metadatas: 元数据列表
            ids: 文档ID列表（可选）
            
        Returns:
            文档ID列表
        """
        try:
            # 生成ID（如果未提供）
            if not ids:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # 获取向量表示
            embeddings = await embedding_service.get_embeddings(documents)
            
            # 添加到ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    async def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            filter_metadata: 元数据过滤条件
            
        Returns:
            搜索结果列表
        """
        try:
            # 获取查询向量
            query_embedding = await embedding_service.get_single_embedding(query)
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            # 格式化结果
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            logger.info(f"Found {len(formatted_results)} relevant documents for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {
                "total_documents": 0,
                "collection_name": self.collection_name,
                "error": str(e)
            }

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息（别名方法）"""
        return self.get_collection_stats()
    
    def delete_collection(self):
        """删除集合（用于重置）"""
        try:
            self.client.delete_collection(name="ferry_knowledge")
            logger.info("Collection deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
    
    async def update_document(
        self, 
        doc_id: str, 
        document: str, 
        metadata: Dict[str, Any]
    ):
        """更新文档"""
        try:
            embedding = await embedding_service.get_single_embedding(document)
            
            self.collection.update(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata],
                embeddings=[embedding]
            )
            
            logger.info(f"Updated document {doc_id}")
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise

# 全局实例
vector_store = VectorStore()
