#!/usr/bin/env python3
"""
新角色检测和添加系统
当故事继续时，自动检测新出现的角色并添加到数据库
"""

import sys
import os
sys.path.append('.')

from database.character_database import CharacterDatabase
from database.database_api import CharacterAPI
import asyncio
from agents import Agent, Runner
from pydantic import BaseModel
from typing import List, Optional
import json
import re

class NewCharacter(BaseModel):
    """新角色信息"""
    name: str
    role_type: str  # 主要角色/次要角色/配角
    first_appearance_chapter: int
    brief_description: str
    relationship_to_main_chars: str

class CharacterDetectionResult(BaseModel):
    """角色检测结果"""
    new_characters: List[NewCharacter]
    existing_characters_mentioned: List[str]

class NewCharacterDetector:
    """新角色检测器"""
    
    def __init__(self):
        self.detector_agent = Agent(
            name="New Character Detector",
            instructions="""你是一个小说角色检测系统。
你的任务是从新写的章节中识别出：
1. 新出现的角色（之前没有详细介绍的）
2. 这些角色的基本信息
3. 他们与主要角色的关系

请准确识别，避免把背景中的龙套角色也当成重要角色。"""
        )
        
        self.info_extractor_agent = Agent(
            name="Character Info Extractor",
            instructions="""你是一个角色信息提取专家。
从章节内容中提取新角色的详细信息，包括：
- 详细背景（如果有）
- 家庭情况（如果提到）
- 性格特点
- 与主角的关系
- 在故事中的作用"""
        )
        
        self.char_api = CharacterAPI()
    
    async def detect_new_characters(self, chapter_content: str, chapter_number: int) -> CharacterDetectionResult:
        """检测新章节中的新角色"""
        
        # 获取已有角色列表
        existing_characters = self.char_api.get_character_names()
        
        prompt = f"""
请分析以下第{chapter_number}章的内容，识别新出现的重要角色：

章节内容：
{chapter_content[:3000]}

已知角色列表：
{', '.join(existing_characters)}

请识别：
1. 新出现的角色（不在已知列表中）
2. 判断他们是否重要（主要角色/次要角色/配角）
3. 提取他们的基本信息

只识别有名字、有对话或有描述的角色，忽略纯路人。

请输出JSON格式：
```json
{{
    "new_characters": [
        {{
            "name": "角色名",
            "role_type": "主要角色/次要角色/配角",
            "first_appearance_chapter": {chapter_number},
            "brief_description": "简短描述",
            "relationship_to_main_chars": "与主角的关系"
        }}
    ],
    "existing_characters_mentioned": ["提到的已有角色1", "提到的已有角色2"]
}}
```
"""
        
        try:
            result = await Runner.run(self.detector_agent, prompt)
            
            # 解析JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', result.final_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = result.final_output
            
            data = json.loads(json_str)
            return CharacterDetectionResult(**data)
        except Exception as e:
            print(f"检测失败: {e}")
            return CharacterDetectionResult(
                new_characters=[],
                existing_characters_mentioned=[]
            )
    
    async def extract_detailed_info(self, character_name: str, chapter_content: str) -> dict:
        """提取新角色的详细信息"""
        
        prompt = f"""
请从以下章节中提取 **{character_name}** 的详细信息：

{chapter_content}

请输出JSON格式：
```json
{{
    "detailed_background": "详细背景（基于章节内容）",
    "family_situation": "家庭情况（如果提到）",
    "personality_traits": ["性格1", "性格2"],
    "speech_patterns": ["说话方式1", "说话方式2"],
    "relationships": [
        {{"target": "角色名", "type": "关系类型", "description": "关系描述"}}
    ],
    "key_facts": ["关键事实1", "关键事实2"]
}}
```

如果某些信息章节中没有提到，可以留空数组或空字符串。
"""
        
        try:
            result = await Runner.run(self.info_extractor_agent, prompt)
            
            json_match = re.search(r'```json\s*(.*?)\s*```', result.final_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = result.final_output
            
            return json.loads(json_str)
        except Exception as e:
            print(f"提取详细信息失败: {e}")
            return {}
    
    async def add_new_character_to_db(self, new_char: NewCharacter, chapter_content: str):
        """将新角色添加到数据库"""
        
        print(f"\n📝 添加新角色：{new_char.name}")
        
        # 提取详细信息
        detailed_info = await self.extract_detailed_info(new_char.name, chapter_content)
        
        # 构建完整背景
        background = f"""{new_char.brief_description}

首次出现：第{new_char.first_appearance_chapter}章
角色类型：{new_char.role_type}
与主角关系：{new_char.relationship_to_main_chars}

{detailed_info.get('detailed_background', '')}

【家庭情况】
{detailed_info.get('family_situation', '暂无信息')}

【关键事实】
{chr(10).join(f"• {fact}" for fact in detailed_info.get('key_facts', []))}"""
        
        # 添加到数据库
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "database", "dragon_characters.db")
        db = CharacterDatabase(db_path)
        
        try:
            db.add_character(
                name=new_char.name,
                background_story=background,
                character_arc=f"{new_char.role_type}，在第{new_char.first_appearance_chapter}章登场"
            )
            
            # 添加性格特点
            if detailed_info.get('personality_traits'):
                db.add_personality_traits(
                    db.get_character_id(new_char.name),
                    detailed_info['personality_traits']
                )
            
            # 添加说话方式
            if detailed_info.get('speech_patterns'):
                db.add_speech_patterns(
                    db.get_character_id(new_char.name),
                    detailed_info['speech_patterns']
                )
            
            # 添加关系
            for rel in detailed_info.get('relationships', []):
                try:
                    db.add_relationship(
                        new_char.name,
                        rel['target'],
                        rel['type'],
                        rel['description'],
                        5  # 默认重要性
                    )
                except:
                    pass
            
            print(f"✅ {new_char.name} 已添加到数据库")
            
        except Exception as e:
            print(f"❌ 添加失败: {e}")

