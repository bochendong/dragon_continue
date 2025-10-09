#!/usr/bin/env python3
"""
龙族续写系统 - 情节规划师与写作师
基于江南风格的AI写作系统

特点：
- 情节规划师：分析前文，规划下一章大纲
- 写作师：根据大纲写作章节内容
- 自动保存：将续写内容和摘要保存到数据库
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.plot_api import PlotAPI
from database.database_api import CharacterAPI
from ai_story_planner import AIStoryPlanningManager
from agents import Agent, Runner
from pydantic import BaseModel
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# ==================== 江南写作风格指南 ====================

JIANGNAN_STYLE_GUIDE = """
江南《龙族》写作风格核心特点：

1. **超密集的小动作和细节 - 最重要！**
   - 每隔几句话就要有具体动作
   - 例：挠头、干笑、踢石子、低头看鞋、两手抄裤兜、歪着脑袋
   - 例：摘下墨镜在衣服上擦、鼓着腮帮子、翻着三白眼
   - ❌ 不要写"他很紧张" ✅ 要写"他挠了挠头，干笑两声"

2. **路明非式的自嘲吐槽内心独白**
   - 大量"真见鬼！"、"TNND！"、"我靠！"、"擦！"
   - 自嘲式吐槽："这什么狗屁剧情？"、"我就是条土狗"
   - 荒诞的比喻："感觉像是穿着圣衣的胸铠"
   - 对自己的嘲讽："路明非觉得自己就是个白痴"

3. **对话要密集，要有信息量**
   - 不要大段环境描写，要用对话推进
   - 路明非的怂话："呵呵，厉害厉害"、"哦哦"、"嗯嗯"
   - 路鸣泽的阴阳怪气："哥哥真是温柔呢"、"哥哥看起来有点落魄呢"
   - 对话中要有小动作穿插

4. **荒诞的生活细节和黑色幽默**
   - 提着马桶圈去聚会
   - 信用卡被拒
   - 走错厕所
   - 各种衰事连连

5. **场景要具体丰富**
   - 不要空洞的"走在街上"
   - 要有"菜贩吆喝"、"煎饼摊香味"、"蝉鸣声"
   - 每个场景都要有具体的细节

6. **节奏：日常→小尴尬→大尴尬**
   - 从平淡的日常开始
   - 逐渐推进到尴尬场面
   - 通过对话和动作展现冲突

写作禁忌：
❌ 大段环境描写没有人物互动
❌ 直接写心理状态
❌ 对话太少
❌ 缺少自嘲吐槽
❌ 动作不够密集
"""

# ==================== 数据模型 ====================

class PlotOutline(BaseModel):
    """情节大纲模型"""
    chapter_number: int
    title: str
    plot_points: List[str]
    character_arcs: Dict[str, str]
    setting: str
    mood: str
    themes: List[str]
    key_events: List[str]
    estimated_word_count: int = 2500

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

# ==================== 情节规划师 ====================

class StoryPlanner:
    """情节规划师"""
    
    def __init__(self):
        self.plot_api = PlotAPI()
        self.character_api = CharacterAPI()
        self.ai_planning_manager = AIStoryPlanningManager()  # AI驱动的规划管理器
        
        self.agent = Agent(
            name="龙族情节规划师",
            instructions=f"""
你是《龙族》系列小说的情节规划师，熟悉江南的写作风格和龙族世界观。

{JIANGNAN_STYLE_GUIDE}

==================== 规划原则 ====================

【核心要求】
1. 情节必须超级具体：人名、地点、具体动作、对话内容
2. 必须包含日常衰事和荒诞情节
3. 必须有人物互动和对话冲突
4. 避免抽象描述如"心理挣扎"、"成长蜕变"

【好的情节设计】
✅ "路明非去超市买东西，遇到开新车的赵孟华炫耀，然后路鸣泽出现嘲讽他"
✅ "塑料袋破了，鸡蛋摔碎，正狼狈时陈雯雯出现"
✅ "婶婶让他跑腿买菜，买大米还要扛回去"

【坏的情节设计】
❌ "路明非反思自己的身份认同问题"
❌ "他在日常生活中感受到孤独和疏离"
❌ "通过与同学的相遇，他意识到成长的意义"

