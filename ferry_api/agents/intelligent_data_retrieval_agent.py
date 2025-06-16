"""
智能数据检索Agent - 第3层：根据策略精确检索相关数据
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .state_models import QueryStrategy, RetrievedData

logger = logging.getLogger(__name__)

class IntelligentDataRetrievalAgent:
    """智能数据检索Agent - 根据策略精确检索数据"""
    
    def __init__(self, vector_store, data_processor):
        self.vector_store = vector_store
        self.data_processor = data_processor
        self.agent_name = "IntelligentDataRetrievalAgent"
        
        # 缓存结构化数据
        self._routes_cache = None
        self._ports_cache = None
        self._companies_cache = None
        self._last_cache_update = None
    
    async def execute_strategy(self, strategy: QueryStrategy, context: Dict[str, Any]) -> List[RetrievedData]:
        """执行查询策略"""
        try:
            logger.info(f"[{self.agent_name}] 开始执行策略: {strategy.strategy_name}")
            
            all_results = []
            
            # 按步骤执行策略
            for step in strategy.steps:
                step_results = await self._execute_strategy_step(step, context, strategy)
                all_results.extend(step_results)
                
                # 将步骤结果添加到上下文中，供后续步骤使用
                context[f"step_{step.get('step', 0)}_results"] = step_results
            
            # 去重和排序
            all_results = self._deduplicate_and_sort(all_results)
            
            logger.info(f"[{self.agent_name}] 策略执行完成，检索到 {len(all_results)} 条数据")
            
            return all_results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 策略执行失败: {e}")
            return []
    
    async def _execute_strategy_step(self, step: Dict[str, Any], context: Dict[str, Any], strategy: QueryStrategy) -> List[RetrievedData]:
        """执行单个策略步骤"""
        try:
            action = step.get("action", "")
            data_needed = step.get("data_needed", [])
            search_params = step.get("search_params", {})
            analysis_type = step.get("analysis_type")
            
            logger.info(f"[{self.agent_name}] 执行步骤: {action}")
            
            results = []
            
            # 如果是分析步骤，不需要检索新数据
            if analysis_type:
                return []
            
            # 根据需要的数据类型进行检索
            if "班次时间" in data_needed or "班次时刻表" in data_needed:
                route_results = await self._search_route_schedules(search_params)
                results.extend(route_results)
            
            if "中转信息" in data_needed or "连接信息" in data_needed:
                connection_results = await self._search_connections(search_params)
                results.extend(connection_results)
            
            if "票价" in data_needed or "价格信息" in data_needed:
                price_results = await self._search_prices(search_params)
                results.extend(price_results)
            
            if "港口信息" in data_needed:
                port_results = await self._search_ports(search_params)
                results.extend(port_results)
            
            # 向量搜索作为补充
            if not results or len(results) < 3:
                vector_results = await self._vector_search(action, search_params)
                results.extend(vector_results)
            
            return results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 步骤执行失败: {e}")
            return []
    
    async def _search_route_schedules(self, search_params: Dict[str, Any]) -> List[RetrievedData]:
        """搜索班次时刻表"""
        try:
            await self._load_structured_data()
            
            departure = search_params.get("departure", "").replace("机场", "").replace("港", "")
            destination = search_params.get("destination", "")
            time_filter = search_params.get("time_filter")
            
            results = []
            
            for route in self._routes_cache:
                # 精确匹配出发地和目的地
                if self._location_matches(route.get("departure", ""), departure) and \
                   self._location_matches(route.get("destination", ""), destination):
                    
                    # 时间过滤
                    if time_filter and not self._time_matches(route, time_filter):
                        continue
                    
                    content = self._format_route_content(route)
                    
                    data = RetrievedData(
                        source_type="structured_route",
                        content=content,
                        metadata={
                            "type": "route_schedule",
                            "departure": route.get("departure", ""),
                            "destination": route.get("destination", ""),
                            "company": route.get("company", ""),
                            "departure_time": route.get("departure_time", ""),
                            "arrival_time": route.get("arrival_time", ""),
                            "duration": route.get("duration", ""),
                            "fare": route.get("fare", "")
                        },
                        relevance_score=self._calculate_route_relevance(route, search_params),
                        timestamp=datetime.now().isoformat()
                    )
                    results.append(data)
            
            return results[:5]  # 限制结果数量
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 班次搜索失败: {e}")
            return []
    
    async def _search_connections(self, search_params: Dict[str, Any]) -> List[RetrievedData]:
        """搜索中转连接信息"""
        try:
            await self._load_structured_data()
            
            departure = search_params.get("departure", "")
            destination = search_params.get("destination", "")
            
            results = []
            
            # 查找需要中转的路线
            if "机场" in departure:
                # 机场到港口的连接
                airport_to_port = self._find_airport_connections(departure)
                results.extend(airport_to_port)
            
            # 查找港口间的连接
            port_connections = self._find_port_connections(departure, destination)
            results.extend(port_connections)
            
            return results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 连接搜索失败: {e}")
            return []
    
    async def _search_prices(self, search_params: Dict[str, Any]) -> List[RetrievedData]:
        """搜索价格信息"""
        try:
            await self._load_structured_data()
            
            departure = search_params.get("departure", "")
            destination = search_params.get("destination", "")
            
            results = []
            
            for route in self._routes_cache:
                if self._location_matches(route.get("departure", ""), departure) and \
                   self._location_matches(route.get("destination", ""), destination):
                    
                    if route.get("fare"):
                        content = f"路线: {route.get('departure')} → {route.get('destination')}\n"
                        content += f"票价: {route.get('fare')}\n"
                        content += f"运营公司: {route.get('company', '未知')}"
                        
                        data = RetrievedData(
                            source_type="structured_price",
                            content=content,
                            metadata={
                                "type": "price_info",
                                "fare": route.get("fare", ""),
                                "company": route.get("company", "")
                            },
                            relevance_score=0.9,
                            timestamp=datetime.now().isoformat()
                        )
                        results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 价格搜索失败: {e}")
            return []
    
    async def _search_ports(self, search_params: Dict[str, Any]) -> List[RetrievedData]:
        """搜索港口信息"""
        try:
            await self._load_structured_data()
            
            results = []
            keywords = [search_params.get("departure", ""), search_params.get("destination", "")]
            
            for port in self._ports_cache:
                if any(self._location_matches(port.get("name", ""), keyword) for keyword in keywords if keyword):
                    content = self._format_port_content(port)
                    
                    data = RetrievedData(
                        source_type="structured_port",
                        content=content,
                        metadata={
                            "type": "port_info",
                            "port_name": port.get("name", "")
                        },
                        relevance_score=0.8,
                        timestamp=datetime.now().isoformat()
                    )
                    results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 港口搜索失败: {e}")
            return []
    
    async def _vector_search(self, action: str, search_params: Dict[str, Any]) -> List[RetrievedData]:
        """向量搜索作为补充"""
        try:
            # 构建搜索查询
            search_query = self._build_vector_search_query(action, search_params)
            
            # 执行向量搜索
            vector_results = await self.vector_store.search(search_query, n_results=5)
            
            retrieved_data = []
            for i, result in enumerate(vector_results):
                data = RetrievedData(
                    source_type="vector",
                    content=result.get("document", ""),
                    metadata=result.get("metadata", {}),
                    relevance_score=0.7 - (i * 0.1),  # 向量搜索的相关性稍低
                    timestamp=datetime.now().isoformat()
                )
                retrieved_data.append(data)
            
            return retrieved_data
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 向量搜索失败: {e}")
            return []
    
    def _location_matches(self, location1: str, location2: str) -> bool:
        """检查地点是否匹配"""
        if not location1 or not location2:
            return False
        
        # 移除常见后缀
        loc1 = location1.replace("港", "").replace("机场", "").strip()
        loc2 = location2.replace("港", "").replace("机场", "").strip()
        
        return loc1 in loc2 or loc2 in loc1
    
    def _time_matches(self, route: Dict[str, Any], time_filter: str) -> bool:
        """检查时间是否匹配"""
        if not time_filter:
            return True
        
        # 简单的时间匹配逻辑
        route_time = route.get("departure_time", "")
        if not route_time:
            return True
        
        try:
            # 这里可以实现更复杂的时间匹配逻辑
            return True
        except:
            return True
    
    def _calculate_route_relevance(self, route: Dict[str, Any], search_params: Dict[str, Any]) -> float:
        """计算路线相关性"""
        score = 0.8  # 基础分数
        
        # 如果有精确的时间匹配，提高分数
        if search_params.get("time_filter") and route.get("departure_time"):
            score += 0.1
        
        # 如果有票价信息，提高分数
        if route.get("fare"):
            score += 0.1
        
        return min(score, 1.0)
    
    async def _load_structured_data(self):
        """加载结构化数据"""
        try:
            current_time = datetime.now()
            
            # 如果缓存存在且未过期（5分钟），直接返回
            if (self._last_cache_update and 
                (current_time - self._last_cache_update).seconds < 300 and
                self._routes_cache is not None):
                return
            
            # 加载数据
            self._routes_cache = self.data_processor.load_ferry_routes()
            self._ports_cache = self.data_processor.load_ports()
            self._companies_cache = self.data_processor.load_companies()
            self._last_cache_update = current_time
            
            logger.info(f"[{self.agent_name}] 结构化数据加载完成")
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 数据加载失败: {e}")
            # 使用空列表作为降级
            self._routes_cache = []
            self._ports_cache = []
            self._companies_cache = []
    
    def _format_route_content(self, route: Dict[str, Any]) -> str:
        """格式化路线内容"""
        content = f"路线: {route.get('departure', '')} → {route.get('destination', '')}\n"
        if route.get("departure_time"):
            content += f"出发时间: {route.get('departure_time')}\n"
        if route.get("arrival_time"):
            content += f"到达时间: {route.get('arrival_time')}\n"
        if route.get("duration"):
            content += f"航行时间: {route.get('duration')}\n"
        if route.get("fare"):
            content += f"票价: {route.get('fare')}\n"
        if route.get("company"):
            content += f"运营公司: {route.get('company')}\n"
        
        return content.strip()
    
    def _format_port_content(self, port: Dict[str, Any]) -> str:
        """格式化港口内容"""
        content = f"港口: {port.get('name', '')}\n"
        if port.get("location"):
            content += f"位置: {port.get('location')}\n"
        if port.get("facilities"):
            content += f"设施: {port.get('facilities')}\n"
        
        return content.strip()
    
    def _build_vector_search_query(self, action: str, search_params: Dict[str, Any]) -> str:
        """构建向量搜索查询"""
        query_parts = [action]
        
        if search_params.get("departure"):
            query_parts.append(search_params["departure"])
        if search_params.get("destination"):
            query_parts.append(search_params["destination"])
        
        return " ".join(query_parts)
    
    def _deduplicate_and_sort(self, results: List[RetrievedData]) -> List[RetrievedData]:
        """去重和排序"""
        # 简单的去重逻辑
        seen_content = set()
        unique_results = []
        
        for result in results:
            content_hash = hash(result.content[:100])  # 使用前100个字符作为去重标识
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        # 按相关性排序
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_results
    
    def _find_airport_connections(self, airport: str) -> List[RetrievedData]:
        """查找机场连接"""
        # 这里可以实现机场到港口的连接查询
        # 暂时返回空列表
        return []
    
    def _find_port_connections(self, departure: str, destination: str) -> List[RetrievedData]:
        """查找港口连接"""
        # 这里可以实现港口间的连接查询
        # 暂时返回空列表
        return []
