#!/usr/bin/env python3
"""
角色信息提取系统 - 从原文中提取角色背景并更新数据库
避免AI硬编码错误的角色信息
"""

import sys
import os
sys.path.append('.')

from database.character_database import CharacterDatabase
import sqlite3
import asyncio
from agents import Agent, Runner
from pydantic import BaseModel
from typing import List, Optional

class CharacterBackground(BaseModel):
    """角色背景信息"""
    name: str
    detailed_background: str
    family_situation: str
    key_relationships: List[str]
    personality_traits: List[str]
    important_facts: List[str]

class CharacterInfoExtractor:
    """角色信息提取器"""
    
    def __init__(self):
        self.agent = Agent(
            name="Character Info Extractor",
            instructions="""你是一个专业的小说角色分析师。
你的任务是从原文中提取角色的详细背景信息，包括：
1. 家庭背景（父母、兄弟姐妹、成长环境）
2. 性格特点（形成原因）
3. 重要关系（与其他角色的关系）
4. 关键事实（不能搞错的重要信息）

请确保提取的信息准确、详细、具体，避免模糊和抽象的描述。
特别注意那些容易被误解或忽略的细节。"""
        )
    
    async def extract_character_info(self, character_name: str, text_content: str) -> CharacterBackground:
        """从文本中提取角色信息"""
        
        prompt = f"""
请从以下原文中提取 **{character_name}** 的详细背景信息：

{text_content[:5000]}  # 限制长度避免超token

请按以下JSON格式输出：
```json
{{
    "name": "{character_name}",
    "detailed_background": "详细的背景故事，包括成长环境、家庭状况等",
    "family_situation": "家庭情况的具体描述",
    "key_relationships": ["与XX的关系描述", "与YY的关系描述"],
    "personality_traits": ["性格特点1", "性格特点2"],
    "important_facts": ["关键事实1（如：父母下落不明）", "关键事实2"]
}}
```

重要提示：
- 如果父母不在身边，明确说明（如：父母下落不明、被XX抚养）
- 如果有特殊家庭结构，详细描述（如：寄人篱下、被叔叔婶婶养大）
- 包含所有会影响角色行为和心理的重要背景
- 避免模糊表述，使用具体的描述
"""
        
        try:
            result = await Runner.run(self.agent, prompt)
            # 解析返回的JSON
            import json
            import re
            
            # 提取JSON部分
            json_match = re.search(r'```json\s*(.*?)\s*```', result.final_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = result.final_output
            
            data = json.loads(json_str)
            return CharacterBackground(**data)
        except Exception as e:
            print(f"提取失败: {e}")
            # 返回空信息
            return CharacterBackground(
                name=character_name,
                detailed_background="",
                family_situation="",
                key_relationships=[],
                personality_traits=[],
                important_facts=[]
            )
    
    def update_character_database(self, character_name: str, background_info: CharacterBackground):
        """更新数据库中的角色信息"""
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "database", "dragon_characters.db")
        
        # 构建完整的背景故事
        full_background = f"""{background_info.detailed_background}

【家庭情况】
{background_info.family_situation}

【重要关系】
{chr(10).join(f"• {rel}" for rel in background_info.key_relationships)}

【关键事实】
{chr(10).join(f"• {fact}" for fact in background_info.important_facts)}"""
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE characters SET background_story = ? WHERE name = ?',
                (full_background, character_name)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ {character_name} 的背景信息已更新")
            else:
                print(f"⚠️ 数据库中不存在角色：{character_name}")

async def main():
    """主函数 - 提取所有主要角色的信息"""
    
    # 读取原文
    original_text_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "《龙族Ⅰ火之晨曦》_readable.txt"
    )
    
    with open(original_text_path, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    extractor = CharacterInfoExtractor()
    
    # 主要角色列表
    main_characters = [
        "路明非",
        "楚子航", 
        "恺撒",
        "诺诺",
        "芬格尔",
        "路鸣泽",
        "昂热",
        "夏弥",
        "陈雯雯"
    ]
    
    print("🔍 开始提取角色信息...")
    print("=" * 60)
    
    for character in main_characters:
        print(f"\n正在提取：{character}")
        background_info = await extractor.extract_character_info(character, original_text)
        
        if background_info.detailed_background:
            print(f"✓ 提取成功")
            print(f"  家庭情况：{background_info.family_situation[:50]}...")
            print(f"  关键事实：{len(background_info.important_facts)}条")
            
            extractor.update_character_database(character, background_info)
        else:
            print(f"✗ 提取失败，跳过")
    
    print("\n" + "=" * 60)
    print("✅ 角色信息提取完成！")

if __name__ == "__main__":
    # 运行异步提取
    try:
        asyncio.run(main())
    except RuntimeError:
        # 如果已经在事件循环中
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(main())

