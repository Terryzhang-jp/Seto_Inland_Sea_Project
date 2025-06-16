"""
智能查询系统 - 重新设计的主协调器
基于用户真实需求：智能的濑户内海跳岛查询助手
"""

import logging
import asyncio
import time
import uuid
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI

from .requirement_analysis_agent import RequirementAnalysisAgent
from .strategy_planning_agent import StrategyPlanningAgent
from .intelligent_data_retrieval_agent import IntelligentDataRetrievalAgent
from .data_validation_agent import DataValidationAgent
from .intelligent_analysis_agent import IntelligentAnalysisAgent

logger = logging.getLogger(__name__)

class IntelligentQuerySystem:
    """智能查询系统 - 濑户内海跳岛查询助手"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI, vector_store, data_processor):
        self.llm = llm
        self.vector_store = vector_store
        self.data_processor = data_processor
        
        # 初始化各层Agent
        self.requirement_agent = RequirementAnalysisAgent(llm)
        self.strategy_agent = StrategyPlanningAgent(llm)
        self.retrieval_agent = IntelligentDataRetrievalAgent(vector_store, data_processor)
        self.validation_agent = DataValidationAgent(data_processor)
        self.analysis_agent = IntelligentAnalysisAgent(llm)
        
        self.system_name = "IntelligentQuerySystem"
        
        # 性能监控
        self.performance_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "average_response_time": 0.0,
            "average_confidence": 0.0
        }
    
    async def process_query(self, user_query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """处理用户查询 - 主要入口点"""
        start_time = time.time()
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        logger.info(f"[{self.system_name}] 开始处理查询: {user_query}")
        
        try:
            # 第1层：需求理解
            requirement = await self._layer_1_requirement_analysis(user_query)
            
            # 第2层：策略规划
            strategy = await self._layer_2_strategy_planning(user_query, requirement)
            
            # 第3层：数据检索
            retrieved_data = await self._layer_3_data_retrieval(strategy, {
                "user_query": user_query,
                "requirement": requirement
            })
            
            # 第4层：数据验证
            validation_results = await self._layer_4_data_validation(retrieved_data)
            
            # 第5层：智能分析
            analysis_result = await self._layer_5_intelligent_analysis(
                requirement, strategy, retrieved_data, validation_results
            )
            
            # 计算总执行时间
            total_time = time.time() - start_time
            
            # 更新性能指标
            confidence = analysis_result.get("confidence", 0.0)
            self._update_performance_metrics(total_time, confidence, True)
            
            logger.info(f"[{self.system_name}] 查询处理完成，耗时: {total_time:.2f}秒")
            
            return self._format_final_response(
                user_query, requirement, strategy, analysis_result, 
                retrieved_data, validation_results, total_time, session_id
            )
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"[{self.system_name}] 查询处理失败: {e}")
            
            # 更新性能指标
            self._update_performance_metrics(error_time, 0.0, False)
            
            return self._format_error_response(user_query, str(e), session_id)
    
    async def _layer_1_requirement_analysis(self, user_query: str):
        """第1层：需求理解"""
        try:
            logger.info(f"[{self.system_name}] 执行第1层：需求理解")
            
            start_time = time.time()
            requirement = await self.requirement_agent.analyze_travel_requirement(user_query)
            execution_time = time.time() - start_time
            
            logger.info(f"[{self.system_name}] 第1层完成，需求类型: {requirement.requirement_type}")
            logger.info(f"[{self.system_name}] 出发地: {requirement.departure_info.location}")
            logger.info(f"[{self.system_name}] 目的地选项: {requirement.destination_options}")
            
            return requirement
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第1层失败: {e}")
            raise
    
    async def _layer_2_strategy_planning(self, user_query: str, requirement):
        """第2层：策略规划"""
        try:
            logger.info(f"[{self.system_name}] 执行第2层：策略规划")
            
            start_time = time.time()
            strategy = await self.strategy_agent.create_query_strategy(requirement)
            execution_time = time.time() - start_time
            
            logger.info(f"[{self.system_name}] 第2层完成，策略: {strategy.strategy_name}")
            logger.info(f"[{self.system_name}] 策略步骤数: {len(strategy.steps)}")
            
            return strategy
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第2层失败: {e}")
            raise
    
    async def _layer_3_data_retrieval(self, strategy, context):
        """第3层：数据检索"""
        try:
            logger.info(f"[{self.system_name}] 执行第3层：数据检索")
            
            start_time = time.time()
            retrieved_data = await self.retrieval_agent.execute_strategy(strategy, context)
            execution_time = time.time() - start_time
            
            logger.info(f"[{self.system_name}] 第3层完成，检索到 {len(retrieved_data)} 条数据")
            
            return retrieved_data
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第3层失败: {e}")
            return []
    
    async def _layer_4_data_validation(self, retrieved_data):
        """第4层：数据验证"""
        try:
            logger.info(f"[{self.system_name}] 执行第4层：数据验证")
            
            start_time = time.time()
            validation_results = await self.validation_agent.validate_data_completeness(retrieved_data)
            execution_time = time.time() - start_time
            
            # 计算数据质量
            data_quality = self.validation_agent.calculate_overall_data_quality(validation_results)
            
            logger.info(f"[{self.system_name}] 第4层完成，数据质量: {data_quality['quality_summary']}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第4层失败: {e}")
            return []
    
    async def _layer_5_intelligent_analysis(self, requirement, strategy, retrieved_data, validation_results):
        """第5层：智能分析"""
        try:
            logger.info(f"[{self.system_name}] 执行第5层：智能分析")
            
            start_time = time.time()
            analysis_result = await self.analysis_agent.analyze_and_recommend(
                requirement, strategy, retrieved_data, validation_results
            )
            execution_time = time.time() - start_time
            
            logger.info(f"[{self.system_name}] 第5层完成，分析类型: {analysis_result.get('analysis_type')}")
            logger.info(f"[{self.system_name}] 推荐结果: {analysis_result.get('recommendation')}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"[{self.system_name}] 第5层失败: {e}")
            return {
                "analysis_type": "错误",
                "recommendation": None,
                "reason": f"分析失败: {str(e)}",
                "confidence": 0.0
            }
    
    def _format_final_response(self, user_query, requirement, strategy, analysis_result, 
                             retrieved_data, validation_results, total_time, session_id):
        """格式化最终响应"""
        
        # 生成用户友好的回复
        response_message = self._generate_user_friendly_response(
            user_query, requirement, analysis_result
        )
        
        # 生成数据来源报告
        source_report = self.validation_agent.generate_data_source_report(retrieved_data)
        
        return {
            "message": response_message,
            "session_id": session_id,
            "requirement_type": requirement.requirement_type.value,
            "analysis_result": analysis_result,
            "data_sources": source_report,
            "execution_time": total_time,
            "system_info": {
                "strategy_used": strategy.strategy_name,
                "data_retrieved": len(retrieved_data),
                "validation_checks": len(validation_results),
                "confidence": analysis_result.get("confidence", 0.0)
            }
        }
    
    def _generate_user_friendly_response(self, user_query, requirement, analysis_result):
        """生成用户友好的回复"""
        try:
            analysis_type = analysis_result.get("analysis_type", "")
            recommendation = analysis_result.get("recommendation")
            reason = analysis_result.get("reason", "")
            confidence = analysis_result.get("confidence", 0.0)

            if not recommendation:
                return f"很抱歉，根据您的查询「{user_query}」，{reason}。建议您提供更具体的信息或查询官方网站获取最新信息。"

            # 根据分析类型生成不同的回复
            if analysis_type == "时间可行性分析":
                # 这是用户最关心的核心问题：能否赶上班次
                response = f"根据您的查询「{user_query}」，我为您分析了时间可行性：\n\n"

                core_analysis = analysis_result.get("core_analysis", {})
                key_findings = analysis_result.get("key_findings", [])

                response += f"⏰ **时间分析**：\n"
                response += f"• 您{core_analysis.get('departure_time', '未知')}落地高松机场\n"
                response += f"• 预计{core_analysis.get('arrival_at_port', '未知')}到达高松港\n"
                response += f"• 机场到港口需要约{core_analysis.get('airport_to_port_time', '40分钟')}\n\n"

                response += f"🚢 **班次可行性**：\n"
                for finding in key_findings:
                    response += f"• {finding}\n"

                response += f"\n🎯 **建议**: {recommendation}\n"
                response += f"💡 **理由**: {reason}\n"

                # 添加详细的班次信息
                feasibility_analysis = core_analysis.get("feasibility_by_destination", {})
                if feasibility_analysis:
                    response += f"\n📋 **详细班次信息**：\n"
                    for dest, analysis in feasibility_analysis.items():
                        schedules = analysis.get("available_schedules", [])
                        if schedules:
                            response += f"• {dest}: {', '.join(schedules[:5])}"
                            if len(schedules) > 5:
                                response += f"等(共{len(schedules)}班)"
                            response += f"\n"

                # 添加置信度信息
                if confidence >= 0.8:
                    response += f"\n✅ 分析置信度: 高 ({confidence:.1%})"
                else:
                    response += f"\n⚠️ 分析置信度: 中等 ({confidence:.1%})，建议确认最新时刻表"

            elif analysis_type == "时间查询" or analysis_type == "多目的地时间查询":
                # 用户询问班次信息
                response = f"根据您的查询「{user_query}」，为您提供班次信息：\n\n"

                # 显示班次选择
                schedule_details = analysis_result.get("schedule_details", {})
                all_schedules = analysis_result.get("all_schedules", {})

                if all_schedules:
                    # 多目的地班次信息
                    response += f"🚢 **各目的地班次选择**：\n"
                    for dest, schedules in all_schedules.items():
                        response += f"• **{dest}**: {', '.join(schedules)}\n"
                elif schedule_details:
                    # 单目的地班次信息
                    schedules = schedule_details.get("available_schedules", [])
                    departure = schedule_details.get("departure", "出发地")
                    destination = schedule_details.get("destination", "目的地")
                    response += f"🚢 **{departure}到{destination}班次**：\n"
                    response += f"• 可选班次: {', '.join(schedules)}\n"
                    response += f"• 总计: {len(schedules)}班\n"

                response += f"\n💡 **说明**: {reason}\n"

                # 添加置信度信息
                if confidence >= 0.8:
                    response += f"\n✅ 信息准确度: 高 ({confidence:.1%})"
                else:
                    response += f"\n⚠️ 信息准确度: 中等 ({confidence:.1%})，建议确认最新时刻表"

            elif analysis_type == "便利性比较":
                response = f"根据您的查询「{user_query}」，我为您分析了各个选项的便利性。\n\n"
                response += f"🎯 **推荐选择**: {recommendation}\n"
                response += f"💡 **推荐理由**: {reason}\n\n"

                # 添加详细比较信息
                if "comparison_details" in analysis_result:
                    response += analysis_result["comparison_details"]

                # 添加置信度信息
                if confidence >= 0.8:
                    response += f"\n\n✅ 推荐置信度: 高 ({confidence:.1%})"
                elif confidence >= 0.6:
                    response += f"\n\n⚠️ 推荐置信度: 中等 ({confidence:.1%})"
                else:
                    response += f"\n\n⚠️ 推荐置信度: 较低 ({confidence:.1%})，建议进一步确认"

            else:
                response = f"根据您的查询「{user_query}」：\n\n"
                response += f"📋 **分析类型**: {analysis_type}\n"
                if recommendation:
                    response += f"💡 **建议**: {recommendation}\n"
                if reason:
                    response += f"📝 **说明**: {reason}\n"

            return response

        except Exception as e:
            logger.error(f"[{self.system_name}] 生成用户回复失败: {e}")
            return f"根据您的查询「{user_query}」，我已为您查找了相关信息，但在生成回复时遇到了问题。请稍后重试或联系客服。"
    
    def _format_error_response(self, query: str, error: str, session_id: str):
        """格式化错误响应"""
        return {
            "message": f"很抱歉，处理您的查询「{query}」时遇到了问题。我们正在努力改进系统，请稍后重试或提供更具体的信息。",
            "session_id": session_id,
            "requirement_type": "错误",
            "analysis_result": {"analysis_type": "错误", "confidence": 0.0},
            "data_sources": {"summary": "无数据", "sources": []},
            "execution_time": 0.0,
            "system_info": {
                "error": error,
                "strategy_used": "无",
                "data_retrieved": 0,
                "validation_checks": 0,
                "confidence": 0.0
            }
        }
    
    def _update_performance_metrics(self, execution_time: float, confidence: float, success: bool):
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
        
        # 更新平均置信度
        if success:
            successful = self.performance_metrics["successful_queries"]
            current_avg_confidence = self.performance_metrics["average_confidence"]
            self.performance_metrics["average_confidence"] = (
                (current_avg_confidence * (successful - 1) + confidence) / successful
            ) if successful > 0 else 0.0
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return self.performance_metrics.copy()