【情节要素】
每个情节点必须包含：
1. 具体场景（超市、菜市场、街角、家里）
2. 具体事件（买东西、遇见人、东西坏了）
3. 对话内容（谁说了什么）
4. 衰事/冲突（出糗、尴尬、被嘲讽）

【关键事件设计】
必须包含以下元素之一：
- 日常衰事（东西掉了、走错地方、被误会）
- 人物冲突（被炫耀、被嘲讽、尴尬相遇）
- 荒诞情节（提着奇怪的东西、说错话、做错事）
- 温情时刻（突然的善意、小小的温暖）

【角色发展要具体】
✅ "路明非从一开始的怂变成最后买双份鸡蛋煎饼"
✅ "路鸣泽出现三次，每次都戳他痛处"

❌ "路明非内心成长"
❌ "路鸣泽展现神秘"

输出JSON格式，包含所有必要字段。
情节点必须具体到可以直接写成场景。
""",
            model="gpt-4o"
        )
    
    def _get_recent_chapters_context(self, current_chapter: int, num_chapters: int = 10) -> str:
        """获取最近N章的详细上下文"""
        
        context = []
        context.append("📖 最近章节详细大纲：")
        context.append("=" * 50)
        
        start = max(1, current_chapter - num_chapters)
        for ch_num in range(start, current_chapter):
            chapter = self.plot_api.get_chapter_by_number(ch_num)
            if chapter:
                context.append(f"\n第{ch_num}章: {chapter['title']}")
                
                # 优先使用notes字段（完整正文或详细总结），否则使用summary
                detailed_content = chapter.get('notes', '') or chapter.get('summary', '')
                
                # 如果是最后一章（即上一章），提供更详细的内容
                if ch_num == current_chapter - 1 and detailed_content:
                    context.append(f"详细内容: {detailed_content[:2000]}...")  # 最多显示2000字
                else:
                    context.append(f"摘要: {chapter['summary']}")
                
                context.append(f"情节要点: {chapter['plot_point']}")
                context.append(f"关键事件: {chapter['key_events']}")
                context.append(f"角色焦点: {chapter['character_focus']}")
                context.append(f"场景: {chapter['setting']}")
        
        return "\n".join(context)
    
    def _get_earlier_chapters_summary(self, current_chapter: int) -> str:
        """获取早期章节的简略摘要"""
        
        if current_chapter <= 10:
            return ""
        
        context = []
        context.append("\n📋 早期章节概览（简略）：")
        context.append("=" * 50)
        
        # 直接列出早期章节的标题和简要信息
        for ch_num in range(1, current_chapter - 10):
            chapter = self.plot_api.get_chapter_by_number(ch_num)
            if chapter:
                context.append(f"第{ch_num}章: {chapter['title']} - {chapter.get('plot_point', '')}")
        
        return "\n".join(context)
    
    def _get_original_text_context(self, num_segments: int = 3) -> str:
        """从chapters_2000_words目录读取原文最后几段作为上下文"""
        
        context = []
        context.append("\n📚 原文最后几段节选（用于风格参考）：")
        context.append("=" * 50)
        
        chapters_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chapters_2000_words")
        
        # 获取所有原文文件（001-131）
        original_files = []
        for f in os.listdir(chapters_dir):
            if f.endswith('_未知章节.txt'):
                try:
                    num = int(f.split('_')[0])
                    if 1 <= num <= 131:  # 只要原文
                        original_files.append((num, f))
                except:
                    pass
        
        if not original_files:
            return ""
        
        # 取最后N个文件
        original_files.sort()
        last_files = original_files[-num_segments:]
        
        for num, filename in last_files:
            filepath = os.path.join(chapters_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 跳过头部和尾部的元数据
                    lines = content.split('\n')
                    
                    # 找到第一行实际正文（跳过标题、作者、分隔符）
                    start_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not any(marker in line for marker in ['《龙族', '作者：', '═', '字数统计', '文件编号']):
                            start_idx = i
                            break
                    
                    # 找到最后一行实际正文（跳过尾部的分隔符和统计）
                    end_idx = len(lines)
                    for i in range(len(lines) - 1, -1, -1):
                        line = lines[i]
                        if line.strip() and not any(marker in line for marker in ['═', '字数统计', '文件编号']):
                            end_idx = i + 1
                            break
                    
                    # 提取正文
                    main_content = lines[start_idx:end_idx]
                    text = '\n'.join(main_content).strip()
                    
                    # 取前500字作为参考
                    if len(text) > 500:
                        text = text[:500] + "..."
                    
                    if text:  # 只有在有正文内容时才添加
                        context.append(f"\n[片段{num}节选]")
                        context.append(text)
            except Exception as e:
                print(f"  ⚠️ 读取{filename}失败: {e}")
        
        return "\n".join(context)
    
    def _get_character_info(self, character_names: List[str]) -> str:
        """获取角色详细信息"""
        
        context = []
        context.append("\n👥 相关角色信息：")
        context.append("=" * 50)
        
        for name in character_names:
            character = self.character_api.get_character(name)
            if character and isinstance(character, dict):
                context.append(f"\n{name}:")
                context.append(f"  背景: {character.get('background_story', '')[:200]}")
                
                if 'bloodline' in character and character['bloodline']:
                    bloodline = character['bloodline']
                    if isinstance(bloodline, dict):
                        context.append(f"  血统: {bloodline.get('bloodline_level', '')}级")
                        context.append(f"  言灵: {bloodline.get('spirit_words', '')}")
                
                if 'personality_traits' in character and character['personality_traits']:
                    traits = character['personality_traits']
                    if isinstance(traits, list):
                        trait_list = [t.get('trait', str(t)) if isinstance(t, dict) else str(t) for t in traits[:5]]
                        context.append(f"  性格: {', '.join(trait_list)}")
        
        return "\n".join(context)
    
    async def plan_next_chapter(self, next_chapter_number: int) -> PlotOutline:
        """规划下一章"""
        
        print(f"📋 规划第{next_chapter_number}章...")
        
        # 构建上下文
        context_parts = []
        
        # ========== AI生成的双层规划 ==========
        ai_guidance = await self.ai_planning_manager.get_chapter_guidance(next_chapter_number)
        context_parts.append(ai_guidance)
        
        # 早期章节概览
        earlier_summary = self._get_earlier_chapters_summary(next_chapter_number)
        if earlier_summary:
            context_parts.append(earlier_summary)
        
        # 最近章节详细
        recent_chapters = self._get_recent_chapters_context(next_chapter_number, 10)
        context_parts.append(recent_chapters)
        
        # 原文最后几段参考（用于保持文风一致）
        original_text = self._get_original_text_context(3)
        if original_text:
            context_parts.append(original_text)
        
        # 主要角色信息
        main_characters = ["路明非", "芬格尔", "诺诺", "楚子航", "恺撒"]
        character_info = self._get_character_info(main_characters)
        context_parts.append(character_info)
        
        context = "\n".join(context_parts)
        
        # 构建提示词
        prompt = f"""
{context}

