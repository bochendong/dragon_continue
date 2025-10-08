#!/usr/bin/env python3
"""
主线/支线数据库
管理故事的主线和支线，支持动态创建和完结
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class StorylineDatabase:
    """主线/支线数据库"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "storylines.db")
        
        self.db_path = db_path
        self._create_tables()
        self._init_mainline()
    
    def _create_tables(self):
        """创建数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 主线表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mainline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    current_phase TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 支线表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS storylines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    storyline_type TEXT NOT NULL,  -- arc/subplot
                    status TEXT NOT NULL,  -- planned/active/completed
                    start_chapter INTEGER,
                    end_chapter INTEGER,
                    actual_end_chapter INTEGER,  -- 实际结束章节
                    main_theme TEXT,
                    tone TEXT,
                    setting TEXT,
                    arc_type TEXT,  -- daily/adventure/crisis/transition
                    summary TEXT,  -- 支线完成后的总结
                    next_storyline_hint TEXT,  -- 下一个支线的提示
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 支线关键事件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS storyline_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    storyline_id INTEGER NOT NULL,
                    event_description TEXT NOT NULL,
                    event_order INTEGER NOT NULL,
                    chapter_number INTEGER,  -- 实际发生的章节（如果已发生）
                    status TEXT DEFAULT 'pending',  -- pending/completed
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (storyline_id) REFERENCES storylines(id)
                )
            ''')
            
            # 支线角色关系表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS storyline_characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    storyline_id INTEGER NOT NULL,
                    character_name TEXT NOT NULL,
                    role TEXT,  -- protagonist/supporting/antagonist
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (storyline_id) REFERENCES storylines(id)
                )
            ''')
            
            # 主线阶段表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mainline_phases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mainline_id INTEGER NOT NULL,
                    phase_name TEXT NOT NULL,
                    phase_description TEXT,
                    start_chapter INTEGER,
                    end_chapter INTEGER,
                    status TEXT DEFAULT 'planned',  -- planned/active/completed
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (mainline_id) REFERENCES mainline(id)
                )
            ''')
            
            conn.commit()
    
    def _init_mainline(self):
        """初始化主线（如果不存在）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM mainline')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO mainline (name, description, current_phase)
                    VALUES (?, ?, ?)
                ''', (
                    "龙族主线：路明非的成长与龙族命运",
                    "路明非从普通高中生到龙族战士的成长历程，揭开龙族世界的秘密，面对命运的选择",
                    "大一第一学期"
                ))
                conn.commit()
    
    # ==================== 主线管理 ====================
    
    def get_mainline(self) -> Optional[Dict[str, Any]]:
        """获取主线信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM mainline LIMIT 1')
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def update_mainline_phase(self, phase: str):
        """更新主线当前阶段"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE mainline SET current_phase = ?, updated_at = ?
                WHERE id = 1
            ''', (phase, datetime.now().isoformat()))
            conn.commit()
    
    def add_mainline_phase(
        self, 
        phase_name: str, 
        description: str,
        start_chapter: int,
        end_chapter: int = None
    ) -> int:
        """添加主线阶段"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO mainline_phases 
                (mainline_id, phase_name, phase_description, start_chapter, end_chapter, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (1, phase_name, description, start_chapter, end_chapter, 'planned'))
            conn.commit()
            return cursor.lastrowid
    
    def get_mainline_phases(self, status: str = None) -> List[Dict[str, Any]]:
        """获取主线阶段列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM mainline_phases 
                    WHERE status = ?
                    ORDER BY start_chapter
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT * FROM mainline_phases 
                    ORDER BY start_chapter
                ''')
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, result)) for result in results]
    
    # ==================== 支线管理 ====================
    
    def create_storyline(
        self,
        name: str,
        storyline_type: str,
        start_chapter: int,
        end_chapter: int,
        main_theme: str,
        tone: str,
        setting: str,
        arc_type: str = "adventure"
    ) -> int:
        """创建新支线"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO storylines 
                (name, storyline_type, status, start_chapter, end_chapter, 
                 main_theme, tone, setting, arc_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, storyline_type, 'planned', start_chapter, end_chapter,
                main_theme, tone, setting, arc_type
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_storyline(self, storyline_id: int) -> Optional[Dict[str, Any]]:
        """获取支线信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM storylines WHERE id = ?', (storyline_id,))
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def get_storylines_by_status(self, status: str) -> List[Dict[str, Any]]:
        """根据状态获取支线列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM storylines 
                WHERE status = ?
                ORDER BY start_chapter
            ''', (status,))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, result)) for result in results]
    
    def get_active_storyline(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """获取当前章节的活跃支线"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM storylines 
                WHERE status = 'active' 
                AND start_chapter <= ?
                AND (end_chapter >= ? OR end_chapter IS NULL)
                ORDER BY start_chapter DESC
                LIMIT 1
            ''', (chapter_number, chapter_number))
            
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def activate_storyline(self, storyline_id: int):
        """激活支线（从planned变为active）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE storylines 
                SET status = 'active', updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), storyline_id))
            conn.commit()
    
    def complete_storyline(
        self, 
        storyline_id: int,
        actual_end_chapter: int,
        summary: str,
        next_hint: str = None
    ):
        """完结支线"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE storylines 
                SET status = 'completed', 
                    actual_end_chapter = ?,
                    summary = ?,
                    next_storyline_hint = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (
                actual_end_chapter, 
                summary, 
                next_hint,
                datetime.now().isoformat(), 
                storyline_id
            ))
            conn.commit()
    
    # ==================== 支线事件管理 ====================
    
    def add_storyline_event(
        self,
        storyline_id: int,
        event_description: str,
        event_order: int
    ) -> int:
        """添加支线关键事件"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO storyline_events 
                (storyline_id, event_description, event_order)
                VALUES (?, ?, ?)
            ''', (storyline_id, event_description, event_order))
            conn.commit()
            return cursor.lastrowid
    
    def get_storyline_events(
        self, 
        storyline_id: int,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """获取支线的关键事件列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM storyline_events 
                    WHERE storyline_id = ? AND status = ?
                    ORDER BY event_order
                ''', (storyline_id, status))
            else:
                cursor.execute('''
                    SELECT * FROM storyline_events 
                    WHERE storyline_id = ?
                    ORDER BY event_order
                ''', (storyline_id,))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, result)) for result in results]
    
    def complete_event(self, event_id: int, chapter_number: int):
        """标记事件为已完成"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE storyline_events 
                SET status = 'completed', chapter_number = ?
                WHERE id = ?
            ''', (chapter_number, event_id))
            conn.commit()
    
    # ==================== 支线角色管理 ====================
    
    def add_storyline_character(
        self,
        storyline_id: int,
        character_name: str,
        role: str = "supporting"
    ) -> int:
        """添加支线相关角色"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO storyline_characters 
                (storyline_id, character_name, role)
                VALUES (?, ?, ?)
            ''', (storyline_id, character_name, role))
            conn.commit()
            return cursor.lastrowid
    
    def get_storyline_characters(self, storyline_id: int) -> List[Dict[str, Any]]:
        """获取支线的角色列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM storyline_characters 
                WHERE storyline_id = ?
            ''', (storyline_id,))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, result)) for result in results]
    
    # ==================== 统计与查询 ====================
    
    def get_database_stats(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # 支线统计
            cursor.execute("SELECT COUNT(*) FROM storylines WHERE status = 'planned'")
            stats['planned_storylines'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM storylines WHERE status = 'active'")
            stats['active_storylines'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM storylines WHERE status = 'completed'")
            stats['completed_storylines'] = cursor.fetchone()[0]
            
            # 事件统计
            cursor.execute("SELECT COUNT(*) FROM storyline_events WHERE status = 'pending'")
            stats['pending_events'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM storyline_events WHERE status = 'completed'")
            stats['completed_events'] = cursor.fetchone()[0]
            
            # 主线阶段统计
            cursor.execute("SELECT COUNT(*) FROM mainline_phases")
            stats['mainline_phases'] = cursor.fetchone()[0]
            
            return stats
    
    def get_all_storylines(self) -> List[Dict[str, Any]]:
        """获取所有支线"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM storylines 
                ORDER BY start_chapter
            ''')
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, result)) for result in results]

# ==================== API层 ====================

class StorylineAPI:
    """支线API - 提供更高级的接口"""
    
    def __init__(self, db_path: str = None):
        self.db = StorylineDatabase(db_path)
    
    def get_current_context(self, chapter_number: int) -> Dict[str, Any]:
        """获取当前章节的完整上下文"""
        
        mainline = self.db.get_mainline()
        active_storyline = self.db.get_active_storyline(chapter_number)
        
        context = {
            "mainline": mainline,
            "active_storyline": None,
            "completed_storylines": [],
            "planned_storylines": []
        }
        
        if active_storyline:
            # 获取支线的事件和角色
            events = self.db.get_storyline_events(active_storyline['id'])
            characters = self.db.get_storyline_characters(active_storyline['id'])
            
            active_storyline['events'] = events
            active_storyline['characters'] = characters
            context['active_storyline'] = active_storyline
        
        # 获取已完成的支线（带总结）
        completed = self.db.get_storylines_by_status('completed')
        context['completed_storylines'] = completed
        
        # 获取计划中的支线
        planned = self.db.get_storylines_by_status('planned')
        context['planned_storylines'] = planned
        
        return context
    
    def format_context_for_ai(self, chapter_number: int) -> str:
        """格式化上下文为AI可读的文本"""
        
        context = self.get_current_context(chapter_number)
        
        lines = []
        lines.append("=" * 60)
        lines.append("📖 主线与支线结构")
        lines.append("=" * 60)
        
        # 主线
        mainline = context['mainline']
        lines.append(f"\n🎯 主线: {mainline['name']}")
        lines.append(f"   描述: {mainline['description']}")
        lines.append(f"   当前阶段: {mainline['current_phase']}")
        
        # 活跃支线
        if context['active_storyline']:
            arc = context['active_storyline']
            lines.append(f"\n📚 当前活跃支线: {arc['name']}")
            lines.append(f"   类型: {arc['arc_type']}")
            lines.append(f"   章节范围: 第{arc['start_chapter']}-{arc['end_chapter']}章")
            lines.append(f"   主题: {arc['main_theme']}")
            lines.append(f"   基调: {arc['tone']}")
            lines.append(f"   场景: {arc['setting']}")
            
            # 关键事件
            pending_events = [e for e in arc['events'] if e['status'] == 'pending']
            completed_events = [e for e in arc['events'] if e['status'] == 'completed']
            
            if completed_events:
                lines.append(f"\n   ✅ 已完成事件:")
                for event in completed_events:
                    lines.append(f"      {event['event_order']}. {event['event_description']} (第{event['chapter_number']}章)")
            
            if pending_events:
                lines.append(f"\n   ⏳ 待完成事件:")
                for event in pending_events:
                    lines.append(f"      {event['event_order']}. {event['event_description']}")
            
            # 角色
            if arc['characters']:
                char_names = [c['character_name'] for c in arc['characters']]
                lines.append(f"\n   👥 相关角色: {', '.join(char_names)}")
        
        # 已完成支线（总结）
        if context['completed_storylines']:
            lines.append(f"\n✅ 已完成的支线:")
            for arc in context['completed_storylines']:
                lines.append(f"\n   [{arc['name']}] (第{arc['start_chapter']}-{arc['actual_end_chapter']}章)")
                if arc['summary']:
                    lines.append(f"   总结: {arc['summary'][:200]}...")
                if arc['next_storyline_hint']:
                    lines.append(f"   后续: {arc['next_storyline_hint']}")
        
        # 计划中的支线
        if context['planned_storylines']:
            lines.append(f"\n📋 计划中的支线:")
            for arc in context['planned_storylines']:
                lines.append(f"   - {arc['name']} (预计第{arc['start_chapter']}-{arc['end_chapter']}章)")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    api = StorylineAPI()
    
    print("📊 数据库统计:")
    stats = api.db.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n📖 主线信息:")
    mainline = api.db.get_mainline()
    print(f"  {mainline['name']}")
    print(f"  当前阶段: {mainline['current_phase']}")

