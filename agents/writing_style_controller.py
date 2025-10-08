#!/usr/bin/env python3
"""
写作风格质量控制系统
确保AI生成的内容符合江南的写作风格
"""

import sys
import os
sys.path.append('.')

from agents import Agent, Runner
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import re
import asyncio

class StyleCheckResult(BaseModel):
    """风格检查结果"""
    score: float  # 0-100分
    passed: bool
    issues: List[str]
    suggestions: List[str]
    details: Dict[str, any]

class JiangnanStyleChecker:
    """江南风格检查器"""
    
    def __init__(self):
        # 创建风格检查Agent
        self.checker_agent = Agent(
            name="Jiangnan Style Checker",
            instructions="""你是一个专业的小说风格分析师，专门分析江南的写作风格。

江南写作风格的核心特征：

1. **大量内心OS和吐槽**
   - "真烦真烦真烦！"
   - "见鬼！"
   - "他想...但他说的是..."（言不由衷）

2. **废柴、白烂、蔫儿坏的性格**
   - 自嘲式的幽默
   - 看似无害的小恶作剧
   - 对自己没什么期待的态度

3. **具体的细节描写**
   - 品牌名称（N96、万宝龙、长城干红）
   - 具体数字（36000美元、6.83汇率）
   - 时间、地点、物品的精确描写

4. **强烈的对比和反差**
   - 路明非 vs 路鸣泽
   - S级混血种 vs 废柴高中生
   - 想象 vs 现实

5. **日常化的语言和网络用语**
   - "GG了"、"秀逗了"
   - 口语化表达
   - 不使用过于文艺的词汇

6. **细腻的情感描写但不抒情**
   - 通过具体场景和细节传达情感
   - 避免直接的情感表达
   - "他想说...但他什么都没说"

请仔细分析提供的文本，评估其是否符合江南风格。"""
        )
    
    async def check_style(self, content: str, chapter_number: int) -> StyleCheckResult:
        """检查写作风格"""
        
        prompt = f"""
请分析以下第{chapter_number}章的内容，评估其是否符合江南的写作风格：

{content[:3000]}  # 取前3000字分析

请从以下维度评分（每项0-20分）：

1. **内心OS和吐槽** (0-20分)
   - 是否有大量内心独白？
   - 是否有吐槽式的幽默？
   - 是否有"言不由衷"的对比？

2. **废柴性格体现** (0-20分)
   - 是否体现路明非的自卑和自嘲？
   - 是否有"路鸣泽的哥哥"类似的梗？
   - 是否有白烂和蔫儿坏的表现？

3. **具体细节描写** (0-20分)
   - 是否有具体的品牌、数字、时间？
   - 是否避免了抽象和模糊的描写？
   - 细节是否生动有趣？

4. **对比和反差** (0-20分)
   - 是否有强烈的对比场景？
   - 是否体现双重身份的矛盾？
   - 想象与现实的落差？

5. **语言风格** (0-20分)
   - 是否口语化、自然？
   - 是否使用网络用语？
   - 是否避免了过于文艺的表达？

请输出JSON格式：
```json
{{
    "total_score": 85,
    "dimension_scores": {{
        "inner_monologue": 18,
        "loser_personality": 16,
        "concrete_details": 17,
        "contrast": 15,
        "language_style": 19
    }},
    "passed": true,
    "issues": [
        "问题1：缺少具体的品牌名称",
        "问题2：吐槽不够频繁"
    ],
    "suggestions": [
        "建议1：增加路明非的内心OS",
        "建议2：添加更多具体细节"
    ],
    "good_examples": [
        "示例1：\"师兄你这是……清理库存？\"",
        "示例2：路鸣泽获奖照片 vs 路明非泛黄照片"
    ],
    "style_issues": [
        "过于抒情：\"心情如同...\"",
        "过于文艺：\"月光如水...\"",
        "缺少吐槽：对话太正经"
    ]
}}
```

评分标准：
- 90-100分：完美符合江南风格
- 80-89分：很好，小问题
- 70-79分：基本符合，有明显问题
- 60-69分：风格偏离，需要大改
- <60分：完全不符合，重写
"""
        
        try:
            result = await Runner.run(self.checker_agent, prompt)
            
            # 解析JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', result.final_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = result.final_output
            
            data = json.loads(json_str)
            
            return StyleCheckResult(
                score=data['total_score'],
                passed=data['passed'],
                issues=data['issues'],
                suggestions=data['suggestions'],
                details=data
            )
        except Exception as e:
            print(f"风格检查失败: {e}")
            return StyleCheckResult(
                score=0,
                passed=False,
                issues=[f"检查失败: {str(e)}"],
                suggestions=["请手动检查"],
                details={}
            )

