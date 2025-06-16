"""
任务规划Agent - 第2层：将复杂查询分解为可执行任务
"""

import json
import logging
import uuid
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from .state_models import IntentAnalysisResult, ExecutionPlan, TaskPlan, ComplexityLevel, QueryType

logger = logging.getLogger(__name__)

class TaskPlanningAgent:
    """任务规划Agent"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent_name = "TaskPlanningAgent"
        
        self.prompt_template = """基于用户查询和意图分析创建具体的执行计划。

用户查询: {query}
意图分析结果: {intent_analysis}

请创建针对性的执行计划，返回JSON格式：

{{
    "tasks": [
        {{
            "task_id": "retrieval_1",
            "task_type": "data_retrieval",
            "description": "检索关于[具体地点]的船班信息",
            "search_keywords": ["出发地", "目的地", "相关关键词"],
            "dependencies": [],
            "priority": 1,
            "estimated_duration": 2.0
        }},
        {{
            "task_id": "verification_1",
            "task_type": "fact_verification",
            "description": "验证检索到的信息准确性",
            "dependencies": ["retrieval_1"],
            "priority": 2,
            "estimated_duration": 1.0
        }},
        {{
            "task_id": "response_1",
            "task_type": "response_generation",
            "description": "生成用户友好的回复",
            "dependencies": ["verification_1"],
            "priority": 3,
            "estimated_duration": 1.0
        }}
    ],
    "execution_order": ["retrieval_1", "verification_1", "response_1"],
    "total_estimated_time": 4.0
}}

规则：
1. 根据意图分析中的entities创建具体的检索描述
2. 在search_keywords中包含提取到的地点名称
3. 确保任务依赖关系正确

