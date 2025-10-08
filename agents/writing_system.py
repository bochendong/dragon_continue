#!/usr/bin/env python3
"""
龙族续写系统 - 情节规划师与写作师
基于江南风格的AI写作系统
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.plot_api import PlotAPI
from database.database_api import CharacterAPI
from database.plot_merge_system import PlotMergeSystem
from openai import AsyncOpenAI
from agents import Agent, Runner
from pydantic import BaseModel
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# ==================== 江南写作风格分析 ====================

JIANGNAN_STYLE_GUIDE = """
江南《龙族》写作风格特点：

1. **细腻的心理描写**
   - 大量内心独白和自我对话
   - 用"他想"、"他觉得"等引导内心活动
   - 展现角色内心的矛盾和挣扎
   
2. **对话风格**
   - 生活化、口语化，带有网络用语
   - 幽默讽刺，略带自嘲
   - 年轻人的对话方式（QQ、游戏术语等）
   
3. **环境描写**
   - 细致的场景描写（阳光、声音、气味）
   - 时间流逝的感受（"又是春天了"）
   - 日常生活细节丰富
   
4. **叙事节奏**
   - 日常与戏剧性交替
   - 梦境与现实交织
   - 多视角叙事（切换不同人物视角）
   
5. **语言特色**
   - 比喻生动（"像只被抛弃的小猎犬"）
   - 短句和长句结合
   - 口语化表达（"真烦真烦真烦！"）
   
6. **情感基调**
   - 略带悲凉的青春感
   - 孤独与渴望被认可
   - 平凡中的不甘心
   
7. **人物刻画**
   - 通过小动作展现性格
   - 通过内心独白展现思想
   - 对比手法塑造角色
"""

# ==================== 数据模型 ====================

class PlotOutline(BaseModel):
    """情节大纲模型"""
    chapter_number: int
    title: str
    plot_points: List[str]  # 3-5个关键情节点
    character_arcs: Dict[str, str]  # 角色名: 发展变化
    setting: str
    mood: str
    themes: List[str]
    key_events: List[str]  # 具体事件序列
    estimated_word_count: int

class ChapterContent(BaseModel):
    """章节内容模型"""
    chapter_number: int
    title: str
    content: str
    word_count: int
    summary: str
    plot_point: str
    key_events: str
    character_focus: str
    setting: str
    mood: str
    themes: str

# ==================== 情节规划师 Agent ====================

class PlotPlannerAgent:
    """情节规划师 - 负责规划下一章的情节大纲"""
    
    def __init__(self):
        self.plot_api = PlotAPI()
        self.character_api = CharacterAPI()
        self.merge_system = PlotMergeSystem()
        
        # 创建规划师Agent
        self.agent = Agent(
            name="龙族情节规划师",
            instructions=f"""
你是《龙族》系列小说的情节规划师，熟悉江南的写作风格和龙族世界观。

{JIANGNAN_STYLE_GUIDE}

你的任务是：
1. 分析已有的情节发展和角色状态
2. 规划下一章的情节大纲
3. 确保情节连贯性和角色发展合理性
4. 保持江南风格的叙事节奏

规划时要考虑：
- 情节的因果关系和逻辑性
- 角色的性格和发展轨迹
- 龙族世界观的设定
- 情节的起承转合
- 高潮与低谷的节奏安排

