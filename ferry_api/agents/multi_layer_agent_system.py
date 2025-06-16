"""
多层Agent系统 - 主要的协调器
"""

import logging
import asyncio
import time
import uuid
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI

from .state_models import FerryQueryState, AgentResponse
from .intent_analysis_agent import IntentAnalysisAgent
from .task_planning_agent import TaskPlanningAgent
from .data_retrieval_agent import DataRetrievalAgent
from .verification_agent import VerificationAgent
from .response_generation_agent import ResponseGenerationAgent

logger = logging.getLogger(__name__)

class MultiLayerAgentSystem:
    """多层Agent系统"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI, vector_store, data_processor):
        self.llm = llm
        self.vector_store = vector_store
        self.data_processor = data_processor
        
        # 初始化各层Agent
        self.intent_agent = IntentAnalysisAgent(llm)
        self.planning_agent = TaskPlanningAgent(llm)
        self.retrieval_agent = DataRetrievalAgent(vector_store, data_processor)
        self.verification_agent = VerificationAgent(data_processor)
        self.response_agent = ResponseGenerationAgent(llm)
        
        self.system_name = "MultiLayerAgentSystem"
        
        # 性能监控
        self.performance_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "average_response_time": 0.0,
            "average_accuracy": 0.0
        }
    
    async def process_query(self, user_query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """处理用户查询 - 主要入口点"""
        start_time = time.time()
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        logger.info(f"[{self.system_name}] 开始处理查询: {user_query}")
        
        # 初始化状态
        state = FerryQueryState(
            user_query=user_query,
            session_id=session_id,
            intent_analysis=None,
            execution_plan=None,
            retrieved_data=None,
            reasoning_result=None,
            verification_results=None,
            overall_accuracy=None,
            final_response=None,
            response_metadata=None,
            errors=None,
            total_execution_time=None,
            agent_responses=[]
        )
        
        try:
            # 第1层：意图分析
            state = await self._layer_1_intent_analysis(state)
            
            # 第2层：任务规划
            state = await self._layer_2_task_planning(state)
            
            # 第3层：执行层
            state = await self._layer_3_execution(state)
            
            # 第4层：验证层
            state = await self._layer_4_verification(state)
            
            # 第5层：响应生成
            state = await self._layer_5_response_generation(state)
            
            # 计算总执行时间
            total_time = time.time() - start_time
            state["total_execution_time"] = total_time
            
            # 更新性能指标
            self._update_performance_metrics(total_time, state.get("overall_accuracy", 0.0), True)
            
            logger.info(f"[{self.system_name}] 查询处理完成，耗时: {total_time:.2f}秒")
            
            return self._format_final_response(state)
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"[{self.system_name}] 查询处理失败: {e}")
            
            # 更新性能指标
            self._update_performance_metrics(error_time, 0.0, False)
            
            return self._format_error_response(user_query, str(e), session_id)
    
    async def _layer_1_intent_analysis(self, state: FerryQueryState) -> FerryQueryState:
        """第1层：意图分析"""
        try:
            logger.info(f"[{self.system_name}] 执行第1层：意图分析")
            
            start_time = time.time()
            intent_result = await self.intent_agent.analyze_intent(state["user_query"])
            execution_time = time.time() - start_time
            
            state["intent_analysis"] = intent_result
            
            # 记录Agent响应
            agent_response = AgentResponse(
                agent_name="IntentAnalysisAgent",
                response_data=intent_result.model_dump(),
                execution_time=execution_time,
                success=True
            )
            state["agent_responses"].append(agent_response)
            
            logger.info(f"[{self.system_name}] 第1层完成，意图: {intent_result.query_type}")
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第1层失败: {e}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append(f"意图分析失败: {str(e)}")
        
        return state
    
    async def _layer_2_task_planning(self, state: FerryQueryState) -> FerryQueryState:
        """第2层：任务规划"""
        try:
            logger.info(f"[{self.system_name}] 执行第2层：任务规划")
            
            if not state.get("intent_analysis"):
                raise ValueError("缺少意图分析结果")
            
            start_time = time.time()
            execution_plan = await self.planning_agent.create_execution_plan(
                state["user_query"], 
                state["intent_analysis"]
            )
            execution_time = time.time() - start_time
            
            state["execution_plan"] = execution_plan
            
            # 记录Agent响应
            agent_response = AgentResponse(
                agent_name="TaskPlanningAgent",
                response_data=execution_plan.model_dump(),
                execution_time=execution_time,
                success=True
            )
            state["agent_responses"].append(agent_response)
            
            logger.info(f"[{self.system_name}] 第2层完成，计划包含 {len(execution_plan.tasks)} 个任务")
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第2层失败: {e}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append(f"任务规划失败: {str(e)}")
        
        return state
    
    async def _layer_3_execution(self, state: FerryQueryState) -> FerryQueryState:
        """第3层：执行层"""
        try:
            logger.info(f"[{self.system_name}] 执行第3层：数据检索")
            
            if not state.get("execution_plan"):
                raise ValueError("缺少执行计划")
            
            start_time = time.time()
            
            # 准备查询上下文
            query_context = {
                "user_query": state["user_query"],
                "intent_analysis": state["intent_analysis"],
                "execution_plan": state["execution_plan"]
            }
            
            # 执行数据检索任务
            all_retrieved_data = []
            for task in state["execution_plan"].tasks:
                if task.task_type == "data_retrieval":
                    task_data = await self.retrieval_agent.retrieve_data(task, query_context)
                    all_retrieved_data.extend(task_data)
            
            execution_time = time.time() - start_time
            
            state["retrieved_data"] = all_retrieved_data
            
            # 记录Agent响应
            agent_response = AgentResponse(
                agent_name="DataRetrievalAgent",
                response_data={"retrieved_count": len(all_retrieved_data)},
                execution_time=execution_time,
                success=True
            )
            state["agent_responses"].append(agent_response)
            
            logger.info(f"[{self.system_name}] 第3层完成，检索到 {len(all_retrieved_data)} 条数据")
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第3层失败: {e}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append(f"数据检索失败: {str(e)}")
        
        return state
    
    async def _layer_4_verification(self, state: FerryQueryState) -> FerryQueryState:
        """第4层：验证层"""
        try:
            logger.info(f"[{self.system_name}] 执行第4层：数据验证")
            
            if not state.get("retrieved_data"):
                logger.warning(f"[{self.system_name}] 没有检索到数据，跳过验证")
                state["verification_results"] = []
                state["overall_accuracy"] = 0.0
                return state
            
            start_time = time.time()
            
            # 验证检索到的数据
            verification_results = await self.verification_agent.verify_retrieved_data(
                state["retrieved_data"]
            )
            
            execution_time = time.time() - start_time
            
            state["verification_results"] = verification_results
            
            # 计算总体准确率
            overall_accuracy = self.verification_agent.calculate_overall_accuracy(verification_results)
            state["overall_accuracy"] = overall_accuracy
            
            # 记录Agent响应
            agent_response = AgentResponse(
                agent_name="VerificationAgent",
                response_data={
                    "verification_count": len(verification_results),
                    "overall_accuracy": overall_accuracy
                },
                execution_time=execution_time,
                success=True
            )
            state["agent_responses"].append(agent_response)
            
            logger.info(f"[{self.system_name}] 第4层完成，准确率: {overall_accuracy:.1%}")
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第4层失败: {e}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append(f"数据验证失败: {str(e)}")
        
        return state
    
    async def _layer_5_response_generation(self, state: FerryQueryState) -> FerryQueryState:
        """第5层：响应生成"""
        try:
            logger.info(f"[{self.system_name}] 执行第5层：响应生成")
            
            start_time = time.time()
            
            # 生成最终回复
            response_result = await self.response_agent.generate_response(
                state["user_query"],
                state.get("retrieved_data", []),
                state.get("verification_results", [])
            )
            
            execution_time = time.time() - start_time
            
            state["final_response"] = response_result["response"]
            state["response_metadata"] = {
                "accuracy_rate": response_result["accuracy_rate"],
                "verification_summary": response_result["verification_summary"],
                "verified_facts_count": response_result["verified_facts_count"],
                "total_facts_count": response_result["total_facts_count"]
            }
            
            # 记录Agent响应
            agent_response = AgentResponse(
                agent_name="ResponseGenerationAgent",
                response_data=response_result,
                execution_time=execution_time,
                success=True
            )
            state["agent_responses"].append(agent_response)
            
            logger.info(f"[{self.system_name}] 第5层完成，生成回复")
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第5层失败: {e}")
            if not state.get("errors"):
                state["errors"] = []
            state["errors"].append(f"响应生成失败: {str(e)}")
        
        return state
    
    def _format_final_response(self, state: FerryQueryState) -> Dict[str, Any]:
        """格式化最终响应"""
        return {
            "message": state.get("final_response", "处理失败，无法生成回复"),
            "session_id": state.get("session_id"),
            "accuracy_rate": state.get("overall_accuracy", 0.0),
            "response_metadata": state.get("response_metadata", {}),
            "execution_time": state.get("total_execution_time", 0.0),
            "agent_performance": [
                {
                    "agent": resp.agent_name,
                    "execution_time": resp.execution_time,
                    "success": resp.success
                }
                for resp in state.get("agent_responses", [])
            ],
            "errors": state.get("errors", [])
        }
    
    def _format_error_response(self, query: str, error: str, session_id: str) -> Dict[str, Any]:
        """格式化错误响应"""
        return {
            "message": f"很抱歉，处理查询「{query}」时遇到了问题：{error}",
            "session_id": session_id,
            "accuracy_rate": 0.0,
            "response_metadata": {},
            "execution_time": 0.0,
            "agent_performance": [],
            "errors": [error]
        }
    
    def _update_performance_metrics(self, execution_time: float, accuracy: float, success: bool):
        """更新性能指标"""
        self.performance_metrics["total_queries"] += 1
        
        if success:
            self.performance_metrics["successful_queries"] += 1
        
        # 更新平均响应时间
        total = self.performance_metrics["total_queries"]
        current_avg_time = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (
            (current_avg_time * (total - 1) + execution_time) / total
        )
        
        # 更新平均准确率
        if success:
            successful = self.performance_metrics["successful_queries"]
            current_avg_accuracy = self.performance_metrics["average_accuracy"]
            self.performance_metrics["average_accuracy"] = (
                (current_avg_accuracy * (successful - 1) + accuracy) / successful
            ) if successful > 0 else 0.0
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return self.performance_metrics.copy()
