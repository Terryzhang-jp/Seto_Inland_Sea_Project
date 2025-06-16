import uuid
import logging
from typing import List, Dict, Any, Optional
from .vector_store import vector_store
from .gemini_service import gemini_service
from ..models.rag_models import ChatMessage, ChatResponse, TripPlanResponse

logger = logging.getLogger(__name__)

class RAGEngine:
    """RAG查询引擎"""
    
    def __init__(self):
        self.sessions = {}  # 存储会话状态
    
    async def chat_query(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        context_history: Optional[List[ChatMessage]] = None
    ) -> ChatResponse:
        """
        处理聊天查询
        
        Args:
            message: 用户消息
            session_id: 会话ID
            context_history: 上下文历史
            
        Returns:
            聊天响应
        """
        try:
            # 生成或使用现有会话ID
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 获取或创建会话历史
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            
            session_history = self.sessions[session_id]
            if context_history:
                session_history.extend(context_history)
            
            # 1. 检索相关信息
            relevant_docs = await self._retrieve_relevant_info(message)
            
            # 2. 构建上下文
            context = self._build_context(relevant_docs)
            
            # 3. 生成回复
            response_text = await gemini_service.generate_response(
                prompt=message,
                context=context,
                chat_history=session_history
            )
            
            # 4. 生成建议
            suggestions = self._generate_suggestions(message, relevant_docs)
            
            # 5. 更新会话历史
            session_history.append(ChatMessage(role="user", content=message))
            session_history.append(ChatMessage(role="assistant", content=response_text))
            
            # 保持会话历史在合理长度
            if len(session_history) > 20:
                session_history = session_history[-20:]
            
            self.sessions[session_id] = session_history
            
            # 6. 构建响应
            sources = [
                {
                    "type": doc["metadata"].get("type", "unknown"),
                    "content": doc["document"][:200] + "..." if len(doc["document"]) > 200 else doc["document"],
                    "metadata": doc["metadata"]
                }
                for doc in relevant_docs[:3]  # 只返回前3个来源
            ]
            
            return ChatResponse(
                message=response_text,
                sources=sources,
                session_id=session_id,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error in chat query: {str(e)}")
            raise
    
    async def _retrieve_relevant_info(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """检索相关信息"""
        try:
            # 基础检索
            results = await vector_store.search(query, n_results=n_results)
            
            # 可以在这里添加更复杂的检索逻辑
            # 例如：重排序、过滤、多轮检索等
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant info: {str(e)}")
            return []
    
    def _build_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """构建上下文信息"""
        if not relevant_docs:
            return ""
        
        context_parts = []
        for doc in relevant_docs:
            doc_type = doc["metadata"].get("type", "信息")
            content = doc["document"]
            context_parts.append(f"[{doc_type}] {content}")
        
        return "\n\n".join(context_parts)
    
    def _generate_suggestions(self, query: str, relevant_docs: List[Dict[str, Any]]) -> List[str]:
        """生成相关建议"""
        suggestions = []
        
        # 基于查询内容生成建议
        query_lower = query.lower()
        
        if "时间" in query or "几点" in query:
            suggestions.append("查看其他时间段的船班")
            suggestions.append("了解换乘信息")
        
        if "价格" in query or "票价" in query or "费用" in query:
            suggestions.append("比较不同公司的票价")
            suggestions.append("查看儿童票价信息")
        
        if "车" in query or "自行车" in query:
            suggestions.append("查看载运车辆的其他路线")
            suggestions.append("了解载运费用")
        
        if any(island in query for island in ["直島", "豊島", "犬島"]):
            suggestions.append("规划艺术岛屿跳岛行程")
            suggestions.append("了解艺术展览信息")
        
        # 基于检索结果生成建议
        route_docs = [doc for doc in relevant_docs if doc["metadata"].get("type") == "route"]
        if route_docs:
            suggestions.append("查看相关路线的详细信息")
            suggestions.append("比较不同船运公司")
        
        # 限制建议数量
        return suggestions[:4]
    
    async def plan_trip(
        self, 
        departure: str, 
        destinations: List[str], 
        preferences: Dict[str, Any]
    ) -> TripPlanResponse:
        """
        规划行程
        
        Args:
            departure: 出发地
            destinations: 目的地列表
            preferences: 用户偏好
            
        Returns:
            行程规划响应
        """
        try:
            # 1. 检索相关路线信息
            all_locations = [departure] + destinations
            route_queries = []
            
            for i in range(len(all_locations) - 1):
                for j in range(i + 1, len(all_locations)):
                    route_queries.append(f"{all_locations[i]} 到 {all_locations[j]}")
            
            relevant_routes = []
            for query in route_queries:
                routes = await vector_store.search(
                    query, 
                    n_results=3,
                    filter_metadata={"type": "route"}
                )
                relevant_routes.extend(routes)
            
            # 2. 使用Gemini生成行程规划
            trip_plan = await gemini_service.generate_trip_plan(
                departure, destinations, preferences
            )
            
            # 3. 构建响应
            return TripPlanResponse(
                itinerary=[],  # 这里需要解析Gemini的响应
                total_cost="待计算",
                total_duration="待计算",
                recommendations=["建议提前预订", "注意船班时间", "准备好相关证件"]
            )
            
        except Exception as e:
            logger.error(f"Error planning trip: {str(e)}")
            raise
    
    async def get_recommendations(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取个性化推荐
        
        Args:
            preferences: 用户偏好
            
        Returns:
            推荐列表
        """
        try:
            # 基于偏好构建查询
            query_parts = []
            
            if preferences.get("interests"):
                interests = preferences["interests"]
                if "art" in interests:
                    query_parts.append("艺术岛屿 直島 豊島 犬島")
                if "nature" in interests:
                    query_parts.append("自然风光 小豆島 女木島 男木島")
            
            if preferences.get("has_vehicle"):
                query_parts.append("车辆载运")
            
            query = " ".join(query_parts) if query_parts else "热门路线推荐"
            
            # 检索推荐信息
            recommendations = await vector_store.search(
                query, 
                n_results=5,
                filter_metadata={"type": "popular_route"}
            )
            
            return [
                {
                    "route": doc["metadata"],
                    "description": doc["document"],
                    "reason": "基于您的偏好推荐"
                }
                for doc in recommendations
            ]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

# 全局实例
rag_engine = RAGEngine()
