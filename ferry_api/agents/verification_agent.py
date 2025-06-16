"""
验证Agent - 第4层：验证检索到的信息和AI回复的准确性
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .state_models import RetrievedData, VerificationResult, VerificationStatus

logger = logging.getLogger(__name__)

class VerificationAgent:
    """验证Agent"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.agent_name = "VerificationAgent"
        
        # 缓存验证数据
        self._verification_cache = {}
    
    async def verify_retrieved_data(self, retrieved_data: List[RetrievedData]) -> List[VerificationResult]:
        """验证检索到的数据"""
        try:
            logger.info(f"[{self.agent_name}] 开始验证 {len(retrieved_data)} 条检索数据")
            
            verification_results = []
            
            for data in retrieved_data:
                # 验证数据完整性
                result = await self._verify_data_integrity(data)
                verification_results.append(result)
            
            logger.info(f"[{self.agent_name}] 数据验证完成")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 数据验证失败: {e}")
            return []
    
    async def verify_response_facts(self, response_text: str, source_data: List[RetrievedData]) -> List[VerificationResult]:
        """验证回复中的事实声明"""
        try:
            logger.info(f"[{self.agent_name}] 开始验证回复事实")
            
            # 提取回复中的事实声明
            facts = self._extract_facts_from_response(response_text)
            
            verification_results = []
            
            for fact in facts:
                # 验证每个事实
                result = await self._verify_fact_against_data(fact, source_data)
                verification_results.append(result)
            
            logger.info(f"[{self.agent_name}] 回复验证完成，验证了 {len(facts)} 个事实")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 回复验证失败: {e}")
            return []
    
    async def _verify_data_integrity(self, data: RetrievedData) -> VerificationResult:
        """验证数据完整性"""
        try:
            # 检查数据来源
            if data.source_type == "vector":
                return await self._verify_vector_data(data)
            elif data.source_type.startswith("structured"):
                return await self._verify_structured_data(data)
            else:
                return VerificationResult(
                    fact=f"数据来源: {data.source_type}",
                    status=VerificationStatus.UNVERIFIED,
                    supporting_data=[data],
                    confidence_score=0.5,
                    verification_details="未知数据来源类型"
                )
                
        except Exception as e:
            logger.error(f"[{self.agent_name}] 数据完整性验证失败: {e}")
            return VerificationResult(
                fact="数据完整性",
                status=VerificationStatus.UNVERIFIED,
                supporting_data=[data],
                confidence_score=0.0,
                verification_details=f"验证过程出错: {str(e)}"
            )
    
    async def _verify_vector_data(self, data: RetrievedData) -> VerificationResult:
        """验证向量数据"""
        # 向量数据通常来自预处理的文档，相对可信
        confidence = 0.8 if data.relevance_score > 0.7 else 0.6
        
        return VerificationResult(
            fact=f"向量检索数据: {data.content[:50]}...",
            status=VerificationStatus.VERIFIED if confidence > 0.7 else VerificationStatus.UNVERIFIED,
            supporting_data=[data],
            confidence_score=confidence,
            verification_details=f"向量数据，相关性评分: {data.relevance_score}"
        )
    
    async def _verify_structured_data(self, data: RetrievedData) -> VerificationResult:
        """验证结构化数据"""
        # 结构化数据来自原始数据库，高度可信
        return VerificationResult(
            fact=f"结构化数据: {data.content[:50]}...",
            status=VerificationStatus.VERIFIED,
            supporting_data=[data],
            confidence_score=0.95,
            verification_details="来自结构化数据库，高度可信"
        )
    
    def _extract_facts_from_response(self, response_text: str) -> List[str]:
        """从回复中提取事实声明"""
        facts = []
        
        # 提取时间信息
        time_pattern = r'\b\d{1,2}:\d{2}\b'
        times = re.findall(time_pattern, response_text)
        for time in times:
            facts.append(f"时间: {time}")
        
        # 提取价格信息
        price_pattern = r'\d+円'
        prices = re.findall(price_pattern, response_text)
        for price in prices:
            facts.append(f"价格: {price}")
        
        # 提取公司信息
        company_keywords = ['四国汽船', '豊島フェリー', '小豆島豊島フェリー', 'ジャンボフェリー']
        for company in company_keywords:
            if company in response_text:
                facts.append(f"公司: {company}")
        
        # 提取路线信息
        route_pattern = r'([^→\s]+)→([^→\s]+)'
        routes = re.findall(route_pattern, response_text)
        for departure, arrival in routes:
            facts.append(f"路线: {departure}→{arrival}")
        
        # 提取港口信息
        port_keywords = ['高松', '直岛', '直島', '豊岛', '豊島', '犬岛', '犬島', '小豆岛', '小豆島', '宇野']
        for port in port_keywords:
            if port in response_text:
                facts.append(f"港口: {port}")
        
        return facts
    
    async def _verify_fact_against_data(self, fact: str, source_data: List[RetrievedData]) -> VerificationResult:
        """根据源数据验证事实"""
        try:
            # 解析事实类型和值
            fact_type, fact_value = self._parse_fact(fact)
            
            # 在源数据中查找支持证据
            supporting_data = []
            confidence_scores = []
            
            for data in source_data:
                if self._fact_supported_by_data(fact_type, fact_value, data):
                    supporting_data.append(data)
                    confidence_scores.append(data.relevance_score)
            
            # 计算总体置信度
            if supporting_data:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                status = VerificationStatus.VERIFIED if avg_confidence > 0.7 else VerificationStatus.UNVERIFIED
                verification_details = f"找到 {len(supporting_data)} 条支持数据"
            else:
                avg_confidence = 0.0
                status = VerificationStatus.UNVERIFIED
                verification_details = "未找到支持数据"
            
            return VerificationResult(
                fact=fact,
                status=status,
                supporting_data=supporting_data,
                confidence_score=avg_confidence,
                verification_details=verification_details
            )
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 事实验证失败: {e}")
            return VerificationResult(
                fact=fact,
                status=VerificationStatus.UNVERIFIED,
                supporting_data=[],
                confidence_score=0.0,
                verification_details=f"验证过程出错: {str(e)}"
            )
    
    def _parse_fact(self, fact: str) -> tuple:
        """解析事实类型和值"""
        if fact.startswith("时间:"):
            return "time", fact.replace("时间:", "").strip()
        elif fact.startswith("价格:"):
            return "price", fact.replace("价格:", "").strip()
        elif fact.startswith("公司:"):
            return "company", fact.replace("公司:", "").strip()
        elif fact.startswith("路线:"):
            return "route", fact.replace("路线:", "").strip()
        elif fact.startswith("港口:"):
            return "port", fact.replace("港口:", "").strip()
        else:
            return "unknown", fact
    
    def _fact_supported_by_data(self, fact_type: str, fact_value: str, data: RetrievedData) -> bool:
        """检查事实是否被数据支持"""
        content_lower = data.content.lower()
        value_lower = fact_value.lower()
        
        if fact_type == "time":
            # 检查时间格式
            return fact_value in data.content
        elif fact_type == "price":
            # 检查价格
            return fact_value in data.content
        elif fact_type == "company":
            # 检查公司名称
            return value_lower in content_lower
        elif fact_type == "route":
            # 检查路线
            return value_lower in content_lower or "→" in data.content
        elif fact_type == "port":
            # 检查港口
            return value_lower in content_lower
        else:
            # 通用文本匹配
            return value_lower in content_lower
    
    def calculate_overall_accuracy(self, verification_results: List[VerificationResult]) -> float:
        """计算总体准确率"""
        if not verification_results:
            return 0.0
        
        verified_count = sum(1 for result in verification_results 
                           if result.status == VerificationStatus.VERIFIED)
        
        return verified_count / len(verification_results)
    
    def generate_verification_summary(self, verification_results: List[VerificationResult]) -> Dict[str, Any]:
        """生成验证摘要"""
        total_facts = len(verification_results)
        verified_facts = [r for r in verification_results if r.status == VerificationStatus.VERIFIED]
        unverified_facts = [r for r in verification_results if r.status == VerificationStatus.UNVERIFIED]
        
        return {
            "total_facts": total_facts,
            "verified_count": len(verified_facts),
            "unverified_count": len(unverified_facts),
            "accuracy_rate": len(verified_facts) / total_facts if total_facts > 0 else 0.0,
            "verified_facts": [r.fact for r in verified_facts],
            "unverified_facts": [r.fact for r in unverified_facts]
        }
