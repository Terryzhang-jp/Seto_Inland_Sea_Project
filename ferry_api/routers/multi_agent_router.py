"""
多层Agent系统API路由
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging

from services.rag_engine import rag_engine
from models.rag_models import ChatMessage, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multi-agent", tags=["Multi-Agent System"])

@router.post("/chat", response_model=ChatResponse)
async def multi_agent_chat(
    message: str,
    session_id: Optional[str] = None,
    force_mode: Optional[str] = Query(None, description="强制使用指定模式: 'multi_agent' 或 'legacy'")
):
    """
    使用多层Agent系统进行聊天查询
    
    Args:
        message: 用户消息
        session_id: 会话ID（可选）
        force_mode: 强制使用的模式（可选）
    
    Returns:
        聊天响应，包含验证信息和Agent性能数据
    """
    try:
        # 临时切换模式（如果指定）
        original_mode = rag_engine.system_mode
        if force_mode:
            rag_engine.set_system_mode(force_mode)
        
        try:
            # 处理查询
            response = await rag_engine.chat_query(
                message=message,
                session_id=session_id
            )
            
            return response
            
        finally:
            # 恢复原始模式
            if force_mode:
                rag_engine.set_system_mode(original_mode)
        
    except Exception as e:
        logger.error(f"多层Agent聊天失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@router.get("/performance")
async def get_system_performance():
    """
    获取系统性能指标
    
    Returns:
        系统性能数据
    """
    try:
        performance = rag_engine.get_system_performance()
        return {
            "status": "success",
            "data": performance
        }
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取性能指标失败: {str(e)}")

@router.post("/mode")
async def set_system_mode(mode: str):
    """
    设置系统模式
    
    Args:
        mode: 系统模式 ('multi_agent' 或 'legacy')
    
    Returns:
        操作结果
    """
    try:
        if mode not in ['multi_agent', 'legacy']:
            raise HTTPException(status_code=400, detail="无效的模式，必须是 'multi_agent' 或 'legacy'")
        
        rag_engine.set_system_mode(mode)
        
        return {
            "status": "success",
            "message": f"系统模式已切换为: {mode}",
            "current_mode": rag_engine.system_mode
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置系统模式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"设置模式失败: {str(e)}")

@router.get("/mode")
async def get_system_mode():
    """
    获取当前系统模式
    
    Returns:
        当前系统模式
    """
    try:
        return {
            "status": "success",
            "current_mode": rag_engine.system_mode,
            "available_modes": ["multi_agent", "legacy"]
        }
    except Exception as e:
        logger.error(f"获取系统模式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模式失败: {str(e)}")

@router.post("/test")
async def test_multi_agent_system():
    """
    测试多层Agent系统
    
    Returns:
        测试结果
    """
    try:
        test_queries = [
            "高松到直岛的船班时间",
            "从宇野到豊岛需要多少钱",
            "我想带车去犬岛，有什么船班",
            "比较一下去小豆岛的不同路线"
        ]
        
        test_results = []
        
        for query in test_queries:
            logger.info(f"测试查询: {query}")
            
            try:
                # 测试多层Agent系统
                rag_engine.set_system_mode('multi_agent')
                multi_agent_response = await rag_engine.chat_query(query)
                
                # 测试传统系统
                rag_engine.set_system_mode('legacy')
                legacy_response = await rag_engine.chat_query(query)
                
                test_results.append({
                    "query": query,
                    "multi_agent": {
                        "accuracy_rate": multi_agent_response.verification.get("accuracy_rate", 0.0),
                        "response_length": len(multi_agent_response.message),
                        "verified_facts": multi_agent_response.verification.get("verified_facts", 0),
                        "agent_performance": multi_agent_response.verification.get("agent_performance", [])
                    },
                    "legacy": {
                        "response_length": len(legacy_response.message),
                        "verification": legacy_response.verification
                    }
                })
                
            except Exception as e:
                test_results.append({
                    "query": query,
                    "error": str(e)
                })
        
        # 恢复多层Agent模式
        rag_engine.set_system_mode('multi_agent')
        
        return {
            "status": "success",
            "test_results": test_results,
            "summary": {
                "total_tests": len(test_queries),
                "successful_tests": len([r for r in test_results if "error" not in r])
            }
        }
        
    except Exception as e:
        logger.error(f"测试多层Agent系统失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")

@router.get("/health")
async def health_check():
    """
    健康检查
    
    Returns:
        系统健康状态
    """
    try:
        # 检查各个组件
        health_status = {
            "status": "healthy",
            "components": {
                "rag_engine": "healthy",
                "multi_layer_system": "unknown",
                "vector_store": "unknown",
                "gemini_service": "unknown"
            }
        }
        
        # 检查多层Agent系统
        try:
            if hasattr(rag_engine, 'multi_layer_system'):
                performance = rag_engine.multi_layer_system.get_performance_metrics()
                health_status["components"]["multi_layer_system"] = "healthy"
                health_status["multi_agent_metrics"] = performance
            else:
                health_status["components"]["multi_layer_system"] = "not_initialized"
        except Exception as e:
            health_status["components"]["multi_layer_system"] = f"error: {str(e)}"
        
        # 检查向量存储
        try:
            # 简单的搜索测试
            from services.vector_store import vector_store
            test_results = await vector_store.search("测试", n_results=1)
            health_status["components"]["vector_store"] = "healthy"
        except Exception as e:
            health_status["components"]["vector_store"] = f"error: {str(e)}"
        
        # 检查Gemini服务
        try:
            from services.gemini_service import gemini_service
            if gemini_service.model:
                health_status["components"]["gemini_service"] = "healthy"
            else:
                health_status["components"]["gemini_service"] = "not_initialized"
        except Exception as e:
            health_status["components"]["gemini_service"] = f"error: {str(e)}"
        
        # 判断总体状态
        if any("error" in status for status in health_status["components"].values()):
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
