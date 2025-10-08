"""
龙族续写情节大纲数据库系统
使用树状结构记录章节情节，支持大纲梳理和后续规划
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import os

class PlotDatabase:
    """情节大纲数据库管理类"""
    
    def __init__(self, db_path: str = "plot_outline.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建章节表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter_number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    word_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed',
                    parent_chapter_id INTEGER,
                    depth_level INTEGER DEFAULT 0,
                    plot_point TEXT,
                    key_events TEXT,
                    character_focus TEXT,
                    setting TEXT,
                    mood TEXT,
                    themes TEXT,
                    notes TEXT,
                    FOREIGN KEY (parent_chapter_id) REFERENCES chapters (id)
                )
            ''')
            
            # 创建情节线表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plot_lines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建章节-情节线关联表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapter_plot_lines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter_id INTEGER,
                    plot_line_id INTEGER,
                    importance INTEGER DEFAULT 1,
                    progress TEXT,
                    FOREIGN KEY (chapter_id) REFERENCES chapters (id),
                    FOREIGN KEY (plot_line_id) REFERENCES plot_lines (id)
                )
            ''')
            
            # 创建角色发展轨迹表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_arcs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_name TEXT NOT NULL,
                    chapter_id INTEGER,
                    development TEXT,
                    emotional_state TEXT,
                    key_decisions TEXT,
                    relationships_changed TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chapter_id) REFERENCES chapters (id)
                )
            ''')
            
            # 创建合并摘要表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS merge_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    current_chapter INTEGER NOT NULL,
                    merge_factor INTEGER NOT NULL,
                    summary_content TEXT NOT NULL,
                    summary_length INTEGER DEFAULT 0,
                    merge_levels INTEGER DEFAULT 0,
                    ai_generated_titles TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(current_chapter, merge_factor)
                )
            ''')
            
            conn.commit()
    
    def add_chapter(self, chapter_number: int, title: str, summary: str = "", 
                   word_count: int = 0, parent_chapter_id: int = None,
                   plot_point: str = "", key_events: str = "", 
                   character_focus: str = "", setting: str = "",
                   mood: str = "", themes: str = "", notes: str = "") -> int:
        """
        添加新章节
        
        Args:
            chapter_number: 章节编号
            title: 章节标题
            summary: 章节摘要
            word_count: 字数
            parent_chapter_id: 父章节ID（用于树状结构）
            plot_point: 关键情节点
            key_events: 关键事件
            character_focus: 主要角色
            setting: 场景设定
            mood: 氛围
            themes: 主题
            notes: 备注
            
        Returns:
            章节ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 计算深度级别
            depth_level = 0
            if parent_chapter_id:
                cursor.execute('SELECT depth_level FROM chapters WHERE id = ?', (parent_chapter_id,))
                parent_depth = cursor.fetchone()
                if parent_depth:
                    depth_level = parent_depth[0] + 1
            
            cursor.execute('''
                INSERT INTO chapters (
                    chapter_number, title, summary, word_count, parent_chapter_id,
                    depth_level, plot_point, key_events, character_focus,
                    setting, mood, themes, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (chapter_number, title, summary, word_count, parent_chapter_id,
                  depth_level, plot_point, key_events, character_focus,
                  setting, mood, themes, notes))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_chapter(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """获取章节信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM chapters WHERE id = ?', (chapter_id,))
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def get_chapter_by_number(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """根据章节编号获取章节信息（返回第一个匹配的章节）"""
        chapters = self.get_chapters_by_number(chapter_number)
        return chapters[0] if chapters else None
    
    def get_chapters_by_number(self, chapter_number: int) -> List[Dict[str, Any]]:
        """根据章节编号获取所有匹配的章节"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM chapters WHERE chapter_number = ?', (chapter_number,))
            results = cursor.fetchall()
            
            if results:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, result)) for result in results]
            return []
    
    def get_all_chapters(self) -> List[Dict[str, Any]]:
        """获取所有章节"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM chapters ORDER BY chapter_number, depth_level')
            results = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, result)) for result in results]
    
    def get_chapter_tree(self) -> Dict[str, Any]:
        """获取章节树状结构"""
        chapters = self.get_all_chapters()
        
        # 构建树状结构
        tree = {}
        chapter_map = {}
        
        # 创建章节映射
        for chapter in chapters:
            chapter_map[chapter['id']] = chapter
            chapter['children'] = []
        
        # 构建父子关系
        for chapter in chapters:
            if chapter['parent_chapter_id']:
                parent = chapter_map.get(chapter['parent_chapter_id'])
                if parent:
                    parent['children'].append(chapter)
            else:
                tree[chapter['chapter_number']] = chapter
        
        return tree
    
    def update_chapter(self, chapter_id: int, **kwargs) -> bool:
        """更新章节信息"""
        if not kwargs:
            return False
        
        # 添加更新时间
        kwargs['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [chapter_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE chapters SET {set_clause} WHERE id = ?', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def add_plot_line(self, name: str, description: str = "", 
                     priority: int = 1) -> int:
        """添加情节线"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO plot_lines (name, description, priority)
                VALUES (?, ?, ?)
            ''', (name, description, priority))
            
            conn.commit()
            return cursor.lastrowid
    
    def link_chapter_plot_line(self, chapter_id: int, plot_line_id: int,
                              importance: int = 1, progress: str = ""):
        """关联章节和情节线"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chapter_plot_lines (chapter_id, plot_line_id, importance, progress)
                VALUES (?, ?, ?, ?)
            ''', (chapter_id, plot_line_id, importance, progress))
            conn.commit()
    
    def add_character_arc(self, character_name: str, chapter_id: int,
                         development: str = "", emotional_state: str = "",
                         key_decisions: str = "", relationships_changed: str = ""):
        """添加角色发展轨迹"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO character_arcs (
                    character_name, chapter_id, development, emotional_state,
                    key_decisions, relationships_changed
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (character_name, chapter_id, development, emotional_state,
                  key_decisions, relationships_changed))
            conn.commit()
    
    def get_plot_summary(self, up_to_chapter: int = None) -> Dict[str, Any]:
        """获取情节大纲摘要"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if up_to_chapter:
                cursor.execute('''
                    SELECT * FROM chapters 
                    WHERE chapter_number <= ? 
                    ORDER BY chapter_number, depth_level
                ''', (up_to_chapter,))
            else:
                cursor.execute('SELECT * FROM chapters ORDER BY chapter_number, depth_level')
            
            chapters = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            chapters = [dict(zip(columns, chapter)) for chapter in chapters]
            
            # 获取情节线
            cursor.execute('SELECT * FROM plot_lines ORDER BY priority DESC')
            plot_lines = cursor.fetchall()
            plot_columns = [description[0] for description in cursor.description]
            plot_lines = [dict(zip(plot_columns, line)) for line in plot_lines]
            
            return {
                'chapters': chapters,
                'plot_lines': plot_lines,
                'total_chapters': len(chapters),
                'total_word_count': sum(ch['word_count'] for ch in chapters)
            }
    
    def get_character_development_timeline(self, character_name: str) -> List[Dict[str, Any]]:
        """获取角色发展时间线"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ca.*, c.chapter_number, c.title
                FROM character_arcs ca
                JOIN chapters c ON ca.chapter_id = c.id
                WHERE ca.character_name = ?
                ORDER BY c.chapter_number
            ''', (character_name,))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, result)) for result in results]
    
    def save_merge_summary(self, current_chapter: int, merge_factor: int, 
                          summary_content: str, merge_levels: int = 0,
                          ai_generated_titles: str = "") -> int:
        """
        保存合并摘要到数据库
        
        Args:
            current_chapter: 当前章节号
            merge_factor: 合并因子
            summary_content: 摘要内容
            merge_levels: 合并层级数
            ai_generated_titles: AI生成的标题（JSON字符串）
            
        Returns:
            摘要记录ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 使用INSERT OR REPLACE来处理重复
            cursor.execute('''
                INSERT OR REPLACE INTO merge_summaries (
                    current_chapter, merge_factor, summary_content, 
                    summary_length, merge_levels, ai_generated_titles
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (current_chapter, merge_factor, summary_content, 
                  len(summary_content), merge_levels, ai_generated_titles))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_merge_summary(self, current_chapter: int, merge_factor: int) -> Optional[Dict[str, Any]]:
        """
        获取保存的合并摘要
        
        Args:
            current_chapter: 当前章节号
            merge_factor: 合并因子
            
        Returns:
            合并摘要信息或None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM merge_summaries 
                WHERE current_chapter = ? AND merge_factor = ?
            ''', (current_chapter, merge_factor))
            
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def get_all_merge_summaries(self) -> List[Dict[str, Any]]:
        """获取所有保存的合并摘要"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM merge_summaries 
                ORDER BY current_chapter DESC, merge_factor ASC
            ''')
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, result)) for result in results]
    
    def get_database_stats(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # 章节统计
            cursor.execute('SELECT COUNT(*) FROM chapters')
            stats['chapter_count'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(word_count) FROM chapters')
            stats['total_word_count'] = cursor.fetchone()[0] or 0
            
            # 情节线统计
            cursor.execute('SELECT COUNT(*) FROM plot_lines')
            stats['plot_line_count'] = cursor.fetchone()[0]
            
            # 角色发展轨迹统计
            cursor.execute('SELECT COUNT(*) FROM character_arcs')
            stats['character_arc_count'] = cursor.fetchone()[0]
            
            # 合并摘要统计
            cursor.execute('SELECT COUNT(*) FROM merge_summaries')
            stats['merge_summary_count'] = cursor.fetchone()[0]
            
            return stats

if __name__ == "__main__":
    # 测试数据库功能
    db = PlotDatabase("test_plot.db")
    
    print("情节大纲数据库初始化完成！")
    stats = db.get_database_stats()
    print(f"数据库统计: {stats}")
