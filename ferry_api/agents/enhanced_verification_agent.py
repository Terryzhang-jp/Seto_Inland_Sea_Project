"""
增强版验证Agent - 更精确的准确率验证
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from .state_models import RetrievedData, VerificationResult, VerificationStatus

logger = logging.getLogger(__name__)

class EnhancedVerificationAgent:
    """增强版验证Agent"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.agent_name = "EnhancedVerificationAgent"
        
        # 预加载验证数据
        self._ferry_routes = None
        self._ports = None
        self._companies = None
    
    async def verify_response_accuracy(self, response_text: str, source_data: List[RetrievedData]) -> List[VerificationResult]:
        """验证回复准确性 - 主要方法"""
        try:
            logger.info(f"[{self.agent_name}] 开始验证回复准确性")
            
            # 1. 提取回复中的所有事实声明
            extracted_facts = self._extract_detailed_facts(response_text)
            logger.info(f"[{self.agent_name}] 提取到 {len(extracted_facts)} 个事实")
            
            # 2. 验证每个事实
            verification_results = []
            for fact in extracted_facts:
                result = await self._verify_fact_with_context(fact, source_data, response_text)
                verification_results.append(result)
            
            # 3. 特殊验证：检查是否有编造信息
            fabrication_check = self._check_for_fabrication(response_text, source_data)
            if fabrication_check:
                verification_results.append(fabrication_check)
            
            logger.info(f"[{self.agent_name}] 验证完成，总计 {len(verification_results)} 项")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 验证失败: {e}")
            return []
    
    def _extract_detailed_facts(self, response_text: str) -> List[Dict[str, Any]]:
        """详细提取事实声明"""
        facts = []
        
        # 1. 提取具体的船班时间
        time_patterns = [
            r'(\d{1,2}:\d{2})',  # 基本时间格式
            r'(\d{1,2}时\d{2}分)',  # 中文时间格式
            r'(上午|下午|早上|晚上)\s*(\d{1,2}:\d{2})',  # 带时段的时间
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, response_text)
            for match in matches:
                time_str = match if isinstance(match, str) else ' '.join(match)
                facts.append({
                    "type": "time",
                    "value": time_str,
                    "context": self._get_context(response_text, time_str),
                    "confidence_required": 0.6  # 降低时间验证要求
                })
        
        # 2. 提取价格信息
        price_patterns = [
            r'(\d+)円',  # 日元价格
            r'(\d+)元',  # 人民币价格
            r'票价[：:]\s*(\d+)円',  # 明确的票价
            r'(大人|成人)[：:]\s*(\d+)円',  # 成人票价
            r'(小人|儿童)[：:]\s*(\d+)円',  # 儿童票价
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, response_text)
            for match in matches:
                price_str = match if isinstance(match, str) else match[-1]
                facts.append({
                    "type": "price",
                    "value": f"{price_str}円",
                    "context": self._get_context(response_text, price_str),
                    "confidence_required": 0.7  # 降低价格验证要求
                })
        
        # 3. 提取公司信息
        company_patterns = [
            r'(四国汽船|四国フェリー)',
            r'(豊島フェリー|豊島渡轮)',
            r'(小豆島豊島フェリー)',
            r'(ジャンボフェリー)',
            r'(国際両備フェリー)',
            r'(雌雄島海運)',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, response_text)
            for match in matches:
                facts.append({
                    "type": "company",
                    "value": match,
                    "context": self._get_context(response_text, match),
                    "confidence_required": 0.7  # 降低公司验证要求
                })
        
        # 4. 提取路线信息
        route_patterns = [
            r'([^→\s，,]{2,8})→([^→\s，,]{2,8})',  # 基本路线格式
            r'从\s*([^到]{2,8})\s*到\s*([^的]{2,8})',  # 中文路线格式
            r'([^出发]{2,8})\s*出发.*?到达\s*([^的]{2,8})',  # 出发到达格式
        ]
        
        for pattern in route_patterns:
            matches = re.findall(pattern, response_text)
            for departure, arrival in matches:
                facts.append({
                    "type": "route",
                    "value": f"{departure}→{arrival}",
                    "context": self._get_context(response_text, f"{departure}→{arrival}"),
                    "confidence_required": 0.6  # 降低路线验证要求
                })
        
        # 5. 提取港口信息
        port_keywords = [
            '高松港', '高松', '直岛港', '直島港', '直岛', '直島',
            '豊岛港', '豊島港', '豊岛', '豊島', '犬岛港', '犬島港', '犬岛', '犬島',
            '小豆岛', '小豆島', '宇野港', '宇野', '神戸港', '神戸'
        ]
        
        for port in port_keywords:
            if port in response_text:
                facts.append({
                    "type": "port",
                    "value": port,
                    "context": self._get_context(response_text, port),
                    "confidence_required": 0.5  # 降低港口验证要求
                })
        
        return facts
    
    def _get_context(self, text: str, target: str, window: int = 50) -> str:
        """获取目标文本的上下文"""
        try:
            index = text.find(target)
            if index == -1:
                return ""
            
            start = max(0, index - window)
            end = min(len(text), index + len(target) + window)
            
            return text[start:end]
        except:
            return ""
    
    async def _verify_fact_with_context(self, fact: Dict[str, Any], source_data: List[RetrievedData], full_response: str) -> VerificationResult:
        """基于上下文验证事实"""
        try:
            fact_type = fact["type"]
            fact_value = fact["value"]
            context = fact["context"]
            required_confidence = fact["confidence_required"]
            
            # 在源数据中查找支持证据
            supporting_data = []
            confidence_scores = []
            verification_details = []
            
            for data in source_data:
                support_score = self._calculate_support_score(fact, data)
                if support_score > 0.3:  # 最低支持阈值
                    supporting_data.append(data)
                    confidence_scores.append(support_score)
                    verification_details.append(f"数据源支持度: {support_score:.2f}")
            
            # 计算总体置信度
            if supporting_data:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                
                # 根据事实类型调整置信度要求
                if avg_confidence >= required_confidence:
                    status = VerificationStatus.VERIFIED
                    details = f"找到 {len(supporting_data)} 条支持数据，平均置信度: {avg_confidence:.2f}"
                else:
                    status = VerificationStatus.UNVERIFIED
                    details = f"支持数据置信度不足: {avg_confidence:.2f} < {required_confidence}"
            else:
                avg_confidence = 0.0
                status = VerificationStatus.UNVERIFIED
                details = "未找到支持数据"
            
            return VerificationResult(
                fact=f"{fact_type}: {fact_value}",
                status=status,
                supporting_data=supporting_data,
                confidence_score=avg_confidence,
                verification_details=details
            )
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 事实验证失败: {e}")
            return VerificationResult(
                fact=f"{fact.get('type', 'unknown')}: {fact.get('value', 'unknown')}",
                status=VerificationStatus.UNVERIFIED,
                supporting_data=[],
                confidence_score=0.0,
                verification_details=f"验证过程出错: {str(e)}"
            )
    
    def _calculate_support_score(self, fact: Dict[str, Any], data: RetrievedData) -> float:
        """计算数据对事实的支持度"""
        fact_type = fact["type"]
        fact_value = fact["value"]
        content = data.content.lower()
        value_lower = fact_value.lower()
        
        score = 0.0
        
        if fact_type == "time":
            # 时间验证：精确匹配
            if fact_value in data.content:
                score = 0.95
            elif any(time_part in content for time_part in fact_value.split(':')):
                score = 0.6
        
        elif fact_type == "price":
            # 价格验证：精确匹配
            if fact_value in data.content:
                score = 0.95
            elif fact_value.replace('円', '') in content:
                score = 0.8
        
        elif fact_type == "company":
            # 公司验证：名称匹配
            if value_lower in content:
                score = 0.9
            elif any(part in content for part in value_lower.split()):
                score = 0.6
        
        elif fact_type == "route":
            # 路线验证：起点终点匹配
            if '→' in fact_value:
                departure, arrival = fact_value.split('→')
                departure_match = departure.lower() in content
                arrival_match = arrival.lower() in content
                
                if departure_match and arrival_match:
                    score = 0.9
                elif departure_match or arrival_match:
                    score = 0.5
        
        elif fact_type == "port":
            # 港口验证：名称匹配
            if value_lower in content:
                score = 0.8
            elif value_lower.replace('港', '') in content:
                score = 0.7
        
        # 基于数据来源调整分数
        if data.source_type.startswith("structured"):
            score *= 1.1  # 结构化数据更可信
        elif data.source_type == "vector":
            score *= data.relevance_score  # 基于向量相关性
        
        return min(score, 1.0)  # 确保不超过1.0
    
    def _check_for_fabrication(self, response_text: str, source_data: List[RetrievedData]) -> Optional[VerificationResult]:
        """检查是否有编造信息"""
        try:
            # 检查是否包含过于具体但无法验证的信息
            suspicious_patterns = [
                r'\d{4}年\d{1,2}月\d{1,2}日',  # 具体日期
                r'每\s*(天|日)\s*\d+\s*班',  # 具体班次数量
                r'约\s*\d+\s*分钟',  # 具体时长
                r'预计\s*\d+\s*点',  # 预计时间
            ]
            
            fabricated_info = []
            for pattern in suspicious_patterns:
                matches = re.findall(pattern, response_text)
                for match in matches:
                    # 检查这个信息是否在源数据中有支持
                    supported = any(match in data.content for data in source_data)
                    if not supported:
                        fabricated_info.append(match)
            
            if fabricated_info:
                return VerificationResult(
                    fact=f"可能编造的信息: {', '.join(fabricated_info)}",
                    status=VerificationStatus.CONFLICTING,
                    supporting_data=[],
                    confidence_score=0.0,
                    verification_details="检测到可能的编造信息，无源数据支持"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 编造检查失败: {e}")
            return None
    
    def calculate_enhanced_accuracy(self, verification_results: List[VerificationResult]) -> Dict[str, float]:
        """计算增强的准确率指标"""
        if not verification_results:
            return {"overall": 0.0, "by_type": {}}
        
        # 按类型分组
        by_type = {}
        for result in verification_results:
            fact_type = result.fact.split(':')[0] if ':' in result.fact else 'unknown'
            if fact_type not in by_type:
                by_type[fact_type] = []
            by_type[fact_type].append(result)
        
        # 计算各类型准确率
        type_accuracy = {}
        for fact_type, results in by_type.items():
            verified = sum(1 for r in results if r.status == VerificationStatus.VERIFIED)
            type_accuracy[fact_type] = verified / len(results)
        
        # 计算总体准确率（加权）
        total_verified = sum(1 for r in verification_results if r.status == VerificationStatus.VERIFIED)
        overall_accuracy = total_verified / len(verification_results)
        
        return {
            "overall": overall_accuracy,
            "by_type": type_accuracy,
            "total_facts": len(verification_results),
            "verified_facts": total_verified
        }