输出格式为JSON，包含：
- chapter_number: 章节号
- title: 章节标题（要具体，包含关键情节元素）
- plot_points: 3-5个关键情节点（具体描述发生什么）
- character_arcs: 主要角色的发展变化（角色名: 变化描述）
- setting: 场景设定（具体地点）
- mood: 情感基调
- themes: 核心主题
- key_events: 关键事件序列（用→连接）
- estimated_word_count: 预计字数
""",
            model="gpt-4o"
        )
    
    def get_context_for_planning(self, current_chapter: int) -> str:
        """获取规划所需的上下文信息"""
        
        context_parts = []
        
        # 1. 获取前情摘要（最近10章详细，之前的简略）
        context_parts.append("=" * 60)
        context_parts.append("📚 前情摘要")
        context_parts.append("=" * 60)
        
        if current_chapter > 10:
            # 之前章节的简略摘要（使用合并因子5）
            merged_summary = self.merge_system.format_merged_plot_summary(
                current_chapter - 1, 
                merge_factor=5
            )
            context_parts.append("\n📋 早期章节概览（简略）：")
            context_parts.append(merged_summary)
            context_parts.append("")
        
        # 2. 获取最近10章的详细大纲
        context_parts.append("\n📖 最近10章详细大纲：")
        context_parts.append("-" * 40)
        
        start_chapter = max(1, current_chapter - 10)
        for ch_num in range(start_chapter, current_chapter):
            chapter = self.plot_api.get_chapter_by_number(ch_num)
            if chapter:
                context_parts.append(f"\n第{ch_num}章: {chapter['title']}")
                context_parts.append(f"  摘要: {chapter['summary']}")
                context_parts.append(f"  情节要点: {chapter['plot_point']}")
                context_parts.append(f"  关键事件: {chapter['key_events']}")
                context_parts.append(f"  角色焦点: {chapter['character_focus']}")
                context_parts.append(f"  场景设定: {chapter['setting']}")
                context_parts.append(f"  情感基调: {chapter['mood']}")
        
        # 3. 获取最近1章的详细文本（如果有）
        if current_chapter > 1:
            context_parts.append(f"\n📝 第{current_chapter-1}章详细内容：")
            context_parts.append("-" * 40)
            prev_chapter = self.plot_api.get_chapter_by_number(current_chapter - 1)
            if prev_chapter and prev_chapter.get('summary'):
                context_parts.append(prev_chapter['summary'])
        
        # 4. 获取主要角色当前状态
        context_parts.append("\n👥 主要角色当前状态：")
        context_parts.append("-" * 40)
        
        main_characters = ["路明非", "楚子航", "恺撒", "诺诺", "夏弥"]
        for char_name in main_characters:
            character = self.character_api.get_character(char_name)
            if character:
                context_parts.append(f"\n{char_name}:")
                context_parts.append(f"  背景: {character.get('background_story', '')[:200]}...")
                
                # 获取角色最近的发展轨迹
                timeline = self.plot_api.get_character_development_timeline(char_name)
                if timeline:
                    latest_arc = timeline[-1]
                    context_parts.append(f"  最近发展: {latest_arc.get('development', '')}")
                    context_parts.append(f"  情感状态: {latest_arc.get('emotional_state', '')}")
        
        return "\n".join(context_parts)
    
    async def plan_next_chapter(self, current_chapter: int) -> PlotOutline:
        """规划下一章的情节大纲"""
        
        print(f"📋 开始规划第{current_chapter}章...")
        
        # 获取上下文
        context = self.get_context_for_planning(current_chapter)
        
        # 构建规划提示词
        prompt = f"""
请基于以下上下文信息，规划《龙族Ⅰ火之晨曦》第{current_chapter}章的情节大纲。

{context}

请规划第{current_chapter}章的详细大纲，要求：
1. 标题要具体，包含关键情节元素（人名、地点、事件）
2. 情节点要清晰，每个点都是具体发生的事情
3. 角色发展要合理，符合角色性格和已有轨迹
4. 保持江南的写作风格和叙事节奏
5. 确保情节与前文连贯

请以JSON格式输出规划结果。
"""
        
        try:
            result = await Runner.run(self.agent, prompt)
            
            # 解析结果
            if hasattr(result, 'final_output'):
                content = result.final_output
            else:
                content = str(result)
            
            # 尝试解析JSON
            plot_data = json.loads(content)
            return PlotOutline(**plot_data)
            
        except Exception as e:
            print(f"❌ 规划失败: {e}")
            # 返回默认大纲
            return PlotOutline(
                chapter_number=current_chapter,
                title=f"第{current_chapter}章",
                plot_points=["待规划"],
                character_arcs={},
                setting="待定",
                mood="待定",
                themes=["待定"],
                key_events=["待规划"],
                estimated_word_count=2000
            )

# ==================== 写作师 Agent ====================

class WriterAgent:
    """写作师 - 负责根据大纲写作章节内容"""
    
    def __init__(self):
        self.plot_api = PlotAPI()
        self.character_api = CharacterAPI()
        
        # 创建写作师Agent
        self.agent = Agent(
            name="龙族写作师",
            instructions=f"""
你是《龙族》系列小说的写作师，精通江南的写作风格。

{JIANGNAN_STYLE_GUIDE}

写作要点：
1. **细腻的心理描写**：大量内心独白，展现角色内心世界
2. **生动的对话**：口语化、幽默、带网络用语
3. **丰富的细节**：环境、动作、表情的细致描写
4. **节奏控制**：日常与戏剧性交替，张弛有度
5. **情感渲染**：略带悲凉的青春感，孤独与渴望

写作风格示例：
- 内心独白: "路明非觉得..."、"他想..."、"真烦真烦真烦！"
- 环境描写: "又是春天了，路明非这一年十八岁。"
- 对话风格: "姐姐……那我该怎么办？"、"你能更没有道德一点么？"
- 比喻: "像只被抛弃的小猎犬"、"钢刀一样的女孩"
- 情感: "路明非觉得自己的灵魂被提升到天空里"

