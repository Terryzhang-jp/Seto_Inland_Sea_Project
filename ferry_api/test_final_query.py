"""
最终测试 - 测试指定查询
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 设置环境变量
os.environ["PYTHONPATH"] = str(Path(__file__).parent)

# 配置日志
logging.basicConfig(
    level=logging.WARNING,  # 只显示警告和错误
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_specific_query():
    """测试指定的查询"""
    try:
        print("🎯 濑户内海智能查询系统 - 最终测试")
        print("="*80)
        
        # 导入必要的模块
        from services.vector_store import vector_store
        from services.gemini_service import gemini_service
        from services.data_processor import data_processor
        from agents.intelligent_query_system import IntelligentQuerySystem
        
        # 初始化智能查询系统
        print("📋 正在初始化系统...")
        intelligent_system = IntelligentQuerySystem(
            llm=gemini_service.model,
            vector_store=vector_store,
            data_processor=data_processor
        )
        print("✅ 系统初始化完成！")
        
        # 指定的测试查询
        test_query = "我下午3:30到高松机场 我想住在直岛和丰岛 有什么班次可以选择"
        
        print(f"\n📝 测试查询: {test_query}")
        print("="*80)
        
        # 处理查询
        result = await intelligent_system.process_query(test_query)
        
        print("\n💬 AI最终回复:")
        print("-" * 80)
        print(result.get('message', '无回复'))
        
        print(f"\n📊 系统处理详情:")
        print("-" * 40)
        print(f"• 需求类型: {result.get('requirement_type', '未知')}")
        print(f"• 分析类型: {result.get('analysis_result', {}).get('analysis_type', '未知')}")
        print(f"• 推荐结果: {result.get('analysis_result', {}).get('recommendation', '无')}")
        print(f"• 置信度: {result.get('system_info', {}).get('confidence', 0.0):.1%}")
        print(f"• 执行时间: {result.get('execution_time', 0.0):.2f}秒")
        print(f"• 数据来源: {result.get('data_sources', {}).get('summary', '无')}")
        print(f"• 使用策略: {result.get('system_info', {}).get('strategy_used', '未知')}")
        
        # 显示AI思考过程
        thinking_process = result.get('analysis_result', {}).get('thinking_process', {})
        if thinking_process:
            print(f"\n🧠 AI思考过程:")
            print("-" * 40)
            print(f"• 核心关切: {thinking_process.get('core_concern', '未知')}")
            print(f"• 用户优先级: {thinking_process.get('user_priority', '未知')}")
            print(f"• 关键需求: {thinking_process.get('critical_info_needed', '未知')}")
            
            key_questions = thinking_process.get('key_questions', [])
            if key_questions:
                print(f"• AI识别的关键问题:")
                for i, question in enumerate(key_questions, 1):
                    print(f"  {i}. {question}")
        
        # 显示核心分析结果
        core_analysis = result.get('analysis_result', {}).get('core_analysis', {})
        if core_analysis:
            print(f"\n⏰ 核心时间分析:")
            print("-" * 40)
            print(f"• 到达时间: {core_analysis.get('departure_time', '未知')}")
            print(f"• 预计到港时间: {core_analysis.get('arrival_at_port', '未知')}")
            print(f"• 机场到港口耗时: {core_analysis.get('airport_to_port_time', '未知')}")
            
            feasibility = core_analysis.get('feasibility_by_destination', {})
            if feasibility:
                print(f"\n🚢 各目的地班次分析:")
                print("-" * 40)
                for dest, analysis in feasibility.items():
                    print(f"📍 {dest}:")
                    all_schedules = analysis.get('available_schedules', [])
                    feasible_schedules = analysis.get('feasible_schedules', [])
                    recommendation = analysis.get('recommendation', '无建议')
                    
                    print(f"  • 所有班次: {', '.join(all_schedules) if all_schedules else '无数据'}")
                    print(f"  • 可赶上班次: {', '.join(feasible_schedules) if feasible_schedules else '无'}")
                    print(f"  • 建议: {recommendation}")
                    print()
        
        # 显示关键发现
        key_findings = result.get('analysis_result', {}).get('key_findings', [])
        if key_findings:
            print(f"💡 关键发现:")
            print("-" * 40)
            for finding in key_findings:
                print(f"• {finding}")
        
        # 显示数据来源详情
        data_sources = result.get('data_sources', {})
        if data_sources.get('sources'):
            print(f"\n📊 数据来源详情:")
            print("-" * 40)
            print(f"• 总结: {data_sources.get('summary', '无')}")
            sources = data_sources.get('sources', {})
            if isinstance(sources, dict):
                for source_type, source_info in sources.items():
                    count = source_info.get('count', 0) if isinstance(source_info, dict) else source_info
                    print(f"  - {source_type}: {count}条数据")
        
        # 系统性能
        performance = intelligent_system.get_performance_metrics()
        print(f"\n🎯 系统性能:")
        print("-" * 40)
        print(f"• 总查询数: {performance.get('total_queries', 0)}")
        print(f"• 成功查询数: {performance.get('successful_queries', 0)}")
        print(f"• 平均响应时间: {performance.get('average_response_time', 0.0):.2f}秒")
        print(f"• 平均置信度: {performance.get('average_confidence', 0.0):.1%}")
        
        print(f"\n🎉 测试完成!")
        
        return result
        
    except Exception as e:
        print(f"💥 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(test_specific_query())