class StyleImprover:
    """风格改进器"""
    
    def __init__(self):
        self.improver_agent = Agent(
            name="Jiangnan Style Improver",
            instructions="""你是一个专业的小说改写专家，擅长将内容改写为江南的风格。

改写原则：
1. 保持情节不变
2. 增加内心OS和吐槽
3. 用具体细节替换抽象描写
4. 增加对比和反差
5. 使用口语化和网络用语
6. 保持废柴和自嘲的基调

示例对比：

❌ 原文："他心情复杂地回到家"
✅ 改写："他回到家，心里空落落的，又有点说不出的紧张。他想自己就是贱，被叔叔婶婶养了十几年，现在回来还紧张个屁。"

❌ 原文："礼物很珍贵"
✅ 改写："一包过期三个月的薯片、两张盗版DVD、还有一串游戏币。师兄你这是……清理库存？"

❌ 原文："他想起了父母"
✅ 改写："他想起那对六年多没见面、只会定期通过花旗银行寄钱的爸妈。他们现在在哪里？在干什么？会不会想起还有他这么个儿子？他不知道，也不敢问。"
"""
        )
    
    async def improve_style(
        self, 
        content: str, 
        check_result: StyleCheckResult
    ) -> str:
        """根据检查结果改进风格"""
        
        if check_result.score >= 85:
            print("✅ 风格已经很好，无需改进")
            return content
        
        prompt = f"""
请将以下内容改写为更符合江南风格的版本。

原文：
{content}

风格检查报告：
- 总分：{check_result.score}/100
- 主要问题：
{chr(10).join(f"  • {issue}" for issue in check_result.issues)}

改进建议：
{chr(10).join(f"  • {suggestion}" for suggestion in check_result.suggestions)}

风格问题：
{chr(10).join(f"  • {issue}" for issue in check_result.details.get('style_issues', []))}

请重写，要求：
1. 保持情节和对话完全不变
2. 增加内心OS和吐槽
3. 替换抽象描写为具体细节
4. 加强对比和反差
5. 使用更口语化的表达
6. 体现废柴和自嘲的性格

直接输出改写后的文本，不要加任何说明。
"""
        
        try:
            result = await Runner.run(self.improver_agent, prompt)
            improved_content = result.final_output
            
            # 清理可能的markdown标记
            improved_content = re.sub(r'```.*?\n', '', improved_content)
            improved_content = re.sub(r'```', '', improved_content)
            
            return improved_content.strip()
        except Exception as e:
            print(f"风格改进失败: {e}")
            return content