要求：
1. 严格遵循给定的情节大纲
2. 保持江南的语言风格和叙事节奏
3. 字数控制在2000字左右
4. 确保与前文情节连贯
5. 刻画角色性格和心理活动

输出为完整的章节文本，包含对话、心理描写、环境描写、情节推进。
""",
            model="gpt-4o"
        )
    
    def get_context_for_writing(self, chapter_outline: PlotOutline) -> str:
        """获取写作所需的上下文信息"""
        
        context_parts = []
        
        # 1. 当前章节大纲
        context_parts.append("📋 本章节大纲")
        context_parts.append("=" * 60)
        context_parts.append(f"章节号: 第{chapter_outline.chapter_number}章")
        context_parts.append(f"标题: {chapter_outline.title}")
        context_parts.append(f"预计字数: {chapter_outline.estimated_word_count}字")
        context_parts.append("")
        
        context_parts.append("🎯 情节要点:")
        for i, point in enumerate(chapter_outline.plot_points, 1):
            context_parts.append(f"  {i}. {point}")
        context_parts.append("")
        
        context_parts.append("⚡ 关键事件序列:")
        for event in chapter_outline.key_events:
            context_parts.append(f"  • {event}")
        context_parts.append("")
        
        context_parts.append("👥 角色发展:")
        for char_name, development in chapter_outline.character_arcs.items():
            context_parts.append(f"  • {char_name}: {development}")
        context_parts.append("")
        
        context_parts.append(f"🏛️ 场景设定: {chapter_outline.setting}")
        context_parts.append(f"🌟 情感基调: {chapter_outline.mood}")
        context_parts.append(f"💭 核心主题: {', '.join(chapter_outline.themes)}")
        context_parts.append("")
        
        # 2. 获取上一章的详细内容作为衔接参考
        if chapter_outline.chapter_number > 1:
            context_parts.append(f"\n📝 上一章({chapter_outline.chapter_number-1}章)结尾参考：")
            context_parts.append("-" * 40)
            prev_chapter = self.plot_api.get_chapter_by_number(chapter_outline.chapter_number - 1)
            if prev_chapter:
                context_parts.append(f"标题: {prev_chapter['title']}")
                context_parts.append(f"摘要: {prev_chapter['summary'][:300]}...")
        
        # 3. 获取相关角色信息
        context_parts.append("\n👤 相关角色详细信息：")
        context_parts.append("-" * 40)
        
        for char_name in chapter_outline.character_arcs.keys():
            character = self.character_api.get_character(char_name)
            if character:
                context_parts.append(f"\n{char_name}:")
                context_parts.append(f"  背景: {character.get('background_story', '')[:200]}")
                
                # 性格特征
                if 'personality_traits' in character and character['personality_traits']:
                    traits = character['personality_traits']
                    if isinstance(traits, list):
                        trait_list = [t.get('trait', str(t)) if isinstance(t, dict) else str(t) for t in traits]
                        context_parts.append(f"  性格: {', '.join(trait_list[:5])}")
                
                # 说话风格
                if 'speech_patterns' in character and character['speech_patterns']:
                    patterns = character['speech_patterns']
                    if isinstance(patterns, list):
                        pattern_list = [p.get('pattern', str(p)) if isinstance(p, dict) else str(p) for p in patterns]
                        context_parts.append(f"  说话风格: {', '.join(pattern_list[:3])}")
        
        return "\n".join(context_parts)
    
    async def write_chapter(self, chapter_outline: PlotOutline) -> ChapterContent:
        """根据大纲写作章节内容"""
        
        print(f"✍️ 开始写作第{chapter_outline.chapter_number}章: {chapter_outline.title}")
        
        # 获取写作上下文
        context = self.get_context_for_writing(chapter_outline)
        
        # 构建写作提示词
        prompt = f"""
请根据以下大纲和上下文信息，写作《龙族Ⅰ火之晨曦》第{chapter_outline.chapter_number}章的完整内容。

{context}

写作要求：
1. **严格遵循江南的写作风格**（见上文风格指南）
2. **字数**: 约{chapter_outline.estimated_word_count}字
3. **包含元素**:
   - 细腻的心理描写（大量内心独白）
   - 生动的对话（口语化、幽默）
   - 环境和氛围描写
   - 情节推进和转折
   - 角色互动和性格展现
4. **叙事风格**:
   - 使用江南特有的比喻和修辞
   - 短句与长句结合
   - 内心独白与对话交替
   - 细节描写丰富
5. **情感渲染**:
   - 略带悲凉的青春感
   - 角色的孤独与渴望
   - 平凡中的不甘心

