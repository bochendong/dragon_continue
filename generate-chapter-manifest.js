#!/usr/bin/env node
/**
 * 生成章节清单文件
 * 在构建时运行，创建一个JSON文件列出所有可用章节
 */

const fs = require('fs');
const path = require('path');

const CHAPTERS_DIR = path.join(__dirname, 'chapters_2000_words');
const OUTPUT_FILE = path.join(__dirname, 'public', 'chapter-manifest.json');

console.log('📚 生成章节清单...');

const chapters = [];

try {
  const files = fs.readdirSync(CHAPTERS_DIR);
  
  files.forEach(filename => {
    if (!filename.endsWith('.txt') || filename === '000_文件索引.txt') {
      return;
    }
    
    // 提取章节号
    const match = filename.match(/^(\d+)_(.+)\.txt$/);
    if (!match) {
      return;
    }
    
    const chapterNum = parseInt(match[1]);
    const chapterName = match[2];
    
    // 读取文件获取标题和字数
    const filePath = path.join(CHAPTERS_DIR, filename);
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    
    let title = chapterName === '未知章节' ? `第${chapterNum}章` : chapterName;
    let wordCount = 0;
    
    // 查找标题（在前20行中）
    for (let i = 0; i < Math.min(lines.length, 20); i++) {
      const line = lines[i].trim();
      if (line && 
          !line.includes('《龙族') && 
          !line.includes('作者：') &&
          !line.includes('══') &&
          !line.includes('字数统计') &&
          !line.includes('文件编号')) {
        // 可能是标题
        if (line.length > 2 && line.length < 50 && !title.includes('第') && chapterName === '未知章节') {
          title = line;
        }
        break;
      }
    }
    
    // 统计字数
    const wordCountMatch = content.match(/字数统计[：:]\s*(\d+)/);
    if (wordCountMatch) {
      wordCount = parseInt(wordCountMatch[1]);
    } else {
      // 粗略估计（排除元数据）
      const mainContent = lines.slice(5, lines.length - 60).join('');
      wordCount = mainContent.length;
    }
    
    chapters.push({
      id: chapterNum,
      filename: filename,
      title: title,
      wordCount: wordCount,
      isAIGenerated: chapterNum >= 132
    });
  });
  
  // 按章节号排序
  chapters.sort((a, b) => a.id - b.id);
  
  // 生成清单
  const manifest = {
    totalChapters: chapters.length,
    originalChapters: chapters.filter(c => !c.isAIGenerated).length,
    aiGeneratedChapters: chapters.filter(c => c.isAIGenerated).length,
    generatedAt: new Date().toISOString(),
    chapters: chapters
  };
  
  // 写入文件
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(manifest, null, 2), 'utf-8');
  
  console.log(`✅ 章节清单已生成: ${OUTPUT_FILE}`);
  console.log(`📊 统计:`);
  console.log(`   总章节: ${manifest.totalChapters}`);
  console.log(`   原文: ${manifest.originalChapters}`);
  console.log(`   AI生成: ${manifest.aiGeneratedChapters}`);
  
} catch (error) {
  console.error('❌ 生成清单失败:', error);
  process.exit(1);
}

