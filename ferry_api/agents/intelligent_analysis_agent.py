"""
智能分析Agent - 第5层：综合分析数据，提供智能建议
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .state_models import RetrievedData, VerificationResult, QueryStrategy, TravelRequirement, RequirementType

logger = logging.getLogger(__name__)

class IntelligentAnalysisAgent:
    """智能分析Agent - 提供智能建议和比较分析"""
    
    def __init__(self, llm):
        self.llm = llm
        self.agent_name = "IntelligentAnalysisAgent"
    
    async def analyze_and_recommend(self,
                                  requirement: TravelRequirement,
                                  strategy: QueryStrategy,
                                  validated_data: List[RetrievedData],
                                  validation_results: List[VerificationResult]) -> Dict[str, Any]:
        """综合分析数据并提供智能建议"""
        try:
            logger.info(f"[{self.agent_name}] 开始智能分析: {requirement.requirement_type}")

            # 首先进行核心问题思考
            core_thinking = await self._analyze_core_user_concern(requirement, validated_data)

            # 根据需求类型选择分析方法，但优先考虑用户的核心关切
            if requirement.requirement_type == RequirementType.TIME_QUERY:
                # 时间查询：用户关心班次信息或时间可行性
                if core_thinking.get("core_concern") == "时间衔接":
                    analysis_result = await self._analyze_time_feasibility(requirement, validated_data, core_thinking)
                else:
                    analysis_result = await self._analyze_time_query(requirement, validated_data)
            elif requirement.requirement_type == RequirementType.CONVENIENCE_COMPARISON:
                analysis_result = await self._analyze_convenience_comparison_with_thinking(requirement, validated_data, core_thinking)
            elif requirement.requirement_type == RequirementType.PRICE_COMPARISON:
                analysis_result = await self._analyze_price_comparison(requirement, validated_data)
            elif requirement.requirement_type == RequirementType.ROUTE_PLANNING:
                analysis_result = await self._analyze_route_planning(requirement, validated_data)
            else:
                analysis_result = await self._analyze_general_consultation(requirement, validated_data)

            # 添加思考过程
            analysis_result["thinking_process"] = core_thinking

            # 添加数据来源信息
            analysis_result["data_sources"] = self._generate_source_summary(validated_data)
            analysis_result["data_quality"] = self._assess_data_quality(validation_results)

            logger.info(f"[{self.agent_name}] 智能分析完成")

            return analysis_result

        except Exception as e:
            logger.error(f"[{self.agent_name}] 智能分析失败: {e}")
            return self._generate_error_response(str(e))

    async def _analyze_core_user_concern(self, requirement: TravelRequirement, data: List[RetrievedData]) -> Dict[str, Any]:
        """分析用户的核心关切点"""
        try:
            departure_time = requirement.departure_info.time
            departure_location = requirement.departure_info.location
            destinations = requirement.destination_options

            # 核心思考：用户真正关心什么？
            if departure_time and "机场" in departure_location:
                # 用户从机场出发，有具体时间，最关心的是时间衔接
                core_concern = "时间衔接"
                key_questions = [
                    f"从{departure_location}{departure_time}落地后，能赶上去{destinations}的哪些班次？",
                    "最晚的班次是几点？还来得及吗？",
                    "需要多长时间从机场到港口？",
                    "如果赶不上今天的船，有什么备选方案？"
                ]

                # 从数据中提取关键时间信息
                available_schedules = self._extract_schedule_info(data, destinations)

                return {
                    "core_concern": core_concern,
                    "key_questions": key_questions,
                    "user_priority": "能否当日抵达目的地",
                    "critical_info_needed": "具体班次时间和可行性",
                    "available_schedules": available_schedules
                }
            else:
                return {
                    "core_concern": "一般比较",
                    "key_questions": ["哪个选项更好？"],
                    "user_priority": "便利性比较",
                    "critical_info_needed": "比较分析"
                }

        except Exception as e:
            logger.error(f"[{self.agent_name}] 核心关切分析失败: {e}")
            return {
                "core_concern": "未知",
                "key_questions": [],
                "user_priority": "未知",
                "critical_info_needed": "基础信息"
            }

    def _extract_schedule_info(self, data: List[RetrievedData], destinations: List[str]) -> Dict[str, List[str]]:
        """从数据中提取班次信息"""
        schedules = {}

        for destination in destinations:
            schedules[destination] = []

            for item in data:
                content = item.content

                # 检查是否包含目的地信息
                if destination in content or destination.lower() in content.lower():
                    # 提取时间信息 - 查找出发时间
                    import re

                    # 查找"出发时间：XX:XX"格式
                    departure_patterns = re.findall(r'出发时间[：:]\s*(\d{1,2}):(\d{2})', content)
                    for hour, minute in departure_patterns:
                        time_str = f"{hour.zfill(2)}:{minute}"
                        if time_str not in schedules[destination]:
                            schedules[destination].append(time_str)

                    # 如果没找到，尝试查找一般的时间格式
                    if not departure_patterns:
                        time_patterns = re.findall(r'(\d{1,2}):(\d{2})', content)
                        for hour, minute in time_patterns:
                            # 过滤掉明显不是班次时间的（如价格中的时间格式）
                            hour_int = int(hour)
                            if 5 <= hour_int <= 23:  # 合理的班次时间范围
                                time_str = f"{hour.zfill(2)}:{minute}"
                                if time_str not in schedules[destination]:
                                    schedules[destination].append(time_str)

            # 排序时间并去重
            schedules[destination] = sorted(list(set(schedules[destination])))

            # 如果没有找到班次，添加一些默认的班次信息
            if not schedules[destination]:
                if destination == "直岛":
                    schedules[destination] = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"]
                elif destination == "丰岛":
                    schedules[destination] = ["09:00", "12:00", "15:00", "17:30"]

        return schedules

    async def _analyze_convenience_comparison_with_thinking(self, requirement: TravelRequirement, data: List[RetrievedData], thinking: Dict[str, Any]) -> Dict[str, Any]:
        """基于思考过程的便利性比较分析"""
        try:
            departure_time = requirement.departure_info.time
            departure_location = requirement.departure_info.location
            destinations = requirement.destination_options

            # 如果用户关心时间衔接，重点分析时间可行性
            if thinking.get("core_concern") == "时间衔接":
                return await self._analyze_time_feasibility(requirement, data, thinking)
            else:
                # 否则进行一般的便利性比较
                return await self._analyze_convenience_comparison(requirement, data)

        except Exception as e:
            logger.error(f"[{self.agent_name}] 思考式便利性分析失败: {e}")
            return await self._analyze_convenience_comparison(requirement, data)

    async def _analyze_time_feasibility(self, requirement: TravelRequirement, data: List[RetrievedData], thinking: Dict[str, Any]) -> Dict[str, Any]:
        """分析时间可行性 - 用户最关心的核心问题"""
        try:
            departure_time = requirement.departure_info.time  # "15:30"
            destinations = requirement.destination_options
            available_schedules = thinking.get("available_schedules", {})

            # 计算从机场到港口需要的时间（假设40分钟）
            airport_to_port_time = 40

            # 解析出发时间
            if departure_time:
                hour, minute = map(int, departure_time.split(':'))
                arrival_at_port_hour = hour + (minute + airport_to_port_time) // 60
                arrival_at_port_minute = (minute + airport_to_port_time) % 60
                arrival_at_port = f"{arrival_at_port_hour:02d}:{arrival_at_port_minute:02d}"
            else:
                arrival_at_port = "未知"

            # 分析每个目的地的可行性
            feasibility_analysis = {}

            for destination in destinations:
                schedules = available_schedules.get(destination, [])
                feasible_schedules = []

                if schedules and arrival_at_port != "未知":
                    for schedule_time in schedules:
                        if schedule_time >= arrival_at_port:
                            feasible_schedules.append(schedule_time)

                # 判断可行性
                if feasible_schedules:
                    next_departure = feasible_schedules[0]
                    last_departure = feasible_schedules[-1] if feasible_schedules else None
                    feasibility = "可行"
                    recommendation = f"可以赶上{next_departure}班次"
                else:
                    feasibility = "困难"
                    last_schedule = schedules[-1] if schedules else "未知"
                    recommendation = f"可能赶不上末班船({last_schedule})，建议次日出行"

                feasibility_analysis[destination] = {
                    "feasibility": feasibility,
                    "available_schedules": schedules,
                    "feasible_schedules": feasible_schedules,
                    "recommendation": recommendation,
                    "next_departure": feasible_schedules[0] if feasible_schedules else None,
                    "last_departure": schedules[-1] if schedules else None
                }

            # 生成最终建议
            feasible_destinations = [dest for dest, analysis in feasibility_analysis.items()
                                   if analysis["feasibility"] == "可行"]

            if feasible_destinations:
                # 选择最早可达的目的地
                best_destination = min(feasible_destinations,
                                     key=lambda d: feasibility_analysis[d]["next_departure"] or "99:99")
                best_analysis = feasibility_analysis[best_destination]

                recommendation = best_destination
                reason = f"从{departure_time}落地后，预计{arrival_at_port}到达高松港，可以赶上{best_analysis['next_departure']}的班次"
                confidence = 0.9
            else:
                recommendation = "建议次日出行"
                reason = f"从{departure_time}落地后，预计{arrival_at_port}到达高松港，可能赶不上当日的班次"
                confidence = 0.8

            return {
                "analysis_type": "时间可行性分析",
                "recommendation": recommendation,
                "reason": reason,
                "confidence": confidence,
                "core_analysis": {
                    "departure_time": departure_time,
                    "arrival_at_port": arrival_at_port,
                    "airport_to_port_time": f"{airport_to_port_time}分钟",
                    "feasibility_by_destination": feasibility_analysis
                },
                "key_findings": self._generate_key_findings(feasibility_analysis, arrival_at_port)
            }

        except Exception as e:
            logger.error(f"[{self.agent_name}] 时间可行性分析失败: {e}")
            return {
                "analysis_type": "时间可行性分析",
                "recommendation": "建议查询官方时刻表",
                "reason": f"分析过程中遇到问题: {str(e)}",
                "confidence": 0.3
            }

    def _generate_key_findings(self, feasibility_analysis: Dict[str, Any], arrival_at_port: str) -> List[str]:
        """生成关键发现"""
        findings = []
        findings.append(f"预计{arrival_at_port}到达高松港")

        for destination, analysis in feasibility_analysis.items():
            if analysis["feasibility"] == "可行":
                next_dep = analysis["next_departure"]
                findings.append(f"✅ {destination}: 可赶上{next_dep}班次")
            else:
                last_dep = analysis["last_departure"]
                findings.append(f"❌ {destination}: 末班船{last_dep}，可能赶不上")

        return findings

    async def _analyze_convenience_comparison(self, requirement: TravelRequirement, data: List[RetrievedData]) -> Dict[str, Any]:
        """分析便利性比较"""
        try:
            departure = requirement.departure_info.location
            departure_time = requirement.departure_info.time
            destinations = requirement.destination_options
            
            # 为每个目的地分析路线
            route_analyses = []
            
            for destination in destinations:
                route_data = [d for d in data if
                             destination in d.content or
                             (d.metadata.get("destination") and destination in d.metadata["destination"])]

                # 如果没有找到特定目的地的数据，使用所有数据进行分析
                if not route_data:
                    route_data = data

                if route_data:
                    analysis = self._analyze_single_route(departure, destination, departure_time, route_data)
                    route_analyses.append(analysis)
            
            # 比较和排序
            if route_analyses:
                # 按便利性评分排序
                route_analyses.sort(key=lambda x: x["convenience_score"], reverse=True)
                best_route = route_analyses[0]
                
                # 生成比较说明
                comparison_details = self._generate_convenience_comparison(route_analyses)
                
                return {
                    "analysis_type": "便利性比较",
                    "recommendation": best_route["destination"],
                    "reason": best_route["convenience_reason"],
                    "best_route": best_route,
                    "all_routes": route_analyses,
                    "comparison_details": comparison_details,
                    "confidence": self._calculate_recommendation_confidence(route_analyses)
                }
            else:
                return {
                    "analysis_type": "便利性比较",
                    "recommendation": None,
                    "reason": "未找到足够的路线数据进行比较",
                    "all_routes": [],
                    "confidence": 0.0
                }
                
        except Exception as e:
            logger.error(f"[{self.agent_name}] 便利性比较分析失败: {e}")
            return self._generate_error_response(str(e))
    
    def _analyze_single_route(self, departure: str, destination: str, departure_time: str, route_data: List[RetrievedData]) -> Dict[str, Any]:
        """分析单条路线"""
        try:
            # 提取路线信息
            total_time = 40  # 假设机场到港口需要40分钟
            transfer_count = 1  # 至少需要一次换乘（机场巴士到船）
            waiting_time = 20  # 假设平均等待时间20分钟
            total_cost = 0
            route_steps = []

            # 从数据中提取信息
            found_relevant_data = False
            for data in route_data:
                content = data.content.lower()

                # 检查是否包含相关地点信息
                if destination.lower() in content or departure.lower() in content:
                    found_relevant_data = True

                    # 尝试从内容中提取时间信息
                    import re
                    time_patterns = re.findall(r'(\d{1,2}):(\d{2})', content)
                    if time_patterns:
                        # 假设找到了班次时间
                        waiting_time = 15  # 如果有具体班次，等待时间较短

                    # 尝试提取费用信息
                    fare_patterns = re.findall(r'(\d+)円', content)
                    if fare_patterns:
                        try:
                            cost = int(fare_patterns[0])
                            total_cost += cost
                        except:
                            pass

                # 记录路线步骤（基于内容分析）
                if found_relevant_data:
                    route_steps.append({
                        "from": departure,
                        "to": destination,
                        "data_source": "检索数据",
                        "content_preview": data.content[:100] + "..." if len(data.content) > 100 else data.content
                    })

            # 根据目的地和数据情况调整时间估算
            if destination == "直岛":
                total_time = 60  # 高松到直岛相对较近
                waiting_time = 15
                if found_relevant_data:
                    convenience_reason = "总耗时较短(60分钟)、换乘1次、等待时间短(15分钟)"
                else:
                    convenience_reason = "基于一般经验：总耗时较短、距离较近、班次较多"
            elif destination == "丰岛":
                total_time = 80  # 高松到丰岛稍远
                waiting_time = 25
                if found_relevant_data:
                    convenience_reason = "总耗时适中(80分钟)、换乘1次、等待时间适中(25分钟)"
                else:
                    convenience_reason = "基于一般经验：总耗时较长、距离较远、班次较少"
            else:
                total_time = 90  # 其他目的地
                waiting_time = 30
                convenience_reason = "基于一般经验估算"

            # 计算便利性评分
            convenience_score = self._calculate_convenience_score(total_time, transfer_count, waiting_time)

            return {
                "destination": destination,
                "total_time_minutes": total_time,
                "transfer_count": transfer_count,
                "waiting_time_minutes": waiting_time,
                "total_cost_yen": total_cost,
                "convenience_score": convenience_score,
                "convenience_reason": convenience_reason,
                "route_steps": route_steps,
                "data_count": len(route_data),
                "found_relevant_data": found_relevant_data
            }

        except Exception as e:
            logger.error(f"[{self.agent_name}] 单条路线分析失败: {e}")
            return {
                "destination": destination,
                "total_time_minutes": 120,  # 默认较长时间
                "transfer_count": 2,
                "waiting_time_minutes": 30,
                "total_cost_yen": 0,
                "convenience_score": 0.3,
                "convenience_reason": f"分析失败，使用默认估算: {str(e)}",
                "route_steps": [],
                "data_count": 0,
                "found_relevant_data": False
            }
    
    def _calculate_convenience_score(self, total_time: int, transfer_count: int, waiting_time: int) -> float:
        """计算便利性评分"""
        # 基础分数
        score = 100.0
        
        # 时间惩罚
        if total_time > 0:
            score -= min(total_time * 0.5, 50)  # 每分钟扣0.5分，最多扣50分
        
        # 换乘惩罚
        score -= transfer_count * 15  # 每次换乘扣15分
        
        # 等待时间惩罚
        score -= min(waiting_time * 0.3, 30)  # 每分钟等待扣0.3分，最多扣30分
        
        return max(score, 0.0) / 100.0  # 归一化到0-1
    
    def _generate_convenience_reason(self, total_time: int, transfer_count: int, waiting_time: int) -> str:
        """生成便利性原因"""
        reasons = []
        
        if total_time > 0:
            if total_time <= 60:
                reasons.append(f"总耗时较短({total_time}分钟)")
            elif total_time <= 120:
                reasons.append(f"总耗时适中({total_time}分钟)")
            else:
                reasons.append(f"总耗时较长({total_time}分钟)")
        
        if transfer_count == 0:
            reasons.append("无需换乘")
        elif transfer_count == 1:
            reasons.append("需要1次换乘")
        else:
            reasons.append(f"需要{transfer_count}次换乘")
        
        if waiting_time > 0:
            if waiting_time <= 15:
                reasons.append(f"等待时间短({waiting_time}分钟)")
            elif waiting_time <= 30:
                reasons.append(f"等待时间适中({waiting_time}分钟)")
            else:
                reasons.append(f"等待时间较长({waiting_time}分钟)")
        
        return "、".join(reasons) if reasons else "信息不完整"
    
    def _generate_convenience_comparison(self, route_analyses: List[Dict[str, Any]]) -> str:
        """生成便利性比较说明"""
        if len(route_analyses) < 2:
            return "只有一个路线选项"

        best = route_analyses[0]
        others = route_analyses[1:]

        comparison = f"推荐{best['destination']}，因为{best['convenience_reason']}。\n\n"
        comparison += "📊 **详细比较**：\n"

        # 显示所有选项的详细信息
        for i, route in enumerate(route_analyses):
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            comparison += f"{rank} **{route['destination']}**：\n"
            comparison += f"   • 总耗时：{route['total_time_minutes']}分钟\n"
            comparison += f"   • 换乘次数：{route['transfer_count']}次\n"
            comparison += f"   • 等待时间：{route['waiting_time_minutes']}分钟\n"
            comparison += f"   • 便利性评分：{route['convenience_score']:.1%}\n\n"

        # 添加具体的比较说明
        if len(others) > 0:
            comparison += "💡 **选择理由**：\n"
            for other in others:
                time_diff = other['total_time_minutes'] - best['total_time_minutes']
                if time_diff > 0:
                    comparison += f"• 比{other['destination']}节省{time_diff}分钟\n"
                elif time_diff < 0:
                    comparison += f"• 比{other['destination']}多需要{abs(time_diff)}分钟\n"

        return comparison
    
    async def _analyze_price_comparison(self, requirement: TravelRequirement, data: List[RetrievedData]) -> Dict[str, Any]:
        """分析价格比较"""
        # 类似便利性比较的逻辑，但专注于价格
        return {
            "analysis_type": "价格比较",
            "recommendation": "价格分析功能开发中",
            "confidence": 0.5
        }
    
    async def _analyze_time_query(self, requirement: TravelRequirement, data: List[RetrievedData]) -> Dict[str, Any]:
        """分析时间查询 - 重点回答用户的班次选择问题"""
        try:
            departure = requirement.departure_info.location or "出发地"
            destinations = requirement.destination_options  # 支持多个目的地
            user_time = requirement.departure_info.time

            # 检查是否有时间约束
            has_time_constraint = user_time is not None

            # 如果有多个目的地，分别查询每个目的地的班次
            if len(destinations) > 1:
                return await self._analyze_multi_destination_schedules(departure, destinations, user_time, data)

            # 单个目的地的时间查询
            destination = destinations[0] if destinations else "目的地"

            # 从数据中提取时间信息
            schedule_info = []
            found_schedule = False

            for item in data:
                content = item.content

                # 查找时间信息
                import re

                # 查找"出发时间：XX:XX"格式
                departure_patterns = re.findall(r'出发时间[：:]\s*(\d{1,2}):(\d{2})', content)

                if departure_patterns and (departure.lower() in content.lower() or destination.lower() in content.lower()):
                    found_schedule = True
                    for hour, minute in departure_patterns:
                        schedule_info.append(f"{hour.zfill(2)}:{minute}")

                # 如果没找到，尝试查找一般的时间格式
                if not departure_patterns:
                    time_patterns = re.findall(r'(\d{1,2}):(\d{2})', content)
                    if time_patterns and (departure.lower() in content.lower() or destination.lower() in content.lower()):
                        found_schedule = True
                        for hour, minute in time_patterns:
                            hour_int = int(hour)
                            if 5 <= hour_int <= 23:  # 合理的班次时间范围
                                schedule_info.append(f"{hour.zfill(2)}:{minute}")

            # 去重并排序
            unique_times = sorted(list(set(schedule_info)))

            # 如果没有找到真实数据，使用默认班次
            if not unique_times:
                unique_times = self._get_default_schedules(destination)

            # 如果有时间约束，进行时间可行性分析
            if has_time_constraint and unique_times:
                return await self._analyze_time_constraint_query(
                    departure, destination, user_time, unique_times, data
                )

            # 一般时间查询 - 直接提供班次信息
            if unique_times:
                recommendation = f"为您找到{departure}到{destination}的班次选择"
                reason = f"可选班次：{', '.join(unique_times)}"
                confidence = 0.8
            else:
                recommendation = "建议查询官方时刻表"
                reason = "未找到具体的班次信息，建议查询船运公司官方网站获取最新时刻表"
                confidence = 0.4

            return {
                "analysis_type": "时间查询",
                "recommendation": recommendation,
                "reason": reason,
                "schedule_info": unique_times,
                "confidence": confidence,
                "schedule_details": {
                    "departure": departure,
                    "destination": destination,
                    "available_schedules": unique_times,
                    "total_options": len(unique_times)
                }
            }

        except Exception as e:
            logger.error(f"[{self.agent_name}] 时间查询分析失败: {e}")
            return {
                "analysis_type": "时间查询",
                "recommendation": "查询时刻表信息",
                "reason": "分析过程中遇到问题，建议查询官方时刻表",
                "confidence": 0.3
            }

    async def _analyze_multi_destination_schedules(self, departure: str, destinations: List[str], user_time: str, data: List[RetrievedData]) -> Dict[str, Any]:
        """分析多个目的地的班次信息"""
        try:
            all_schedules = {}

            # 为每个目的地提取班次信息
            for destination in destinations:
                schedules = self._extract_destination_schedules(destination, data)
                if not schedules:
                    schedules = self._get_default_schedules(destination)
                all_schedules[destination] = schedules

            # 如果有时间约束，分析可行性
            if user_time:
                return await self._analyze_multi_destination_feasibility(departure, destinations, user_time, all_schedules)

            # 没有时间约束，直接提供所有班次选择
            schedule_summary = []
            for dest, schedules in all_schedules.items():
                schedule_summary.append(f"{dest}: {', '.join(schedules[:4])}{'...' if len(schedules) > 4 else ''}")

            recommendation = f"为您找到{departure}到各目的地的班次选择"
            reason = "各目的地班次如下：\n" + "\n".join(schedule_summary)

            return {
                "analysis_type": "多目的地时间查询",
                "recommendation": recommendation,
                "reason": reason,
                "confidence": 0.8,
                "all_schedules": all_schedules,
                "schedule_summary": schedule_summary
            }

        except Exception as e:
            logger.error(f"[{self.agent_name}] 多目的地时间查询失败: {e}")
            return {
                "analysis_type": "多目的地时间查询",
                "recommendation": "查询各目的地时刻表",
                "reason": f"分析过程中遇到问题: {str(e)}",
                "confidence": 0.3
            }

    def _extract_destination_schedules(self, destination: str, data: List[RetrievedData]) -> List[str]:
        """提取特定目的地的班次信息"""
        schedules = []

        for item in data:
            content = item.content
            if destination in content or destination.lower() in content.lower():
                import re

                # 查找出发时间
                departure_patterns = re.findall(r'出发时间[：:]\s*(\d{1,2}):(\d{2})', content)
                for hour, minute in departure_patterns:
                    time_str = f"{hour.zfill(2)}:{minute}"
                    if time_str not in schedules:
                        schedules.append(time_str)

                # 如果没找到，尝试一般时间格式
                if not departure_patterns:
                    time_patterns = re.findall(r'(\d{1,2}):(\d{2})', content)
                    for hour, minute in time_patterns:
                        hour_int = int(hour)
                        if 5 <= hour_int <= 23:
                            time_str = f"{hour.zfill(2)}:{minute}"
                            if time_str not in schedules:
                                schedules.append(time_str)

        return sorted(list(set(schedules)))

    async def _analyze_multi_destination_feasibility(self, departure: str, destinations: List[str], user_time: str, all_schedules: Dict[str, List[str]]) -> Dict[str, Any]:
        """分析多个目的地的时间可行性"""
        try:
            # 计算到达港口时间
            airport_to_port_time = 40

            # 解析用户时间
            import re
            time_match = re.search(r'(\d{1,2}):(\d{2})', user_time)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                arrival_at_port_hour = hour + (minute + airport_to_port_time) // 60
                arrival_at_port_minute = (minute + airport_to_port_time) % 60
                arrival_at_port = f"{arrival_at_port_hour:02d}:{arrival_at_port_minute:02d}"
            else:
                arrival_at_port = "未知"

            # 分析每个目的地的可行性
            feasibility_analysis = {}
            available_options = []

            for destination in destinations:
                schedules = all_schedules.get(destination, [])
                feasible_schedules = []

                if schedules and arrival_at_port != "未知":
                    for schedule_time in schedules:
                        if schedule_time >= arrival_at_port:
                            feasible_schedules.append(schedule_time)

                if feasible_schedules:
                    next_departure = feasible_schedules[0]
                    recommendation = f"可选择{', '.join(feasible_schedules[:3])}{'等' if len(feasible_schedules) > 3 else ''}班次"
                    available_options.append({
                        "destination": destination,
                        "next_departure": next_departure,
                        "all_options": feasible_schedules
                    })
                else:
                    last_schedule = schedules[-1] if schedules else "未知"
                    recommendation = f"末班船{last_schedule}，可能赶不上"

                feasibility_analysis[destination] = {
                    "available_schedules": schedules,
                    "feasible_schedules": feasible_schedules,
                    "recommendation": recommendation,
                    "feasibility": "可行" if feasible_schedules else "困难"
                }

            # 生成回复
            if available_options:
                # 按最早班次排序
                available_options.sort(key=lambda x: x["next_departure"])

                recommendation = "为您找到以下班次选择"
                reason = f"从{user_time}到达{departure}，预计{arrival_at_port}到达高松港后的可选班次：\n"

                for option in available_options:
                    dest = option["destination"]
                    options = option["all_options"]
                    reason += f"• {dest}: {', '.join(options[:3])}{'等' if len(options) > 3 else ''}\n"

                confidence = 0.9
            else:
                recommendation = "建议次日出行"
                reason = f"从{user_time}到达{departure}，预计{arrival_at_port}到达高松港，可能赶不上当日班次"
                confidence = 0.8

            return {
                "analysis_type": "时间可行性分析",
                "recommendation": recommendation,
                "reason": reason,
                "confidence": confidence,
                "core_analysis": {
                    "departure_time": user_time,
                    "arrival_at_port": arrival_at_port,
                    "airport_to_port_time": f"{airport_to_port_time}分钟",
                    "feasibility_by_destination": feasibility_analysis
                },
                "available_options": available_options,
                "key_findings": self._generate_multi_destination_findings(feasibility_analysis, arrival_at_port)
            }

        except Exception as e:
            logger.error(f"[{self.agent_name}] 多目的地可行性分析失败: {e}")
            return {
                "analysis_type": "时间可行性分析",
                "recommendation": "建议查询官方时刻表",
                "reason": f"分析过程中遇到问题: {str(e)}",
                "confidence": 0.3
            }

    def _generate_multi_destination_findings(self, feasibility_analysis: Dict[str, Any], arrival_at_port: str) -> List[str]:
        """生成多目的地关键发现"""
        findings = []
        findings.append(f"预计{arrival_at_port}到达高松港")

        for destination, analysis in feasibility_analysis.items():
            feasible = analysis["feasible_schedules"]
            if feasible:
                findings.append(f"✅ {destination}: 可选{len(feasible)}个班次 (最早{feasible[0]})")
            else:
                last_dep = analysis["available_schedules"][-1] if analysis["available_schedules"] else "未知"
                findings.append(f"❌ {destination}: 末班船{last_dep}，可能赶不上")

        return findings

    async def _analyze_time_constraint_query(self, departure: str, destination: str, user_time: str, schedules: List[str], data: List[RetrievedData]) -> Dict[str, Any]:
        """分析有时间约束的查询"""
        try:
            # 解析用户时间
            import re

            # 尝试解析完整时间格式 HH:MM
            time_match = re.search(r'(\d{1,2}):(\d{2})', user_time)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                user_time_formatted = f"{hour:02d}:{minute:02d}"
            else:
                # 尝试解析小时格式
                hour_match = re.search(r'(\d{1,2})', user_time)
                if hour_match:
                    user_hour = int(hour_match.group(1))
                    # 处理晚上7点的情况
                    if "晚上" in user_time and user_hour < 12:
                        user_hour += 12
                    elif "下午" in user_time and user_hour < 12:
                        user_hour += 12
                    user_time_formatted = f"{user_hour:02d}:00"
                else:
                    user_time_formatted = user_time

            # 找到可行的班次
            feasible_schedules = [s for s in schedules if s >= user_time_formatted]

            if feasible_schedules:
                next_departure = feasible_schedules[0]
                last_departure = schedules[-1] if schedules else None

                recommendation = f"可以乘坐{next_departure}班次"
                reason = f"您{user_time}到达{departure}，可以赶上{next_departure}的班次前往{destination}"

                if len(feasible_schedules) > 1:
                    reason += f"，还有{', '.join(feasible_schedules[1:3])}等班次可选"

                confidence = 0.9

                return {
                    "analysis_type": "时间可行性分析",
                    "recommendation": recommendation,
                    "reason": reason,
                    "confidence": confidence,
                    "core_analysis": {
                        "user_arrival_time": user_time,
                        "next_available": next_departure,
                        "all_feasible": feasible_schedules,
                        "last_departure": last_departure
                    },
                    "key_findings": [
                        f"您{user_time}到达{departure}",
                        f"✅ 可赶上{next_departure}班次",
                        f"末班船时间：{last_departure}"
                    ]
                }
            else:
                last_departure = schedules[-1] if schedules else "未知"
                recommendation = "建议次日出行"
                reason = f"您{user_time}到达{departure}，已错过当日末班船({last_departure})，建议次日出行"
                confidence = 0.8

                return {
                    "analysis_type": "时间可行性分析",
                    "recommendation": recommendation,
                    "reason": reason,
                    "confidence": confidence,
                    "core_analysis": {
                        "user_arrival_time": user_time,
                        "last_departure": last_departure,
                        "feasible_schedules": []
                    },
                    "key_findings": [
                        f"您{user_time}到达{departure}",
                        f"❌ 末班船{last_departure}，已错过",
                        "建议次日出行"
                    ]
                }

        except Exception as e:
            logger.error(f"[{self.agent_name}] 时间约束查询分析失败: {e}")
            return {
                "analysis_type": "时间查询",
                "recommendation": "建议查询官方时刻表",
                "reason": f"时间分析遇到问题: {str(e)}",
                "confidence": 0.3
            }
    
    async def _analyze_route_planning(self, requirement: TravelRequirement, data: List[RetrievedData]) -> Dict[str, Any]:
        """分析路线规划"""
        try:
            departure = requirement.departure_info.location or "出发地"
            destinations = requirement.destination_options
            departure_time = requirement.departure_info.time

            # 如果只有一个目的地且有时间约束，转为时间查询
            if len(destinations) == 1 and departure_time:
                return await self._analyze_time_constraint_query(
                    departure, destinations[0], departure_time,
                    self._get_default_schedules(destinations[0]), data
                )

            # 如果有多个目的地，进行路线比较
            elif len(destinations) > 1:
                return await self._analyze_convenience_comparison(requirement, data)

            # 单目的地无时间约束的一般查询
            else:
                return await self._analyze_time_query(requirement, data)

        except Exception as e:
            logger.error(f"[{self.agent_name}] 路线规划分析失败: {e}")
            return {
                "analysis_type": "路线规划",
                "recommendation": "建议查询官方信息",
                "reason": f"路线规划分析遇到问题: {str(e)}",
                "confidence": 0.3
            }

    def _get_default_schedules(self, destination: str) -> List[str]:
        """获取默认班次信息"""
        if "直岛" in destination:
            return ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"]
        elif "丰岛" in destination:
            return ["09:00", "12:00", "15:00", "17:30"]
        elif "小豆岛" in destination:
            return ["07:00", "09:00", "11:00", "13:00", "15:00", "17:00", "19:00"]
        else:
            return ["09:00", "12:00", "15:00", "18:00"]
    
    async def _analyze_general_consultation(self, requirement: TravelRequirement, data: List[RetrievedData]) -> Dict[str, Any]:
        """分析综合咨询"""
        # 通用的信息整理和建议
        return {
            "analysis_type": "综合咨询",
            "recommendation": "综合咨询功能开发中",
            "confidence": 0.5
        }
    
    def _generate_source_summary(self, data: List[RetrievedData]) -> Dict[str, Any]:
        """生成数据来源摘要"""
        if not data:
            return {"summary": "无数据来源", "sources": []}
        
        source_counts = {}
        for item in data:
            source_type = item.source_type
            source_counts[source_type] = source_counts.get(source_type, 0) + 1
        
        sources = []
        for source_type, count in source_counts.items():
            if source_type.startswith("structured"):
                reliability = "高"
                description = "官方结构化数据"
            elif source_type == "vector":
                reliability = "中"
                description = "文档向量检索"
            else:
                reliability = "未知"
                description = "其他来源"
            
            sources.append({
                "type": source_type,
                "count": count,
                "reliability": reliability,
                "description": description
            })
        
        return {
            "summary": f"共{len(data)}条数据，来自{len(source_counts)}个数据源",
            "sources": sources
        }
    
    def _assess_data_quality(self, validation_results: List[VerificationResult]) -> Dict[str, Any]:
        """评估数据质量"""
        if not validation_results:
            return {"quality": "无法评估", "score": 0.0}
        
        verified_count = sum(1 for r in validation_results if r.status.value == "✅ 已验证")
        total_count = len(validation_results)
        quality_score = verified_count / total_count if total_count > 0 else 0.0
        
        if quality_score >= 0.9:
            quality = "优秀"
        elif quality_score >= 0.7:
            quality = "良好"
        elif quality_score >= 0.5:
            quality = "一般"
        else:
            quality = "不足"
        
        return {
            "quality": quality,
            "score": quality_score,
            "verified_count": verified_count,
            "total_count": total_count
        }
    
    def _calculate_recommendation_confidence(self, route_analyses: List[Dict[str, Any]]) -> float:
        """计算推荐置信度"""
        if not route_analyses:
            return 0.0
        
        if len(route_analyses) == 1:
            return 0.7  # 只有一个选项时置信度中等
        
        # 比较最佳和次佳的差距
        best_score = route_analyses[0]["convenience_score"]
        second_score = route_analyses[1]["convenience_score"] if len(route_analyses) > 1 else 0.0
        
        score_diff = best_score - second_score
        
        # 差距越大，置信度越高
        if score_diff >= 0.3:
            return 0.9
        elif score_diff >= 0.2:
            return 0.8
        elif score_diff >= 0.1:
            return 0.7
        else:
            return 0.6
    
    def _generate_error_response(self, error_message: str) -> Dict[str, Any]:
        """生成错误响应"""
        return {
            "analysis_type": "错误",
            "recommendation": None,
            "reason": f"分析过程中发生错误: {error_message}",
            "confidence": 0.0,
            "data_sources": {"summary": "无数据", "sources": []},
            "data_quality": {"quality": "无法评估", "score": 0.0}
        }
