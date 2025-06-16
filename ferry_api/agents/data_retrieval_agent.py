"""
数据检索Agent - 第3层执行层：从数据库检索相关信息
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from .state_models import RetrievedData, TaskPlan

logger = logging.getLogger(__name__)

class DataRetrievalAgent:
    """数据检索Agent"""
    
    def __init__(self, vector_store, data_processor):
        self.vector_store = vector_store
        self.data_processor = data_processor
        self.agent_name = "DataRetrievalAgent"
        
        # 缓存已加载的数据
        self._routes_cache = None
        self._ports_cache = None
        self._companies_cache = None
    
    async def retrieve_data(self, task: TaskPlan, query_context: Dict[str, Any]) -> List[RetrievedData]:
        """检索数据"""
        try:
            logger.info(f"[{self.agent_name}] 开始执行数据检索任务: {task.task_id}")
            
            results = []
            
            # 1. 向量检索
            vector_results = await self._vector_search(task, query_context)
            results.extend(vector_results)
            
            # 2. 结构化数据检索
            structured_results = await self._structured_search(task, query_context)
            results.extend(structured_results)
            
            # 3. 去重和排序
            results = self._deduplicate_and_sort(results)
            
            logger.info(f"[{self.agent_name}] 数据检索完成，找到 {len(results)} 条结果")
            
            return results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 数据检索失败: {e}")
            return []
    
    async def _vector_search(self, task: TaskPlan, query_context: Dict[str, Any]) -> List[RetrievedData]:
        """向量搜索"""
        try:
            # 构建搜索查询
            search_query = self._build_search_query(task, query_context)
            
            # 执行向量搜索
            vector_results = await self.vector_store.search(search_query, n_results=10)
            
            retrieved_data = []
            for i, result in enumerate(vector_results):
                data = RetrievedData(
                    source_type="vector",
                    content=result.get("document", ""),
                    metadata=result.get("metadata", {}),
                    relevance_score=1.0 - (i * 0.1),  # 简单的相关性评分
                    timestamp=datetime.now().isoformat()
                )
                retrieved_data.append(data)
            
            return retrieved_data
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 向量搜索失败: {e}")
            return []
    
    async def _structured_search(self, task: TaskPlan, query_context: Dict[str, Any]) -> List[RetrievedData]:
        """结构化数据搜索"""
        try:
            # 加载结构化数据
            await self._load_structured_data()
            
            retrieved_data = []
            
            # 搜索船班路线
            route_results = self._search_routes(task, query_context)
            retrieved_data.extend(route_results)
            
            # 搜索港口信息
            port_results = self._search_ports(task, query_context)
            retrieved_data.extend(port_results)
            
            # 搜索公司信息
            company_results = self._search_companies(task, query_context)
            retrieved_data.extend(company_results)
            
            return retrieved_data
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 结构化搜索失败: {e}")
            return []
    
    async def _load_structured_data(self):
        """加载结构化数据到缓存"""
        if self._routes_cache is None:
            self._routes_cache = self.data_processor.load_ferry_routes()
            self._ports_cache = self.data_processor.load_ports()
            self._companies_cache = self.data_processor.load_companies()
    
    def _search_routes(self, task: TaskPlan, query_context: Dict[str, Any]) -> List[RetrievedData]:
        """搜索船班路线"""
        results = []
        
        # 提取搜索关键词
        keywords = self._extract_keywords(task, query_context)
        
        for route in self._routes_cache:
            # 检查是否匹配
            if self._route_matches_keywords(route, keywords):
                content = self._format_route_content(route)
                
                data = RetrievedData(
                    source_type="structured_route",
                    content=content,
                    metadata={
                        "type": "ferry_route",
                        "route_id": route.get("id", ""),
                        "company": route.get("company", ""),
                        "departure_port": route.get("departure_port", ""),
                        "arrival_port": route.get("arrival_port", "")
                    },
                    relevance_score=self._calculate_route_relevance(route, keywords),
                    timestamp=datetime.now().isoformat()
                )
                results.append(data)
        
        return results[:5]  # 限制结果数量
    
    def _search_ports(self, task: TaskPlan, query_context: Dict[str, Any]) -> List[RetrievedData]:
        """搜索港口信息"""
        results = []
        keywords = self._extract_keywords(task, query_context)
        
        for port in self._ports_cache:
            if self._port_matches_keywords(port, keywords):
                content = self._format_port_content(port)
                
                data = RetrievedData(
                    source_type="structured_port",
                    content=content,
                    metadata={
                        "type": "port",
                        "port_name": port.get("name", ""),
                        "location": port.get("location", "")
                    },
                    relevance_score=self._calculate_port_relevance(port, keywords),
                    timestamp=datetime.now().isoformat()
                )
                results.append(data)
        
        return results[:3]  # 限制结果数量
    
    def _search_companies(self, task: TaskPlan, query_context: Dict[str, Any]) -> List[RetrievedData]:
        """搜索公司信息"""
        results = []
        keywords = self._extract_keywords(task, query_context)
        
        for company in self._companies_cache:
            if self._company_matches_keywords(company, keywords):
                content = self._format_company_content(company)
                
                data = RetrievedData(
                    source_type="structured_company",
                    content=content,
                    metadata={
                        "type": "company",
                        "company_name": company.get("name", "")
                    },
                    relevance_score=self._calculate_company_relevance(company, keywords),
                    timestamp=datetime.now().isoformat()
                )
                results.append(data)
        
        return results[:2]  # 限制结果数量
    
    def _build_search_query(self, task: TaskPlan, query_context: Dict[str, Any]) -> str:
        """构建搜索查询"""
        query_parts = []

        # 优先使用原始用户查询
        user_query = query_context.get("user_query", "")
        if user_query:
            query_parts.append(user_query)

        # 从意图分析中提取具体的地点信息
        intent_analysis = query_context.get("intent_analysis")
        if intent_analysis and hasattr(intent_analysis, 'entities'):
            entities = intent_analysis.entities

            # 提取具体的地点名称
            departure = entities.get("departure")
            destination = entities.get("destination")

            if departure and departure != "出发地" and departure != "具体的出发地名称（如果有）":
                query_parts.append(departure)

            if destination and destination != "目的地" and destination != "具体的目的地名称（如果有）":
                query_parts.append(destination)

            # 提取特殊需求
            special_req = entities.get("special_requirements")
            if special_req and special_req not in ["特殊需求", "特殊需求（如价格、载车等，如果有）"]:
                query_parts.append(special_req)

        # 添加通用关键词
        query_parts.extend(["船班", "渡轮", "フェリー"])

        search_query = " ".join(query_parts)
        logger.info(f"[{self.agent_name}] 构建的搜索查询: {search_query}")

        return search_query
    
    def _extract_keywords(self, task: TaskPlan, query_context: Dict[str, Any]) -> List[str]:
        """提取搜索关键词"""
        keywords = []

        # 从原始查询中提取
        user_query = query_context.get("user_query", "")
        if user_query:
            # 提取地名
            locations = ["高松", "直岛", "直島", "豊岛", "豊島", "犬岛", "犬島", "小豆岛", "小豆島", "宇野", "神戸", "神戶"]
            for location in locations:
                if location in user_query:
                    keywords.append(location)

            # 提取需求类型
            if any(word in user_query for word in ["时间", "時間", "几点", "幾點"]):
                keywords.extend(["时间", "時間", "出发", "到达"])

            if any(word in user_query for word in ["价格", "票价", "費用", "多少钱", "多少錢"]):
                keywords.extend(["价格", "票价", "費用", "料金"])

            if any(word in user_query for word in ["车", "載車", "汽车", "自行车"]):
                keywords.extend(["载车", "載車", "车辆"])

        # 从意图分析中提取具体实体
        intent_analysis = query_context.get("intent_analysis")
        if intent_analysis and hasattr(intent_analysis, 'entities'):
            entities = intent_analysis.entities
            for key, value in entities.items():
                if value and value not in ["出发地", "目的地", "时间约束", "特殊需求"]:
                    keywords.append(value)

        # 添加通用船班关键词
        keywords.extend(["船班", "渡轮", "フェリー", "ferry"])

        # 清理和去重
        keywords = [kw.strip() for kw in keywords if kw.strip() and len(kw.strip()) > 1]
        unique_keywords = list(set(keywords))

        logger.info(f"[{self.agent_name}] 提取的关键词: {unique_keywords}")

        return unique_keywords
    
    def _route_matches_keywords(self, route: Dict[str, Any], keywords: List[str]) -> bool:
        """检查路线是否匹配关键词"""
        route_text = " ".join([
            str(route.get("departure_port", "")),
            str(route.get("arrival_port", "")),
            str(route.get("company", "")),
            str(route.get("departure_time", "")),
            str(route.get("arrival_time", ""))
        ]).lower()
        
        return any(keyword.lower() in route_text for keyword in keywords)
    
    def _port_matches_keywords(self, port: Dict[str, Any], keywords: List[str]) -> bool:
        """检查港口是否匹配关键词"""
        port_text = " ".join([
            str(port.get("name", "")),
            str(port.get("location", "")),
            str(port.get("description", ""))
        ]).lower()
        
        return any(keyword.lower() in port_text for keyword in keywords)
    
    def _company_matches_keywords(self, company: Dict[str, Any], keywords: List[str]) -> bool:
        """检查公司是否匹配关键词"""
        company_text = " ".join([
            str(company.get("name", "")),
            str(company.get("description", ""))
        ]).lower()
        
        return any(keyword.lower() in company_text for keyword in keywords)
    
    def _format_route_content(self, route: Dict[str, Any]) -> str:
        """格式化路线内容"""
        return f"船班路线: {route.get('departure_port', '')} → {route.get('arrival_port', '')} " \
               f"时间: {route.get('departure_time', '')} - {route.get('arrival_time', '')} " \
               f"公司: {route.get('company', '')} " \
               f"成人票价: {route.get('adult_fare', '')} " \
               f"儿童票价: {route.get('child_fare', '')}"
    
    def _format_port_content(self, port: Dict[str, Any]) -> str:
        """格式化港口内容"""
        return f"港口: {port.get('name', '')} " \
               f"位置: {port.get('location', '')} " \
               f"描述: {port.get('description', '')}"
    
    def _format_company_content(self, company: Dict[str, Any]) -> str:
        """格式化公司内容"""
        return f"船运公司: {company.get('name', '')} " \
               f"描述: {company.get('description', '')}"
    
    def _calculate_route_relevance(self, route: Dict[str, Any], keywords: List[str]) -> float:
        """计算路线相关性"""
        # 简单的相关性计算
        matches = 0
        total_fields = 0
        
        fields = ["departure_port", "arrival_port", "company"]
        for field in fields:
            total_fields += 1
            field_value = str(route.get(field, "")).lower()
            if any(keyword.lower() in field_value for keyword in keywords):
                matches += 1
        
        return matches / total_fields if total_fields > 0 else 0.0
    
    def _calculate_port_relevance(self, port: Dict[str, Any], keywords: List[str]) -> float:
        """计算港口相关性"""
        matches = 0
        total_fields = 0
        
        fields = ["name", "location"]
        for field in fields:
            total_fields += 1
            field_value = str(port.get(field, "")).lower()
            if any(keyword.lower() in field_value for keyword in keywords):
                matches += 1
        
        return matches / total_fields if total_fields > 0 else 0.0
    
    def _calculate_company_relevance(self, company: Dict[str, Any], keywords: List[str]) -> float:
        """计算公司相关性"""
        company_name = str(company.get("name", "")).lower()
        return 1.0 if any(keyword.lower() in company_name for keyword in keywords) else 0.5
    
    def _deduplicate_and_sort(self, results: List[RetrievedData]) -> List[RetrievedData]:
        """去重和排序"""
        # 简单的去重：基于内容相似性
        unique_results = []
        seen_contents = set()
        
        for result in results:
            content_key = result.content[:100]  # 使用前100个字符作为去重键
            if content_key not in seen_contents:
                seen_contents.add(content_key)
                unique_results.append(result)
        
        # 按相关性排序
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_results[:15]  # 限制总结果数量
