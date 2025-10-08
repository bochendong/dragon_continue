#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《龙族Ⅰ火之晨曦》按2000字切分工具
将小说按2000字为单位分割成多个文件，便于阅读和分享
"""

import os
import re
from pathlib import Path

def count_chinese_chars(text):
    """统计中文字符数量"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def split_by_word_count(input_file, output_dir="chapters_2000_words", words_per_file=2000):
    """
    按字数分割小说
    
    Args:
        input_file: 输入文件路径
        output_dir: 输出目录
        words_per_file: 每个文件的字数
    """
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 读取原文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 清理内容，移除分隔线
    lines = content.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        # 跳过分隔线和空行
        if line.startswith('═') or not line:
            continue
        clean_lines.append(line)
    
    # 重新组合内容
    clean_content = '\n'.join(clean_lines)
    
    # 按段落分割
    paragraphs = clean_content.split('\n')
    
    current_content = ""
    current_word_count = 0
    file_count = 0
    chapter_title = ""
    
    # 检测当前章节标题
    def get_chapter_title(text):
        """从文本中提取章节标题"""
        lines = text.split('\n')
        for line in lines[:5]:  # 只检查前5行
            line = line.strip()
            if re.match(r'^楔子：', line):
                return line
            elif re.match(r'^第.*幕', line):
                return line
            elif re.match(r'^\d+\.', line):
                return line
        return "未知章节"
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        paragraph_word_count = count_chinese_chars(paragraph)
        
        # 如果加上这一段会超过字数限制，先保存当前内容
        if current_word_count + paragraph_word_count > words_per_file and current_content:
            file_count += 1
            
            # 生成文件名
            chapter_title = get_chapter_title(current_content)
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', chapter_title)
            safe_title = safe_title.replace('·', '_').replace(' ', '_').replace('——', '_')
            filename = f"{file_count:03d}_{safe_title}.txt"
            
            # 保存文件
            file_path = output_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("《龙族Ⅰ火之晨曦》\n")
                f.write("作者：江南\n\n")
                f.write("═" * 50 + "\n\n")
                
                # 写入内容
                f.write(current_content.strip())
                
                f.write(f"\n\n═" * 50 + "\n")
                f.write(f"字数统计：{current_word_count} 字\n")
                f.write(f"文件编号：{file_count:03d}\n")
            
            print(f"✅ 生成文件 {file_count:03d}: {filename} ({current_word_count} 字)")
            
            # 重置
            current_content = ""
            current_word_count = 0
        
        # 添加新段落
        current_content += paragraph + "\n\n"
        current_word_count += paragraph_word_count
    
    # 保存最后一个文件
    if current_content:
        file_count += 1
        
        chapter_title = get_chapter_title(current_content)
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', chapter_title)
        safe_title = safe_title.replace('·', '_').replace(' ', '_').replace('——', '_')
        filename = f"{file_count:03d}_{safe_title}.txt"
        
        file_path = output_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("《龙族Ⅰ火之晨曦》\n")
            f.write("作者：江南\n\n")
            f.write("═" * 50 + "\n\n")
            
            f.write(current_content.strip())
            
            f.write(f"\n\n═" * 50 + "\n")
            f.write(f"字数统计：{current_word_count} 字\n")
            f.write(f"文件编号：{file_count:03d}\n")
        
        print(f"✅ 生成文件 {file_count:03d}: {filename} ({current_word_count} 字)")
    
    print(f"\n🎉 分割完成！共生成 {file_count} 个文件")
    print(f"📁 输出目录：{output_path.absolute()}")
    
    # 显示文件列表
    print(f"\n📚 生成的文件列表：")
    chapter_files = sorted(output_path.glob("*.txt"))
    total_words = 0
    
    for i, file_path in enumerate(chapter_files, 1):
        file_size = file_path.stat().st_size
        
        # 统计字数
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            word_count = count_chinese_chars(content)
            total_words += word_count
        
        print(f"  {i:2d}. {file_path.name} ({word_count} 字, {file_size:,} bytes)")
    
    print(f"\n📊 总计：{total_words:,} 字")
    print(f"📊 平均每文件：{total_words//file_count if file_count > 0 else 0} 字")
    
    # 生成索引文件
    create_word_index(output_path, chapter_files, total_words)

def create_word_index(output_path, chapter_files, total_words):
    """创建字数索引文件"""
    
    index_file = output_path / "000_文件索引.txt"
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("《龙族Ⅰ火之晨曦》文件索引\n")
        f.write("作者：江南\n\n")
        f.write("═" * 50 + "\n\n")
        f.write("📖 按2000字分割的文件列表：\n\n")
        
        for i, file_path in enumerate(chapter_files, 1):
            # 统计字数
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                word_count = count_chinese_chars(content)
            
            # 提取标题
            filename = file_path.stem
            title = filename.split('_', 1)[1] if '_' in filename else filename
            
            f.write(f"{i:3d}. {title}\n")
            f.write(f"     文件：{file_path.name}\n")
            f.write(f"     字数：{word_count} 字\n\n")
        
        f.write("═" * 50 + "\n")
        f.write(f"📊 总计：{len(chapter_files)} 个文件\n")
        f.write(f"📊 总字数：{total_words:,} 字\n")
        f.write(f"📊 平均每文件：{total_words//len(chapter_files) if len(chapter_files) > 0 else 0} 字\n")

def main():
    """主函数"""
    input_file = "《龙族Ⅰ火之晨曦》_readable.txt"
    
    if not os.path.exists(input_file):
        print(f"❌ 错误：找不到输入文件 {input_file}")
        return
    
    print("🚀 开始按2000字分割《龙族Ⅰ火之晨曦》...")
    print(f"📖 输入文件：{input_file}")
    print(f"📝 每文件字数：2000字")
    
    try:
        split_by_word_count(input_file)
        print("\n🎉 按字数分割完成！")
    except Exception as e:
        print(f"❌ 分割过程中出现错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
