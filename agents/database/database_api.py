"""
角色数据库API接口
提供简化的数据库操作接口，供Agent系统使用
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from character_database import CharacterDatabase, get_character_db

class CharacterAPI:
    """角色数据库API类"""
    
    def __init__(self, db_path: str = None):
        """
        初始化API
        
        Args:
            db_path: 数据库路径，默认使用database目录下的dragon_characters.db
        """
        if db_path is None:
            # 查找数据库文件
            current_dir = os.path.dirname(__file__)
            possible_paths = [
                os.path.join(current_dir, "dragon_characters.db"),
                os.path.join(current_dir, "..", "dragon_characters.db"),
                "dragon_characters.db"
            ]
            
            db_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            
            if db_path is None:
                # 如果都没找到，使用默认路径
                db_path = os.path.join(current_dir, "dragon_characters.db")
        
        self.db = CharacterDatabase(db_path)
    
    # ==================== 角色查询接口 ====================
    
    def get_character(self, name: str) -> dict:
        """
        获取角色档案
        
        Args:
            name: 角色名称
            
        Returns:
            角色档案字典，如果不存在返回None
        """
        return self.db.get_character_profile(name)
    
    def get_character_detail(self, name: str) -> str:
        """
        获取格式化的角色详细信息
        
        Args:
            name: 角色名称
            
        Returns:
            格式化的角色详细信息字符串
        """
        character = self.get_character(name)
        if not character:
            return f"角色 {name} 不存在"
        
        # 格式化输出
        detail = f"📖 角色档案: {character['name']}\n"
        detail += "=" * 50 + "\n"
        
        # 基本信息
        detail += f"🎭 背景故事:\n{character['background_story']}\n\n"
        
        if character['character_arc']:
            detail += f"📈 角色发展:\n{character['character_arc']}\n\n"
        
        # 性格特征
        detail += f"🧠 性格特征:\n"
        for i, trait in enumerate(character['personality_traits'], 1):
            detail += f"  {i}. {trait}\n"
        detail += "\n"
        
        # 说话特点
        detail += f"💬 说话特点:\n"
        for i, pattern in enumerate(character['speech_patterns'], 1):
            detail += f"  {i}. {pattern}\n"
        detail += "\n"
        
        # 经典台词
        detail += f"🌟 经典台词:\n"
        for i, quote_data in enumerate(character['memorable_quotes'][:5], 1):
            quote = quote_data['quote']
            context = quote_data.get('context', '')
            score = quote_data.get('score', 0)
            detail += f"  {i}. \"{quote}\"\n"
            if context:
                detail += f"     情境: {context}\n"
            if score > 0:
                detail += f"     评分: {score}/10\n"
            detail += "\n"
        
        # 角色关系
        relationships = character['relationships']
        if relationships:
            detail += f"🔗 重要关系:\n"
            for rel_name, rel_data in relationships.items():
                rel_type = rel_data['type']
                strength = rel_data['strength']
                description = rel_data.get('description', '')
                detail += f"  • {rel_name}: {rel_type} (强度: {strength}/10)\n"
                if description:
                    detail += f"    描述: {description}\n"
            detail += "\n"
        
        # 血统信息
        bloodline = self.get_character_bloodline(name)
        if bloodline:
            detail += f"🩸 血统信息:\n"
            detail += f"   等级: {bloodline['bloodline_level']}\n"
            detail += f"   纯度: {bloodline['bloodline_percentage']}%\n"
            if bloodline['dragon_heritage']:
                detail += f"   龙族血统: {bloodline['dragon_heritage']}\n"
            if bloodline['description']:
                detail += f"   描述: {bloodline['description']}\n"
            detail += "\n"
        
        # 言灵信息
        spirit_words = self.get_character_spirit_words(name)
        if spirit_words:
            detail += f"⚡ 言灵能力:\n"
            for i, sw in enumerate(spirit_words, 1):
                detail += f"   {i}. {sw['name']} (序列{sw['sequence_number']})\n"
                detail += f"      掌握等级: {sw['mastery_level']}/5\n"
                detail += f"      稀有度: {sw['rarity_level']}\n"
                if sw['effects']:
                    detail += f"      效果: {sw['effects']}\n"
                if sw['activation_condition']:
                    detail += f"      激活条件: {sw['activation_condition']}\n"
                detail += "\n"
        
        # 角色重要性
        importance = self.get_character_importance(name)
        relationship_count = len(relationships)
        detail += f"⭐ 角色重要性: {importance} (关系数: {relationship_count})\n"
        
        return detail
    
    def get_character_names(self) -> list:
        """获取所有角色名称"""
        profiles = self.db.get_all_characters()
        return [profile['name'] for profile in profiles if profile]
    
    def search_characters(self, keyword: str) -> list:
        """
        搜索角色
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的角色档案列表
        """
        return self.db.search_characters(keyword)
    
    # ==================== 关系查询接口 ====================
    
    def get_relationships(self, character_name: str) -> dict:
        """
        获取角色的所有关系
        
        Args:
            character_name: 角色名称
            
        Returns:
            关系字典 {角色名: {type, description, strength}}
        """
        return self.db.get_character_relationships(character_name)
    
    def get_relationship_strength(self, char1: str, char2: str) -> int:
        """
        获取两个角色之间的关系强度
        
        Args:
            char1: 角色1名称
            char2: 角色2名称
            
        Returns:
            关系强度 (1-10)，如果没有关系返回0
        """
        relationships = self.get_relationships(char1)
        if char2 in relationships:
            return relationships[char2]['strength']
        return 0
    
    def get_relationship_type(self, char1: str, char2: str) -> str:
        """
        获取两个角色之间的关系类型
        
        Args:
            char1: 角色1名称
            char2: 角色2名称
            
        Returns:
            关系类型，如果没有关系返回""
        """
        relationships = self.get_relationships(char1)
        if char2 in relationships:
            return relationships[char2]['type']
        return ""
    
    def are_characters_related(self, char1: str, char2: str) -> bool:
        """
        检查两个角色是否有关系
        
        Args:
            char1: 角色1名称
            char2: 角色2名称
            
        Returns:
            是否有关系
        """
        return self.get_relationship_strength(char1, char2) > 0
    
    # ==================== 角色特征接口 ====================
    
    def get_personality_traits(self, character_name: str) -> list:
        """获取角色性格特征"""
        character = self.get_character(character_name)
        return character['personality_traits'] if character else []
    
    def get_speech_patterns(self, character_name: str) -> list:
        """获取角色说话特点"""
        character = self.get_character(character_name)
        return character['speech_patterns'] if character else []
    
    def get_memorable_quotes(self, character_name: str, limit: int = 5) -> list:
        """
        获取角色经典台词
        
        Args:
            character_name: 角色名称
            limit: 返回数量限制
            
        Returns:
            台词列表，按评分排序
        """
        character = self.get_character(character_name)
        if character:
            quotes = character['memorable_quotes']
            return quotes[:limit]
        return []
    
    def get_top_quote(self, character_name: str) -> str:
        """获取角色最高评分的台词"""
        quotes = self.get_memorable_quotes(character_name, 1)
        return quotes[0]['quote'] if quotes else ""
    
    # ==================== 统计信息接口 ====================
    
    def get_database_info(self) -> dict:
        """获取数据库信息"""
        return self.db.get_database_stats()
    
    def get_character_count(self) -> int:
        """获取角色数量"""
        return len(self.get_character_names())
    
    # ==================== 便捷函数 ====================
    
    def is_main_character(self, character_name: str) -> bool:
        """检查是否为主要角色"""
        main_characters = ["路明非", "路鸣泽", "凯撒", "诺诺", "楚子航"]
        return character_name in main_characters
    
    def get_character_importance(self, character_name: str) -> str:
        """获取角色重要性等级"""
        if self.is_main_character(character_name):
            return "主角"
        
        relationships = self.get_relationships(character_name)
        if len(relationships) >= 5:
            return "重要配角"
        elif len(relationships) >= 2:
            return "配角"
        else:
            return "龙套"
    
    # ==================== 血统和言灵接口 ====================
    
    def get_character_bloodline(self, character_name: str) -> dict:
        """获取角色血统信息"""
        return self.db.get_character_bloodline(character_name)
    
    def get_character_spirit_words(self, character_name: str) -> list:
        """获取角色言灵信息"""
        return self.db.get_character_spirit_words(character_name)
    
    def get_all_spirit_words(self) -> list:
        """获取所有言灵"""
        return self.db.get_all_spirit_words()
    
    def search_spirit_words(self, keyword: str) -> list:
        """搜索言灵"""
        return self.db.search_spirit_words(keyword)
    
    def get_spirit_word_info(self, spirit_word_name: str) -> dict:
        """获取特定言灵信息"""
        all_spirit_words = self.get_all_spirit_words()
        for spirit_word in all_spirit_words:
            if spirit_word['name'] == spirit_word_name:
                return spirit_word
        return None


# 全局API实例
_character_api = None

def get_character_api() -> CharacterAPI:
    """获取全局角色API实例"""
    global _character_api
    if _character_api is None:
        _character_api = CharacterAPI()
    return _character_api

# 便捷函数
def get_character(name: str) -> dict:
    """获取角色档案"""
    return get_character_api().get_character(name)

def get_character_detail(name: str) -> str:
    """获取格式化的角色详细信息"""
    return get_character_api().get_character_detail(name)


def get_relationships(character_name: str) -> dict:
    """获取角色关系"""
    return get_character_api().get_relationships(character_name)

if __name__ == "__main__":
    # 测试API功能
    api = CharacterAPI()
    
    print("=== 测试角色API ===")
    
    # 测试角色查询
    lumingfei = api.get_character("路明非")
    print(f"路明非档案: {lumingfei['name'] if lumingfei else '不存在'}")
    
    # 测试关系查询
    relationships = api.get_relationships("路明非")
    print(f"路明非的关系: {list(relationships.keys())}")
    
    # 测试一致性检查
    test_text = "路明非心想：我们都是小怪兽，都将被正义的奥特曼杀死！"
    consistency = api.check_character_consistency(test_text, "路明非")
    print(f"一致性检查: {consistency['status']} (得分: {consistency['consistency_score']:.2f})")
    
    # 测试对话生成
    dialogue = api.generate_character_dialogue("路明非", "危险情况")
    print(f"生成的对话: {dialogue}")
    
    # 测试统计信息
    stats = api.get_database_info()
    print(f"数据库统计: {stats}")
