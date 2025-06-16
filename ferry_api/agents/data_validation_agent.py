"""
数据验证Agent - 第4层：验证数据完整性和来源，不是验证对错
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .state_models import RetrievedData, VerificationResult, VerificationStatus

logger = logging.getLogger(__name__)

class DataValidationAgent:
    """数据验证Agent - 专注于数据源和完整性检查"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.agent_name = "DataValidationAgent"
    
    async def validate_data_completeness(self, retrieved_data: List[RetrievedData]) -> List[VerificationResult]:
        """验证数据完整性和来源"""
        try:
            logger.info(f"[{self.agent_name}] 开始验证 {len(retrieved_data)} 条数据的完整性")
            
            validation_results = []
            
            for data in retrieved_data:
                # 验证数据来源
                source_validation = self._validate_data_source(data)
                validation_results.append(source_validation)
                
                # 验证数据完整性
                completeness_validation = self._validate_data_completeness_single(data)
                validation_results.append(completeness_validation)
                
                # 验证数据时效性
                timeliness_validation = self._validate_data_timeliness(data)
                validation_results.append(timeliness_validation)
            
            logger.info(f"[{self.agent_name}] 数据验证完成，生成 {len(validation_results)} 个验证结果")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 数据验证失败: {e}")
            return []
    
    def _validate_data_source(self, data: RetrievedData) -> VerificationResult:
        """验证数据来源"""
        try:
            source_type = data.source_type
            metadata = data.metadata
            
            # 根据数据来源类型进行验证
            if source_type.startswith("structured"):
                return VerificationResult(
                    fact=f"数据来源: {source_type}",
                    status=VerificationStatus.VERIFIED,
                    supporting_data=[data],
                    confidence_score=0.95,
                    verification_details=f"来源: 结构化数据库 | 类型: {metadata.get('type', '未知')} | 可信度: 高"
                )
            elif source_type == "vector":
                return VerificationResult(
                    fact=f"数据来源: 向量数据库",
                    status=VerificationStatus.VERIFIED,
                    supporting_data=[data],
                    confidence_score=0.8,
                    verification_details=f"来源: 向量数据库 | 相关性: {data.relevance_score:.2f} | 可信度: 中等"
                )
            else:
                return VerificationResult(
                    fact=f"数据来源: {source_type}",
                    status=VerificationStatus.UNVERIFIED,
                    supporting_data=[data],
                    confidence_score=0.5,
                    verification_details=f"来源: 未知类型 ({source_type}) | 可信度: 低"
                )
                
        except Exception as e:
            logger.error(f"[{self.agent_name}] 数据来源验证失败: {e}")
            return VerificationResult(
                fact="数据来源验证",
                status=VerificationStatus.UNVERIFIED,
                supporting_data=[data],
                confidence_score=0.0,
                verification_details=f"验证过程出错: {str(e)}"
            )
    
    def _validate_data_completeness_single(self, data: RetrievedData) -> VerificationResult:
        """验证单条数据的完整性"""
        try:
            content = data.content
            metadata = data.metadata
            
            # 检查关键字段
            missing_fields = []
            completeness_score = 1.0
            
            # 根据数据类型检查不同的字段
            data_type = metadata.get("type", "")
            
            if data_type == "route_schedule":
                required_fields = ["departure", "destination", "departure_time"]
                optional_fields = ["arrival_time", "duration", "fare", "company"]
                
                for field in required_fields:
                    if not metadata.get(field):
                        missing_fields.append(field)
                        completeness_score -= 0.3
                
                for field in optional_fields:
                    if not metadata.get(field):
                        completeness_score -= 0.1
            
            elif data_type == "price_info":
                if not metadata.get("fare"):
                    missing_fields.append("fare")
                    completeness_score -= 0.5
            
            elif data_type == "port_info":
                if not metadata.get("port_name"):
                    missing_fields.append("port_name")
                    completeness_score -= 0.4
            
            # 检查内容长度
            if len(content.strip()) < 10:
                missing_fields.append("详细内容")
                completeness_score -= 0.2
            
            completeness_score = max(completeness_score, 0.0)
            
            # 生成验证结果
            if completeness_score >= 0.8:
                status = VerificationStatus.VERIFIED
                details = f"数据完整性: 优秀 ({completeness_score:.1%})"
            elif completeness_score >= 0.6:
                status = VerificationStatus.VERIFIED
                details = f"数据完整性: 良好 ({completeness_score:.1%})"
            elif completeness_score >= 0.4:
                status = VerificationStatus.UNVERIFIED
                details = f"数据完整性: 一般 ({completeness_score:.1%}) | 缺失字段: {', '.join(missing_fields)}"
            else:
                status = VerificationStatus.INSUFFICIENT
                details = f"数据完整性: 不足 ({completeness_score:.1%}) | 缺失字段: {', '.join(missing_fields)}"
            
            return VerificationResult(
                fact=f"数据完整性检查",
                status=status,
                supporting_data=[data],
                confidence_score=completeness_score,
                verification_details=details
            )
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 数据完整性验证失败: {e}")
            return VerificationResult(
                fact="数据完整性检查",
                status=VerificationStatus.UNVERIFIED,
                supporting_data=[data],
                confidence_score=0.0,
                verification_details=f"验证过程出错: {str(e)}"
            )
    
    def _validate_data_timeliness(self, data: RetrievedData) -> VerificationResult:
        """验证数据时效性"""
        try:
            timestamp_str = data.timestamp
            
            if not timestamp_str:
                return VerificationResult(
                    fact="数据时效性",
                    status=VerificationStatus.UNVERIFIED,
                    supporting_data=[data],
                    confidence_score=0.5,
                    verification_details="无时间戳信息"
                )
            
            try:
                data_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                current_time = datetime.now()
                time_diff = current_time - data_time.replace(tzinfo=None)
                
                # 根据时间差判断时效性
                if time_diff < timedelta(minutes=5):
                    status = VerificationStatus.VERIFIED
                    confidence = 0.95
                    details = f"数据时效性: 最新 (检索于 {time_diff.seconds//60} 分钟前)"
                elif time_diff < timedelta(hours=1):
                    status = VerificationStatus.VERIFIED
                    confidence = 0.9
                    details = f"数据时效性: 较新 (检索于 {time_diff.seconds//60} 分钟前)"
                elif time_diff < timedelta(hours=24):
                    status = VerificationStatus.VERIFIED
                    confidence = 0.8
                    details = f"数据时效性: 当日 (检索于 {time_diff.seconds//3600} 小时前)"
                else:
                    status = VerificationStatus.UNVERIFIED
                    confidence = 0.6
                    details = f"数据时效性: 较旧 (检索于 {time_diff.days} 天前)"
                
                return VerificationResult(
                    fact="数据时效性",
                    status=status,
                    supporting_data=[data],
                    confidence_score=confidence,
                    verification_details=details
                )
                
            except ValueError as e:
                return VerificationResult(
                    fact="数据时效性",
                    status=VerificationStatus.UNVERIFIED,
                    supporting_data=[data],
                    confidence_score=0.3,
                    verification_details=f"时间戳格式错误: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"[{self.agent_name}] 数据时效性验证失败: {e}")
            return VerificationResult(
                fact="数据时效性",
                status=VerificationStatus.UNVERIFIED,
                supporting_data=[data],
                confidence_score=0.0,
                verification_details=f"验证过程出错: {str(e)}"
            )
    
    def calculate_overall_data_quality(self, validation_results: List[VerificationResult]) -> Dict[str, Any]:
        """计算总体数据质量"""
        if not validation_results:
            return {
                "overall_quality": 0.0,
                "source_reliability": 0.0,
                "completeness_rate": 0.0,
                "timeliness_rate": 0.0,
                "verified_count": 0,
                "total_count": 0,
                "quality_summary": "无数据"
            }
        
        # 按验证类型分组
        source_results = [r for r in validation_results if "数据来源" in r.fact]
        completeness_results = [r for r in validation_results if "完整性" in r.fact]
        timeliness_results = [r for r in validation_results if "时效性" in r.fact]
        
        # 计算各项指标
        source_reliability = self._calculate_average_confidence(source_results)
        completeness_rate = self._calculate_average_confidence(completeness_results)
        timeliness_rate = self._calculate_average_confidence(timeliness_results)
        
        # 计算总体质量
        overall_quality = (source_reliability * 0.4 + completeness_rate * 0.4 + timeliness_rate * 0.2)
        
        # 统计验证状态
        verified_count = sum(1 for r in validation_results if r.status == VerificationStatus.VERIFIED)
        total_count = len(validation_results)
        
        # 生成质量摘要
        if overall_quality >= 0.9:
            quality_summary = "数据质量优秀"
        elif overall_quality >= 0.8:
            quality_summary = "数据质量良好"
        elif overall_quality >= 0.6:
            quality_summary = "数据质量一般"
        else:
            quality_summary = "数据质量不足"
        
        return {
            "overall_quality": overall_quality,
            "source_reliability": source_reliability,
            "completeness_rate": completeness_rate,
            "timeliness_rate": timeliness_rate,
            "verified_count": verified_count,
            "total_count": total_count,
            "quality_summary": quality_summary
        }
    
    def _calculate_average_confidence(self, results: List[VerificationResult]) -> float:
        """计算平均置信度"""
        if not results:
            return 0.0
        
        total_confidence = sum(r.confidence_score for r in results)
        return total_confidence / len(results)
    
    def generate_data_source_report(self, retrieved_data: List[RetrievedData]) -> Dict[str, Any]:
        """生成数据来源报告"""
        if not retrieved_data:
            return {"sources": [], "summary": "无数据"}
        
        # 按来源类型统计
        source_stats = {}
        for data in retrieved_data:
            source_type = data.source_type
            if source_type not in source_stats:
                source_stats[source_type] = {
                    "count": 0,
                    "avg_relevance": 0.0,
                    "data_types": set()
                }
            
            source_stats[source_type]["count"] += 1
            source_stats[source_type]["avg_relevance"] += data.relevance_score
            source_stats[source_type]["data_types"].add(data.metadata.get("type", "未知"))
        
        # 计算平均相关性
        for source_type in source_stats:
            count = source_stats[source_type]["count"]
            source_stats[source_type]["avg_relevance"] /= count
            source_stats[source_type]["data_types"] = list(source_stats[source_type]["data_types"])
        
        # 生成摘要
        total_sources = len(source_stats)
        total_data = len(retrieved_data)
        
        summary = f"共检索到 {total_data} 条数据，来自 {total_sources} 个数据源"
        
        return {
            "sources": source_stats,
            "total_data_count": total_data,
            "total_source_count": total_sources,
            "summary": summary
        }