async def process_new_chapter(chapter_file: str):
    """处理新生成的章节，检测并添加新角色"""
    
    print(f"🔍 分析章节文件：{chapter_file}")
    print("=" * 60)
    
    # 读取章节内容
    with open(chapter_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取章节号
    import re
    chapter_match = re.search(r'第(\d+)章', content)
    chapter_number = int(chapter_match.group(1)) if chapter_match else 26
    
    # 创建检测器
    detector = NewCharacterDetector()
    
    # 检测新角色
    print(f"\n🎭 检测新角色...")
    result = await detector.detect_new_characters(content, chapter_number)
    
    if result.new_characters:
        print(f"\n发现 {len(result.new_characters)} 个新角色：")
        for new_char in result.new_characters:
            print(f"  • {new_char.name} ({new_char.role_type})")
            
            # 添加到数据库
            await detector.add_new_character_to_db(new_char, content)
    else:
        print("\n未发现新的重要角色")
    
    if result.existing_characters_mentioned:
        print(f"\n提到的已有角色：")
        for char in result.existing_characters_mentioned:
            print(f"  • {char}")
    
    print("\n" + "=" * 60)
    print("✅ 章节分析完成！")

if __name__ == "__main__":
    # 示例：分析最新生成的章节
    latest_chapter = "/Users/dongpochen/Github/dragon_continue/agents/output/chapter_26_content_20241007_151234.txt"
    
    if len(sys.argv) > 1:
        latest_chapter = sys.argv[1]
    
    if os.path.exists(latest_chapter):
        try:
            asyncio.run(process_new_chapter(latest_chapter))
        except RuntimeError:
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(process_new_chapter(latest_chapter))
    else:
        print(f"❌ 文件不存在: {latest_chapter}")
        print("\n用法: python3 new_character_detector.py <章节文件路径>")

