from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatQuery(BaseModel):
    """聊天查询请求"""
    message: str
    session_id: Optional[str] = None
    context: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    sources: Optional[List[Dict[str, Any]]] = []
    session_id: str
    suggestions: Optional[List[str]] = []

class TripPlanRequest(BaseModel):
    """行程规划请求"""
    departure: str
    destinations: List[str]
    preferences: Optional[Dict[str, Any]] = {}
    duration: Optional[str] = None  # "1day", "2days", etc.

class TripPlanResponse(BaseModel):
    """行程规划响应"""
    itinerary: List[Dict[str, Any]]
    total_cost: Optional[str] = None
    total_duration: Optional[str] = None
    recommendations: Optional[List[str]] = []

class UserPreferences(BaseModel):
    """用户偏好"""
    interests: Optional[List[str]] = []  # ["art", "nature", "food", etc.]
    budget: Optional[str] = None  # "low", "medium", "high"
    travel_style: Optional[str] = None  # "relaxed", "active", "cultural"
    group_size: Optional[int] = 1
    has_vehicle: Optional[bool] = False

class RecommendationResponse(BaseModel):
    """推荐响应"""
    routes: List[Dict[str, Any]]
    reasons: List[str]
    tips: Optional[List[str]] = []

class DocumentChunk(BaseModel):
    """文档块模型"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    source: str

class EmbeddingRequest(BaseModel):
    """向量化请求"""
    texts: List[str]
    
class EmbeddingResponse(BaseModel):
    """向量化响应"""
    embeddings: List[List[float]]
    model: str