只返回JSON，不要其他文字。"""
    
    async def create_execution_plan(self, query: str, intent_analysis: IntentAnalysisResult) -> ExecutionPlan:
        """创建执行计划"""
        try:
            logger.info(f"[{self.agent_name}] 开始创建执行计划")
            
            # 对于简单查询，使用预定义模板
            if intent_analysis.complexity == ComplexityLevel.LOW:
                return self._create_simple_plan(query, intent_analysis)
            
            # 对于复杂查询，使用LLM规划
            prompt = self.prompt_template.format(
                query=query,
                intent_analysis=intent_analysis.model_dump_json(indent=2)
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
                    plan_dict = json.loads(json_text)
                else:
                    raise json.JSONDecodeError("No valid JSON found", response_text, 0)
            except json.JSONDecodeError as e:
                logger.error(f"[{self.agent_name}] JSON解析失败: {e}")
                return self._create_fallback_plan(query, intent_analysis)
            
            # 验证和转换计划
            execution_plan = self._validate_and_convert_plan(plan_dict, query, intent_analysis)
            
            logger.info(f"[{self.agent_name}] 执行计划创建完成，包含 {len(execution_plan.tasks)} 个任务")
            
            return execution_plan
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 创建执行计划失败: {e}")
            return self._create_fallback_plan(query, intent_analysis)
    
    def _create_simple_plan(self, query: str, intent_analysis: IntentAnalysisResult) -> ExecutionPlan:
        """创建简单查询的执行计划"""
        plan_id = str(uuid.uuid4())
        
        # 基本数据检索任务
        retrieval_task = TaskPlan(
            task_id="retrieval_1",
            task_type="data_retrieval",
            description=f"检索相关船班信息",
            dependencies=[],
            priority=1,
            estimated_duration=2.0
        )
        
        # 验证任务
        verification_task = TaskPlan(
            task_id="verification_1",
            task_type="fact_verification",
            description="验证检索到的信息",
            dependencies=["retrieval_1"],
            priority=2,
            estimated_duration=1.0
        )
        
        # 响应生成任务
        response_task = TaskPlan(
            task_id="response_1",
            task_type="response_generation",
            description="生成最终回复",
            dependencies=["verification_1"],
            priority=4,
            estimated_duration=1.0
        )
        
        tasks = [retrieval_task, verification_task, response_task]
        execution_order = ["retrieval_1", "verification_1", "response_1"]
        
        return ExecutionPlan(
            plan_id=plan_id,
            tasks=tasks,
            execution_order=execution_order,
            total_estimated_time=4.0
        )
    
    def _create_fallback_plan(self, query: str, intent_analysis: IntentAnalysisResult) -> ExecutionPlan:
        """创建降级执行计划"""
        logger.warning(f"[{self.agent_name}] 使用降级执行计划")
        
        plan_id = str(uuid.uuid4())
        
        tasks = []
        execution_order = []
        
        # 根据意图分析结果创建任务
        entities = intent_analysis.entities
        
        # 1. 数据检索任务
        search_terms = []
        if entities.get("departure"):
            search_terms.append(entities["departure"])
        if entities.get("destination"):
            search_terms.append(entities["destination"])
        if not search_terms:
            search_terms = [query[:50]]  # 使用查询的前50个字符
        
        retrieval_task = TaskPlan(
            task_id="retrieval_fallback",
            task_type="data_retrieval",
            description=f"检索关于 {', '.join(search_terms)} 的信息",
            dependencies=[],
            priority=1,
            estimated_duration=3.0
        )
        tasks.append(retrieval_task)
        execution_order.append("retrieval_fallback")
        
        # 2. 验证任务
        verification_task = TaskPlan(
            task_id="verification_fallback",
            task_type="fact_verification",
            description="验证检索结果",
            dependencies=["retrieval_fallback"],
            priority=2,
            estimated_duration=2.0
        )
        tasks.append(verification_task)
        execution_order.append("verification_fallback")
        
        # 3. 如果是复杂查询，添加推理任务
        if intent_analysis.complexity in [ComplexityLevel.MEDIUM, ComplexityLevel.HIGH]:
            reasoning_task = TaskPlan(
                task_id="reasoning_fallback",
                task_type="reasoning",
                description="基于验证数据进行推理",
                dependencies=["verification_fallback"],
                priority=3,
                estimated_duration=2.0
            )
            tasks.append(reasoning_task)
            execution_order.append("reasoning_fallback")
        
        # 4. 响应生成任务
        last_dependency = execution_order[-1]
        response_task = TaskPlan(
            task_id="response_fallback",
            task_type="response_generation",
            description="生成最终回复",
            dependencies=[last_dependency],
            priority=4,
            estimated_duration=1.0
        )
        tasks.append(response_task)
        execution_order.append("response_fallback")
        
        total_time = sum(task.estimated_duration for task in tasks)
        
        return ExecutionPlan(
            plan_id=plan_id,
            tasks=tasks,
            execution_order=execution_order,
            total_estimated_time=total_time
        )
    
    def _validate_and_convert_plan(self, plan_dict: Dict[str, Any], query: str, intent_analysis: IntentAnalysisResult) -> ExecutionPlan:
        """验证和转换执行计划"""
        try:
            plan_id = str(uuid.uuid4())
            
            # 验证tasks
            tasks_data = plan_dict.get("tasks", [])
            if not isinstance(tasks_data, list):
                raise ValueError("tasks必须是列表")
            
            tasks = []
            for task_data in tasks_data:
                if not isinstance(task_data, dict):
                    continue
                
                task = TaskPlan(
                    task_id=task_data.get("task_id", str(uuid.uuid4())),
                    task_type=task_data.get("task_type", "data_retrieval"),
                    description=task_data.get("description", ""),
                    dependencies=task_data.get("dependencies", []),
                    priority=task_data.get("priority", 1),
                    estimated_duration=task_data.get("estimated_duration", 1.0)
                )
                tasks.append(task)
            
            if not tasks:
                raise ValueError("没有有效的任务")
            
            # 验证execution_order
            execution_order = plan_dict.get("execution_order", [])
            if not isinstance(execution_order, list):
                execution_order = [task.task_id for task in tasks]
            
            # 验证total_estimated_time
            total_estimated_time = plan_dict.get("total_estimated_time", 0)
            if not isinstance(total_estimated_time, (int, float)) or total_estimated_time <= 0:
                total_estimated_time = sum(task.estimated_duration for task in tasks)
            
            return ExecutionPlan(
                plan_id=plan_id,
                tasks=tasks,
                execution_order=execution_order,
                total_estimated_time=total_estimated_time
            )
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 计划验证失败: {e}")
            return self._create_fallback_plan(query, intent_analysis)
