"""
情节大纲API接口
提供情节大纲管理的便捷接口
"""

import os
import sys
from typing import Dict, List, Optional, Any
sys.path.append(os.path.dirname(__file__))
from plot_database import PlotDatabase

class PlotAPI:
    """情节大纲API类"""
    
    def __init__(self, db_path: str = None):
        """
        初始化API
        
        Args:
            db_path: 数据库路径，默认使用database目录下的plot_outline.db
        """
        if db_path is None:
            # 查找数据库文件
            current_dir = os.path.dirname(__file__)
            possible_paths = [
                os.path.join(current_dir, "plot_outline.db"),
                os.path.join(current_dir, "..", "plot_outline.db"),
                "plot_outline.db"
            ]
            
            db_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            
            if db_path is None:
                db_path = os.path.join(current_dir, "plot_outline.db")
        
        self.db = PlotDatabase(db_path)
    
    def add_chapter(self, chapter_number: int, title: str, summary: str = "", 
                   word_count: int = 0, **kwargs) -> int:
        """添加新章节"""
        return self.db.add_chapter(chapter_number, title, summary, word_count, **kwargs)
    
    def get_chapter(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """获取章节信息"""
        return self.db.get_chapter(chapter_id)
    
    def get_chapter_by_number(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """根据章节编号获取章节信息（返回第一个匹配的章节）"""
        chapters = self.get_chapters_by_number(chapter_number)
        return chapters[0] if chapters else None
    
    def get_chapters_by_number(self, chapter_number: int) -> List[Dict[str, Any]]:
        """根据章节编号获取所有匹配的章节"""
        return self.db.get_chapters_by_number(chapter_number)
    
    def get_all_chapters(self) -> List[Dict[str, Any]]:
        """获取所有章节"""
        return self.db.get_all_chapters()
    
    def get_chapter_tree(self) -> Dict[str, Any]:
        """获取章节树状结构"""
        return self.db.get_chapter_tree()
    
    def update_chapter(self, chapter_id: int, **kwargs) -> bool:
        """更新章节信息"""
        return self.db.update_chapter(chapter_id, **kwargs)
    
    def add_plot_line(self, name: str, description: str = "", priority: int = 1) -> int:
        """添加情节线"""
        return self.db.add_plot_line(name, description, priority)
    
    def link_chapter_plot_line(self, chapter_id: int, plot_line_id: int,
                              importance: int = 1, progress: str = ""):
        """关联章节和情节线"""
        return self.db.link_chapter_plot_line(chapter_id, plot_line_id, importance, progress)
    
    def add_character_arc(self, character_name: str, chapter_id: int, **kwargs):
        """添加角色发展轨迹"""
        return self.db.add_character_arc(character_name, chapter_id, **kwargs)
    
    def get_plot_summary(self, up_to_chapter: int = None) -> Dict[str, Any]:
        """获取情节大纲摘要"""
        return self.db.get_plot_summary(up_to_chapter)
    
    def get_character_development_timeline(self, character_name: str) -> List[Dict[str, Any]]:
        """获取角色发展时间线"""
        return self.db.get_character_development_timeline(character_name)
    
    def save_merge_summary(self, current_chapter: int, merge_factor: int, 
                          summary_content: str, merge_levels: int = 0,
                          ai_generated_titles: str = "") -> int:
        """保存合并摘要到数据库"""
        return self.db.save_merge_summary(current_chapter, merge_factor, summary_content, 
                                        merge_levels, ai_generated_titles)
    
    def get_merge_summary(self, current_chapter: int, merge_factor: int) -> Optional[Dict[str, Any]]:
        """获取保存的合并摘要"""
        return self.db.get_merge_summary(current_chapter, merge_factor)
    
    def get_all_merge_summaries(self) -> List[Dict[str, Any]]:
        """获取所有保存的合并摘要"""
        return self.db.get_all_merge_summaries()
    
    def get_database_stats(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        return self.db.get_database_stats()
    
    def format_chapter_tree(self, tree: Dict[str, Any] = None, indent: str = "") -> str:
        """格式化章节树状结构为文本"""
        if tree is None:
            tree = self.get_chapter_tree()
        
        result = []
        for chapter_num, chapter in tree.items():
            # 添加当前章节
            result.append(f"{indent}第{chapter_num}章: {chapter['title']}")
            if chapter['summary']:
                result.append(f"{indent}  └─ 摘要: {chapter['summary'][:100]}...")
            
            # 递归添加子章节
            if chapter['children']:
                for child in chapter['children']:
                    result.append(f"{indent}  ├─ 子章节: {child['title']}")
                    if child['summary']:
                        result.append(f"{indent}  │   └─ 摘要: {child['summary'][:80]}...")
        
        return "\n".join(result)
    
    def format_plot_summary(self, up_to_chapter: int = None) -> str:
        """格式化情节大纲摘要"""
        summary = self.get_plot_summary(up_to_chapter)
        
        result = []
        result.append("📚 情节大纲摘要")
        result.append("=" * 50)
        
        # 统计信息
        result.append(f"📊 统计信息:")
        result.append(f"  • 总章节数: {summary['total_chapters']}")
        result.append(f"  • 总字数: {summary['total_word_count']:,}字")
        result.append("")
        
        # 章节列表
        result.append("📖 章节概览:")
        for chapter in summary['chapters']:
            indent = "  " * chapter['depth_level']
            result.append(f"{indent}第{chapter['chapter_number']}章: {chapter['title']}")
            if chapter['summary']:
                result.append(f"{indent}  └─ {chapter['summary'][:100]}...")
            if chapter['key_events']:
                result.append(f"{indent}  └─ 关键事件: {chapter['key_events'][:80]}...")
        
        result.append("")
        
        # 情节线
        if summary['plot_lines']:
            result.append("🎭 情节线:")
            for plot_line in summary['plot_lines']:
                result.append(f"  • {plot_line['name']}: {plot_line['description']}")
        
        return "\n".join(result)
    
    def format_character_timeline(self, character_name: str) -> str:
        """格式化角色发展时间线"""
        timeline = self.get_character_development_timeline(character_name)
        
        result = []
        result.append(f"👤 {character_name} 角色发展时间线")
        result.append("=" * 50)
        
        for arc in timeline:
            result.append(f"第{arc['chapter_number']}章: {arc['title']}")
            if arc['development']:
                result.append(f"  发展: {arc['development']}")
            if arc['emotional_state']:
                result.append(f"  情感状态: {arc['emotional_state']}")
            if arc['key_decisions']:
                result.append(f"  关键决定: {arc['key_decisions']}")
            if arc['relationships_changed']:
                result.append(f"  关系变化: {arc['relationships_changed']}")
            result.append("")
        
        return "\n".join(result)

# 便捷函数
def get_plot_api() -> PlotAPI:
    """获取情节大纲API实例"""
    return PlotAPI()

def add_chapter(chapter_number: int, title: str, summary: str = "", **kwargs) -> int:
    """添加新章节"""
    return get_plot_api().add_chapter(chapter_number, title, summary, **kwargs)

def get_plot_summary(up_to_chapter: int = None) -> str:
    """获取情节大纲摘要"""
    return get_plot_api().format_plot_summary(up_to_chapter)

def get_character_timeline(character_name: str) -> str:
    """获取角色发展时间线"""
    return get_plot_api().format_character_timeline(character_name)

if __name__ == "__main__":
    # 测试API功能
    api = PlotAPI()
    
    print("=== 情节大纲API测试 ===")
    
    # 测试添加章节
    chapter_id = api.add_chapter(
        1, 
        "卡塞尔之门", 
        "路明非收到卡塞尔学院的录取通知书，开始了解龙族世界的真相",
        word_count=2000,
        plot_point="路明非进入龙族世界",
        key_events="收到录取通知书，了解血统测试",
        character_focus="路明非",
        setting="卡塞尔学院",
        mood="神秘好奇",
        themes="新世界探索"
    )
    
    print(f"添加章节成功，ID: {chapter_id}")
    
    # 测试获取统计信息
    stats = api.get_database_stats()
    print(f"数据库统计: {stats}")
    
    # 测试获取情节摘要
    summary = api.format_plot_summary()
    print(summary)