请直接输出章节的完整文本内容，不要包含JSON格式，直接就是小说正文。
"""
        
        try:
            result = await Runner.run(self.agent, prompt)
            
            # 提取内容
            if hasattr(result, 'final_output'):
                content = result.final_output
            else:
                content = str(result)
            
            # 生成摘要
            summary = self._generate_summary(content, chapter_outline)
            
            # 创建章节内容对象
            chapter_content = ChapterContent(
                chapter_number=chapter_outline.chapter_number,
                title=chapter_outline.title,
                content=content,
                word_count=len(content),
                summary=summary,
                plot_point=", ".join(chapter_outline.plot_points),
                key_events=" → ".join(chapter_outline.key_events),
                character_focus=", ".join(chapter_outline.character_arcs.keys()),
                setting=chapter_outline.setting,
                mood=chapter_outline.mood,
                themes=", ".join(chapter_outline.themes)
            )
            
            return chapter_content
            
        except Exception as e:
            print(f"❌ 写作失败: {e}")
            raise
    
    def _generate_summary(self, content: str, outline: PlotOutline) -> str:
        """根据章节内容生成摘要"""
        
        # 简单实现：取前300字作为摘要的基础
        summary_base = content[:300] if len(content) > 300 else content
        
        # 添加情节要点
        summary = f"{summary_base}... 本章主要情节：{', '.join(outline.plot_points[:3])}"
        
        return summary

# ==================== 续写管理器 ====================

class ContinuationManager:
    """续写管理器 - 统筹规划和写作流程"""
    
    def __init__(self):
        self.planner = PlotPlannerAgent()
        self.writer = WriterAgent()
        self.plot_api = PlotAPI()
    
    async def continue_story(self, next_chapter_number: int) -> ChapterContent:
        """续写下一章"""
        
        print(f"🚀 开始续写第{next_chapter_number}章")
        print("=" * 80)
        
        # Step 1: 规划情节大纲
        print("\n📋 Step 1: 规划情节大纲...")
        outline = await self.planner.plan_next_chapter(next_chapter_number)
        
        print(f"✅ 大纲已生成:")
        print(f"  标题: {outline.title}")
        print(f"  情节点数: {len(outline.plot_points)}")
        print(f"  涉及角色: {', '.join(outline.character_arcs.keys())}")
        
        # Step 2: 根据大纲写作
        print(f"\n✍️ Step 2: 写作章节内容...")
        chapter_content = await self.writer.write_chapter(outline)
        
        print(f"✅ 写作完成:")
        print(f"  字数: {chapter_content.word_count}字")
        print(f"  摘要: {chapter_content.summary[:100]}...")
        
        # Step 3: 保存到数据库
        print(f"\n💾 Step 3: 保存到数据库...")
        self._save_to_database(chapter_content)
        
        print(f"✅ 已保存到数据库")
        print("=" * 80)
        print(f"🎉 第{next_chapter_number}章续写完成！")
        
        return chapter_content
    
    def _save_to_database(self, chapter: ChapterContent):
        """保存章节内容到数据库"""
        
        # 保存章节信息
        chapter_id = self.plot_api.add_chapter(
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            summary=chapter.summary,
            word_count=chapter.word_count,
            plot_point=chapter.plot_point,
            key_events=chapter.key_events,
            character_focus=chapter.character_focus,
            setting=chapter.setting,
            mood=chapter.mood,
            themes=chapter.themes,
            notes=f"AI续写于{datetime.now().isoformat()}"
        )
        
        # 保存章节完整文本（作为笔记）
        # 注意：这里只保存到数据库的notes字段，实际文本可以保存到独立文件
        
        # 保存角色发展轨迹
        # TODO: 解析章节内容中的角色发展，保存到character_arcs表
        
        return chapter_id

# ==================== 测试函数 ====================

async def test_writing_system():
    """测试写作系统"""
    
    print("🧪 测试龙族续写系统")
    print("=" * 80)
    
    manager = ContinuationManager()
    
    # 测试规划第26章
    next_chapter = 26
    
    chapter_content = await manager.continue_story(next_chapter)
    
    print("\n📄 生成的章节预览:")
    print("-" * 60)
    print(chapter_content.content[:500])
    print("...")
    
    print(f"\n📊 章节信息:")
    print(f"  章节号: 第{chapter_content.chapter_number}章")
    print(f"  标题: {chapter_content.title}")
    print(f"  字数: {chapter_content.word_count}字")
    print(f"  摘要: {chapter_content.summary[:150]}...")

if __name__ == "__main__":
    asyncio.run(test_writing_system())