请基于以上信息，规划《龙族Ⅰ火之晨曦》第{next_chapter_number}章的情节大纲。

⚠️ 重要：请特别注意上面的【📚 长期故事规划】和【💡 本章具体内容建议】！
这些是整体故事弧线的规划，确保本章内容符合长期规划的方向。

==================== 规划要求 ====================

【标题要求】
✅ 好：超市、煎饼和赵孟华的新车
✅ 好：路明非的尴尬相遇
❌ 坏：成长与反思
❌ 坏：双重身份的困惑

【情节点要求】每个情节点必须超级具体
✅ 好：
- "婶婶让路明非去超市买菜，还要买十斤大米扛回去"
- "路边遇到赵孟华开新车炫耀，说去了马尔代夫"
- "塑料袋破了，鸡蛋摔碎一地，正狼狈时陈雯雯出现"
- "路鸣泽突然出现，阴阳怪气地说'哥哥看起来有点落魄呢'"

❌ 坏：
- "路明非反思自己的处境"
- "他感受到身份的割裂"
- "与同学的相遇让他思考未来"

【关键事件要求】必须包含以下元素
1. 具体的日常衰事（东西坏了、走错地方、被误会）
2. 人物对话和冲突（被炫耀、被嘲讽、尴尬对话）
3. 小温暖或小悬念（芬格尔的消息、意外的善意）

【角色发展要求】
✅ 好："路明非从怂怂地应付赵孟华，到最后买双份煎饼，略有成长"
❌ 坏："路明非内心成长，更加坚定"

【场景要求】
必须是具体场景：家里、超市、菜市场、街角、煎饼摊、路边
不要抽象场景：内心世界、回忆中的某处

