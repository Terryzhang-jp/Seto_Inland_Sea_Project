"""
需求理解Agent - 第1层：深度理解用户的旅行需求和约束条件
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from .state_models import TravelRequirement, RequirementType, TransportInfo

logger = logging.getLogger(__name__)

class RequirementAnalysisAgent:
    """需求理解Agent - 专注于旅行需求分析"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent_name = "RequirementAnalysisAgent"
        
        self.prompt_template = """你是濑户内海旅行需求分析专家。深度分析用户的旅行需求和约束条件。

用户查询: {query}

请分析并提取以下信息，返回JSON格式：

{{
    "requirement_type": "路线规划|时间查询|便利性比较|价格比较|综合咨询",
    "departure_info": {{
        "location": "具体出发地点",
        "time": "出发时间或到达时间",
        "transport_type": "交通方式(飞机/火车/汽车等)"
    }},
    "destination_options": ["目的地1", "目的地2"],
    "constraints": {{
        "time_constraints": "时间约束描述",
        "budget_constraints": "预算约束",
        "convenience_priority": "便利性要求",
        "special_needs": "特殊需求(载车/无障碍等)"
    }},
    "user_priority": "用户最关心的因素",
    "analysis_needed": ["需要分析的方面1", "需要分析的方面2"],
    "confidence_score": 0.0-1.0
}}

分析重点：
1. 识别用户的真实旅行需求
2. 提取所有约束条件和偏好
3. 理解用户想要什么样的帮助
4. 确定需要进行哪些分析

示例分析：
- "我3点30落地高松机场，想住直岛或丰岛，哪个方便？"
  → requirement_type: "便利性比较"
  → departure_info: {{"location": "高松机场", "time": "15:30", "transport_type": "飞机"}}
  → destination_options: ["直岛", "丰岛"]
  → user_priority: "便利性"
  → analysis_needed: ["交通时间", "换乘次数", "等待时间"]

只返回JSON，不要其他文字。"""
    
    async def analyze_travel_requirement(self, query: str) -> TravelRequirement:
        """分析用户旅行需求"""
        try:
            logger.info(f"[{self.agent_name}] 开始分析旅行需求: {query}")
            
            # 构建prompt
            prompt = self.prompt_template.format(query=query)
            
            # 调用LLM (异步)
            import asyncio
            response = await asyncio.to_thread(self.llm.generate_content, prompt)

            logger.info(f"[{self.agent_name}] LLM原始响应: {response.text[:200]}...")

            # 解析JSON响应
            try:
                response_text = response.text.strip()
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    result_dict = json.loads(json_text)
                else:
                    raise json.JSONDecodeError("No valid JSON found", response_text, 0)
            except json.JSONDecodeError as e:
                logger.error(f"[{self.agent_name}] JSON解析失败: {e}")
                return self._fallback_analysis(query)
            
            # 验证和转换结果
            requirement = self._validate_and_convert(result_dict, query)
            
            logger.info(f"[{self.agent_name}] 需求分析完成: {requirement.requirement_type}")
            
            return requirement
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 需求分析失败: {e}")
            return self._fallback_analysis(query)
    
    def _validate_and_convert(self, result_dict: Dict[str, Any], query: str) -> TravelRequirement:
        """验证和转换分析结果"""
        try:
            # 验证requirement_type
            requirement_type_str = result_dict.get("requirement_type", "综合咨询")
            try:
                requirement_type = RequirementType(requirement_type_str)
            except ValueError:
                requirement_type = RequirementType.COMPREHENSIVE_CONSULTATION
            
            # 提取departure_info
            departure_data = result_dict.get("departure_info", {})
            departure_info = TransportInfo(
                location=departure_data.get("location"),
                time=departure_data.get("time"),
                transport_type=departure_data.get("transport_type")
            )
            
            # 提取destination_options
            destination_options = result_dict.get("destination_options", [])
            if not isinstance(destination_options, list):
                destination_options = []
            
            # 提取constraints
            constraints = result_dict.get("constraints", {})
            if not isinstance(constraints, dict):
                constraints = {}
            
            # 提取其他字段
            user_priority = result_dict.get("user_priority")
            analysis_needed = result_dict.get("analysis_needed", [])
            if not isinstance(analysis_needed, list):
                analysis_needed = []
            
            confidence_score = result_dict.get("confidence_score", 0.8)
            if not isinstance(confidence_score, (int, float)) or not (0 <= confidence_score <= 1):
                confidence_score = 0.8
            
            return TravelRequirement(
                requirement_type=requirement_type,
                departure_info=departure_info,
                destination_options=destination_options,
                constraints=constraints,
                user_priority=user_priority,
                analysis_needed=analysis_needed,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 结果验证失败: {e}")
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str) -> TravelRequirement:
        """降级分析 - 基于简单规则"""
        logger.warning(f"[{self.agent_name}] 使用降级分析")

        query_lower = query.lower()

        # 检测地点
        locations = ["高松", "直岛", "丰岛", "犬岛", "小豆岛", "宇野", "神戸", "高松机场", "高松港"]
        departure_location = None
        destination_options = []

        for location in locations:
            if location in query:
                if "机场" in location or "港" in location:
                    departure_location = location
                else:
                    destination_options.append(location)

        # 检测时间 - 更精确的时间检测
        time_pattern = r'(\d{1,2})[点:](\d{0,2})'
        time_match = re.search(time_pattern, query)
        departure_time = None
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(2) or "00"
            departure_time = f"{hour}:{minute}"

        # 检测更多时间表达
        if not departure_time:
            # 检测"晚上7点"、"早上8点"等
            time_patterns = [
                r'晚上(\d{1,2})点',
                r'早上(\d{1,2})点',
                r'上午(\d{1,2})点',
                r'下午(\d{1,2})点',
                r'(\d{1,2})点'
            ]
            for pattern in time_patterns:
                match = re.search(pattern, query)
                if match:
                    hour = int(match.group(1))
                    if "下午" in pattern and hour < 12:
                        hour += 12
                    elif "晚上" in pattern and hour < 12:
                        hour += 12
                    departure_time = f"{hour:02d}:00"
                    break

        # 检测交通方式
        transport_type = None
        if "机场" in query or "飞机" in query:
            transport_type = "飞机"
        elif "火车" in query or "电车" in query:
            transport_type = "火车"
        elif "港" in query:
            transport_type = "船运"

        # 判断需求类型 - 基于用户真实意图，而不是简单规则
        requirement_type = RequirementType.COMPREHENSIVE_CONSULTATION

        # 优先检查用户的核心问题词汇
        if "班次" in query or "时间表" in query or "什么时候" in query or "有什么班次" in query or "班次可以选择" in query:
            # 用户明确询问班次信息，无论有几个目的地都是时间查询
            requirement_type = RequirementType.TIME_QUERY
        elif departure_time and ("还能" in query or "能去" in query or "可以" in query):
            # 有时间约束的可行性查询
            requirement_type = RequirementType.TIME_QUERY
        elif departure_time and len(destination_options) >= 1:
            # 有具体时间的查询，用户关心时间衔接
            requirement_type = RequirementType.TIME_QUERY
        elif "哪个方便" in query or "哪个更方便" in query:
            requirement_type = RequirementType.CONVENIENCE_COMPARISON
        elif "多少钱" in query or "价格" in query or "便宜" in query:
            requirement_type = RequirementType.PRICE_COMPARISON
        elif len(destination_options) > 1 and not departure_time:
            # 多个目的地但没有时间约束的一般比较
            requirement_type = RequirementType.ROUTE_PLANNING
        else:
            # 其他情况
            requirement_type = RequirementType.COMPREHENSIVE_CONSULTATION

        # 构建约束条件
        constraints = {}
        if departure_time:
            if "还能" in query or "能去" in query:
                constraints["time_constraints"] = f"需要在{departure_time}之后还有班次"
            else:
                constraints["time_constraints"] = f"需要在{departure_time}之后的班次"
        if "方便" in query:
            constraints["convenience_priority"] = "优先考虑便利性"
        if "载车" in query or "汽车" in query:
            constraints["special_needs"] = "载车需求"
        if "还能" in query:
            constraints["urgency"] = "时间紧急，需要确认可行性"

        # 确定分析需求
        analysis_needed = []
        if requirement_type == RequirementType.CONVENIENCE_COMPARISON:
            analysis_needed = ["交通时间", "换乘次数", "等待时间"]
        elif requirement_type == RequirementType.PRICE_COMPARISON:
            analysis_needed = ["票价比较", "总费用"]
        elif requirement_type == RequirementType.TIME_QUERY:
            if departure_time:
                analysis_needed = ["时间可行性", "可用班次", "末班船时间"]
            else:
                analysis_needed = ["班次时间", "运行时间"]

        # 确定用户优先级
        user_priority = "时间匹配"
        if "方便" in query:
            user_priority = "便利性"
        elif "还能" in query or "能去" in query:
            user_priority = "时间可行性"
        elif "班次" in query:
            user_priority = "班次信息"

        return TravelRequirement(
            requirement_type=requirement_type,
            departure_info=TransportInfo(
                location=departure_location,
                time=departure_time,
                transport_type=transport_type
            ),
            destination_options=destination_options,
            constraints=constraints,
            user_priority=user_priority,
            analysis_needed=analysis_needed,
            confidence_score=0.7  # 降级分析的置信度
        )
