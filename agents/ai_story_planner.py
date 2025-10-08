#!/usr/bin/env python3
"""
AI驱动的故事规划系统
使用AI Agent动态生成长期和短期规划
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.plot_api import PlotAPI
from database.database_api import CharacterAPI
from database.storyline_database import StorylineAPI
from agents import Agent, Runner
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json

# ==================== 数据模型 ====================

class StoryArcPlan(BaseModel):
    """故事弧线规划"""
    arc_name: str
    arc_number: int
    start_chapter: int
    estimated_end_chapter: int
    main_theme: str
    key_events: List[str]
    character_focus: List[str]
    setting: str
    tone: str
    arc_type: str  # daily/adventure/crisis/transition

class ChapterGuidance(BaseModel):
    """单章指导"""
    chapter_number: int
    position_in_arc: str
    suggested_focus: str
    pacing: str
    tone: str
    character_notes: Dict[str, str]  # 角色名 -> 性格提醒
    content_suggestions: List[str]
    avoid_list: List[str]

# ==================== AI长期规划师 ====================

class AILongTermPlanner:
    """AI驱动的长期规划师 - 负责生成故事弧线规划"""
    
    def __init__(self):
        self.plot_api = PlotAPI()
        self.character_api = CharacterAPI()
        self.storyline_api = StorylineAPI()  # 添加支线API
        
        self.agent = Agent(
            name="龙族长期规划师",
            instructions="""
你是《龙族》系列的长期故事规划师。你的任务是：

1. 分析当前故事进度
2. 规划接下来的故事弧线（10-15章为一个弧线）
3. 确定弧线的主题、节奏、关键事件
4. 保持江南的叙事风格和节奏

规划原则：
- 日常与冒险交替：紧张的冒险后要有日常缓冲
- 角色成长：每个弧线都要有角色的成长和变化
- 伏笔与揭秘：埋下伏笔，适时揭开谜团
- 节奏控制：开篇慢热，中期发展，高潮迭起，结尾留白

请输出JSON格式的规划。
""",
            model="gpt-4o"
        )
    
    def _get_story_context(self) -> str:
        """获取当前故事上下文"""
        
        # 获取最新章节
        all_chapters = []
        for i in range(1, 100):  # 假设最多100章
            ch = self.plot_api.get_chapter_by_number(i)
            if ch:
                all_chapters.append(ch)
            else:
                break
        
        if not all_chapters:
            return "当前没有任何章节"
        
        latest_chapter = all_chapters[-1]
        total_chapters = len(all_chapters)
        
        context = []
        context.append(f"当前进度: 已写到第{total_chapters}章")
        context.append(f"最新章节: 第{latest_chapter['chapter_number']}章 - {latest_chapter['title']}")
        context.append(f"最新摘要: {latest_chapter.get('summary', '')[:200]}")
        
        # 最近5章概览
        context.append("\n最近5章概览:")
        for ch in all_chapters[-5:]:
            context.append(f"  第{ch['chapter_number']}章: {ch['title']}")
            context.append(f"    情节: {ch.get('plot_point', '')}")
        
        return "\n".join(context)
    
    async def generate_next_arc_plan(self, current_chapter: int) -> Dict[str, Any]:
        """生成下一个故事弧线的规划"""
        
        print(f"🎬 AI长期规划师正在规划第{current_chapter}章之后的故事弧线...")
        
        context = self._get_story_context()
        
        prompt = f"""
{context}

请基于以上信息，规划接下来的故事弧线（从第{current_chapter}章开始）。

当前故事背景：
- 第一部（1-25章）：路明非在卡塞尔学院的第一学期，经历三峡任务，对抗龙王诺顿
- 现在应该进入：暑假回国篇

请规划一个新的故事弧线，包含：
1. 弧线名称（简洁有力）
2. 起始章节和预计结束章节（一个弧线通常10-15章）
3. 主题（这个弧线要表达什么）
4. 关键事件列表（5-8个主要事件）
5. 聚焦角色（主要涉及哪些角色）
6. 主要场景（故事发生在哪里）
7. 基调（轻松/紧张/悲凉/热血等）
8. 弧线类型（daily日常/adventure冒险/crisis危机/transition过渡）

注意事项：
- 第一部结束后，路明非应该回国度暑假
- 回国篇应该是日常为主，展现双重身份的矛盾
- 要见到高中同学（陈雯雯、赵孟华等）
- 家庭关系的探讨
- 可以有小型龙族事件，但不要太大规模
- 为第二学期铺垫

