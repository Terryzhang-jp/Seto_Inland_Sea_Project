import os
import asyncio
from typing import List, Dict, Any, Optional
import logging
import google.generativeai as genai
from models.rag_models import ChatMessage

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini 2.5 Flash 服务"""
    
    def __init__(self):
        # 从环境变量获取API密钥
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        else:
            genai.configure(api_key=self.api_key)
        
        self.model_name = "gemini-2.5-flash-preview-05-20"
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化模型"""
        if self.api_key:
            try:
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini model {self.model_name} initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {str(e)}")
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        chat_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """
        生成回复
        
        Args:
            prompt: 用户输入
            context: 检索到的相关信息
            chat_history: 聊天历史
            
        Returns:
            生成的回复
        """
        if not self.model:
            raise ValueError("Gemini model not initialized")
        
        try:
            # 构建完整的提示词
            full_prompt = self._build_prompt(prompt, context, chat_history)
            
            # 异步调用Gemini API
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _build_prompt(
        self, 
        user_query: str, 
        context: Optional[str] = None,
        chat_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """构建完整的提示词"""
        
        system_prompt = """你是瀬户内海跳岛查询系统的专业助手。你的核心任务是帮助用户查询岛屿间的船班信息和跳岛连接。

你的专业能力：
1. 精确查询船班时间、票价、运营公司
2. 分析岛屿间的最佳跳岛路线和连接方式
3. 提供载运车辆、自行车的船班信息
4. 解答换乘、中转的具体操作方法
5. 推荐高效的跳岛顺序和时间安排

严格回答原则：
- 专注于跳岛查询，不做详细行程规划
- 只能基于提供的检索数据回答，绝对不能编造信息
- 如果检索到的数据中没有相关信息，必须明确说"查询不到相关信息"或"数据库中没有此信息"
- 严禁推测、估算或编造船班时间、票价、公司名称
- 严禁基于常识或经验补充未在数据中找到的具体信息
- 如果数据不完整，必须诚实告知并建议用户查询官方网站
- 对于具体的时间、价格、公司信息，只能引用检索到的准确数据
- 明确说明换乘点和等待时间（仅基于检索数据）
- 如果查询信息不足，引导用户提供具体需求

关键约束：
- 如果用户询问的路线、时间、公司在检索数据中不存在，必须回复"查询不到相关信息"
- 不得提供任何未在检索数据中明确出现的具体船班信息
- 不得基于相似信息进行推理或建议

重要提醒：宁可说"查询不到"也不要编造任何具体的船班时间、票价或公司信息。

当前可用的岛屿包括：
- 本州港口：高松、宇野、神戸、新岡山港
- 艺术岛屿：直島、豊島、犬島
- 其他岛屿：小豆島、女木島、男木島

主要船运公司：
- 四国汽船、ジャンボフェリー、国際両備フェリー、四国フェリー、雌雄島海運、豊島フェリー、小豆島豊島フェリー
"""
        
        # 添加上下文信息
        if context:
            system_prompt += f"\n\n相关船班信息：\n{context}"
        
        # 添加聊天历史
        conversation = ""
        if chat_history:
            for msg in chat_history[-5:]:  # 只保留最近5条消息
                role = "用户" if msg.role == "user" else "助手"
                conversation += f"{role}: {msg.content}\n"
        
        if conversation:
            system_prompt += f"\n\n对话历史：\n{conversation}"
        
        # 构建最终提示词
        full_prompt = f"{system_prompt}\n\n用户问题: {user_query}\n\n请提供有帮助的回答："
        
        return full_prompt
    
    async def generate_trip_plan(
        self, 
        departure: str, 
        destinations: List[str], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成行程规划
        
        Args:
            departure: 出发地
            destinations: 目的地列表
            preferences: 用户偏好
            
        Returns:
            行程规划
        """
        if not self.model:
            raise ValueError("Gemini model not initialized")
        
        try:
            prompt = f"""请为以下跳岛行程制定详细计划：

出发地：{departure}
目的地：{', '.join(destinations)}
用户偏好：{preferences}

请提供：
1. 详细的行程安排（包括时间、路线、换乘）
2. 推荐的船班选择
3. 预估费用
4. 旅行建议和注意事项

请以JSON格式返回，包含以下字段：
- itinerary: 行程安排列表
- total_cost: 总费用估算
- total_duration: 总时长
- recommendations: 建议列表
"""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # 这里可以添加JSON解析逻辑
            return {"raw_response": response.text}
            
        except Exception as e:
            logger.error(f"Error generating trip plan: {str(e)}")
            raise

# 全局实例
gemini_service = GeminiService()
