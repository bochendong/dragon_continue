#!/usr/bin/env python3
"""
龙族续写工具 - 简单使用脚本
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from continuation_writers import ContinuationManager
from database.plot_api import PlotAPI
import asyncio

async def continue_story(chapter_number: int = None):
    """续写指定章节或下一章"""
    
    # 获取当前最新章节
    api = PlotAPI()
    all_chapters = api.get_all_chapters()
    
    if not chapter_number:
        # 自动续写下一章
        max_chapter = max(ch['chapter_number'] for ch in all_chapters) if all_chapters else 0
        chapter_number = max_chapter + 1
    
    print(f"\n🚀 龙族续写工具")
    print("=" * 80)
    print(f"📖 准备续写第{chapter_number}章...")
    print()
    
    # 创建管理器
    manager = ContinuationManager()
    
    # 续写
    chapter = await manager.continue_next_chapter(chapter_number)
    
    # 显示结果
    print(f"\n✨ 续写成功！")
    print("=" * 80)
    print(f"📖 第{chapter.chapter_number}章: {chapter.title}")
    print(f"📝 字数: {chapter.word_count}字")
    print(f"📁 文件已保存到: agents/output/")
    print(f"💾 数据已保存到数据库")
    print()
    
    print("📄 内容预览:")
    print("-" * 60)
    print(chapter.content[:400])
    print("...")
    print()
    
    return chapter

def main():
    """主函数"""
    
    # 解析命令行参数
    chapter_num = None
    if len(sys.argv) > 1:
        try:
            chapter_num = int(sys.argv[1])
        except:
            print("❌ 章节号必须是整数")
            sys.exit(1)
    
    # 运行续写
    asyncio.run(continue_story(chapter_num))

if __name__ == "__main__":
    main()
