"""
AI合并接口 - 真实调用AI模型生成合并节点
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from typing import List, Dict, Any, Optional
import json
import asyncio
from agents import Agent, Runner
from pydantic import BaseModel

class ChapterAnalysisResult(BaseModel):
    """章节分析结果模型"""
    title: str
    summary: str
    plot_point: str
    key_events: str
    character_focus: str
    setting: str
    mood: str
    themes: str

class AIMergeInterface:
    """AI合并接口"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        初始化AI接口
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的模型名称
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.agent = None
        
        # 如果提供了API密钥，创建Agent
        if self.api_key:
            try:
                # 设置环境变量
                os.environ["OPENAI_API_KEY"] = self.api_key
                
                # 创建章节分析Agent
                self.agent = Agent(
                    name="Chapter Merge Agent",
                    instructions="""你是一个专业的小说情节分析师，专门负责分析章节内容并生成合并节点的标题和摘要。

你的任务是：
1. 分析多个章节的内容和结构
2. 识别章节的主要主题和情节发展
3. 生成有意义的合并标题
4. 创建连贯的合并摘要
5. 提取关键信息（情节要点、关键事件、角色发展等）

请始终以JSON格式返回结果，包含以下字段：
- title: 合并后的章节标题
- summary: 合并后的情节摘要
- plot_point: 核心情节要点
- key_events: 关键事件序列
- character_focus: 主要角色及其发展
- setting: 场景变化
- mood: 情感基调变化
- themes: 核心主题

确保输出格式正确，字段完整。"""
                )
                print("OpenAI Agent创建成功")
            except Exception as e:
                print(f"警告: 创建OpenAI Agent失败: {e}，将使用模拟模式")
                self.agent = None
        else:
            print("警告: 未提供OpenAI API密钥，将使用模拟模式")
    
    def generate_merge_node(self, chapters: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        使用AI生成合并节点
        
        Args:
            chapters: 章节信息列表
            
        Returns:
            合并后的节点信息
        """
        
        if not chapters:
            return self._get_default_merge_node()
        
        if len(chapters) == 1:
            return self._single_chapter_merge(chapters[0])
        
        # 检查是否已在事件循环中
        try:
            loop = asyncio.get_running_loop()
            # 如果已在事件循环中，使用nest_asyncio
            try:
                import nest_asyncio
                nest_asyncio.apply()
            except ImportError:
                print("⚠️ nest_asyncio未安装，尝试直接创建任务")
            return asyncio.run(self._generate_merge_node_async(chapters))
        except RuntimeError:
            # 没有运行中的事件循环，正常运行
            return asyncio.run(self._generate_merge_node_async(chapters))
    
    async def _generate_merge_node_async(self, chapters: List[Dict[str, Any]]) -> Dict[str, str]:
        """异步生成合并节点"""
        
        # 构建提示词
        prompt = self._build_merge_prompt(chapters)
        
        # 调用AI生成合并节点
        if self.agent:
            try:
                result = await Runner.run(self.agent, prompt)
                return self._parse_agent_response(result)
            except Exception as e:
                print(f"Agent调用失败: {e}")
                return self._simulate_ai_response(chapters)
        else:
            return self._simulate_ai_response(chapters)
    
    def _build_merge_prompt(self, chapters: List[Dict[str, Any]]) -> str:
        """构建AI提示词"""
        
        chapters_info = self._format_chapters_for_ai(chapters)
        
        prompt = f"""
        你是一个专业的小说情节分析师。请根据以下章节信息，生成一个合并节点的标题和详细摘要。

        章节信息：
        {chapters_info}

        请按照以下JSON格式输出：
        ```json
        {{
            "title": "合并后的章节标题，要包含具体情节元素",
            "summary": "合并后的情节摘要，必须包含具体的人名、地名、事件名称",
            "plot_point": "核心情节要点，列出具体发生了什么",
            "key_events": "关键事件序列，用→连接，要具体明确",
            "character_focus": "主要角色及其具体行为，用逗号分隔",
            "setting": "具体场景，用→连接",
            "mood": "情感基调，用、分隔",
            "themes": "核心主题，用、分隔"
        }}
        ```

        重要要求：
        1. **标题必须包含具体元素**：例如"路明非收到卡塞尔学院邀请并前往"而不是"命运的召唤"
        2. **摘要必须详细具体**：
        - 必须包含人名：路明非、楚子航、恺撒、诺诺等
        - 必须包含地点：卡塞尔学院、三峡、青铜之城等
        - 必须包含具体事件：血统测试、龙王诺顿苏醒、水下战斗等
        - 必须包含结果：击败龙王、获救、觉醒等
        3. **关键事件要清晰**：例如"路明非收到邀请 → 前往芝加哥 → 通过自由一日测试 → 成为S级"
        4. **避免抽象词汇**：少用"命运"、"觉醒"、"抉择"等模糊词，多用具体名词和动词
        5. **让人一看就能回忆起具体情节**：Agent看到这个摘要后，应该能立即想起"哦对，是那段路明非在卡塞尔学院的情节"

        错误示例：
        - 标题："命运觉醒：从凡人到龙族世界的门槛" ❌ (太抽象)
        - 摘要："主角经历了一系列试炼和挑战" ❌ (没有具体内容)

        正确示例：
        - 标题："路明非收到卡塞尔学院邀请，通过自由一日测试成为S级" ✅
        - 摘要："路明非收到神秘的卡塞尔学院邀请信。前往芝加哥后，在自由一日活动中意外击败学生会长恺撒和狮心会长楚子航，被评为S级。校长昂热解释这是因为他的血统特殊。路明非开始接受血统测试，发现自己的龙族血统异常强大。" ✅

        请确保输出是有效的JSON格式，且内容具体、可以唤起对情节的回忆。
        """
        
        return prompt
    
    def _format_chapters_for_ai(self, chapters: List[Dict[str, Any]]) -> str:
        """格式化章节信息供AI处理"""
        
        formatted_info = []
        
        for i, chapter in enumerate(chapters, 1):
            chapter_info = f"""
            章节 {i}:
            - 标题: {chapter.get('title', '未知标题')}
            - 摘要: {chapter.get('summary', '无摘要')}
            - 情节要点: {chapter.get('plot_point', '无要点')}
            - 关键事件: {chapter.get('key_events', '无事件')}
            - 角色焦点: {chapter.get('character_focus', '无角色')}
            - 场景设定: {chapter.get('setting', '无场景')}
            - 氛围: {chapter.get('mood', '无氛围')}
            - 主题: {chapter.get('themes', '无主题')}
            """
            formatted_info.append(chapter_info)
        
        return "\n".join(formatted_info)
    
    def _parse_agent_response(self, result) -> Dict[str, str]:
        """解析Agent响应"""
        try:
            # 从RunResult中提取最终输出
            if hasattr(result, 'final_output'):
                content = result.final_output
            elif hasattr(result, 'output'):
                content = result.output
            else:
                content = str(result)
            
            # 尝试解析JSON
            try:
                merged_info = json.loads(content)
                return self._validate_merge_info(merged_info)
            except json.JSONDecodeError:
                # 如果不是JSON，尝试从文本中提取信息
                return self._extract_info_from_text(content)
                
        except Exception as e:
            print(f"解析Agent响应失败: {e}")
            return self._get_default_merge_node()
    
    def _extract_info_from_text(self, text: str) -> Dict[str, str]:
        """从文本中提取信息"""
        # 简单的文本解析逻辑
        lines = text.split('\n')
        
        result = {
            "title": "AI生成的合并章节",
            "summary": text[:200] + "..." if len(text) > 200 else text,
            "plot_point": "",
            "key_events": "",
            "character_focus": "",
            "setting": "",
            "mood": "",
            "themes": ""
        }
        
        # 尝试从文本中提取标题
        for line in lines:
            if "标题" in line or "title" in line.lower():
                result["title"] = line.split(":")[-1].strip() if ":" in line else line
                break
        
        return result
    
    
    def _validate_merge_info(self, merged_info: Dict[str, Any]) -> Dict[str, str]:
        """验证和清理合并信息"""
        
        # 验证必要字段
        required_fields = ["title", "summary", "plot_point", "key_events", 
                         "character_focus", "setting", "mood", "themes"]
        
        validated_info = {}
        for field in required_fields:
            value = merged_info.get(field, "")
            if isinstance(value, str):
                validated_info[field] = value
            else:
                validated_info[field] = str(value) if value else ""
        
        return validated_info
    
    def _simulate_ai_response(self, chapters: List[Dict[str, Any]]) -> Dict[str, str]:
        """模拟AI响应（用于测试）"""
        
        # 使用简单的启发式规则生成合并节点
        chapter_count = len(chapters)
        
        # 分析章节内容
        all_summaries = " ".join([ch.get('summary', '') for ch in chapters])
        all_titles = [ch.get('title', '') for ch in chapters]
        
        # 生成智能标题
        if "龙王" in all_summaries:
            title = f"龙王篇章（第{chapter_count}章合并）"
        elif "学院" in all_summaries:
            title = f"学院篇章（第{chapter_count}章合并）"
        elif "血统" in all_summaries:
            title = f"血统觉醒（第{chapter_count}章合并）"
        elif "任务" in all_summaries:
            title = f"任务篇章（第{chapter_count}章合并）"
        else:
            # 使用第一个和最后一个标题的关键词
            first_title = all_titles[0] if all_titles else "未知"
            last_title = all_titles[-1] if all_titles else "未知"
            title = f"{first_title} → {last_title}"
        
        # 生成智能摘要
        summary = f"【{chapter_count}个章节的合并摘要】"
        
        # 提取关键信息
        key_themes = self._extract_themes(all_summaries)
        key_characters = self._extract_characters(all_summaries)
        
        if key_themes:
            summary += f" 核心围绕{', '.join(key_themes)}展开，"
        
        if key_characters:
            summary += f" 主要角色{', '.join(key_characters)}经历了重要发展，"
        
        # 添加开头和结尾信息
        if len(chapters) >= 2:
            start_summary = chapters[0].get('summary', '')[:100]
            end_summary = chapters[-1].get('summary', '')[:100]
            summary += f" 从{start_summary}...发展到{end_summary}..."
        
        # 合并其他信息
        plot_point = " → ".join([ch.get('plot_point', '') for ch in chapters if ch.get('plot_point')])
        key_events = " → ".join([ch.get('key_events', '') for ch in chapters if ch.get('key_events')])
        
        # 合并角色焦点
        characters = []
        for ch in chapters:
            if ch.get('character_focus'):
                characters.extend(ch['character_focus'].split('，'))
        character_focus = "，".join(list(set([c.strip() for c in characters if c.strip()])))
        
        setting = " → ".join([ch.get('setting', '') for ch in chapters if ch.get('setting')])
        mood = "、".join(list(set([ch.get('mood', '') for ch in chapters if ch.get('mood')])))
        themes = "、".join(list(set([ch.get('themes', '') for ch in chapters if ch.get('themes')])))
        
        return {
            "title": title,
            "summary": summary,
            "plot_point": plot_point,
            "key_events": key_events,
            "character_focus": character_focus,
            "setting": setting,
            "mood": mood,
            "themes": themes
        }
    
    def _extract_themes(self, text: str) -> List[str]:
        """提取主题关键词"""
        themes = []
        theme_keywords = {
            "成长": ["成长", "发展", "变化", "成熟"],
            "友谊": ["友谊", "朋友", "关系", "合作"],
            "战斗": ["战斗", "对决", "攻击", "击败"],
            "探索": ["探索", "发现", "寻找", "调查"],
            "危机": ["危机", "危险", "威胁", "困境"],
            "爱情": ["爱情", "感情", "喜欢", "心动"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _extract_characters(self, text: str) -> List[str]:
        """提取角色关键词"""
        characters = []
        character_keywords = ["路明非", "诺诺", "恺撒", "楚子航", "昂热", "龙王", "叶胜", "亚纪"]
        
        for char in character_keywords:
            if char in text:
                characters.append(char)
        
        return characters
    
    def _fallback_merge(self, ai_content: str) -> Dict[str, str]:
        """AI响应解析失败时的备用方案"""
        
        # 尝试从AI返回的文本中提取信息
        lines = ai_content.split('\n')
        
        title = "AI生成的合并章节"
        summary = ai_content[:200] + "..." if len(ai_content) > 200 else ai_content
        
        # 尝试提取标题
        for line in lines:
            if "标题" in line or "title" in line.lower():
                title = line.split(":")[-1].strip() if ":" in line else line
                break
        
        return {
            "title": title,
            "summary": summary,
            "plot_point": "",
            "key_events": "",
            "character_focus": "",
            "setting": "",
            "mood": "",
            "themes": ""
        }
    
    def _single_chapter_merge(self, chapter: Dict[str, Any]) -> Dict[str, str]:
        """单章节合并（直接返回）"""
        return {
            "title": chapter.get('title', '未知标题'),
            "summary": chapter.get('summary', '无摘要'),
            "plot_point": chapter.get('plot_point', ''),
            "key_events": chapter.get('key_events', ''),
            "character_focus": chapter.get('character_focus', ''),
            "setting": chapter.get('setting', ''),
            "mood": chapter.get('mood', ''),
            "themes": chapter.get('themes', '')
        }
    
    def _get_default_merge_node(self) -> Dict[str, str]:
        """获取默认合并节点"""
        return {
            "title": "未知章节",
            "summary": "无章节信息",
            "plot_point": "",
            "key_events": "",
            "character_focus": "",
            "setting": "",
            "mood": "",
            "themes": ""
        }

def test_ai_merge_interface():
    """测试AI合并接口"""
    
    # 测试模拟模式
    print("=== 测试AI合并接口（模拟模式）===")
    ai_interface = AIMergeInterface()
    
    # 测试数据
    test_chapters = [
        {
            "title": "楔子：白帝城",
            "summary": "神秘的梦境开场：一个白衣男子在梦中与名为康斯坦丁的孩子对话，孩子询问哥哥是否会吃掉自己，男子回答会一起君临世界。",
            "plot_point": "梦境与现实的分界，龙族世界的序幕",
            "key_events": "康斯坦丁的梦境，白帝城毁灭，兄弟情深的对话",
            "character_focus": "路明非（梦境中的男子），康斯坦丁",
            "setting": "梦境中的白帝城，现实中的城市",
            "mood": "神秘、悲伤、震撼",
            "themes": "命运、牺牲、兄弟情"
        },
        {
            "title": "路明非的日常",
            "summary": "介绍路明非的平凡生活：18岁高中生，与叔叔婶婶同住，堂弟路鸣泽成绩优秀受宠爱。路明非沉迷《星际争霸》游戏，成绩平平，存在感很低。",
            "plot_point": "平凡少年的生活状态",
            "key_events": "游戏对战，婶婶的抱怨，天台独处，父母缺席",
            "character_focus": "路明非，路鸣泽，叔叔婶婶",
            "setting": "家中，学校，天台",
            "mood": "平淡、孤独、迷茫",
            "themes": "青春迷茫、家庭关系、自我认知"
        },
        {
            "title": "留学申请",
            "summary": "婶婶主张路明非申请美国大学，因为英语成绩不错。路明非收到十几封拒信，只剩下芝加哥大学未回复。婶婶心疼申请费，路明非心态平和。最后收到芝加哥大学的拒信，但卡塞尔学院发来邀请信，提供每年36000美元奖学金。",
            "plot_point": "命运的转折点",
            "key_events": "申请美国大学，收到拒信，卡塞尔学院邀请",
            "character_focus": "路明非，婶婶，路鸣泽",
            "setting": "家中，传达室",
            "mood": "意外、惊喜、怀疑",
            "themes": "命运转折、机会与选择"
        }
    ]
    
    # 生成合并节点
    merged_node = ai_interface.generate_merge_node(test_chapters)
    
    print(f"输入章节数: {len(test_chapters)}")
    print("\n=== 生成的合并节点 ===")
    for key, value in merged_node.items():
        print(f"{key}: {value}")
    
    # 测试真实AI模式（如果有API密钥）
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("\n=== 测试AI合并接口（OpenAI Agents模式）===")
        try:
            real_ai_interface = AIMergeInterface(api_key=api_key)
            print(f"创建的Agent: {real_ai_interface.agent.name if real_ai_interface.agent else 'None'}")
            
            real_merged_node = real_ai_interface.generate_merge_node(test_chapters)
            
            print("\n=== OpenAI Agents生成的合并节点 ===")
            for key, value in real_merged_node.items():
                print(f"{key}: {value}")
            
        except Exception as e:
            print(f"OpenAI Agents测试失败: {e}")
            print("将使用模拟模式")
    else:
        print("\n=== 跳过OpenAI Agents测试（未提供API密钥）===")
        print("设置OPENAI_API_KEY环境变量来测试真实Agent功能")

if __name__ == "__main__":
    test_ai_merge_interface()
