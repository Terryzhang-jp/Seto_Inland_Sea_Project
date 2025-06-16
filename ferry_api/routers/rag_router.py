from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.rag_models import (
    ChatQuery, ChatResponse, TripPlanRequest, TripPlanResponse,
    UserPreferences, RecommendationResponse
)
from services.rag_engine import rag_engine
from services.data_processor import data_processor
from services.vector_store import vector_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

@router.post("/chat", response_model=ChatResponse)
async def chat_query(query: ChatQuery):
    """
    智能聊天查询
    
    处理用户的自然语言查询，返回智能回复
    """
    try:
        response = await rag_engine.chat_query(
            message=query.message,
            session_id=query.session_id,
            context_history=query.context
        )
        return response
        
    except Exception as e:
        logger.error(f"Chat query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"聊天查询失败: {str(e)}")

@router.post("/plan", response_model=TripPlanResponse)
async def plan_trip(request: TripPlanRequest):
    """
    行程规划
    
    基于用户需求生成详细的跳岛行程规划
    """
    try:
        response = await rag_engine.plan_trip(
            departure=request.departure,
            destinations=request.destinations,
            preferences=request.preferences
        )
        return response
        
    except Exception as e:
        logger.error(f"Trip planning error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"行程规划失败: {str(e)}")

@router.post("/recommendations")
async def get_recommendations(preferences: UserPreferences):
    """
    个性化推荐
    
    基于用户偏好推荐最适合的路线
    """
    try:
        recommendations = await rag_engine.get_recommendations(preferences.dict())
        
        return {
            "success": True,
            "data": recommendations,
            "message": "推荐生成成功"
        }
        
    except Exception as e:
        logger.error(f"Recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"推荐生成失败: {str(e)}")

@router.post("/initialize")
async def initialize_knowledge_base(background_tasks: BackgroundTasks):
    """
    初始化知识库
    
    处理并存储所有数据到向量数据库
    """
    try:
        # 在后台任务中处理数据
        background_tasks.add_task(data_processor.process_and_store_all_data)
        
        return {
            "success": True,
            "message": "知识库初始化已开始，请稍后查看状态"
        }
        
    except Exception as e:
        logger.error(f"Knowledge base initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"知识库初始化失败: {str(e)}")

@router.get("/status")
async def get_rag_status():
    """
    获取RAG系统状态
    
    返回向量数据库和各服务的状态信息
    """
    try:
        # 获取向量数据库状态
        vector_stats = vector_store.get_collection_stats()
        
        # 检查各服务状态
        from services.embedding_service import embedding_service
        from services.gemini_service import gemini_service
        
        status = {
            "vector_store": {
                "status": "active",
                "stats": vector_stats
            },
            "embedding_service": {
                "status": "active" if embedding_service.api_key else "not_configured",
                "model": embedding_service.model_name
            },
            "gemini_service": {
                "status": "active" if gemini_service.api_key else "not_configured",
                "model": gemini_service.model_name
            }
        }
        
        return {
            "success": True,
            "data": status,
            "message": "状态获取成功"
        }
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"状态检查失败: {str(e)}")

@router.delete("/reset")
async def reset_knowledge_base():
    """
    重置知识库
    
    清空向量数据库并重新初始化
    """
    try:
        # 删除现有集合
        vector_store.delete_collection()
        
        # 重新初始化
        vector_store._initialize_client()
        
        return {
            "success": True,
            "message": "知识库已重置，请重新初始化数据"
        }
        
    except Exception as e:
        logger.error(f"Knowledge base reset error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"知识库重置失败: {str(e)}")

@router.get("/search")
async def search_knowledge_base(
    query: str,
    limit: int = 5,
    doc_type: str = None
):
    """
    搜索知识库
    
    直接搜索向量数据库中的内容
    """
    try:
        # 构建过滤条件
        filter_metadata = None
        if doc_type:
            filter_metadata = {"type": doc_type}
        
        # 执行搜索
        results = await vector_store.search(
            query=query,
            n_results=limit,
            filter_metadata=filter_metadata
        )
        
        return {
            "success": True,
            "data": results,
            "message": f"找到 {len(results)} 条相关结果"
        }
        
    except Exception as e:
        logger.error(f"Knowledge base search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"知识库搜索失败: {str(e)}")

@router.get("/health")
async def rag_health_check():
    """RAG系统健康检查"""
    try:
        # 检查各组件状态
        health_status = {
            "rag_engine": "healthy",
            "vector_store": "healthy" if vector_store.client else "unhealthy",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return {
            "success": True,
            "data": health_status,
            "message": "RAG系统运行正常"
        }
        
    except Exception as e:
        logger.error(f"RAG health check error: {str(e)}")
        return {
            "success": False,
            "message": f"RAG系统健康检查失败: {str(e)}"
        }
