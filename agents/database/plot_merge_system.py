"""
情节大纲合并系统 - 类似B-tree的merge操作
对远距离章节进行合并，只保留最近章节的详细内容
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from plot_api import PlotAPI
from plot_database import PlotDatabase
from merge_agent import MergeAgent
import sqlite3
from typing import List, Dict, Any, Optional

class PlotMergeSystem:
    """情节大纲合并系统"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "plot_outline.db")
        self.db_path = db_path
        self.api = PlotAPI(db_path)
        self.merge_agent = MergeAgent()
    
    def merge_chapters(self, current_chapter: int, merge_factor: int = 3) -> Dict[str, Any]:
        """
        合并章节，创建分层的情节摘要
        
        Args:
            current_chapter: 当前章节号
            merge_factor: 合并因子，每merge_factor个章节合并一次
            
        Returns:
            合并后的情节结构
        """
        
        # 获取所有章节
        all_chapters = self.api.get_all_chapters()
        all_chapters.sort(key=lambda x: x['chapter_number'])
        
        # 按章节号分组
        chapters_by_number = {}
        for chapter in all_chapters:
            num = chapter['chapter_number']
            if num not in chapters_by_number:
                chapters_by_number[num] = []
            chapters_by_number[num].append(chapter)
        
        # 获取唯一的章节号列表
        chapter_numbers = sorted(chapters_by_number.keys())
        
        # 创建合并结构
        merged_structure = {
            "current_chapter": current_chapter,
            "layers": [],
            "total_chapters": len(chapter_numbers),
            "merge_factor": merge_factor
        }
        
        # 计算需要多少层
        max_layers = self._calculate_layers(len(chapter_numbers), merge_factor)
        
        # 为每一层创建合并数据
        for layer in range(max_layers + 1):
            layer_data = self._create_layer_data(
                chapter_numbers, current_chapter, layer, merge_factor
            )
            if layer_data:
                merged_structure["layers"].append(layer_data)
        
        return merged_structure
    
    def _calculate_layers(self, total_chapters: int, merge_factor: int) -> int:
        """计算需要的层数"""
        layers = 0
        remaining = total_chapters
        
        while remaining > merge_factor:
            remaining = (remaining + merge_factor - 1) // merge_factor
            layers += 1
        
        return layers
    
    def _create_layer_data(self, chapter_numbers: List[int], current_chapter: int, 
                          layer: int, merge_factor: int) -> Optional[Dict[str, Any]]:
        """为指定层创建数据"""
        
        if layer == 0:
            # 第0层：最近章节的详细内容
            return self._create_detail_layer(chapter_numbers, current_chapter)
        else:
            # 其他层：合并摘要
            return self._create_summary_layer(chapter_numbers, current_chapter, 
                                            layer, merge_factor)
    
    def _create_detail_layer(self, chapter_numbers: List[int], current_chapter: int) -> Dict[str, Any]:
        """创建详细层（最近章节）"""
        
        # 获取最近3个章节的详细内容
        recent_chapters = []
        start_idx = max(0, len(chapter_numbers) - 3)
        
        for i in range(start_idx, len(chapter_numbers)):
            chapter_num = chapter_numbers[i]
            chapters = self.api.get_chapters_by_number(chapter_num)
            if chapters:
                # 取第一个章节（假设同一章节号的内容相似）
                chapter = chapters[0]
                recent_chapters.append({
                    "chapter_number": chapter_num,
                    "title": chapter['title'],
                    "summary": chapter['summary'],
                    "plot_point": chapter['plot_point'],
                    "key_events": chapter['key_events'],
                    "character_focus": chapter['character_focus'],
                    "setting": chapter['setting'],
                    "mood": chapter['mood'],
                    "themes": chapter['themes'],
                    "detail_level": "full"
                })
        
        return {
            "layer": 0,
            "type": "detail",
            "description": "最近章节的详细内容",
            "chapters": recent_chapters
        }
    
    def _create_summary_layer(self, chapter_numbers: List[int], current_chapter: int, 
                            layer: int, merge_factor: int) -> Optional[Dict[str, Any]]:
        """创建摘要层"""
        
        # 计算当前层的章节范围
        layer_chapters = self._get_layer_chapters(chapter_numbers, layer, merge_factor)
        
        if not layer_chapters:
            return None
        
        # 为每个范围创建合并摘要
        merged_ranges = []
        for start_idx, end_idx in layer_chapters:
            range_chapters = chapter_numbers[start_idx:end_idx]
            if range_chapters:
                merged_summary = self._create_range_summary(range_chapters)
                if merged_summary:
                    merged_ranges.append(merged_summary)
        
        if not merged_ranges:
            return None
        
        return {
            "layer": layer,
            "type": "summary",
            "description": f"第{layer}层合并摘要（每{merge_factor**layer}个章节合并）",
            "ranges": merged_ranges
        }
    
    def _get_layer_chapters(self, chapter_numbers: List[int], layer: int, merge_factor: int) -> List[tuple]:
        """获取指定层的章节范围"""
        
        # 计算当前层的合并大小
        merge_size = merge_factor ** layer
        
        # 排除最近3个章节（它们在第0层）
        exclude_count = min(3, len(chapter_numbers))
        available_chapters = chapter_numbers[:-exclude_count] if exclude_count > 0 else chapter_numbers
        
        if not available_chapters:
            return []
        
        # 按merge_size分组
        ranges = []
        for i in range(0, len(available_chapters), merge_size):
            end_idx = min(i + merge_size, len(available_chapters))
            if i < len(available_chapters):
                ranges.append((i, end_idx))
        
        return ranges
    
    def _create_range_summary(self, chapter_numbers: List[int]) -> Optional[Dict[str, Any]]:
        """为章节范围创建合并摘要（使用AI Agent）"""
        
        if not chapter_numbers:
            return None
        
        # 获取范围内的所有章节
        chapters_data = []
        for chapter_num in chapter_numbers:
            chapters = self.api.get_chapters_by_number(chapter_num)
            if chapters:
                chapters_data.append(chapters[0])
        
        if not chapters_data:
            return None
        
        # 使用AI Agent生成智能合并摘要
        start_chapter = min(chapter_numbers)
        end_chapter = max(chapter_numbers)
        
        # 调用AI Agent生成合并节点
        merged_node = self.merge_agent.generate_merge_node(chapters_data)
        
        # 构建合并摘要
        merged_summary = {
            "range": f"第{start_chapter}-{end_chapter}章",
            "title": merged_node["title"],
            "summary": merged_node["summary"],
            "plot_point": merged_node["plot_point"],
            "key_events": merged_node["key_events"],
            "character_focus": merged_node["character_focus"],
            "setting": merged_node["setting"],
            "mood": merged_node["mood"],
            "themes": merged_node["themes"],
            "chapter_count": len(chapters_data)
        }
        
        return merged_summary
    
    def _merge_titles(self, chapters: List[Dict]) -> str:
        """合并标题"""
        titles = [ch['title'] for ch in chapters if ch.get('title')]
        if len(titles) == 1:
            return titles[0]
        elif len(titles) <= 3:
            return " → ".join(titles)
        else:
            return f"{titles[0]} → ... → {titles[-1]}"
    
    def _merge_summaries(self, chapters: List[Dict]) -> str:
        """合并摘要"""
        summaries = [ch['summary'] for ch in chapters if ch.get('summary')]
        if not summaries:
            return ""
        
        # 如果只有一个摘要，直接返回
        if len(summaries) == 1:
            return summaries[0]
        
        # 合并多个摘要
        merged = f"【{len(summaries)}个章节的合并摘要】"
        
        # 取前两个和后一个摘要的关键部分
        if len(summaries) >= 2:
            first_summary = summaries[0][:100] + "..." if len(summaries[0]) > 100 else summaries[0]
            merged += f" {first_summary}"
        
        if len(summaries) > 2:
            merged += f" ... [中间省略{len(summaries)-2}个章节] ..."
        
        if len(summaries) > 1:
            last_summary = summaries[-1][:100] + "..." if len(summaries[-1]) > 100 else summaries[-1]
            merged += f" {last_summary}"
        
        return merged
    
    def _merge_plot_points(self, chapters: List[Dict]) -> str:
        """合并情节要点"""
        points = [ch['plot_point'] for ch in chapters if ch.get('plot_point')]
        return " → ".join(points) if points else ""
    
    def _merge_key_events(self, chapters: List[Dict]) -> str:
        """合并关键事件"""
        events = [ch['key_events'] for ch in chapters if ch.get('key_events')]
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
    
    def _merge_settings(self, chapters: List[Dict]) -> str:
        """合并场景设定"""
        settings = [ch['setting'] for ch in chapters if ch.get('setting')]
        return " → ".join(settings) if settings else ""
    
    def _merge_moods(self, chapters: List[Dict]) -> str:
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
    
    def format_merged_plot_summary(self, current_chapter: int, merge_factor: int = 3) -> str:
        """格式化合并后的情节摘要，并自动保存到数据库"""
        
        # 首先检查是否已有保存的摘要
        saved_summary = self.api.get_merge_summary(current_chapter, merge_factor)
        if saved_summary:
            print(f"✅ 使用已保存的合并摘要 (第{current_chapter}章, 合并因子{merge_factor})")
            return saved_summary['summary_content']
        
        print(f"🔄 生成新的合并摘要 (第{current_chapter}章, 合并因子{merge_factor})")
        
        merged_structure = self.merge_chapters(current_chapter, merge_factor)
        
        result = []
        result.append("📚 分层情节大纲摘要")
        result.append("=" * 60)
        result.append(f"📊 当前章节: 第{current_chapter}章")
        result.append(f"📊 总章节数: {merged_structure['total_chapters']}")
        result.append(f"📊 合并因子: {merge_factor}")
        result.append("")
        
        # 收集AI生成的标题用于保存
        ai_titles = []
        
        # 按层显示
        for layer_data in reversed(merged_structure["layers"]):  # 从高层到低层
            layer = layer_data["layer"]
            layer_type = layer_data["type"]
            
            if layer == 0:
                result.append("🔍 第0层 - 最近章节详细内容")
                result.append("-" * 40)
                for chapter in layer_data["chapters"]:
                    result.append(f"📖 第{chapter['chapter_number']}章: {chapter['title']}")
                    result.append(f"   📝 摘要: {chapter['summary']}")
                    result.append(f"   🎯 情节要点: {chapter['plot_point']}")
                    result.append(f"   ⚡ 关键事件: {chapter['key_events']}")
                    result.append(f"   👥 角色焦点: {chapter['character_focus']}")
                    result.append(f"   🏛️ 场景设定: {chapter['setting']}")
                    result.append(f"   🌟 氛围: {chapter['mood']}")
                    result.append(f"   💭 主题: {chapter['themes']}")
                    result.append("")
            else:
                result.append(f"📋 第{layer}层 - {layer_data['description']}")
                result.append("-" * 40)
                for range_data in layer_data["ranges"]:
                    result.append(f"📚 {range_data['range']}: {range_data['title']}")
                    result.append(f"   📝 合并摘要: {range_data['summary']}")
                    result.append(f"   🎯 情节发展: {range_data['plot_point']}")
                    result.append(f"   ⚡ 关键事件: {range_data['key_events']}")
                    result.append(f"   👥 主要角色: {range_data['character_focus']}")
                    result.append(f"   🏛️ 场景变化: {range_data['setting']}")
                    result.append(f"   🌟 情感基调: {range_data['mood']}")
                    result.append(f"   💭 核心主题: {range_data['themes']}")
                    result.append(f"   📊 包含章节数: {range_data['chapter_count']}")
                    result.append("")
                    
                    # 收集AI生成的标题
                    if 'title' in range_data and range_data['title']:
                        ai_titles.append(range_data['title'])
        
        summary_content = "\n".join(result)
        
        # 计算合并层级数
        merge_levels = len([layer for layer in merged_structure["layers"] if layer["layer"] > 0])
        
        # 保存到数据库
        try:
            import json
            ai_titles_json = json.dumps(ai_titles, ensure_ascii=False)
            self.api.save_merge_summary(
                current_chapter=current_chapter,
                merge_factor=merge_factor,
                summary_content=summary_content,
                merge_levels=merge_levels,
                ai_generated_titles=ai_titles_json
            )
            print(f"💾 合并摘要已保存到数据库")
        except Exception as e:
            print(f"⚠️ 保存合并摘要时出错: {str(e)}")
        
        return summary_content
    
    def get_chapters_by_number(self, chapter_number: int) -> List[Dict]:
        """获取指定章节号的所有章节"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chapters WHERE chapter_number = ?
        """, (chapter_number,))
        
        columns = [description[0] for description in cursor.description]
        chapters = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return chapters

def test_merge_system():
    """测试合并系统"""
    
    merge_system = PlotMergeSystem()
    
    print("=== 测试情节大纲合并系统 ===")
    
    # 测试当前章节为第20章的情况
    current_chapter = 20
    merge_factor = 3
    
    print(f"\n当前章节: 第{current_chapter}章，合并因子: {merge_factor}")
    
    # 生成合并摘要
    merged_summary = merge_system.format_merged_plot_summary(current_chapter, merge_factor)
    
    print("\n" + "="*80)
    print(merged_summary)
    print("="*80)
    
    # 测试不同章节的情况
    test_chapters = [10, 15, 20, 25]
    
    for test_chapter in test_chapters:
        print(f"\n--- 测试第{test_chapter}章的合并结果 ---")
        summary = merge_system.format_merged_plot_summary(test_chapter, merge_factor)
        print(summary[:500] + "...\n")

if __name__ == "__main__":
    test_merge_system()
