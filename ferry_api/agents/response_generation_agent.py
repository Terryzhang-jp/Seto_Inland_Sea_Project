"""
响应生成Agent - 第5层：生成带验证标注的最终回复
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from .state_models import RetrievedData, VerificationResult, VerificationStatus

logger = logging.getLogger(__name__)

class ResponseGenerationAgent:
    """响应生成Agent"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent_name = "ResponseGenerationAgent"
        
        self.prompt_template = """你是瀬户内海跳岛查询系统的回复生成专家。

基于以下验证过的数据生成用户友好的回复：

原始查询: {query}

已验证的数据:
{verified_data}

验证结果摘要:
{verification_summary}

生成回复要求：
1. 只基于已验证的数据回答
2. 对于未验证的信息，明确说明"查询不到相关信息"
3. 使用友好、专业的语调
4. 结构清晰，易于理解
5. 如果数据不完整，诚实告知并建议查询官方网站

严格禁止：
- 编造任何船班时间、票价、公司信息
- 基于常识或经验补充信息
- 推测或估算未在数据中找到的信息

回复格式：
- 直接回答用户问题
- 提供具体的已验证信息
- 对不确定信息明确标注
"""
    
    async def generate_response(self, 
                              query: str, 
                              retrieved_data: List[RetrievedData],
                              verification_results: List[VerificationResult]) -> Dict[str, Any]:
        """生成最终回复"""
        try:
            logger.info(f"[{self.agent_name}] 开始生成回复")
            
            # 准备已验证的数据
            verified_data = self._prepare_verified_data(retrieved_data, verification_results)
            
            # 生成验证摘要
            verification_summary = self._generate_verification_summary(verification_results)
            
            # 如果没有已验证的数据，返回标准回复
            if not verified_data:
                return self._generate_no_data_response(query)
            
            # 构建prompt
            prompt = self.prompt_template.format(
                query=query,
                verified_data=verified_data,
                verification_summary=verification_summary
            )
            
            # 生成回复 (异步)
            import asyncio
            response = await asyncio.to_thread(self.llm.generate_content, prompt)
            response_text = response.text

            logger.info(f"[{self.agent_name}] LLM响应长度: {len(response_text)}字符")
            
            # 添加验证标注
            annotated_response = self._add_verification_annotations(response_text, verification_results)
            
            # 计算准确率
            accuracy_rate = self._calculate_accuracy_rate(verification_results)
            
            logger.info(f"[{self.agent_name}] 回复生成完成，准确率: {accuracy_rate:.1%}")
            
            return {
                "response": annotated_response,
                "accuracy_rate": accuracy_rate,
                "verification_summary": verification_summary,
                "verified_facts_count": len([r for r in verification_results if r.status == VerificationStatus.VERIFIED]),
                "total_facts_count": len(verification_results)
            }
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] 回复生成失败: {e}")
            return self._generate_error_response(query, str(e))
    
    def _prepare_verified_data(self, retrieved_data: List[RetrievedData], verification_results: List[VerificationResult]) -> str:
        """准备已验证的数据"""
        verified_data_list = []
        
        # 获取已验证的数据
        verified_sources = set()
        for result in verification_results:
            if result.status == VerificationStatus.VERIFIED:
                for data in result.supporting_data:
                    verified_sources.add(id(data))
        
        # 收集已验证的数据内容
        for data in retrieved_data:
            if id(data) in verified_sources:
                verified_data_list.append(f"- {data.content}")
        
        if not verified_data_list:
            return "无已验证数据"
        
        return "\n".join(verified_data_list)
    
    def _generate_verification_summary(self, verification_results: List[VerificationResult]) -> str:
        """生成验证摘要"""
        total = len(verification_results)
        verified = len([r for r in verification_results if r.status == VerificationStatus.VERIFIED])
        unverified = len([r for r in verification_results if r.status == VerificationStatus.UNVERIFIED])
        
        summary = f"总计 {total} 个事实，已验证 {verified} 个，未验证 {unverified} 个"
        
        if verified > 0:
            verified_facts = [r.fact for r in verification_results if r.status == VerificationStatus.VERIFIED]
            summary += f"\n已验证事实: {', '.join(verified_facts[:5])}"  # 只显示前5个
        
        if unverified > 0:
            unverified_facts = [r.fact for r in verification_results if r.status == VerificationStatus.UNVERIFIED]
            summary += f"\n未验证事实: {', '.join(unverified_facts[:3])}"  # 只显示前3个
        
        return summary
    
    def _add_verification_annotations(self, response_text: str, verification_results: List[VerificationResult]) -> str:
        """添加验证标注"""
        annotated_response = response_text
        
        # 计算准确率
        accuracy_rate = self._calculate_accuracy_rate(verification_results)
        
        # 添加验证信息
        verification_info = f"\n\n📋 信息验证结果："
        verification_info += f"\n准确率: {accuracy_rate:.1%}"
        
        verified_facts = [r.fact for r in verification_results if r.status == VerificationStatus.VERIFIED]
        unverified_facts = [r.fact for r in verification_results if r.status == VerificationStatus.UNVERIFIED]
        
        if verified_facts:
            verification_info += f"\n✅ 已验证信息: {', '.join(verified_facts[:3])}"
            if len(verified_facts) > 3:
                verification_info += f" 等{len(verified_facts)}项"
        
        if unverified_facts:
            verification_info += f"\n⚠️  未验证信息: {', '.join(unverified_facts[:2])}"
            if len(unverified_facts) > 2:
                verification_info += f" 等{len(unverified_facts)}项"
        
        if accuracy_rate < 0.8:
            verification_info += f"\n\n⚠️  建议：部分信息未能验证，请在出行前查询官方网站确认最新信息。"
        
        return annotated_response + verification_info
    
    def _calculate_accuracy_rate(self, verification_results: List[VerificationResult]) -> float:
        """计算准确率"""
        if not verification_results:
            return 1.0
        
        verified_count = len([r for r in verification_results if r.status == VerificationStatus.VERIFIED])
        return verified_count / len(verification_results)
    
    def _generate_no_data_response(self, query: str) -> Dict[str, Any]:
        """生成无数据回复"""
        response = f"很抱歉，查询不到关于「{query}」的相关信息。\n\n" \
                  f"可能的原因：\n" \
                  f"1. 查询的路线或时间在数据库中不存在\n" \
                  f"2. 查询条件过于具体或特殊\n" \
                  f"3. 数据库信息可能不完整\n\n" \
                  f"建议：\n" \
                  f"- 尝试使用更通用的查询条件\n" \
                  f"- 查询官方网站获取最新信息\n" \
                  f"- 联系相关船运公司确认"
        
        return {
            "response": response,
            "accuracy_rate": 0.0,
            "verification_summary": "无可验证数据",
            "verified_facts_count": 0,
            "total_facts_count": 0
        }
    
    def _generate_error_response(self, query: str, error_message: str) -> Dict[str, Any]:
        """生成错误回复"""
        response = f"很抱歉，处理您的查询「{query}」时遇到了技术问题。\n\n" \
                  f"请稍后重试，或联系技术支持。\n\n" \
                  f"错误信息：{error_message}"
        
        return {
            "response": response,
            "accuracy_rate": 0.0,
            "verification_summary": f"处理错误: {error_message}",
            "verified_facts_count": 0,
            "total_facts_count": 0
        }