class WritingQualityController:
    """写作质量控制器"""
    
    def __init__(self):
        self.style_checker = JiangnanStyleChecker()
        self.style_improver = StyleImprover()
        
        # 风格参考库（从原著中提取的优秀片段）
        self.style_references = self._load_style_references()
    
    def _load_style_references(self) -> List[Dict[str, str]]:
        """加载风格参考库"""
        return [
            {
                "category": "内心OS",
                "example": "真烦真烦真烦！哥哥？这里没有！",
                "feature": "重复强调+吐槽"
            },
            {
                "category": "废柴自嘲",
                "example": "作为'路鸣泽的哥哥'他从自己身上找不出什么优点可以自豪",
                "feature": "自我定位+对比"
            },
            {
                "category": "具体细节",
                "example": "N96手机，水货都卖四千多块，行货超五千了",
                "feature": "品牌+价格+对比"
            },
            {
                "category": "反差幽默",
                "example": "见鬼！这是什么'我们是相亲相爱的食人族一家'的话剧桥段么？",
                "feature": "内心吐槽+荒谬对比"
            },
            {
                "category": "言不由衷",
                "example": "他想说...可他轻轻地点头，声音里透着冷硬的威严",
                "feature": "想vs说的对比"
            }
        ]
    
    async def check_and_improve(
        self, 
        content: str, 
        chapter_number: int,
        max_iterations: int = 3
    ) -> tuple[str, StyleCheckResult]:
        """检查并改进内容，直到达到质量标准"""
        
        print(f"\n{'='*60}")
        print(f"🔍 开始质量检查：第{chapter_number}章")
        print(f"{'='*60}\n")
        
        current_content = content
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n📊 第{iteration}轮检查...")
            
            # 风格检查
            check_result = await self.style_checker.check_style(
                current_content, 
                chapter_number
            )
            
            print(f"  总分: {check_result.score:.1f}/100")
            print(f"  评级: {'✅ 通过' if check_result.passed else '❌ 不通过'}")
            
            if check_result.details:
                scores = check_result.details.get('dimension_scores', {})
                print(f"  详细评分:")
                print(f"    • 内心OS: {scores.get('inner_monologue', 0)}/20")
                print(f"    • 废柴性格: {scores.get('loser_personality', 0)}/20")
                print(f"    • 具体细节: {scores.get('concrete_details', 0)}/20")
                print(f"    • 对比反差: {scores.get('contrast', 0)}/20")
                print(f"    • 语言风格: {scores.get('language_style', 0)}/20")
            
            if check_result.issues:
                print(f"\n  ⚠️ 主要问题:")
                for issue in check_result.issues[:3]:
                    print(f"    • {issue}")
            
            # 如果达标，返回
            if check_result.score >= 80:
                print(f"\n✅ 质量达标！(第{iteration}轮)")
                return current_content, check_result
            
            # 否则进行改进
            if iteration < max_iterations:
                print(f"\n🔧 进行风格改进...")
                current_content = await self.style_improver.improve_style(
                    current_content,
                    check_result
                )
                print(f"  ✓ 改进完成，准备下一轮检查")
        
        # 达到最大迭代次数
        print(f"\n⚠️ 已达最大迭代次数({max_iterations})，当前分数: {check_result.score:.1f}")
        
        if check_result.score >= 70:
            print("  质量基本可接受")
        else:
            print("  ❌ 质量不达标，建议人工审核")
        
        return current_content, check_result
    
    def save_improved_chapter(
        self, 
        content: str, 
        chapter_number: int,
        check_result: StyleCheckResult
    ):
        """保存改进后的章节"""
        
        from datetime import datetime
        import sqlite3
        
        # 更新数据库
        current_dir = os.path.dirname(os.path.abspath(__file__))
        plot_db = os.path.join(current_dir, 'database', 'plot_outline.db')
        
        with sqlite3.connect(plot_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE chapters 
                SET notes = ?,
                    summary = ?
                WHERE chapter_number = ?
            ''', (
                content,
                content[:500] + "...",
                chapter_number
            ))
            conn.commit()
        
        # 保存到文件
        output_dir = os.path.join(current_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chapter_{chapter_number}_improved_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"《龙族Ⅰ火之晨曦》第{chapter_number}章\n")
            f.write("=" * 60 + "\n")
            f.write(f"质量分数: {check_result.score:.1f}/100\n")
            f.write(f"生成时间: {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(content)
        
        print(f"\n💾 已保存改进版本: {filename}")

async def test_quality_control():
    """测试质量控制系统"""
    
    # 测试内容（模拟AI生成的内容）
    test_content = """第26章 归途

路明非坐在机场，心情复杂。他即将回到中国，回到那个家。

芬格尔递给他一个礼物，是一个龙族徽章。路明非很感动。

飞机起飞了，路明非看着窗外，想起了很多事情。

到了中国，父母来接他。他们拥抱在一起，很温馨。

回到家，路明非给母亲打了电话，聊了很久。

晚上，路明非躺在床上，思考着未来。

他知道，生活还要继续。"""
    
    controller = WritingQualityController()
    
    # 检查并改进
    improved_content, check_result = await controller.check_and_improve(
        test_content,
        chapter_number=26
    )
    
    print(f"\n{'='*60}")
    print("✅ 质量控制完成")
    print(f"{'='*60}")
    print(f"\n最终分数: {check_result.score:.1f}/100")
    print(f"\n改进后内容预览:")
    print("-" * 60)
    print(improved_content[:500])
    print("...")

if __name__ == "__main__":
    # 测试
    try:
        asyncio.run(test_quality_control())
    except RuntimeError:
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(test_quality_control())

