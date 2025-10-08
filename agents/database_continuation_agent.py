"""
基于数据库的龙族续写Agent系统
使用SQLite数据库管理角色档案和关系
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.database_api import get_character_api
from database.plot_api import get_plot_api
from simple_continuation_agent import (
    Agent, handoff, function_tool, 
    MemoryManager, ChapterContext, continue_dragon_novel
)

# ==================== 数据库工具函数 ====================


@function_tool
def get_character_detail_from_db(character_name: str) -> str:
    """从数据库获取详细的角色信息"""
    try:
        api = get_character_api()
        return api.get_character_detail(character_name)
    except Exception as e:
        return f"获取角色详细信息时出错: {str(e)}"


@function_tool
def get_plot_summary_from_db(current_chapter: int = None, merge_factor: int = 3) -> str:
    """从数据库获取分层合并的情节大纲摘要
    
    Args:
        current_chapter: 当前章节号，如果不提供则显示所有章节
        merge_factor: 合并因子，默认每3个章节合并一次
    
    Returns:
        分层合并的情节摘要，远距离章节被合并，最近章节保持详细
    """
    try:
        from database.plot_merge_system import PlotMergeSystem
        
        merge_system = PlotMergeSystem()
        
        # 如果没有指定当前章节，使用数据库中的最大章节号
        if current_chapter is None:
            plot_api = get_plot_api()
            all_chapters = plot_api.get_all_chapters()
            if all_chapters:
                current_chapter = max(chapter['chapter_number'] for chapter in all_chapters)
            else:
                return "数据库中没有章节数据"
        
        # 获取分层合并的情节摘要
        summary = merge_system.format_merged_plot_summary(current_chapter, merge_factor)
        return summary
        
    except Exception as e:
        return f"获取分层情节大纲时出错: {str(e)}"


@function_tool
def get_character_timeline_from_db(character_name: str) -> str:
    """从数据库获取角色发展时间线"""
    try:
        plot_api = get_plot_api()
        timeline = plot_api.format_character_timeline(character_name)
        return timeline
    except Exception as e:
        return f"获取角色发展时间线时出错: {str(e)}"


@function_tool
def add_new_chapter_to_plot(chapter_number: int, title: str, summary: str, 
                          word_count: int = 2000, plot_point: str = "",
                          key_events: str = "", character_focus: str = "",
                          setting: str = "", mood: str = "", themes: str = "",
                          notes: str = "") -> str:
    """添加新章节到情节大纲"""
    try:
        plot_api = get_plot_api()
        chapter_id = plot_api.add_chapter(
            chapter_number=chapter_number,
            title=title,
            summary=summary,
            word_count=word_count,
            plot_point=plot_point,
            key_events=key_events,
            character_focus=character_focus,
            setting=setting,
            mood=mood,
            themes=themes,
            notes=notes
        )
        return f"成功添加第{chapter_number}章到情节大纲，章节ID: {chapter_id}"
    except Exception as e:
        return f"添加章节到情节大纲时出错: {str(e)}"


@function_tool
def update_chapter_in_plot(chapter_id: int, **kwargs) -> str:
    """更新情节大纲中的章节信息"""
    try:
        plot_api = get_plot_api()
        success = plot_api.update_chapter(chapter_id, **kwargs)
        if success:
            return f"成功更新章节ID {chapter_id} 的信息"
        else:
            return f"更新章节ID {chapter_id} 失败"
    except Exception as e:
        return f"更新章节信息时出错: {str(e)}"


@function_tool
def add_character_arc_to_plot(character_name: str, chapter_id: int,
                            development: str = "", emotional_state: str = "",
                            key_decisions: str = "", relationships_changed: str = "") -> str:
    """为角色添加发展轨迹记录"""
    try:
        plot_api = get_plot_api()
        plot_api.add_character_arc(
            character_name=character_name,
            chapter_id=chapter_id,
            development=development,
            emotional_state=emotional_state,
            key_decisions=key_decisions,
            relationships_changed=relationships_changed
        )
        return f"成功为{character_name}添加第{chapter_id}章的发展轨迹记录"
    except Exception as e:
        return f"添加角色发展轨迹时出错: {str(e)}"





# ==================== 数据库版Agent定义 ====================

# 内容衔接Agent (使用数据库)
continuity_agent_db = Agent(
    name="内容衔接师(数据库版)",
    instructions="""
    你是内容衔接专家，使用数据库确保故事的连贯性。
    
    你的任务:
    1. 使用数据库查询角色关系，确保关系发展合理
    2. 检查情节逻辑的一致性
    3. 维护世界观设定的统一性
    4. 确保前后章节的连贯性
    
    执行流程:
    1. 使用 get_character_relationships_db() 检查角色关系
    2. 使用 search_characters_db() 查找相关角色
    3. 分析情节发展是否符合角色设定
    4. 确保新内容与已有内容自然衔接
    
    重点关注:
    - 角色关系的发展要符合数据库记录
    - 情节发展要符合角色性格特点
    - 新内容要与前面章节自然衔接
    - 保持故事逻辑的一致性
    """,
    tools=[
        get_character_detail_from_db,
        get_plot_summary_from_db,
        get_character_timeline_from_db
    ]
)

# 主笔写作Agent (使用数据库)
main_writer_agent_db = Agent(
    name="主笔写作师(数据库版)",
    instructions="""
    你是主笔写作专家，使用数据库中的角色档案进行创作。
    
    你的任务:
    1. 使用数据库查询角色信息，确保角色行为一致
    2. 生成符合江南风格的2000字章节
    3. 保持角色的语言特色和性格特点
    4. 设置适当的悬念和伏笔
    5. 创作完成后更新情节大纲数据库
    
    执行流程:
    1. 使用 get_plot_summary_from_db() 了解当前情节大纲
    2. 使用 get_character_detail_from_db() 获取主要角色档案
    3. 使用 get_character_timeline_from_db() 了解角色发展历程
    4. 创作符合角色设定的情节发展
    5. 使用 add_new_chapter_to_plot() 记录新章节
    6. 使用 add_character_arc_to_plot() 记录角色发展
    
    写作要求:
    - 字数控制在1800-2200字之间
    - 保持江南细腻的心理描写风格
    - 确保角色行为符合数据库档案
    - 对话要符合角色的说话特点
    - 情节发展要符合角色关系设定
    - 创作完成后必须更新情节大纲
    """,
    tools=[
        get_character_detail_from_db,
        get_plot_summary_from_db,
        get_character_timeline_from_db,
        add_new_chapter_to_plot,
        update_chapter_in_plot,
        add_character_arc_to_plot
    ]
)

# 质量检查Agent (使用数据库)
quality_agent_db = Agent(
    name="质量检查师(数据库版)",
    instructions="""
    你是质量检查专家，使用数据库验证续写内容的质量。
    
    你的任务:
    1. 使用数据库检查角色一致性
    2. 验证角色关系的合理性
    3. 检查文本风格是否符合江南特色
    4. 确保内容质量达到标准
    
    执行流程:
    1. 使用 check_character_consistency_db() 检查所有角色的一致性
    2. 使用 get_character_relationships_db() 验证角色关系
    3. 使用 get_character_from_db() 确认角色设定
    4. 进行全面质量评估
    
    质量标准:
    - 角色一致性评分 > 0.7
    - 角色关系符合数据库设定
    - 文本风格符合江南特色
    - 字数控制在合理范围内
    - 情节逻辑清晰合理
    """,
    tools=[
        get_character_detail_from_db,
        get_plot_summary_from_db,
        get_character_timeline_from_db
    ]
)

# ==================== 主协调Agent (数据库版) ====================

def on_continuity_handoff_db(message: str) -> str:
    return f"内容衔接师(数据库版)接手: {message}"

def on_writing_handoff_db(message: str) -> str:
    return f"主笔写作师(数据库版)接手: {message}"

def on_quality_handoff_db(message: str) -> str:
    return f"质量检查师(数据库版)接手: {message}"

# 主协调Agent (数据库版)
novel_continuation_agent_db = Agent(
    name="龙族续写总协调(数据库版)",
    instructions="""
    你是《龙族》续写项目的总协调员，使用数据库管理角色档案。
    
    你的任务:
    1. 协调各个专业Agent完成续写任务
    2. 使用数据库确保角色一致性
    3. 管理记忆和上下文信息
    4. 控制Token使用量
    5. 确保输出质量
    
    执行流程:
    1. 分析续写需求和上下文
    2. 使用数据库查询相关角色信息
    3. 协调内容衔接Agent确保连贯性
    4. 协调主笔写作Agent生成新章节
    5. 协调质量检查Agent验证输出
    
    数据库优势:
    - 角色档案完整准确
    - 关系网络清晰明确
    - 台词和特点详细记录
    - 支持复杂查询和分析
    
    重点关注:
    - 使用数据库确保角色行为一致
    - 保持江南的写作风格
    - 确保内容自然衔接
    - 控制Token使用量
    - 防止遗忘问题
    - 生成2000字左右的章节
    
    请根据用户需求，智能调用相应的专业Agent和数据库工具。
    """,
    handoffs=[
        handoff(continuity_agent_db, on_handoff=on_continuity_handoff_db),
        handoff(main_writer_agent_db, on_handoff=on_writing_handoff_db),
        handoff(quality_agent_db, on_handoff=on_quality_handoff_db),
    ]
)

# ==================== 便捷函数 ====================

async def continue_dragon_novel_db(
    current_chapter: int,
    previous_content: str,
    memory_manager: MemoryManager,
    target_word_count: int = 2000
) -> str:
    """
    使用数据库版Agent系统续写龙族小说
    
    Args:
        current_chapter: 当前章节号
        previous_content: 前面章节的内容
        memory_manager: 记忆管理器
        target_word_count: 目标字数
        
    Returns:
        续写的章节内容
    """
    try:
        # 构建续写请求
        request = f"""
        请续写《龙族》第{current_chapter}章。
        
        前面章节内容:
        {previous_content}
        
        目标字数: {target_word_count}字
        要求: 使用数据库确保角色一致性，保持江南的写作风格
        
        请协调各个专业Agent完成续写任务。
        """
        
        # 调用主协调Agent
        response = await novel_continuation_agent_db.run(request)
        
        return response
        
    except Exception as e:
        return f"续写过程中出现错误: {str(e)}"

def get_database_agent_info() -> dict:
    """获取数据库Agent系统信息"""
    return {
        "system_name": "龙族续写Agent系统(数据库版)",
        "version": "2.0.0",
        "features": [
            "SQLite数据库管理角色档案",
            "完整的关系网络支持",
            "智能角色一致性检查",
            "基于数据库的对话生成",
            "高级搜索和查询功能",
            "数据持久化和备份"
        ],
        "agents": [
            "内容衔接师(数据库版)",
            "主笔写作师(数据库版)",
            "质量检查师(数据库版)",
            "龙族续写总协调(数据库版)"
        ],
        "database_tools": [
            "get_character_detail_from_db",
            "get_plot_summary_from_db",
            "get_character_timeline_from_db",
            "add_new_chapter_to_plot",
            "update_chapter_in_plot",
            "add_character_arc_to_plot"
        ]
    }

if __name__ == "__main__":
    # 测试数据库Agent系统
    print("=== 龙族续写Agent系统(数据库版) ===")
    
    info = get_database_agent_info()
    print(f"系统名称: {info['system_name']}")
    print(f"版本: {info['version']}")
    print(f"特性: {', '.join(info['features'])}")
    
    # 测试数据库连接
    try:
        api = get_character_api()
        stats = api.get_database_info()
        print(f"\n数据库状态:")
        print(f"- 角色数量: {stats['character_count']}")
        print(f"- 关系数量: {stats['relationship_count']}")
        print(f"- 台词数量: {stats['quote_count']}")
        
        # 测试角色查询
        lumingfei = api.get_character("路明非")
        if lumingfei:
            print(f"\n测试角色查询: {lumingfei['name']}")
            print(f"性格特征: {lumingfei['personality_traits'][:3]}...")
        
        print("\n✅ 数据库Agent系统初始化成功！")
        
    except Exception as e:
        print(f"\n❌ 数据库连接失败: {str(e)}")
        print("请先运行 migrate_data.py 初始化数据库")
