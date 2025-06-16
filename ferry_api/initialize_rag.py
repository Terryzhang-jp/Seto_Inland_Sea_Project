#!/usr/bin/env python3
"""
RAG系统初始化脚本
用于初始化向量数据库和处理数据
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def initialize_rag_system():
    """初始化RAG系统"""
    try:
        logger.info("开始初始化RAG系统...")
        
        # 检查环境变量
        gemini_key = os.getenv("GEMINI_API_KEY")
        qwen_key = os.getenv("QWEN_API_KEY")
        
        if not gemini_key:
            logger.warning("GEMINI_API_KEY 未设置")
        else:
            logger.info("GEMINI_API_KEY 已配置")
        
        if not qwen_key:
            logger.warning("QWEN_API_KEY 未设置，将使用本地embedding模型")
        else:
            logger.info("QWEN_API_KEY 已配置")
        
        # 导入服务
        from services.vector_store import vector_store
        from services.data_processor import data_processor
        
        logger.info("正在初始化向量数据库...")
        
        # 检查数据文件是否存在
        data_files = [
            "data/ferry_routes.csv",
            "data/ports.csv", 
            "data/companies.csv",
            "data/popular_routes.json"
        ]
        
        missing_files = []
        for file_path in data_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"缺少数据文件: {missing_files}")
            logger.info("请确保以下文件存在:")
            for file_path in missing_files:
                logger.info(f"  - {file_path}")
            return False
        
        # 处理并存储数据
        logger.info("正在处理和存储数据到向量数据库...")
        await data_processor.process_and_store_all_data()
        
        # 获取统计信息
        stats = vector_store.get_collection_stats()
        logger.info(f"RAG系统初始化完成！")
        logger.info(f"向量数据库统计: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"RAG系统初始化失败: {str(e)}")
        return False

async def test_rag_system():
    """测试RAG系统"""
    try:
        logger.info("开始测试RAG系统...")
        
        from services.rag_engine import rag_engine
        
        # 测试查询
        test_queries = [
            "从高松到直島有什么船？",
            "小豆島有什么特色？",
            "四国汽船的联系方式"
        ]
        
        for query in test_queries:
            logger.info(f"测试查询: {query}")
            try:
                response = await rag_engine.chat_query(query)
                logger.info(f"回复: {response.message[:100]}...")
                logger.info(f"来源数量: {len(response.sources)}")
            except Exception as e:
                logger.error(f"查询失败: {str(e)}")
        
        logger.info("RAG系统测试完成")
        return True
        
    except Exception as e:
        logger.error(f"RAG系统测试失败: {str(e)}")
        return False

async def main():
    """主函数"""
    logger.info("=== RAG系统初始化和测试 ===")
    
    # 初始化系统
    init_success = await initialize_rag_system()
    
    if not init_success:
        logger.error("初始化失败，退出")
        return
    
    # 测试系统
    test_success = await test_rag_system()
    
    if test_success:
        logger.info("✅ RAG系统初始化和测试成功完成！")
    else:
        logger.error("❌ RAG系统测试失败")

if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 运行主函数
    asyncio.run(main())