【情节结构建议】
开场：日常任务（买菜、跑腿）
发展：衰事连连（遇见人、东西坏）
高潮：尴尬或冲突（被炫耀、被嘲讽）  
结尾：小温暖（朋友消息、自我接纳）

现在请输出JSON格式的大纲：
{{
    "chapter_number": {next_chapter_number},
    "title": "具体的章节标题（必须包含人物、地点或事件）",
    "plot_points": ["超级具体的情节点1", "超级具体的情节点2", "超级具体的情节点3", "超级具体的情节点4", "超级具体的情节点5"],
    "character_arcs": {{"路明非": "具体的行为变化，不要说内心成长"}},
    "setting": "具体场景列表",
    "mood": "基调",
    "themes": ["主题"],
    "key_events": ["超级具体的事件1", "超级具体的事件2", "超级具体的事件3"],
    "estimated_word_count": 2500
}}
"""
        
        try:
            result = await Runner.run(self.agent, prompt)
            
            # 解析结果
            if hasattr(result, 'final_output'):
                output = result.final_output
            else:
                output = str(result)
            
            # 尝试从output中提取JSON
            output = output.strip()
            if '```json' in output:
                output = output.split('```json')[1].split('```')[0].strip()
            elif '```' in output:
                output = output.split('```')[1].split('```')[0].strip()
            
            plot_data = json.loads(output)
            
            print(f"✅ 规划完成: {plot_data['title']}")
            
            return PlotOutline(**plot_data)
            
        except Exception as e:
            print(f"❌ 规划失败: {e}")
            import traceback
            traceback.print_exc()
            raise

# ==================== 写作师 ====================

class StoryWriter:
    """写作师"""
    
    def __init__(self):
        self.plot_api = PlotAPI()
        self.character_api = CharacterAPI()
        
        self.agent = Agent(
            name="龙族写作师",
            instructions=f"""
你是《龙族》系列小说的写作师，必须严格模仿江南的写作风格。

{JIANGNAN_STYLE_GUIDE}

==================== 核心写作原则 ====================

【原则1：动作密度 - 每3-5句话必须有一个具体动作】
✅ 好的写法：
"路明非挠了挠头，干笑两声：'呵呵，厉害厉害。'"
"他低头看着自己的人字拖，用脚尖踢了踢地上的小石子。"
"赵孟华摘下墨镜，在衣服上慢慢擦了擦，动作很慢，像生怕别人没注意到那是雷朋。"

❌ 禁止的写法：
"他心里很不爽。"
"他感到一阵尴尬。"
"他的语气充满了炫耀。"

【原则2：路明非的自嘲吐槽内心独白 - 每段必须有】
✅ 必须使用的句式：
- "真见鬼！"、"TNND！"、"我靠！"、"擦！"
- "这什么狗屁剧情？"
- "路明非觉得自己就是个白痴"
- "真他妈的丢人"

例子：
"真见鬼！婶婶这是让他去超市搬家吗？"
"TNND！每次这小子出现都要说些莫名其妙的话！"
"真他妈的丢人。S级路明非，此刻正扛着一袋大米，像个搬家的民工。"

【原则3：对话推进 - 对话量占比至少50%】
✅ 对话要有来有往，要有小动作穿插：
"你在美国过得怎么样？"赵孟华问。
"还行吧。"路明非挠了挠头。
"我现在在一家外企工作，待遇不错。"赵孟华掏出手机，"你看，这是在马尔代夫拍的。"
路明非凑过去看了一眼："哦，不错不错。"
心里想：我能说我在学怎么屠龙吗？

❌ 禁止大段环境描写：
不要写"阳光洒在街道上，微风吹过树梢，远处传来鸟鸣声……"这种连续的环境描写。

【原则4：荒诞的生活细节】
必须加入日常生活中的衰事：
- 塑料袋破了
- 忘带钱包
- 走错地方
- 被人误会
- 尴尬的巧遇

例子：
"塑料袋突然破了。鸡蛋'啪'的一声掉在地上，蛋液流了一地。"
"正狼狈时，陈雯雯出现了。真见鬼！怎么这时候遇见她？"

【原则5：具体的场景细节】
不要空洞描写，要有具体的：
✅ 声音："蝉鸣声一阵阵的"、"菜贩扯着嗓子吆喝"
✅ 气味："煎饼的香味"、"鱼腥味混着蔬菜的味道"
✅ 温度："太阳毒得很"、"汗水把T恤都湿透了"
✅ 触觉："十斤的大米扛在肩上，越来越重"

