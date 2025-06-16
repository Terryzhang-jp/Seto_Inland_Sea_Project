"""
状态模型定义 - 多层Agent系统的状态管理
"""

from typing import Dict, List, Optional, Any, TypedDict
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class RequirementType(str, Enum):
    """需求类型枚举"""
    ROUTE_PLANNING = "路线规划"
    TIME_QUERY = "时间查询"
    CONVENIENCE_COMPARISON = "便利性比较"
    PRICE_COMPARISON = "价格比较"
    COMPREHENSIVE_CONSULTATION = "综合咨询"

class QueryType(str, Enum):
    """查询类型枚举（保持兼容性）"""
    SIMPLE_INFO = "简单信息查询"
    COMPLEX_ROUTE = "复杂路线规划"
    COMPARISON = "比较分析"
    TIME_CONSTRAINT = "时间约束查询"

class ComplexityLevel(str, Enum):
    """复杂度级别"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"

class VerificationStatus(str, Enum):
    """验证状态"""
    VERIFIED = "✅ 已验证"
    UNVERIFIED = "⚠️ 未验证"
    CONFLICTING = "❌ 数据冲突"
    INSUFFICIENT = "📋 数据不足"

class TransportInfo(BaseModel):
    """交通信息"""
    location: Optional[str] = None
    time: Optional[str] = None
    transport_type: Optional[str] = None

class TimeConstraint(BaseModel):
    """时间约束"""
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    time_window: Optional[str] = None
    flexibility: Optional[str] = None

class TravelRequirement(BaseModel):
    """旅行需求分析结果"""
    requirement_type: RequirementType
    departure_info: TransportInfo
    destination_options: List[str]
    constraints: Dict[str, Optional[str]]
    user_priority: Optional[str]
    analysis_needed: List[str]
    confidence_score: float

class QueryStrategy(BaseModel):
    """查询策略"""
    strategy_id: str
    strategy_name: str
    steps: List[Dict[str, Any]]
    analysis_criteria: List[str]
    expected_outcome: str

class IntentAnalysisResult(BaseModel):
    """意图分析结果（保持兼容性）"""
    query_type: QueryType
    entities: Dict[str, Optional[str]]
    complexity: ComplexityLevel
    requires_decomposition: bool
    confidence_score: float

class TaskPlan(BaseModel):
    """任务计划"""
    task_id: str
    task_type: str
    description: str
    dependencies: List[str]
    priority: int
    estimated_duration: float

class ExecutionPlan(BaseModel):
    """执行计划"""
    plan_id: str
    tasks: List[TaskPlan]
    execution_order: List[str]
    total_estimated_time: float

class RetrievedData(BaseModel):
    """检索到的数据"""
    source_type: str  # vector, sql, cache
    content: str
    metadata: Dict[str, Any]
    relevance_score: float
    timestamp: str

class VerificationResult(BaseModel):
    """验证结果"""
    fact: str
    status: VerificationStatus
    supporting_data: List[RetrievedData]
    confidence_score: float
    verification_details: str

class AgentResponse(BaseModel):
    """Agent响应"""
    agent_name: str
    response_data: Dict[str, Any]
    execution_time: float
    success: bool
    error_message: Optional[str] = None

# LangGraph状态定义
class FerryQueryState(TypedDict):
    """Ferry查询状态 - LangGraph使用"""
    # 输入
    user_query: str
    session_id: Optional[str]
    
    # 意图分析层
    intent_analysis: Optional[IntentAnalysisResult]
    
    # 任务规划层
    execution_plan: Optional[ExecutionPlan]
    
    # 执行层
    retrieved_data: Optional[List[RetrievedData]]
    reasoning_result: Optional[Dict[str, Any]]
    
    # 验证层
    verification_results: Optional[List[VerificationResult]]
    overall_accuracy: Optional[float]
    
    # 响应生成层
    final_response: Optional[str]
    response_metadata: Optional[Dict[str, Any]]
    
    # 错误处理
    errors: Optional[List[str]]
    
    # 性能指标
    total_execution_time: Optional[float]
    agent_responses: Optional[List[AgentResponse]]

class AgentMessage(BaseModel):
    """Agent间通信消息"""
    from_agent: str
    to_agent: str
    message_type: str  # request, response, error, notification
    payload: Dict[str, Any]
    timestamp: str
    correlation_id: str
    priority: int = 1

class CacheEntry(BaseModel):
    """缓存条目"""
    query_hash: str
    query_text: str
    response: str
    verification_results: List[VerificationResult]
    accuracy_score: float
    created_at: str
    expires_at: str
    hit_count: int = 0
