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

1. **心理描写细腻**
   - 大量内心独白："他想..."、"路明非觉得..."
   - 自问自答："真烦！谁家的小孩跑丢了？"
   - 情感波动："一颗心却悄无声息地沉了下去"

2. **对话生动自然**
   - 口语化："你能更没有道德一点么？"、"姐姐……那我该怎么办？"
   - 网络用语："GG"、"秀逗"、"欠扁"
   - 幽默讽刺："作弊死全家！"

3. **环境描写诗意**
   - 时间感："又是春天了，路明非这一年十八岁。"
   - 光影："夕阳的斜光照在新换的课桌上"
   - 声音："窗外的花草疯长，蝉鸣声仿佛加速了一百倍"

4. **节奏控制**
   - 日常与戏剧性交织
   - 长短句结合："真烦！谁家的小孩跑丢了？"
   - 细节铺陈后突然转折

5. **人物塑造**
   - 通过小动作："路明非两手抄在裤兜里，歪着脑袋"
   - 通过比喻："像只被抛弃的小猎犬"、"钢刀一样的女孩"
   - 对比手法：路明非与路鸣泽的对比

6. **情感基调**
   - 略带悲凉的青春：孤独、不被认可
   - 平凡中的不甘："作为一个没什么存在感的人"
   - 温暖时刻的珍惜："路明非忽然有点感动"
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
    estimated_word_count: int = 2000

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

你的任务：
1. 分析前情发展和角色状态
2. 规划下一章的详细情节大纲
3. 确保情节连贯、角色发展合理
4. 保持江南风格的叙事节奏和主题深度

规划原则：
- 情节必须具体，包含人名、地点、事件
- 避免抽象概括，要能让人立即想起具体内容
- 角色行为符合性格设定
- 保持龙族世界观的严肃性与日常的幽默感交织

输出JSON格式，包含所有必要字段。
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

要求：
1. **严格遵循长期规划**：确保本章内容符合当前故事弧线的主题、节奏和在弧线中的位置
2. **参考本章具体建议**：重点内容和注意事项必须体现在大纲中
3. 标题要具体明确，包含关键人物、地点或事件
4. 情节点要详细，描述具体发生什么
5. 确保与前文连贯，符合角色性格
6. 保持江南风格的节奏和氛围

请输出JSON格式，包含以下字段：
{{
    "chapter_number": {next_chapter_number},
    "title": "具体的章节标题",
    "plot_points": ["情节点1", "情节点2", "情节点3"],
    "character_arcs": {{"角色名": "发展变化描述"}},
    "setting": "具体场景",
    "mood": "情感基调",
    "themes": ["主题1", "主题2"],
    "key_events": ["事件1", "事件2", "事件3"],
    "estimated_word_count": 2000
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
你是《龙族》系列小说的写作师，精通江南的写作风格。

{JIANGNAN_STYLE_GUIDE}

写作要求：
1. **严格模仿江南风格**
2. **细腻心理描写**：大量"他想..."、"路明非觉得..."
3. **对话生动**：口语化、幽默、真实
4. **环境诗意**：光影、声音、时间流逝的感受
5. **节奏舒缓**：日常细节与戏剧冲突交替
6. **情感真挚**：孤独、渴望、温暖的瞬间

语言特点：
- 短句与长句结合
- 生动比喻："像只被抛弃的小猎犬"
- 内心独白丰富
- 细节描写充分
- 略带悲凉的青春感

写作时要：
- 展现角色性格（通过行为、对话、心理）
- 推进情节（但不要太快，要有日常）
- 渲染氛围（环境、光线、声音）
- 刻画情感（内心起伏、情绪变化）
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

写作要求：
1. 字数约{outline.estimated_word_count}字
2. 严格遵循江南的写作风格（见上文风格指南）
3. 包含丰富的心理描写、对话、环境描写
4. 情节推进自然，符合大纲要点
5. 刻画角色性格和内心世界
6. 保持与前文的连贯性

请直接输出章节正文，不要包含任何JSON或标记格式。
从章节标题开始，然后是正文内容。

格式示例：
第X章 标题

正文第一段...

正文第二段...
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
