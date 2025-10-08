"""
龙族角色关系数据库管理系统
使用SQLite数据库存储和管理角色信息、关系、台词等数据
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import os

class CharacterDatabase:
    """角色数据库管理类"""
    
    def __init__(self, db_path: str = "characters.db"):
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
            
            # 角色基本信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    background_story TEXT,
                    character_arc TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 角色性格特征表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personality_traits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    trait TEXT NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                )
            ''')
            
            # 说话特点表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS speech_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    pattern TEXT NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                )
            ''')
            
            # 经典台词表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memorable_quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    quote TEXT NOT NULL,
                    context TEXT,
                    popularity_score INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                )
            ''')
            
            # 角色关系表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character1_id INTEGER,
                    character2_id INTEGER,
                    relationship_type TEXT NOT NULL,
                    description TEXT,
                    strength INTEGER DEFAULT 1, -- 关系强度 1-10
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character1_id) REFERENCES characters (id) ON DELETE CASCADE,
                    FOREIGN KEY (character2_id) REFERENCES characters (id) ON DELETE CASCADE,
                    UNIQUE(character1_id, character2_id)
                )
            ''')
            
            # 角色发展轨迹表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_development (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    stage TEXT NOT NULL, -- 发展阶段
                    description TEXT,
                    chapter_range TEXT, -- 章节范围
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                )
            ''')
            
            # 角色血统等级表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_bloodline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    bloodline_level TEXT NOT NULL, -- 血统等级
                    bloodline_percentage INTEGER, -- 血统纯度百分比
                    dragon_heritage TEXT, -- 龙族血统来源
                    description TEXT,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                )
            ''')
            
            # 言灵库表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spirit_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL, -- 言灵名称
                    sequence_number INTEGER, -- 序列号
                    dragon_name TEXT, -- 对应龙王名称
                    description TEXT NOT NULL, -- 言灵描述
                    effects TEXT, -- 效果描述
                    limitations TEXT, -- 限制条件
                    rarity_level TEXT, -- 稀有度等级
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 角色言灵表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_spirit_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    spirit_word_id INTEGER,
                    mastery_level INTEGER DEFAULT 1, -- 掌握等级 1-5
                    activation_condition TEXT, -- 激活条件
                    notes TEXT, -- 备注
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE,
                    FOREIGN KEY (spirit_word_id) REFERENCES spirit_words (id) ON DELETE CASCADE,
                    UNIQUE(character_id, spirit_word_id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_name ON characters (name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_char1 ON character_relationships (character1_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_char2 ON character_relationships (character2_id)')
            
            conn.commit()
    
    def add_character(self, name: str, background_story: str = "", character_arc: str = "") -> int:
        """
        添加新角色
        
        Args:
            name: 角色名称
            background_story: 背景故事
            character_arc: 角色发展轨迹
            
        Returns:
            角色ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO characters (name, background_story, character_arc, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (name, background_story, character_arc))
            return cursor.lastrowid
    
    def add_personality_traits(self, character_id: int, traits: List[str]):
        """添加角色性格特征"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM personality_traits WHERE character_id = ?', (character_id,))
            for trait in traits:
                cursor.execute('''
                    INSERT INTO personality_traits (character_id, trait)
                    VALUES (?, ?)
                ''', (character_id, trait))
    
    def add_speech_patterns(self, character_id: int, patterns: List[str]):
        """添加说话特点"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM speech_patterns WHERE character_id = ?', (character_id,))
            for pattern in patterns:
                cursor.execute('''
                    INSERT INTO speech_patterns (character_id, pattern)
                    VALUES (?, ?)
                ''', (character_id, pattern))
    
    def add_memorable_quotes(self, character_id: int, quotes: List[Tuple[str, str, int]]):
        """
        添加经典台词
        
        Args:
            character_id: 角色ID
            quotes: [(quote, context, popularity_score), ...]
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM memorable_quotes WHERE character_id = ?', (character_id,))
            for quote, context, score in quotes:
                cursor.execute('''
                    INSERT INTO memorable_quotes (character_id, quote, context, popularity_score)
                    VALUES (?, ?, ?, ?)
                ''', (character_id, quote, context, score))
    
    def add_relationship(self, char1_name: str, char2_name: str, relationship_type: str, 
                        description: str = "", strength: int = 1):
        """添加角色关系"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取角色ID
            char1_id = self.get_character_id(char1_name)
            char2_id = self.get_character_id(char2_name)
            
            if not char1_id or not char2_id:
                raise ValueError(f"角色不存在: {char1_name} 或 {char2_name}")
            
            cursor.execute('''
                INSERT OR REPLACE INTO character_relationships 
                (character1_id, character2_id, relationship_type, description, strength)
                VALUES (?, ?, ?, ?, ?)
            ''', (char1_id, char2_id, relationship_type, description, strength))
    
    def add_bloodline_info(self, character_name: str, bloodline_level: str, 
                          bloodline_percentage: int, dragon_heritage: str = "", 
                          description: str = ""):
        """添加角色血统信息"""
        char_id = self.get_character_id(character_name)
        if not char_id:
            raise ValueError(f"角色不存在: {character_name}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO character_bloodline 
                (character_id, bloodline_level, bloodline_percentage, dragon_heritage, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (char_id, bloodline_level, bloodline_percentage, dragon_heritage, description))
    
    def add_spirit_word(self, name: str, sequence_number: int, dragon_name: str,
                       description: str, effects: str = "", limitations: str = "",
                       rarity_level: str = "普通"):
        """添加言灵到言灵库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO spirit_words 
                (name, sequence_number, dragon_name, description, effects, limitations, rarity_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, sequence_number, dragon_name, description, effects, limitations, rarity_level))
    
    def add_character_spirit_word(self, character_name: str, spirit_word_name: str,
                                 mastery_level: int = 1, activation_condition: str = "",
                                 notes: str = ""):
        """为角色添加言灵"""
        char_id = self.get_character_id(character_name)
        if not char_id:
            raise ValueError(f"角色不存在: {character_name}")
        
        # 获取言灵ID
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM spirit_words WHERE name = ?', (spirit_word_name,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"言灵不存在: {spirit_word_name}")
            spirit_word_id = result[0]
            
            cursor.execute('''
                INSERT OR REPLACE INTO character_spirit_words 
                (character_id, spirit_word_id, mastery_level, activation_condition, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (char_id, spirit_word_id, mastery_level, activation_condition, notes))
    
    def get_character_id(self, name: str) -> Optional[int]:
        """获取角色ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM characters WHERE name = ?', (name,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_character_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """获取完整的角色档案"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取基本信息
            cursor.execute('''
                SELECT id, background_story, character_arc 
                FROM characters WHERE name = ?
            ''', (name,))
            basic_info = cursor.fetchone()
            
            if not basic_info:
                return None
            
            char_id = basic_info[0]
            
            # 获取性格特征
            cursor.execute('''
                SELECT trait FROM personality_traits WHERE character_id = ?
            ''', (char_id,))
            traits = [row[0] for row in cursor.fetchall()]
            
            # 获取说话特点
            cursor.execute('''
                SELECT pattern FROM speech_patterns WHERE character_id = ?
            ''', (char_id,))
            speech_patterns = [row[0] for row in cursor.fetchall()]
            
            # 获取经典台词
            cursor.execute('''
                SELECT quote, context, popularity_score FROM memorable_quotes 
                WHERE character_id = ? ORDER BY popularity_score DESC
            ''', (char_id,))
            quotes = [{"quote": row[0], "context": row[1], "score": row[2]} 
                     for row in cursor.fetchall()]
            
            # 获取关系
            cursor.execute('''
                SELECT c2.name, cr.relationship_type, cr.description, cr.strength
                FROM character_relationships cr
                JOIN characters c2 ON cr.character2_id = c2.id
                WHERE cr.character1_id = ?
            ''', (char_id,))
            relationships = {row[0]: {"type": row[1], "description": row[2], "strength": row[3]} 
                           for row in cursor.fetchall()}
            
            return {
                "id": char_id,
                "name": name,
                "background_story": basic_info[1],
                "character_arc": basic_info[2],
                "personality_traits": traits,
                "speech_patterns": speech_patterns,
                "memorable_quotes": quotes,
                "relationships": relationships
            }
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """获取所有角色档案"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM characters ORDER BY name')
            names = [row[0] for row in cursor.fetchall()]
            
            return [self.get_character_profile(name) for name in names]
    
    def search_characters(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索角色"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT c.name FROM characters c
                LEFT JOIN personality_traits pt ON c.id = pt.character_id
                LEFT JOIN speech_patterns sp ON c.id = sp.character_id
                LEFT JOIN memorable_quotes mq ON c.id = mq.character_id
                WHERE c.name LIKE ? OR c.background_story LIKE ? OR 
                      pt.trait LIKE ? OR sp.pattern LIKE ? OR mq.quote LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            
            names = [row[0] for row in cursor.fetchall()]
            return [self.get_character_profile(name) for name in names]
    
    def get_character_relationships(self, name: str) -> Dict[str, Dict[str, Any]]:
        """获取角色的所有关系"""
        char_id = self.get_character_id(name)
        if not char_id:
            return {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c2.name, cr.relationship_type, cr.description, cr.strength
                FROM character_relationships cr
                JOIN characters c2 ON cr.character2_id = c2.id
                WHERE cr.character1_id = ?
            ''', (char_id,))
            
            return {row[0]: {"type": row[1], "description": row[2], "strength": row[3]} 
                   for row in cursor.fetchall()}
    
    def update_character(self, name: str, **kwargs):
        """更新角色信息"""
        char_id = self.get_character_id(name)
        if not char_id:
            raise ValueError(f"角色不存在: {name}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 更新基本信息
            if 'background_story' in kwargs:
                cursor.execute('''
                    UPDATE characters SET background_story = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (kwargs['background_story'], char_id))
            
            if 'character_arc' in kwargs:
                cursor.execute('''
                    UPDATE characters SET character_arc = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (kwargs['character_arc'], char_id))
            
            # 更新其他属性
            if 'personality_traits' in kwargs:
                self.add_personality_traits(char_id, kwargs['personality_traits'])
            
            if 'speech_patterns' in kwargs:
                self.add_speech_patterns(char_id, kwargs['speech_patterns'])
            
            if 'memorable_quotes' in kwargs:
                self.add_memorable_quotes(char_id, kwargs['memorable_quotes'])
    
    def delete_character(self, name: str):
        """删除角色"""
        char_id = self.get_character_id(name)
        if not char_id:
            raise ValueError(f"角色不存在: {name}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM characters WHERE id = ?', (char_id,))
    
    def export_to_json(self, output_file: str = "characters_export.json"):
        """导出所有角色数据到JSON文件"""
        characters = self.get_all_characters()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(characters, f, ensure_ascii=False, indent=2)
    
    def import_from_json(self, input_file: str):
        """从JSON文件导入角色数据"""
        with open(input_file, 'r', encoding='utf-8') as f:
            characters = json.load(f)
        
        for char_data in characters:
            name = char_data['name']
            
            # 添加角色基本信息
            char_id = self.add_character(
                name, 
                char_data.get('background_story', ''),
                char_data.get('character_arc', '')
            )
            
            # 添加性格特征
            if 'personality_traits' in char_data:
                self.add_personality_traits(char_id, char_data['personality_traits'])
            
            # 添加说话特点
            if 'speech_patterns' in char_data:
                self.add_speech_patterns(char_id, char_data['speech_patterns'])
            
            # 添加经典台词
            if 'memorable_quotes' in char_data:
                quotes = []
                for quote_data in char_data['memorable_quotes']:
                    if isinstance(quote_data, dict):
                        quotes.append((quote_data['quote'], quote_data.get('context', ''), quote_data.get('score', 0)))
                    else:
                        quotes.append((quote_data, '', 0))
                self.add_memorable_quotes(char_id, quotes)
            
            # 添加关系
            if 'relationships' in char_data:
                for rel_name, rel_data in char_data['relationships'].items():
                    if isinstance(rel_data, dict):
                        self.add_relationship(name, rel_name, rel_data.get('type', ''), 
                                            rel_data.get('description', ''), rel_data.get('strength', 1))
                    else:
                        self.add_relationship(name, rel_name, str(rel_data))
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM characters')
            char_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM character_relationships')
            rel_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM memorable_quotes')
            quote_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(popularity_score) FROM memorable_quotes')
            avg_score = cursor.fetchone()[0] or 0
            
        cursor.execute('SELECT COUNT(*) FROM character_bloodline')
        bloodline_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM spirit_words')
        spirit_word_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM character_spirit_words')
        character_spirit_word_count = cursor.fetchone()[0]
        
        return {
            "character_count": char_count,
            "relationship_count": rel_count,
            "quote_count": quote_count,
            "bloodline_count": bloodline_count,
            "spirit_word_count": spirit_word_count,
            "character_spirit_word_count": character_spirit_word_count,
            "average_quote_score": round(avg_score, 2),
            "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }
    
    def get_character_bloodline(self, character_name: str) -> Optional[Dict[str, Any]]:
        """获取角色血统信息"""
        char_id = self.get_character_id(character_name)
        if not char_id:
            return None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT bloodline_level, bloodline_percentage, dragon_heritage, description
                FROM character_bloodline WHERE character_id = ?
            ''', (char_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    "bloodline_level": result[0],
                    "bloodline_percentage": result[1],
                    "dragon_heritage": result[2],
                    "description": result[3]
                }
            return None
    
    def get_character_spirit_words(self, character_name: str) -> List[Dict[str, Any]]:
        """获取角色言灵信息"""
        char_id = self.get_character_id(character_name)
        if not char_id:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sw.name, sw.sequence_number, sw.dragon_name, sw.description,
                       sw.effects, sw.limitations, sw.rarity_level,
                       csw.mastery_level, csw.activation_condition, csw.notes
                FROM character_spirit_words csw
                JOIN spirit_words sw ON csw.spirit_word_id = sw.id
                WHERE csw.character_id = ?
                ORDER BY sw.sequence_number
            ''', (char_id,))
            
            results = cursor.fetchall()
            spirit_words = []
            for row in results:
                spirit_words.append({
                    "name": row[0],
                    "sequence_number": row[1],
                    "dragon_name": row[2],
                    "description": row[3],
                    "effects": row[4],
                    "limitations": row[5],
                    "rarity_level": row[6],
                    "mastery_level": row[7],
                    "activation_condition": row[8],
                    "notes": row[9]
                })
            return spirit_words
    
    def get_all_spirit_words(self) -> List[Dict[str, Any]]:
        """获取所有言灵"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, sequence_number, dragon_name, description,
                       effects, limitations, rarity_level
                FROM spirit_words
                ORDER BY sequence_number
            ''')
            
            results = cursor.fetchall()
            spirit_words = []
            for row in results:
                spirit_words.append({
                    "name": row[0],
                    "sequence_number": row[1],
                    "dragon_name": row[2],
                    "description": row[3],
                    "effects": row[4],
                    "limitations": row[5],
                    "rarity_level": row[6]
                })
            return spirit_words
    
    def search_spirit_words(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索言灵"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, sequence_number, dragon_name, description,
                       effects, limitations, rarity_level
                FROM spirit_words
                WHERE name LIKE ? OR description LIKE ? OR dragon_name LIKE ?
                ORDER BY sequence_number
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            
            results = cursor.fetchall()
            spirit_words = []
            for row in results:
                spirit_words.append({
                    "name": row[0],
                    "sequence_number": row[1],
                    "dragon_name": row[2],
                    "description": row[3],
                    "effects": row[4],
                    "limitations": row[5],
                    "rarity_level": row[6]
                })
            return spirit_words


# 便捷函数
def create_database(db_path: str = "characters.db") -> CharacterDatabase:
    """创建数据库实例"""
    return CharacterDatabase(db_path)

def get_character_db() -> CharacterDatabase:
    """获取默认数据库实例"""
    return CharacterDatabase()

if __name__ == "__main__":
    # 测试数据库功能
    db = CharacterDatabase("test_characters.db")
    
    # 添加测试角色
    char_id = db.add_character("路明非", "普通高中生成长为龙族战士", "寻找自我价值")
    db.add_personality_traits(char_id, ["自卑但善良", "内心孤独", "有正义感"])
    db.add_speech_patterns(char_id, ["善于自嘲", "内心独白丰富"])
    db.add_memorable_quotes(char_id, [("我们都是小怪兽！", "经典台词", 10)])
    
    # 测试查询
    profile = db.get_character_profile("路明非")
    print(f"角色档案: {profile['name']}")
    print(f"性格特征: {profile['personality_traits']}")
    
    # 获取统计信息
    stats = db.get_database_stats()
    print(f"数据库统计: {stats}")
