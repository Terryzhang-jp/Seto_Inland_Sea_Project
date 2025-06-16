"""
策略规划Agent - 第2层：动态制定查询策略，支持复杂的多步骤分析
"""

import json
import logging
import uuid
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from .state_models import TravelRequirement, RequirementType, QueryStrategy

logger = logging.getLogger(__name__)

class StrategyPlanningAgent:
    """策略规划Agent - 动态制定查询策略"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent_name = "StrategyPlanningAgent"
        
        self.prompt_template = """你是濑户内海旅行策略规划专家。根据用户需求动态制定查询策略。

用户需求分析: {requirement_analysis}

请制定具体的查询策略，返回JSON格式：

{{
    "strategy_name": "策略名称",
    "steps": [
        {{
            "step": 1,
            "action": "具体要执行的查询动作",
            "data_needed": ["需要的数据类型1", "需要的数据类型2"],
            "search_params": {{
                "departure": "出发地",
                "destination": "目的地",
                "time_filter": "时间筛选条件"
            }},
            "priority": "high|medium|low"
        }}
    ],
    "analysis_criteria": ["分析标准1", "分析标准2"],
    "comparison_logic": "如何比较和分析数据",
    "expected_outcome": "预期输出什么样的结果"
}}

策略制定原则：
1. 根据需求类型动态调整查询步骤
2. 便利性比较需要查询多个路线并比较
3. 时间查询需要精确的时刻表信息
4. 价格比较需要票价和总费用信息
5. 路线规划需要考虑连接和中转

示例策略：
- 便利性比较："高松机场→直岛 vs 高松机场→丰岛"
  步骤1: 查询高松机场到高松港的交通
  步骤2: 查询高松港到直岛的班次
  步骤3: 查询高松港到丰岛的班次（可能需要查宇野港路线）
  步骤4: 比较总耗时、换乘次数、等待时间