请输出JSON格式：
{{
    "arc_name": "弧线名称",
    "arc_number": {(current_chapter // 25) + 2},
    "start_chapter": {current_chapter},
    "estimated_end_chapter": {current_chapter + 14},
    "main_theme": "主题描述",
    "key_events": ["事件1", "事件2", ...],
    "character_focus": ["路明非", ...],
    "setting": "主要场景",
    "tone": "基调",
    "arc_type": "类型"
}}
"""
        
        try:
            result = await Runner.run(self.agent, prompt)
            
            # 解析AI返回的JSON
            response_text = str(result)
            
            # 提取JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                arc_plan = json.loads(json_match.group(0))
                print(f"✅ 生成弧线规划: {arc_plan.get('arc_name', '未命名')}")
                return arc_plan
            else:
                print("⚠️ AI返回格式错误，使用默认规划")
                return self._get_default_arc_plan(current_chapter)
        
        except Exception as e:
            print(f"⚠️ 生成弧线规划失败: {e}")
            return self._get_default_arc_plan(current_chapter)
    
    def _get_default_arc_plan(self, current_chapter: int) -> Dict[str, Any]:
        """默认弧线规划（作为后备）"""
        return {
            "arc_name": "暑假回国：平凡与不凡的交界",
            "arc_number": 2,
            "start_chapter": current_chapter,
            "estimated_end_chapter": current_chapter + 14,
            "main_theme": "双重身份的矛盾与家庭关系",
            "key_events": [
                "学期结束，准备回国",
                "与家人团聚",
                "高中同学聚会",
                "见到陈雯雯",
                "意外的龙族线索",
                "小型事件",
                "路鸣泽再现",
                "做出选择"
            ],
            "character_focus": ["路明非", "陈雯雯", "赵孟华", "路明非家人", "路鸣泽"],
            "setting": "中国国内、路明非家乡",
            "tone": "日常、温情、暗流涌动",
            "arc_type": "daily-transition"
        }

# ==================== AI短期规划师 ====================

class AIShortTermPlanner:
    """AI驱动的短期规划师 - 为单章提供具体指导"""
    
    def __init__(self):
        self.plot_api = PlotAPI()
        self.character_api = CharacterAPI()
        self.storyline_api = StorylineAPI()  # 添加支线API
        
        self.agent = Agent(
            name="龙族单章规划师",
            instructions="""
你是《龙族》系列的单章规划师。你的任务是：

1. 基于长期弧线规划，为单章提供具体建议
2. 提醒重要的人物性格特点
3. 建议本章的节奏、重点、避免事项
4. 确保符合江南的写作风格

重要原则：
- 路明非：废柴、爱吐槽、网络用语、内心OS多、怂但温柔
- 芬格尔：无厘头、损友、搞怪
- 基调要符合弧线类型（日常=轻松，冒险=紧张）
- 暑假回国不是告别，秋季还会回学院

请输出JSON格式的建议。
""",
            model="gpt-4o"
        )
    
    def _get_chapter_context(self, chapter_number: int) -> str:
        """获取章节上下文"""
        
        context = []
        
        # 前一章
        prev_ch = self.plot_api.get_chapter_by_number(chapter_number - 1)
        if prev_ch:
            context.append(f"上一章（第{chapter_number-1}章）: {prev_ch['title']}")
            context.append(f"摘要: {prev_ch.get('summary', '')[:300]}")
            context.append(f"关键事件: {prev_ch.get('key_events', '')}")
        
        # 最近3章趋势
        context.append("\n最近章节趋势:")
        for i in range(max(1, chapter_number - 3), chapter_number):
            ch = self.plot_api.get_chapter_by_number(i)
            if ch:
                context.append(f"  第{i}章: {ch['title']} - {ch.get('mood', '')}")
        
        return "\n".join(context)
    
    def _get_character_notes(self, characters: List[str]) -> Dict[str, str]:
        """获取角色性格提醒"""
        
        notes = {}
        for char_name in characters:
            char_data = self.character_api.get_character(char_name)
            if char_data and isinstance(char_data, dict):
                traits = []
                
                # 性格特质
                if 'personality_traits' in char_data:
                    personality = char_data['personality_traits']
                    if isinstance(personality, list) and len(personality) > 0:
                        for trait in personality[:3]:  # 取前3个
                            if isinstance(trait, dict):
                                traits.append(trait.get('trait', ''))
                
                # 说话方式
                if 'speech_patterns' in char_data:
                    speech = char_data['speech_patterns']
                    if isinstance(speech, list) and len(speech) > 0:
                        pattern = speech[0]
                        if isinstance(pattern, dict):
                            traits.append(f"说话: {pattern.get('pattern', '')}")
                
                if traits:
                    notes[char_name] = ", ".join(traits)
        
        return notes
    
    async def generate_chapter_guidance(
        self, 
        chapter_number: int, 
        arc_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """为单章生成具体指导"""
        
        print(f"📋 AI短期规划师正在为第{chapter_number}章生成指导...")
        
        chapter_context = self._get_chapter_context(chapter_number)
        character_notes = self._get_character_notes(arc_plan.get('character_focus', []))
        
        # 计算在弧线中的位置
        end_chapter = arc_plan.get('estimated_end_chapter') or arc_plan.get('end_chapter', chapter_number + 10)
        progress = (chapter_number - arc_plan['start_chapter']) / \
                   (end_chapter - arc_plan['start_chapter'])
        
        if progress < 0.2:
            position = "opening"
            pacing = "slow"
        elif progress < 0.5:
            position = "development"
            pacing = "medium"
        elif progress < 0.8:
            position = "climax_building"
            pacing = "medium-fast"
        else:
            position = "ending"
            pacing = "fast"
        
        # 兼容数据库字段名
        arc_name = arc_plan.get('arc_name') or arc_plan.get('name', '未命名')
        arc_type = arc_plan.get('arc_type', 'adventure')
        main_theme = arc_plan.get('main_theme', '')
        tone = arc_plan.get('tone', '')
        
        # 获取关键事件（可能在events字段中）
        key_events = arc_plan.get('key_events', [])
        if not key_events and 'events' in arc_plan:
            key_events = [e['event_description'] for e in arc_plan['events']]
        
        prompt = f"""
当前故事弧线: {arc_name}
弧线类型: {arc_type}
弧线主题: {main_theme}
弧线基调: {tone}
弧线关键事件: {', '.join(key_events) if key_events else '无'}

当前章节: 第{chapter_number}章
在弧线中的位置: {position} (进度{progress*100:.0f}%)
建议节奏: {pacing}

{chapter_context}

聚焦角色性格提醒:
{json.dumps(character_notes, ensure_ascii=False, indent=2)}

请为第{chapter_number}章提供具体写作指导：

1. 本章应该聚焦什么（suggested_focus）
2. 本章的基调（tone，符合弧线基调）
3. 本章的节奏（pacing）
4. 角色性格提醒（character_notes，提醒关键性格特点）
5. 内容建议（content_suggestions，3-5条具体建议）
6. 避免事项（avoid_list，3-5条要避免的问题）

特别注意：
- 如果是暑假回国篇，要轻松日常，不是生离死别
- 路明非要有废柴属性、吐槽、网络用语
- 芬格尔要无厘头、搞怪
- 如果是opening阶段，要建立新环境
- 如果是development阶段，要推进情节
- 如果是ending阶段，要收束情节

请输出JSON格式：
{{
    "chapter_number": {chapter_number},
    "position_in_arc": "{position}",
    "suggested_focus": "本章重点",
    "pacing": "{pacing}",
    "tone": "基调",
    "character_notes": {{
        "角色名": "性格提醒",
        ...
    }},
    "content_suggestions": [
        "建议1",
        "建议2",
        ...
    ],
    "avoid_list": [
        "避免1",
        "避免2",
        ...
    ]
}}
"""
        
        try:
            result = await Runner.run(self.agent, prompt)
            
            # 解析AI返回的JSON
            response_text = str(result)
            
            # 提取JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                guidance = json.loads(json_match.group(0))
                print(f"✅ 生成章节指导")
                return guidance
            else:
                print("⚠️ AI返回格式错误，使用默认指导")
                return self._get_default_guidance(chapter_number, arc_plan, position, pacing)
        
        except Exception as e:
            print(f"⚠️ 生成章节指导失败: {e}")
            return self._get_default_guidance(chapter_number, arc_plan, position, pacing)
    
    def _get_default_guidance(
        self, 
        chapter_number: int, 
        arc_plan: Dict[str, Any],
        position: str,
        pacing: str
    ) -> Dict[str, Any]:
        """默认章节指导（作为后备）"""
        return {
            "chapter_number": chapter_number,
            "position_in_arc": position,
            "suggested_focus": arc_plan.get('main_theme', '故事推进'),
            "pacing": pacing,
            "tone": arc_plan.get('tone', '平衡'),
            "character_notes": {
                "路明非": "废柴、爱吐槽、网络用语、内心OS多",
                "芬格尔": "无厘头、损友、搞怪"
            },
            "content_suggestions": [
                f"推进弧线主题：{arc_plan.get('main_theme', '')}",
                f"展现角色：{', '.join(arc_plan.get('character_focus', [])[:2])}",
                f"保持基调：{arc_plan.get('tone', '')}"
            ],
            "avoid_list": [
                "过于沉重的基调",
                "人物性格失真",
                "节奏过快或过慢"
            ]
        }

# ==================== 统一的规划管理器 ====================

class AIStoryPlanningManager:
    """AI驱动的故事规划管理器"""
    
    def __init__(self):
        self.long_term_planner = AILongTermPlanner()
        self.short_term_planner = AIShortTermPlanner()
        self.current_arc_plan = None
    
    async def get_chapter_guidance(self, chapter_number: int) -> str:
        """获取章节的完整规划指导"""
        
        print("=" * 60)
        print(f"🎯 AI规划系统：为第{chapter_number}章生成规划")
        print("=" * 60)
        
        # 1. 从数据库获取主线/支线上下文
        storyline_context = self.long_term_planner.storyline_api.format_context_for_ai(chapter_number)
        
        # 2. 获取当前活跃支线
        active_storyline = self.long_term_planner.storyline_api.db.get_active_storyline(chapter_number)
        
        if active_storyline is None:
            print("⚠️ 没有活跃支线，需要AI生成新支线")
            # TODO: 让AI生成新支线并保存到数据库
            active_storyline = await self.long_term_planner.generate_next_arc_plan(chapter_number)
        
        # 3. 为当前章节生成短期指导
        chapter_guidance = await self.short_term_planner.generate_chapter_guidance(
            chapter_number, 
            active_storyline
        )
        
        # 4. 格式化输出（包含数据库的主线/支线信息）
        guidance_text = storyline_context + "\n\n" + self._format_chapter_guidance(chapter_guidance)
        
        return guidance_text
    
    def _format_chapter_guidance(self, chapter_guidance: Dict) -> str:
        """格式化章节指导为文本"""
        
        lines = []
        lines.append("=" * 60)
        lines.append("💡 AI生成的本章具体指导")
        lines.append("=" * 60)
        lines.append(f"\n📍 本章位置: {chapter_guidance['position_in_arc']}")
        lines.append(f"⏱️ 建议节奏: {chapter_guidance['pacing']}")
        lines.append(f"🎭 本章基调: {chapter_guidance['tone']}")
        lines.append(f"🎯 本章重点: {chapter_guidance['suggested_focus']}")
        
        lines.append(f"\n👥 角色性格提醒:")
        for char, note in chapter_guidance.get('character_notes', {}).items():
            lines.append(f"   【{char}】{note}")
        
        lines.append(f"\n✅ 内容建议:")
        for i, suggestion in enumerate(chapter_guidance.get('content_suggestions', []), 1):
            lines.append(f"   {i}. {suggestion}")
        
        lines.append(f"\n❌ 避免事项:")
        for i, avoid in enumerate(chapter_guidance.get('avoid_list', []), 1):
            lines.append(f"   {i}. {avoid}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def _format_guidance(self, arc_plan: Dict, chapter_guidance: Dict) -> str:
        """格式化规划指导为文本（旧版本，保留兼容）"""
        
        lines = []
        lines.append("=" * 60)
        lines.append("📚 AI生成的长期故事规划")
        lines.append("=" * 60)
        lines.append(f"\n🎬 当前故事弧线: {arc_plan['arc_name']}")
        lines.append(f"   章节范围: 第{arc_plan['start_chapter']}-{arc_plan['estimated_end_chapter']}章")
        lines.append(f"   弧线类型: {arc_plan['arc_type']}")
        lines.append(f"   主题: {arc_plan['main_theme']}")
        lines.append(f"   基调: {arc_plan['tone']}")
        lines.append(f"\n🎯 弧线关键事件:")
        for i, event in enumerate(arc_plan['key_events'], 1):
            lines.append(f"   {i}. {event}")
        lines.append(f"\n👥 聚焦角色: {', '.join(arc_plan['character_focus'])}")
        lines.append(f"🏛️ 主要场景: {arc_plan['setting']}")
        
        lines.append("\n" + "=" * 60)
        lines.append("💡 AI生成的本章具体指导")
        lines.append("=" * 60)
        lines.append(f"\n📍 本章位置: {chapter_guidance['position_in_arc']}")
        lines.append(f"⏱️ 建议节奏: {chapter_guidance['pacing']}")
        lines.append(f"🎭 本章基调: {chapter_guidance['tone']}")
        lines.append(f"🎯 本章重点: {chapter_guidance['suggested_focus']}")
        
        lines.append(f"\n👥 角色性格提醒:")
        for char, note in chapter_guidance.get('character_notes', {}).items():
            lines.append(f"   【{char}】{note}")
        
        lines.append(f"\n✅ 内容建议:")
        for i, suggestion in enumerate(chapter_guidance.get('content_suggestions', []), 1):
            lines.append(f"   {i}. {suggestion}")
        
        lines.append(f"\n❌ 避免事项:")
        for i, avoid in enumerate(chapter_guidance.get('avoid_list', []), 1):
            lines.append(f"   {i}. {avoid}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)

# ==================== 测试 ====================

async def test_ai_planning():
    """测试AI规划系统"""
    
    manager = AIStoryPlanningManager()
    
    # 测试第26章的规划
    guidance = await manager.get_chapter_guidance(26)
    print(guidance)
    
    print("\n✅ AI规划系统测试完成！")

if __name__ == "__main__":
    asyncio.run(test_ai_planning())