==================== 写作流程 ====================

第1步：开场
- 必须从具体的日常场景开始
- 立即加入对话或动作
- 不要大段环境铺垫

第2步：推进
- 用对话推进情节
- 每段对话后加小动作
- 插入路明非的自嘲吐槽

第3步：冲突
- 通过对话展现冲突
- 用小动作展现情绪
- 不要直接说"他很生气"

第4步：结尾
- 可以略带温情
- 路明非的自我反思（但不要说教）
- 为下一章留悬念

==================== 具体要求 ====================

1. 每个场景必须有具体的动作描写
2. 每段必须有对话或内心吐槽
3. 路明非的语言：怂、自嘲、但偶尔有小温暖
4. 路鸣泽的语言：阴阳怪气、句句戳心
5. 其他人物：每人都要有特点

6. 禁止使用的表达：
   - "他心里/心中……"（除非是吐槽）
   - "他感到……"
   - "他觉得……"（除非是自嘲）
   - 大段环境描写
   - 抽象的情绪描述

7. 必须使用的表达：
   - 具体动作（挠头、踢石子等）
   - "真见鬼！"、"TNND！"等吐槽
   - 荒诞的比喻
   - 密集的对话

8. 字数控制：
   - 对话和动作：60%
   - 自嘲吐槽：20%
   - 场景描写：20%
""",
            model="gpt-4o"
        )
    
    async def write_chapter(self, outline: PlotOutline) -> str:
        """根据大纲写作章节"""
        
        print(f"✍️ 开始写作第{outline.chapter_number}章...")
        
        # 获取上一章的详细内容作为衔接
        prev_chapter_context = ""
        if outline.chapter_number > 1:
            prev_ch = self.plot_api.get_chapter_by_number(outline.chapter_number - 1)
            if prev_ch:
                # 优先使用notes字段存储的完整文本，否则使用summary
                full_text = prev_ch.get('notes', '') or prev_ch.get('summary', '')
                
                # 如果文本很长，取最后1000字作为衔接参考
                if len(full_text) > 1000:
                    text_excerpt = "..." + full_text[-1000:]
                else:
                    text_excerpt = full_text
                
                prev_chapter_context = f"""
上一章详细内容（第{outline.chapter_number-1}章: {prev_ch['title']}）：
{text_excerpt}

注：请根据上一章的结尾，自然地展开第{outline.chapter_number}章的内容。
"""
        
        # 获取角色信息
        character_details = []
        for char_name in outline.character_arcs.keys():
            character = self.character_api.get_character(char_name)
            if character and isinstance(character, dict):
                char_info = f"{char_name}: {character.get('background_story', '')[:150]}"
                
                # 添加性格特征
                if 'personality_traits' in character and character['personality_traits']:
                    traits = character['personality_traits']
                    if isinstance(traits, list) and traits:
                        trait_list = [t.get('trait', str(t)) if isinstance(t, dict) else str(t) for t in traits[:3]]
                        char_info += f"  性格: {', '.join(trait_list)}"
                
                character_details.append(char_info)
        
        character_context = "\n".join(character_details) if character_details else "无特定角色信息"
        
        # 构建写作提示词
        prompt = f"""
请根据以下大纲，写作《龙族Ⅰ火之晨曦》第{outline.chapter_number}章的完整内容。

{prev_chapter_context}

📋 本章大纲：
标题: {outline.title}
场景: {outline.setting}
情感基调: {outline.mood}
核心主题: {', '.join(outline.themes)}

🎯 情节要点：
{chr(10).join(f"{i}. {point}" for i, point in enumerate(outline.plot_points, 1))}

⚡ 关键事件序列：
{' → '.join(outline.key_events)}

👥 角色发展：
{chr(10).join(f"• {name}: {dev}" for name, dev in outline.character_arcs.items())}

👤 角色详情：
{character_context}

==================== 写作要求 ====================

【字数要求】至少{outline.estimated_word_count}字

【结构要求】
开头：从具体场景/对话开始（不要大段环境铺垫）
中间：对话推进为主（60%），动作和吐槽穿插（40%）
结尾：略带温情或悬念

