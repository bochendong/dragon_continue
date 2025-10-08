#!/usr/bin/env python3
"""
将质量控制系统集成到写作流程
"""

import sys
import os
sys.path.append('.')

def integrate_to_continuation_writers():
    """集成到continuation_writers.py"""
    
    continuation_file = os.path.join(
        os.path.dirname(__file__),
        'continuation_writers.py'
    )
    
    # 读取现有内容
    with open(continuation_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经集成
    if 'WritingQualityController' in content:
        print("✅ 质量控制系统已集成")
        return
    
    # 在imports部分添加
    import_addition = """
# ==================== 质量控制系统 ====================
from writing_style_controller import WritingQualityController
"""
    
    # 找到imports结束的位置
    import_end = content.find('\n# ==================== 数据模型')
    if import_end > 0:
        content = content[:import_end] + import_addition + content[import_end:]
    
    # 在ContinuationManager.__init__中添加
    init_addition = """        
        # 质量控制器
        self.quality_controller = WritingQualityController()
"""
    
    # 找到__init__方法的位置
    init_pattern = "self.writer = StoryWriter(self.plot_api, self.character_api)"
    init_pos = content.find(init_pattern)
    if init_pos > 0:
        insert_pos = content.find('\n', init_pos) + 1
        content = content[:insert_pos] + init_addition + content[insert_pos:]
    
    # 修改continue_next_chapter方法，添加质量控制
    method_modification = """
        # ========== 质量控制 ==========
        print("\\n" + "=" * 80)
        print("🔍 质量控制检查...")
        print("=" * 80)
        
        # 对生成的内容进行质量检查和改进
        improved_content, style_check = await self.quality_controller.check_and_improve(
            chapter_content.content,
            chapter_number,
            max_iterations=2  # 最多改进2轮
        )
        
        # 如果内容被改进，更新chapter_content
        if improved_content != chapter_content.content:
            print("\\n✅ 内容已通过质量控制改进")
            print(f"   风格分数: {style_check.score:.1f}/100")
            
            # 更新content
            old_word_count = chapter_content.word_count
            chapter_content.content = improved_content
            chapter_content.word_count = len(improved_content)
            
            print(f"   字数变化: {old_word_count} → {chapter_content.word_count}")
        else:
            print(f"\\n✅ 内容质量已达标")
            print(f"   风格分数: {style_check.score:.1f}/100")
        
        # 如果质量分数太低，警告
        if style_check.score < 70:
            print("\\n⚠️ 警告：质量分数较低，建议人工审核")
            if style_check.issues:
                print("   主要问题:")
                for issue in style_check.issues[:3]:
                    print(f"   • {issue}")
"""
    
    # 找到保存数据库之前的位置
    save_pattern = "# 保存到数据库"
    save_pos = content.find(save_pattern)
    if save_pos > 0:
        # 在这之前插入质量控制
        content = content[:save_pos] + method_modification + "\\n        " + content[save_pos:]
    
    # 写回文件
    with open(continuation_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 质量控制系统已集成到continuation_writers.py")
    print("\\n集成内容：")
    print("  1. 导入WritingQualityController")
    print("  2. 在ContinuationManager中初始化质量控制器")
    print("  3. 在continue_next_chapter中添加质量检查和改进")
    print("\\n效果：")
    print("  • 每次生成章节后自动进行风格检查")
    print("  • 如果分数<80，自动改进（最多2轮）")
    print("  • 如果分数<70，警告需要人工审核")

def create_quality_check_guide():
    """创建质量检查使用指南"""
    
    guide_content = """# 写作质量控制系统使用指南

## 🎯 系统目标

确保AI生成的内容**持续**符合江南的写作风格，而不是依赖手动修复。

---

## 🏗️ 系统架构

\`\`\`
原文 → 风格学习 → 风格参考库
                          ↓
AI生成内容 → 质量检查 → 评分 → 是否达标？
                ↓              ↓ 否
                是             风格改进 → 重新检查
                ↓                         ↓
            保存发布 ←←←←←←←←←←←←←←←←←←
\`\`\`

---

## 📊 质量检查维度

### 1. 内心OS和吐槽 (20分)
**检查项**：
- [ ] 是否有大量内心独白？
- [ ] 是否有吐槽式的幽默？
- [ ] 是否有"想vs说"的对比？

**好的例子**：
```
他想说你们家的家庭伦理真的好奇怪，可他轻轻地点头，声音里透着
冷硬的威严。
```

**差的例子**：
```
他心情复杂地回答了。
```

### 2. 废柴性格体现 (20分)
**检查项**：
- [ ] 是否有自卑和自嘲？
- [ ] 是否有"路鸣泽的哥哥"类似的梗？
- [ ] 是否有白烂和蔫儿坏？

**好的例子**：
```
作为"路鸣泽的哥哥"他从自己身上找不出什么优点可以自豪。
```

**差的例子**：
```
他觉得自己不够好。
```

### 3. 具体细节描写 (20分)
**检查项**：
- [ ] 是否有具体的品牌、数字、时间？
- [ ] 是否避免了抽象和模糊的描写？
- [ ] 细节是否生动有趣？

**好的例子**：
```
N96手机，水货都卖四千多块，行货超五千了。
```

**差的例子**：
```
一部昂贵的手机。
```

### 4. 对比和反差 (20分)
**检查项**：
- [ ] 是否有强烈的对比场景？
- [ ] 是否体现双重身份的矛盾？
- [ ] 想象与现实的落差？

**好的例子**：
```
路鸣泽获奖照片灿烂，路明非的照片在角落，已经泛黄。
```

**差的例子**：
```
两人的照片都在墙上。
```

### 5. 语言风格 (20分)
**检查项**：
- [ ] 是否口语化、自然？
- [ ] 是否使用网络用语？
- [ ] 是否避免了过于文艺的表达？

**好的例子**：
```
"师兄你这是……清理库存？"
"GG了。"
```

**差的例子**：
```
"您这是在做什么呢？"
"我失败了。"
```

---

## 🔧 使用方法

### 方式1：自动集成（推荐）

**已集成到写作流程**：
\`\`\`bash
cd agents
python3 continue_story.py 27
\`\`\`

流程会自动：
1. 生成章节内容
2. 进行风格检查（评分）
3. 如果<80分，自动改进
4. 最多改进2轮
5. 保存最终版本

### 方式2：手动检查

**检查已生成的章节**：
\`\`\`bash
cd agents
python3 << 'EOF'
import asyncio
from writing_style_controller import WritingQualityController

async def check():
    # 读取章节文件
    with open('output/chapter_27_content_xxx.txt', 'r') as f:
        content = f.read()
    
    # 检查
    controller = WritingQualityController()
    improved, result = await controller.check_and_improve(content, 27)
    
    # 保存
    if improved != content:
        controller.save_improved_chapter(improved, 27, result)

asyncio.run(check())
EOF
\`\`\`

---

## 📈 评分标准

| 分数范围 | 评级 | 处理方式 |
|---------|------|---------|
| 90-100 | 优秀 | 直接发布 |
| 80-89 | 良好 | 直接发布 |
| 70-79 | 合格 | 发布但标记待改进 |
| 60-69 | 不合格 | 自动改进后再检查 |
| <60 | 差 | 需要人工重写 |

---

## 🎓 风格改进策略

### 策略1：增加内心OS

**原文**：
```
他回到家，看见了父母。
```

**改进**：
```
他回到家，看见叔叔婶婶站在门口。他心里咯噔一下，想自己都快
记不清上次见他们是什么时候了。六年？还是七年？反正肯定比路
鸣泽上次钢琴比赛的时间要长。
```

### 策略2：具体化描写

**原文**：
```
芬格尔给了他一个礼物。
```

**改进**：
```
芬格尔从包里掏出一个破破烂烂的塑料袋，"来来来，师兄我也礼貌
性地送你个礼物。"

路明非接过来一看，差点没笑出声。一包已经过期三个月的薯片、
两张盗版的《变形金刚》DVD、还有一串不知道哪个游戏厅淘汰下
来的游戏币。
```

### 策略3：加强对比

**原文**：
```
墙上有照片。
```

**改进**：
```
墙上挂着新的照片，是路鸣泽前段时间参加钢琴比赛获奖的照片。
照片里的路鸣泽笑得很灿烂，捧着奖杯，旁边是骄傲的叔叔婶婶。

路明非的照片？当然也有，在角落里，小学毕业那年的，已经有点
泛黄了。
```

### 策略4：口语化表达

**原文**：
```
"您准备何时返回？"
```

**改进**：
```
"哟，小师弟，啥时候回去啊？"
```

---

## ⚠️ 常见问题

### Q1：为什么有时候改进后分数反而降低？

**A**: AI改进可能引入新问题。系统设置了最多2轮改进，避免过度修改。

**解决**: 
- 调整`max_iterations`参数
- 人工审核分数异常的章节

### Q2：如何处理分数<70的章节？

**A**: 系统会发出警告，建议：
1. 查看具体问题（issues列表）
2. 手动修改关键部分
3. 重新运行质量检查

### Q3：能否自定义评分标准？

**A**: 可以修改`JiangnanStyleChecker`的prompt：
\`\`\`python
# 在writing_style_controller.py中
instructions='''...你的自定义标准...'''
\`\`\`

---

## 📊 质量报告示例

\`\`\`
============================================================
🔍 第26章质量检查报告
============================================================

总分: 87.5/100
评级: ✅ 良好

详细评分:
  • 内心OS和吐槽: 18/20
  • 废柴性格: 17/20
  • 具体细节: 18/20
  • 对比反差: 16/20
  • 语言风格: 18.5/20

优秀示例:
  • "师兄你这是……清理库存？"
  • 路鸣泽获奖照片 vs 路明非泛黄照片
  • 用"夕阳的刻痕"继续戏弄路鸣泽

待改进:
  • 第3段缺少内心OS
  • "心情复杂"过于抽象

✅ 通过质量检查，可以发布
============================================================
\`\`\`

---

## 🚀 持续改进

### 1. 风格参考库扩充
定期从原著中提取优秀片段，更新参考库。

### 2. 评分标准调整
根据实际使用反馈，调整各维度权重。

### 3. 自动学习
未来可以实现：
- 从高分章节中自动学习特征
- 建立个人化的风格模型
- 动态调整改进策略

---

## ✅ 最佳实践

1. **生成前准备**
   - 确保角色数据库信息准确
   - 检查最近章节质量
   - 准备风格参考示例

2. **生成中监控**
   - 关注质量检查日志
   - 记录低分原因
   - 及时调整参数

3. **生成后审核**
   - 人工快速浏览
   - 重点检查低分章节
   - 收集读者反馈

---

🎉 **有了这套系统，就能确保持续生成高质量内容！**
"""
    
    guide_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'WRITING_QUALITY_CONTROL_GUIDE.md'
    )
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✅ 质量检查使用指南已创建: WRITING_QUALITY_CONTROL_GUIDE.md")

if __name__ == "__main__":
    print("🔧 集成写作质量控制系统")
    print("=" * 60)
    print()
    
    # 集成到写作流程
    integrate_to_continuation_writers()
    print()
    
    # 创建使用指南
    create_quality_check_guide()
    print()
    
    print("=" * 60)
    print("✅ 集成完成！")
    print()
    print("现在的工作流程：")
    print("  1. python3 continue_story.py 27")
    print("  2. → AI生成内容")
    print("  3. → 自动质量检查（评分）")
    print("  4. → 如果<80分，自动改进")
    print("  5. → 保存最终版本")
    print()
    print("特点：")
    print("  ✅ 自动化质量控制")
    print("  ✅ 多轮迭代改进")
    print("  ✅ 详细的评分报告")
    print("  ✅ 持续保证质量")