只返回JSON，不要其他文字。"""
    
    async def create_query_strategy(self, requirement: TravelRequirement) -> QueryStrategy:
        """创建查询策略"""
        try:
            logger.info(f"[{self.agent_name}] 开始制定查询策略")
            
            # 对于简单需求，使用预定义策略
            if requirement.requirement_type in [RequirementType.TIME_QUERY] and len(requirement.destination_options) == 1:
                return self._create_simple_time_strategy(requirement)
            
            # 对于复杂需求，使用LLM规划
            prompt = self.prompt_template.format(
                requirement_analysis=requirement.model_dump_json(indent=2)
            )
            
            # 调用LLM (异步)
            import asyncio
            response = await asyncio.to_thread(self.llm.generate_content, prompt)

            logger.info(f"[{self.agent_name}] LLM原始响应: {response.text[:200]}...")

            try:
                # 提取JSON部分
                response_text = response.text.strip()
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    strategy_dict = json.loads(json_text)
                else:
                    raise json.JSONDecodeError("No valid JSON found", response_text, 0)
            except json.JSONDecodeError as e:
                logger.error(f"[{self.agent_name}] JSON解析失败: {e}")
                return self._create_fallback_strategy(requirement)
            
            # 验证和转换策略
            query_strategy = self._validate_and_convert_strategy(strategy_dict, requirement)
            
            logger.info(f"[{self.agent_name}] 策略制定完成: {query_strategy.strategy_name}")
            
            return query_strategy
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 策略制定失败: {e}")
            return self._create_fallback_strategy(requirement)
    
    def _create_simple_time_strategy(self, requirement: TravelRequirement) -> QueryStrategy:
        """创建简单时间查询策略"""
        strategy_id = str(uuid.uuid4())
        
        departure = requirement.departure_info.location or "未指定"
        destination = requirement.destination_options[0] if requirement.destination_options else "未指定"
        
        steps = [
            {
                "step": 1,
                "action": f"查询{departure}到{destination}的班次时间",
                "data_needed": ["班次时刻表", "运行时间", "票价信息"],
                "search_params": {
                    "departure": departure,
                    "destination": destination,
                    "time_filter": requirement.departure_info.time
                },
                "priority": "high"
            }
        ]
        
        return QueryStrategy(
            strategy_id=strategy_id,
            strategy_name=f"简单时间查询: {departure}→{destination}",
            steps=steps,
            analysis_criteria=["班次时间", "运行时间"],
            expected_outcome="提供具体的班次时间和相关信息"
        )
    
    def _create_fallback_strategy(self, requirement: TravelRequirement) -> QueryStrategy:
        """创建降级策略"""
        logger.warning(f"[{self.agent_name}] 使用降级策略")
        
        strategy_id = str(uuid.uuid4())
        
        # 根据需求类型创建基础策略
        if requirement.requirement_type == RequirementType.CONVENIENCE_COMPARISON:
            return self._create_convenience_comparison_strategy(requirement)
        elif requirement.requirement_type == RequirementType.PRICE_COMPARISON:
            return self._create_price_comparison_strategy(requirement)
        elif requirement.requirement_type == RequirementType.ROUTE_PLANNING:
            return self._create_route_planning_strategy(requirement)
        else:
            return self._create_general_strategy(requirement)
    
    def _create_convenience_comparison_strategy(self, requirement: TravelRequirement) -> QueryStrategy:
        """创建便利性比较策略"""
        strategy_id = str(uuid.uuid4())
        departure = requirement.departure_info.location or "出发地"
        
        steps = []
        step_num = 1
        
        # 为每个目的地创建查询步骤
        for destination in requirement.destination_options:
            steps.append({
                "step": step_num,
                "action": f"查询{departure}到{destination}的交通方案",
                "data_needed": ["班次时间", "中转信息", "总耗时"],
                "search_params": {
                    "departure": departure,
                    "destination": destination,
                    "time_filter": requirement.departure_info.time
                },
                "priority": "high"
            })
            step_num += 1
        
        # 添加比较分析步骤
        steps.append({
            "step": step_num,
            "action": "比较各路线的便利性",
            "data_needed": ["所有路线数据"],
            "analysis_type": "convenience_comparison",
            "priority": "high"
        })
        
        return QueryStrategy(
            strategy_id=strategy_id,
            strategy_name=f"便利性比较: {departure}到多个目的地",
            steps=steps,
            analysis_criteria=["总耗时", "换乘次数", "等待时间", "班次频率"],
            expected_outcome="推荐最便利的路线选择"
        )
    
    def _create_price_comparison_strategy(self, requirement: TravelRequirement) -> QueryStrategy:
        """创建价格比较策略"""
        strategy_id = str(uuid.uuid4())
        departure = requirement.departure_info.location or "出发地"
        
        steps = []
        step_num = 1
        
        for destination in requirement.destination_options:
            steps.append({
                "step": step_num,
                "action": f"查询{departure}到{destination}的价格信息",
                "data_needed": ["票价", "中转费用", "总费用"],
                "search_params": {
                    "departure": departure,
                    "destination": destination
                },
                "priority": "high"
            })
            step_num += 1
        
        steps.append({
            "step": step_num,
            "action": "比较各路线的价格",
            "data_needed": ["所有价格数据"],
            "analysis_type": "price_comparison",
            "priority": "high"
        })
        
        return QueryStrategy(
            strategy_id=strategy_id,
            strategy_name=f"价格比较: {departure}到多个目的地",
            steps=steps,
            analysis_criteria=["单程票价", "往返票价", "总费用"],
            expected_outcome="推荐最经济的路线选择"
        )
    
    def _create_route_planning_strategy(self, requirement: TravelRequirement) -> QueryStrategy:
        """创建路线规划策略"""
        strategy_id = str(uuid.uuid4())
        
        steps = [
            {
                "step": 1,
                "action": "查询主要路线信息",
                "data_needed": ["班次时间", "路线图", "连接信息"],
                "priority": "high"
            },
            {
                "step": 2,
                "action": "分析最优路线组合",
                "data_needed": ["所有路线数据"],
                "analysis_type": "route_optimization",
                "priority": "high"
            }
        ]
        
        return QueryStrategy(
            strategy_id=strategy_id,
            strategy_name="综合路线规划",
            steps=steps,
            analysis_criteria=["时间效率", "成本效益", "便利性"],
            expected_outcome="提供最优的跳岛路线规划"
        )
    
    def _create_general_strategy(self, requirement: TravelRequirement) -> QueryStrategy:
        """创建通用策略"""
        strategy_id = str(uuid.uuid4())
        
        steps = [
            {
                "step": 1,
                "action": "查询相关交通信息",
                "data_needed": ["班次信息", "路线信息", "价格信息"],
                "priority": "medium"
            }
        ]
        
        return QueryStrategy(
            strategy_id=strategy_id,
            strategy_name="通用信息查询",
            steps=steps,
            analysis_criteria=["信息完整性", "数据准确性"],
            expected_outcome="提供相关的交通信息"
        )
    
    def _validate_and_convert_strategy(self, strategy_dict: Dict[str, Any], requirement: TravelRequirement) -> QueryStrategy:
        """验证和转换策略"""
        try:
            strategy_id = str(uuid.uuid4())
            
            strategy_name = strategy_dict.get("strategy_name", "未命名策略")
            steps = strategy_dict.get("steps", [])
            analysis_criteria = strategy_dict.get("analysis_criteria", [])
            expected_outcome = strategy_dict.get("expected_outcome", "提供查询结果")
            
            # 验证steps格式
            if not isinstance(steps, list):
                steps = []
            
            return QueryStrategy(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                steps=steps,
                analysis_criteria=analysis_criteria,
                expected_outcome=expected_outcome
            )
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 策略验证失败: {e}")
            return self._create_fallback_strategy(requirement)
