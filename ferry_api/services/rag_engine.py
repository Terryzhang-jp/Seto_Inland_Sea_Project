import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from services.vector_store import vector_store
from services.gemini_service import gemini_service
from services.response_verifier import response_verifier
from services.data_processor import data_processor
from models.rag_models import ChatMessage, ChatResponse, TripPlanResponse
from agents.multi_layer_agent_system import MultiLayerAgentSystem

logger = logging.getLogger(__name__)

class RAGEngine:
    """RAG查询引擎"""
    
    def __init__(self):
        self.sessions = {}  # 存储会话状态

        # 初始化多层Agent系统
        self.multi_layer_system = MultiLayerAgentSystem(
            llm=gemini_service.model,
            vector_store=vector_store,
            data_processor=data_processor
        )

        # 系统模式：'legacy' 或 'multi_agent'
        self.system_mode = 'multi_agent'  # 默认使用多层Agent系统
    
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

            # 根据系统模式选择处理方式
            if self.system_mode == 'multi_agent':
                return await self._process_with_multi_agent(message, session_id, context_history)
            else:
                return await self._process_with_legacy(message, session_id, context_history)
            
        except Exception as e:
            logger.error(f"Error in chat query: {str(e)}")
            raise

    async def _process_with_multi_agent(self, message: str, session_id: str, context_history: Optional[List[ChatMessage]] = None) -> ChatResponse:
        """使用多层Agent系统处理查询"""
        try:
            logger.info(f"使用多层Agent系统处理查询: {message}")

            # 使用多层Agent系统处理查询
            agent_result = await self.multi_layer_system.process_query(message, session_id)

            # 更新会话历史
            if session_id not in self.sessions:
                self.sessions[session_id] = []

            session_history = self.sessions[session_id]
            if context_history:
                session_history.extend(context_history)

            session_history.append(ChatMessage(role="user", content=message))
            session_history.append(ChatMessage(role="assistant", content=agent_result["message"]))

            # 保持会话历史在合理长度
            if len(session_history) > 20:
                session_history = session_history[-20:]

            self.sessions[session_id] = session_history

            # 生成建议（基于传统方法）
            suggestions = self._generate_suggestions_from_agent_result(message, agent_result)

            # 构建来源信息
            sources = self._build_sources_from_agent_result(agent_result)

            # 构建验证结果
            verification_result = {
                "accuracy_rate": agent_result.get("accuracy_rate", 0.0),
                "verified_facts": agent_result.get("response_metadata", {}).get("verified_facts_count", 0),
                "total_facts": agent_result.get("response_metadata", {}).get("total_facts_count", 0),
                "verification_summary": agent_result.get("response_metadata", {}).get("verification_summary", ""),
                "agent_performance": agent_result.get("agent_performance", [])
            }

            return ChatResponse(
                message=agent_result["message"],
                sources=sources,
                session_id=session_id,
                suggestions=suggestions,
                verification=verification_result
            )

        except Exception as e:
            logger.error(f"多层Agent处理失败: {str(e)}")
            # 降级到传统方法
            logger.info("降级到传统RAG方法")
            return await self._process_with_legacy(message, session_id, context_history)

    async def _process_with_legacy(self, message: str, session_id: str, context_history: Optional[List[ChatMessage]] = None) -> ChatResponse:
        """使用传统RAG方法处理查询"""
        try:
            logger.info(f"使用传统RAG方法处理查询: {message}")

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

            # 4. 验证AI回复的准确性
            verification_result = response_verifier.verify_response(response_text)
            verification_message = response_verifier.format_verification_message(verification_result)

            # 将验证信息添加到回复中
            final_response = response_text + verification_message

            # 5. 生成建议
            suggestions = self._generate_suggestions(message, relevant_docs)

            # 6. 更新会话历史
            session_history.append(ChatMessage(role="user", content=message))
            session_history.append(ChatMessage(role="assistant", content=final_response))

            # 保持会话历史在合理长度
            if len(session_history) > 20:
                session_history = session_history[-20:]

            self.sessions[session_id] = session_history

            # 7. 构建响应
            sources = [
                {
                    "type": doc["metadata"].get("type", "unknown"),
                    "content": doc["document"][:200] + "..." if len(doc["document"]) > 200 else doc["document"],
                    "metadata": doc["metadata"]
                }
                for doc in relevant_docs[:3]  # 只返回前3个来源
            ]

            return ChatResponse(
                message=final_response,
                sources=sources,
                session_id=session_id,
                suggestions=suggestions,
                verification=verification_result  # 添加验证结果
            )

        except Exception as e:
            logger.error(f"传统RAG处理失败: {str(e)}")
            raise

    def _generate_suggestions_from_agent_result(self, query: str, agent_result: Dict[str, Any]) -> List[str]:
        """基于Agent结果生成建议"""
        suggestions = []

        # 基于准确率生成建议
        accuracy_rate = agent_result.get("accuracy_rate", 0.0)
        if accuracy_rate < 0.8:
            suggestions.append("建议查询官方网站获取最新信息")

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

        # 基于Agent性能生成建议
        agent_performance = agent_result.get("agent_performance", [])
        if any(not perf.get("success", True) for perf in agent_performance):
            suggestions.append("尝试重新表述您的问题")

        return suggestions[:4]

    def _build_sources_from_agent_result(self, agent_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于Agent结果构建来源信息"""
        sources = []

        # 从Agent性能中提取来源信息
        agent_performance = agent_result.get("agent_performance", [])

        for perf in agent_performance:
            if perf.get("agent") == "DataRetrievalAgent" and perf.get("success"):
                sources.append({
                    "type": "multi_agent_retrieval",
                    "content": f"多层Agent系统检索到 {perf.get('response_data', {}).get('retrieved_count', 0)} 条相关数据",
                    "metadata": {
                        "agent": perf.get("agent"),
                        "execution_time": perf.get("execution_time", 0.0)
                    }
                })

        # 添加验证信息作为来源
        verification_summary = agent_result.get("response_metadata", {}).get("verification_summary", "")
        if verification_summary:
            sources.append({
                "type": "verification_result",
                "content": verification_summary,
                "metadata": {
                    "accuracy_rate": agent_result.get("accuracy_rate", 0.0),
                    "verified_facts": agent_result.get("response_metadata", {}).get("verified_facts_count", 0)
                }
            })

        return sources[:3]  # 限制来源数量

    def set_system_mode(self, mode: str):
        """设置系统模式"""
        if mode in ['legacy', 'multi_agent']:
            self.system_mode = mode
            logger.info(f"系统模式已切换为: {mode}")
        else:
            logger.warning(f"无效的系统模式: {mode}")

    def get_system_performance(self) -> Dict[str, Any]:
        """获取系统性能指标"""
        if hasattr(self, 'multi_layer_system'):
            return {
                "system_mode": self.system_mode,
                "multi_agent_performance": self.multi_layer_system.get_performance_metrics(),
                "active_sessions": len(self.sessions)
            }
        else:
            return {
                "system_mode": self.system_mode,
                "active_sessions": len(self.sessions)
            }
    
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