【必须做到】
✅ 每3-5句话有一个具体动作（挠头、踢石子、干笑等）
✅ 每段有路明非的自嘲吐槽（"真见鬼！"、"TNND！"等）
✅ 对话占比至少50%，每段对话后加小动作
✅ 加入荒诞的日常衰事（东西掉了、走错地方、尴尬相遇等）
✅ 具体的五感细节（声音、气味、温度、触觉）

【绝对禁止】
❌ "他心里很不爽"、"他感到尴尬"、"他很紧张"
❌ "他的语气充满了炫耀"、"心中升起某种感觉"
❌ 大段连续的环境描写（超过3句）
❌ 抽象的情绪描述

【写作示例】

坏的写法：
"路明非心里很不高兴，他觉得赵孟华在炫耀。阳光洒在街道上，微风吹过树梢，远处传来鸟鸣声。他感到一阵疏离。"

好的写法：
"路明非低头看着自己的人字拖，用脚尖踢了踢地上的小石子。
'哦，挺好的。'他干笑两声。
心里想：真他妈的，买个车就了不起啊？我在卡塞尔……算了，说了也没人信。"

【对话写法】
必须有来有往，有小动作穿插：

"你在美国过得怎么样？"赵孟华问，掏出手机翻照片。
"还行吧。"路明非挠了挠头。
"我现在在外企，待遇不错。"赵孟华把手机凑过来，"你看，这是在马尔代夫拍的。"
路明非凑过去看了一眼："哦，不错不错。"
心里想：我能说我在学怎么屠龙吗？

【场景写法】
必须有具体细节：

煎饼在铁板上滋滋作响，面粉的香味混着葱花的味道。路明非接过热乎乎的煎饼，咬了一大口。太阳越来越毒，汗水把T恤都湿透了。

