"""
需求理解Agent - 第1层：深度理解用户的旅行需求和约束条件
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from .state_models import TravelRequirement, RequirementType, TransportInfo, TimeConstraint

logger = logging.getLogger(__name__)

class RequirementAnalysisAgent:
    """需求理解Agent - 专注于旅行需求分析"""

    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent_name = "RequirementAnalysisAgent"

        self.prompt_template = """你是濑户内海旅行需求分析专家。深度分析用户的旅行需求。

用户查询: {query}

请分析查询并提取具体的地点、时间、需求等信息，返回JSON格式：

{{
    "query_type": "简单信息查询",
    "entities": {{
        "departure": "具体的出发地名称（如果有）",
        "destination": "具体的目的地名称（如果有）",
        "time_constraints": "具体的时间要求（如果有）",
        "special_requirements": "特殊需求（如价格、载车等，如果有）"
    }},
    "complexity": "低",
    "requires_decomposition": false,
    "confidence_score": 0.9
}}

分析规则：
1. 仔细识别查询中的地名（如高松、直岛、豊岛、犬岛、小豆岛、宇野、神戸等）
2. 识别时间相关词汇（如时间、几点、上午、下午、明天等）
3. 识别特殊需求（如价格、票价、费用、载车、自行车等）
4. 如果没有找到具体信息，对应字段设为null

只返回JSON，不要其他文字。"""
    
    async def analyze_intent(self, query: str) -> IntentAnalysisResult:
        """分析用户查询意图"""
        try:
            logger.info(f"[{self.agent_name}] 开始分析查询意图: {query}")
            
            # 构建prompt
            prompt = self.prompt_template.format(query=query)
            
            # 调用LLM (异步)
            import asyncio
            response = await asyncio.to_thread(self.llm.generate_content, prompt)

            logger.info(f"[{self.agent_name}] LLM原始响应: {response.text[:200]}...")

            # 解析JSON响应
            try:
                # 提取JSON部分（如果响应包含其他文本）
                response_text = response.text.strip()

                # 查找JSON开始和结束位置
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    result_dict = json.loads(json_text)
                else:
                    raise json.JSONDecodeError("No valid JSON found", response_text, 0)
            except json.JSONDecodeError as e:
                logger.error(f"[{self.agent_name}] JSON解析失败: {e}")
                # 降级处理
                return self._fallback_analysis(query)
            
            # 验证和转换结果
            intent_result = self._validate_and_convert(result_dict, query)
            
            logger.info(f"[{self.agent_name}] 意图分析完成: {intent_result.query_type}, 复杂度: {intent_result.complexity}")
            
            return intent_result
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 意图分析失败: {e}")
            # 返回降级结果
            return self._fallback_analysis(query)
    
    def _validate_and_convert(self, result_dict: Dict[str, Any], query: str) -> IntentAnalysisResult:
        """验证和转换分析结果"""
        try:
            # 验证query_type
            query_type_str = result_dict.get("query_type", "简单信息查询")
            if query_type_str not in [qt.value for qt in QueryType]:
                query_type = QueryType.SIMPLE_INFO
            else:
                query_type = QueryType(query_type_str)
            
            # 验证complexity
            complexity_str = result_dict.get("complexity", "低")
            if complexity_str not in [cl.value for cl in ComplexityLevel]:
                complexity = ComplexityLevel.LOW
            else:
                complexity = ComplexityLevel(complexity_str)
            
            # 提取entities
            entities = result_dict.get("entities", {})
            if not isinstance(entities, dict):
                entities = {}
            
            # 验证其他字段
            requires_decomposition = result_dict.get("requires_decomposition", False)
            if not isinstance(requires_decomposition, bool):
                requires_decomposition = complexity in [ComplexityLevel.MEDIUM, ComplexityLevel.HIGH]
            
            confidence_score = result_dict.get("confidence_score", 0.8)
            if not isinstance(confidence_score, (int, float)) or not (0 <= confidence_score <= 1):
                confidence_score = 0.8
            
            return IntentAnalysisResult(
                query_type=query_type,
                entities=entities,
                complexity=complexity,
                requires_decomposition=requires_decomposition,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 结果验证失败: {e}")
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str) -> IntentAnalysisResult:
        """降级分析 - 基于简单规则"""
        logger.warning(f"[{self.agent_name}] 使用降级分析")
        
        query_lower = query.lower()
        
        # 简单的关键词检测
        entities = {}
        
        # 检测地点
        locations = ["高松", "直岛", "豊岛", "犬岛", "小豆岛", "宇野", "神戸"]
        for location in locations:
            if location in query:
                if not entities.get("departure"):
                    entities["departure"] = location
                elif not entities.get("destination"):
                    entities["destination"] = location
        
        # 检测时间
        time_keywords = ["时间", "点", ":", "上午", "下午", "早上", "晚上"]
        if any(keyword in query for keyword in time_keywords):
            entities["time_constraints"] = "有时间要求"
        
        # 检测特殊需求
        if any(keyword in query for keyword in ["车", "载车", "汽车"]):
            entities["special_requirements"] = "载车需求"
        elif any(keyword in query for keyword in ["价格", "票价", "费用", "多少钱"]):
            entities["special_requirements"] = "价格查询"
        
        # 判断复杂度
        entity_count = len([v for v in entities.values() if v])
        if entity_count <= 1:
            complexity = ComplexityLevel.LOW
            query_type = QueryType.SIMPLE_INFO
        elif entity_count <= 3:
            complexity = ComplexityLevel.MEDIUM
            query_type = QueryType.TIME_CONSTRAINT if entities.get("time_constraints") else QueryType.SIMPLE_INFO
        else:
            complexity = ComplexityLevel.HIGH
            query_type = QueryType.COMPLEX_ROUTE
        
        return IntentAnalysisResult(
            query_type=query_type,
            entities=entities,
            complexity=complexity,
            requires_decomposition=complexity != ComplexityLevel.LOW,
            confidence_score=0.6  # 降级分析的置信度较低
        )
