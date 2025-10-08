"""
合并节点生成Agent - 使用AI来生成智能的父节点title和summary
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from typing import List, Dict, Any
import json
from ai_merge_interface import AIMergeInterface

class MergeAgent:
    """合并节点生成Agent"""
    
    def __init__(self, api_key: str = None):
        """
        初始化合并Agent
        
        Args:
            api_key: OpenAI API密钥，如果不提供则使用模拟模式
        """
        self.ai_interface = AIMergeInterface(api_key=api_key)
        self.merge_prompt_template = """
你是一个专业的小说情节分析师。请根据以下章节信息，生成一个合并节点的标题和摘要。

章节信息：
{chapters_info}

请按照以下格式输出：
```json
{{
    "title": "合并后的章节标题",
    "summary": "合并后的情节摘要，应该体现整个阶段的核心情节发展",
    "plot_point": "这个阶段的核心情节要点",
    "key_events": "关键事件序列，用箭头连接",
    "character_focus": "主要角色及其发展",
    "setting": "场景变化，用箭头连接",
    "mood": "情感基调变化，用顿号分隔",
    "themes": "核心主题，用顿号分隔"
}}
```

要求：
1. 标题要概括整个阶段的核心主题
2. 摘要要体现情节的连贯性和发展脉络
3. 关键事件要按时间顺序排列
4. 角色发展要突出重要变化
5. 场景变化要体现故事空间的发展
6. 情感基调要反映故事的起伏
7. 主题要体现深层含义
"""
    
    def generate_merge_node(self, chapters: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        为章节列表生成合并节点（使用AI）
        
        Args:
            chapters: 章节信息列表
            
        Returns:
            合并后的节点信息
        """
        
        # 直接使用AI接口生成合并节点
        return self.ai_interface.generate_merge_node(chapters)
    
    def _format_chapters_for_agent(self, chapters: List[Dict[str, Any]]) -> str:
        """格式化章节信息供Agent处理"""
        
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
    
    def _simulate_ai_merge(self, chapters: List[Dict[str, Any]], prompt: str) -> Dict[str, str]:
        """模拟AI合并结果（实际使用时替换为真实AI调用）"""
        
        # 分析章节信息
        chapter_titles = [ch.get('title', '') for ch in chapters]
        chapter_summaries = [ch.get('summary', '') for ch in chapters]
        
        # 生成智能合并的标题
        merged_title = self._generate_smart_title(chapter_titles, chapters)
        
        # 生成智能合并的摘要
        merged_summary = self._generate_smart_summary(chapter_summaries, chapters)
        
        # 合并其他信息
        plot_point = self._merge_plot_points(chapters)
        key_events = self._merge_key_events(chapters)
        character_focus = self._merge_character_focus(chapters)
        setting = self._merge_setting(chapters)
        mood = self._merge_mood(chapters)
        themes = self._merge_themes(chapters)
        
        return {
            "title": merged_title,
            "summary": merged_summary,
            "plot_point": plot_point,
            "key_events": key_events,
            "character_focus": character_focus,
            "setting": setting,
            "mood": mood,
            "themes": themes
        }
    
    def _generate_smart_title(self, titles: List[str], chapters: List[Dict]) -> str:
        """生成智能合并标题"""
        
        if not titles:
            return "未知章节"
        
        # 分析标题模式
        if len(titles) == 1:
            return titles[0]
        
        # 提取关键词
        keywords = self._extract_title_keywords(titles)
        
        # 根据章节内容生成主题性标题
        chapter_count = len(chapters)
        
        # 分析章节类型
        if any("龙王" in str(ch.get('summary', '')) for ch in chapters):
            return f"龙王篇章（第{chapter_count}章合并）"
        elif any("学院" in str(ch.get('summary', '')) for ch in chapters):
            return f"学院篇章（第{chapter_count}章合并）"
        elif any("血统" in str(ch.get('summary', '')) for ch in chapters):
            return f"血统觉醒（第{chapter_count}章合并）"
        elif any("任务" in str(ch.get('summary', '')) for ch in chapters):
            return f"任务篇章（第{chapter_count}章合并）"
        else:
            # 使用第一个和最后一个标题的关键词
            first_keywords = self._extract_keywords_from_title(titles[0])
            last_keywords = self._extract_keywords_from_title(titles[-1])
            
            if first_keywords and last_keywords:
                return f"{first_keywords[0]} → {last_keywords[0]}"
            else:
                return f"第{chapter_count}章合并"
    
    def _generate_smart_summary(self, summaries: List[str], chapters: List[Dict]) -> str:
        """生成智能合并摘要"""
        
        if not summaries:
            return "无摘要信息"
        
        if len(summaries) == 1:
            return summaries[0]
        
        # 分析摘要内容，提取关键情节线
        key_themes = self._extract_key_themes(summaries)
        character_arcs = self._extract_character_arcs(summaries)
        plot_progression = self._analyze_plot_progression(summaries)
        
        # 生成连贯的合并摘要
        merged_summary = f"【{len(summaries)}个章节的合并摘要】"
        
        if plot_progression:
            merged_summary += f" 故事从{plot_progression['start']}发展到{plot_progression['end']}，"
        
        if character_arcs:
            merged_summary += f" 主要角色{', '.join(character_arcs)}经历了重要变化，"
        
        if key_themes:
            merged_summary += f" 核心围绕{', '.join(key_themes)}展开。"
        
        # 添加开头和结尾的关键信息
        if len(summaries) >= 2:
            start_summary = summaries[0][:100] + "..." if len(summaries[0]) > 100 else summaries[0]
            end_summary = summaries[-1][:100] + "..." if len(summaries[-1]) > 100 else summaries[-1]
            
            merged_summary += f" 章节开始：{start_summary} 章节结束：{end_summary}"
        
        return merged_summary
    
    def _extract_title_keywords(self, titles: List[str]) -> List[str]:
        """从标题中提取关键词"""
        keywords = []
        for title in titles:
            words = self._extract_keywords_from_title(title)
            keywords.extend(words)
        return list(set(keywords))  # 去重
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """从单个标题中提取关键词"""
        # 简单的关键词提取逻辑
        important_words = ["龙王", "学院", "血统", "任务", "战斗", "学院", "诺诺", "路明非", "恺撒", "楚子航"]
        found_keywords = []
        
        for word in important_words:
            if word in title:
                found_keywords.append(word)
        
        return found_keywords
    
    def _extract_key_themes(self, summaries: List[str]) -> List[str]:
        """从摘要中提取关键主题"""
        themes = []
        
        # 主题关键词
        theme_keywords = {
            "成长": ["成长", "发展", "变化", "成熟"],
            "友谊": ["友谊", "朋友", "关系", "合作"],
            "战斗": ["战斗", "对决", "攻击", "击败"],
            "探索": ["探索", "发现", "寻找", "调查"],
            "危机": ["危机", "危险", "威胁", "困境"],
            "爱情": ["爱情", "感情", "喜欢", "心动"]
        }
        
        all_text = " ".join(summaries)
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _extract_character_arcs(self, summaries: List[str]) -> List[str]:
        """从摘要中提取角色发展弧线"""
        characters = []
        
        # 主要角色关键词
        character_keywords = ["路明非", "诺诺", "恺撒", "楚子航", "昂热", "龙王", "叶胜", "亚纪"]
        
        all_text = " ".join(summaries)
        
        for char in character_keywords:
            if char in all_text:
                characters.append(char)
        
        return characters
    
    def _analyze_plot_progression(self, summaries: List[str]) -> Dict[str, str]:
        """分析情节发展进程"""
        if not summaries:
            return {}
        
        # 分析开头和结尾的情节状态
        start_summary = summaries[0]
        end_summary = summaries[-1]
        
        # 简单的情节状态分析
        start_state = "平静开始" if "平静" in start_summary or "日常" in start_summary else "紧张开始"
        end_state = "危机结束" if "危机" in end_summary or "战斗" in end_summary else "平静结束"
        
        return {
            "start": start_state,
            "end": end_state
        }
    
    def _merge_plot_points(self, chapters: List[Dict]) -> str:
        """合并情节要点"""
        points = [ch.get('plot_point', '') for ch in chapters if ch.get('plot_point')]
        return " → ".join(points) if points else ""
    
    def _merge_key_events(self, chapters: List[Dict]) -> str:
        """合并关键事件"""
        events = [ch.get('key_events', '') for ch in chapters if ch.get('key_events')]
        return " → ".join(events) if events else ""
    
    def _merge_character_focus(self, chapters: List[Dict]) -> str:
        """合并角色焦点"""
        characters = []
        for ch in chapters:
            if ch.get('character_focus'):
                characters.extend(ch['character_focus'].split('，'))
        
        # 去重并保持顺序
        unique_characters = []
        seen = set()
        for char in characters:
            char = char.strip()
            if char and char not in seen:
                unique_characters.append(char)
                seen.add(char)
        
        return "，".join(unique_characters) if unique_characters else ""
    
    def _merge_setting(self, chapters: List[Dict]) -> str:
        """合并场景设定"""
        settings = [ch.get('setting', '') for ch in chapters if ch.get('setting')]
        return " → ".join(settings) if settings else ""
    
    def _merge_mood(self, chapters: List[Dict]) -> str:
        """合并氛围描述"""
        moods = []
        for ch in chapters:
            if ch.get('mood'):
                moods.extend(ch['mood'].split('、'))
        
        # 去重
        unique_moods = list(dict.fromkeys([mood.strip() for mood in moods if mood.strip()]))
        return "、".join(unique_moods) if unique_moods else ""
    
    def _merge_themes(self, chapters: List[Dict]) -> str:
        """合并主题分析"""
        themes = []
        for ch in chapters:
            if ch.get('themes'):
                themes.extend(ch['themes'].split('、'))
        
        # 去重
        unique_themes = list(dict.fromkeys([theme.strip() for theme in themes if theme.strip()]))
        return "、".join(unique_themes) if unique_themes else ""
    
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

def test_merge_agent():
    """测试合并Agent"""
    
    merge_agent = MergeAgent()
    
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
    
    print("=== 测试合并Agent ===")
    print(f"输入章节数: {len(test_chapters)}")
    
    # 生成合并节点
    merged_node = merge_agent.generate_merge_node(test_chapters)
    
    print("\n=== 生成的合并节点 ===")
    for key, value in merged_node.items():
        print(f"{key}: {value}")
    
    # 测试单章节合并
    print("\n=== 测试单章节合并 ===")
    single_merged = merge_agent.generate_merge_node([test_chapters[0]])
    print(f"单章节标题: {single_merged['title']}")
    
    # 测试空章节合并
    print("\n=== 测试空章节合并 ===")
    empty_merged = merge_agent.generate_merge_node([])
    print(f"空章节标题: {empty_merged['title']}")

if __name__ == "__main__":
    test_merge_agent()