现在开始写作，直接输出章节正文。
格式：第X章 标题，然后是正文。
不要有任何JSON或标记格式。
"""
        
        try:
            result = await Runner.run(self.agent, prompt)
            
            # 提取内容
            if hasattr(result, 'final_output'):
                content = result.final_output
            else:
                content = str(result)
            
            # 清理可能的markdown标记
            content = content.strip()
            if content.startswith('```'):
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
            
            print(f"✅ 写作完成: {len(content)}字")
            
            return content
            
        except Exception as e:
            print(f"❌ 写作失败: {e}")
            raise

# ==================== 续写管理器 ====================

class ContinuationManager:
    """续写管理器"""
    
    def __init__(self):
        self.planner = StoryPlanner()
        self.writer = StoryWriter()
        self.plot_api = PlotAPI()
    
    async def continue_next_chapter(self, next_chapter_number: int) -> ChapterContent:
        """续写下一章（完整流程）"""
        
        print(f"\n{'='*80}")
        print(f"🚀 开始续写第{next_chapter_number}章")
        print(f"{'='*80}\n")
        
        # Step 1: 规划情节大纲
        print("📋 Step 1/3: 规划情节大纲...")
        print("-" * 60)
        
        outline = await self.planner.plan_next_chapter(next_chapter_number)
        
        print(f"\n✅ 大纲已生成:")
        print(f"  📖 标题: {outline.title}")
        print(f"  🎯 情节点: {len(outline.plot_points)}个")
        print(f"  👥 涉及角色: {', '.join(outline.character_arcs.keys())}")
        print(f"  🏛️ 场景: {outline.setting}")
        print(f"  💭 主题: {', '.join(outline.themes)}")
        
        # Step 2: 写作章节内容
        print(f"\n✍️ Step 2/3: 写作章节内容...")
        print("-" * 60)
        
        content = await self.writer.write_chapter(outline)
        
        print(f"\n✅ 写作完成:")
        print(f"  📝 字数: {len(content)}字")
        print(f"  📄 预览: {content[:100]}...")
        
        # 生成摘要
        summary = self._generate_summary(content, outline)
        
        # 创建章节对象
        chapter_content = ChapterContent(
            chapter_number=outline.chapter_number,
            title=outline.title,
            content=content,
            word_count=len(content),
            summary=summary,
            plot_point=", ".join(outline.plot_points),
            key_events=" → ".join(outline.key_events),
            character_focus=", ".join(outline.character_arcs.keys()),
            setting=outline.setting,
            mood=outline.mood,
            themes=", ".join(outline.themes)
        )
        
        # Step 3: 保存到数据库
        print(f"\n💾 Step 3/3: 保存到数据库...")
        print("-" * 60)
        
        self._save_to_database(chapter_content)
        
        print(f"✅ 已保存到数据库")
        
        # 保存章节文本到文件
        self._save_to_file(chapter_content)
        
        print(f"\n{'='*80}")
        print(f"🎉 第{next_chapter_number}章续写完成！")
        print(f"{'='*80}\n")
        
        return chapter_content
    
    def _generate_summary(self, content: str, outline: PlotOutline) -> str:
        """生成章节摘要"""
        
        # 取前200字
        summary_start = content[:200] if len(content) > 200 else content
        
        # 添加情节要点
        summary = f"{summary_start}... 本章主要情节：{outline.plot_points[0]}"
        
        return summary
    
    def _save_to_database(self, chapter: ChapterContent):
        """保存到数据库"""
        
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
            notes=f"AI续写于{datetime.now().isoformat()}\n\n完整内容见文件: chapter_{chapter.chapter_number}_content.txt"
        )
        
        print(f"  ✅ 章节信息已保存 (ID: {chapter_id})")
        
        return chapter_id
    
    def _save_to_file(self, chapter: ChapterContent):
        """保存章节文本到文件"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存到output目录（详细版本）
        filename_output = f"chapter_{chapter.chapter_number}_content_{timestamp}.txt"
        filepath_output = os.path.join(os.path.dirname(__file__), "output", filename_output)
        
        # 创建output目录
        os.makedirs(os.path.join(os.path.dirname(__file__), "output"), exist_ok=True)
        
        with open(filepath_output, 'w', encoding='utf-8') as f:
            f.write(f"《龙族Ⅰ火之晨曦》第{chapter.chapter_number}章\n")
            f.write("=" * 60 + "\n")
            f.write(f"标题: {chapter.title}\n")
            f.write(f"字数: {chapter.word_count}字\n")
            f.write(f"生成时间: {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(chapter.content)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write(f"摘要: {chapter.summary}\n")
        
        print(f"  ✅ 章节文本已保存: {filename_output}")
        
        # 2. 保存到chapters_2000_words目录（标准格式）
        # 注意：chapters_2000_words是按2000字切分的片段，不是按章节号
        # 需要找到最后一个文件编号，然后+1
        chapters_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chapters_2000_words")
        
        # 获取现有文件的最大编号
        existing_files = [f for f in os.listdir(chapters_dir) if f.endswith('_未知章节.txt')]
        if existing_files:
            # 提取编号
            numbers = []
            for f in existing_files:
                try:
                    num = int(f.split('_')[0])
                    numbers.append(num)
                except:
                    pass
            next_number = max(numbers) + 1 if numbers else 132
        else:
            next_number = 132  # 默认从132开始（131是最后一个原文片段）
        
        filename_standard = f"{next_number:03d}_未知章节.txt"
        filepath_standard = os.path.join(chapters_dir, filename_standard)
        
        # 确保chapters_2000_words目录存在
        os.makedirs(os.path.dirname(filepath_standard), exist_ok=True)
        
        with open(filepath_standard, 'w', encoding='utf-8') as f:
            f.write("《龙族Ⅰ火之晨曦》\n")
            f.write("作者：江南\n")
            f.write("\n")
            f.write("═" * 50 + "\n")
            f.write("\n")
            f.write(chapter.content)
            f.write("\n\n")
            
            # 添加分隔线
            for _ in range(50):
                f.write("═\n\n")
            
            f.write(f"字数统计：{chapter.word_count} 字\n")
            f.write(f"文件编号：{chapter.chapter_number}\n")
        
        print(f"  ✅ 标准格式已保存: chapters_2000_words/{filename_standard}")

# ==================== 测试函数 ====================

async def test_continuation():
    """测试续写系统"""
    
    print("\n🧪 测试龙族续写系统")
    print("=" * 80)
    
    manager = ContinuationManager()
    
    # 续写第26章
    chapter = await manager.continue_next_chapter(26)
    
    print("\n📄 生成结果预览:")
    print("-" * 60)
    print(f"标题: {chapter.title}")
    print(f"字数: {chapter.word_count}字")
    print(f"\n正文预览:")
    print(chapter.content[:300])
    print("...")

if __name__ == "__main__":
    asyncio.run(test_continuation())
