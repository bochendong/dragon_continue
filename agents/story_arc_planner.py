#!/usr/bin/env python3
"""
故事弧线规划系统
提供长期规划和短期规划的双层结构
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.plot_api import PlotAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

# ==================== 数据模型 ====================

class StoryArc(BaseModel):
    """故事弧线模型"""
    arc_name: str  # 弧线名称，如"暑假回国篇"
    arc_number: int  # 弧线编号
    start_chapter: int  # 起始章节
    end_chapter: int  # 结束章节（预估）
    current_chapter: int  # 当前章节
    arc_type: str  # 类型：daily/adventure/crisis/transition
    main_theme: str  # 主题
    key_events: List[str]  # 关键事件列表
    character_focus: List[str]  # 聚焦角色
    setting: str  # 主要场景
    tone: str  # 基调
    story_phase: str  # 故事阶段：beginning/development/climax/ending
    
class ChapterPlan(BaseModel):
    """单章计划模型"""
    chapter_number: int
    position_in_arc: str  # 在弧线中的位置：opening/development/transition/climax/ending
    suggested_content: str  # 建议内容
    pacing: str  # 节奏：slow/medium/fast
    focus: str  # 重点：character/plot/world/emotion

# ==================== 故事弧线规划器 ====================

class StoryArcPlanner:
    """故事弧线规划器 - 负责长期规划"""
    
    def __init__(self):
        self.plot_api = PlotAPI()
        self.arcs = self._initialize_story_arcs()
    
    def _initialize_story_arcs(self) -> List[Dict[str, Any]]:
        """初始化故事弧线规划"""
        
        arcs = [
            # 第一部（已完成）
            {
                "arc_name": "第一学期：龙族觉醒",
                "arc_number": 1,
                "start_chapter": 1,
                "end_chapter": 25,
                "status": "completed",
                "arc_type": "adventure",
                "main_theme": "身份觉醒与第一次冒险",
                "key_events": [
                    "收到卡塞尔学院邀请",
                    "血统测试成为S级",
                    "三峡任务",
                    "对抗龙王诺顿",
                    "与诺诺感情线开始",
                    "路鸣泽契约伏笔"
                ],
                "character_focus": ["路明非", "诺诺", "楚子航", "恺撒"],
                "setting": "卡塞尔学院、三峡",
                "tone": "热血、成长、略带悲凉",
                "story_phase": "completed"
            },
            
            # 第二部：暑假回国篇
            {
                "arc_name": "暑假回国：平凡与不凡的交界",
                "arc_number": 2,
                "start_chapter": 26,
                "end_chapter": 40,  # 预估
                "status": "active",
                "arc_type": "daily-transition",
                "main_theme": "双重身份的矛盾与家庭关系",
                "key_events": [
                    "学期结束，准备回国",
                    "与家人团聚的尴尬",
                    "高中同学聚会",
                    "陈雯雯的新生活",
                    "赵孟华的炫耀",
                    "意外发现国内的龙族线索",
                    "小型事件：保护家人或朋友",
                    "路鸣泽的再次出现",
                    "做出重要选择"
                ],
                "character_focus": ["路明非", "陈雯雯", "赵孟华", "路明非父母", "路鸣泽"],
                "setting": "中国国内、路明非家乡、高中母校",
                "tone": "日常、温情、暗流涌动",
                "story_phase": "beginning",
                "sub_phases": [
                    {
                        "phase": "学期结束与告别",
                        "chapters": [26, 27, 28],
                        "focus": "卡塞尔学院的日常生活和离别"
                    },
                    {
                        "phase": "回国与家庭",
                        "chapters": [29, 30, 31, 32],
                        "focus": "与家人的相处，双重身份的矛盾"
                    },
                    {
                        "phase": "同学聚会篇",
                        "chapters": [33, 34, 35],
                        "focus": "面对陈雯雯和高中同学，心境对比"
                    },
                    {
                        "phase": "危机萌芽",
                        "chapters": [36, 37, 38],
                        "focus": "发现国内的龙族线索，小型事件"
                    },
                    {
                        "phase": "抉择与转折",
                        "chapters": [39, 40],
                        "focus": "路鸣泽出现，做出选择，准备返校"
                    }
                ]
            },
            
            # 第三部：第二学期（预规划）
            {
                "arc_name": "第二学期：更深的阴谋",
                "arc_number": 3,
                "start_chapter": 41,
                "end_chapter": 65,  # 预估
                "status": "planned",
                "arc_type": "adventure",
                "main_theme": "揭开更多真相，面对更强敌人",
                "key_events": [
                    "返回学院",
                    "新的任务",
                    "与夏弥的关系发展",
                    "龙王身份的部分揭露",
                    "更危险的对抗"
                ],
                "character_focus": ["路明非", "夏弥", "楚子航", "恺撒"],
                "setting": "卡塞尔学院、新任务地点",
                "tone": "紧张、悬疑、情感纠葛",
                "story_phase": "planned"
            }
        ]
        
        return arcs
    
    def get_current_arc(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """获取当前章节所在的故事弧线"""
        for arc in self.arcs:
            if arc["start_chapter"] <= chapter_number <= arc["end_chapter"]:
                return arc
        return None
    
    def get_current_sub_phase(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """获取当前章节所在的子阶段"""
        arc = self.get_current_arc(chapter_number)
        if not arc or "sub_phases" not in arc:
            return None
        
        for phase in arc["sub_phases"]:
            if chapter_number in phase["chapters"]:
                return phase
        return None
    
    def get_chapter_position(self, chapter_number: int) -> Dict[str, Any]:
        """分析章节在故事中的位置"""
        arc = self.get_current_arc(chapter_number)
        if not arc:
            return {"error": "无法确定章节所在弧线"}
        
        sub_phase = self.get_current_sub_phase(chapter_number)
        
        # 计算在弧线中的进度
        progress = (chapter_number - arc["start_chapter"]) / (arc["end_chapter"] - arc["start_chapter"])
        
        # 确定在弧线中的位置
        if progress < 0.2:
            position = "opening"
            pacing = "slow"
        elif progress < 0.5:
            position = "development"
            pacing = "medium"
        elif progress < 0.8:
            position = "climax_building"
            pacing = "medium-fast"
        else:
            position = "climax_or_ending"
            pacing = "fast"
        
        return {
            "arc": arc,
            "sub_phase": sub_phase,
            "progress": progress,
            "position": position,
            "pacing": pacing,
            "chapters_remaining_in_arc": arc["end_chapter"] - chapter_number
        }
    
    def generate_long_term_guidance(self, chapter_number: int) -> str:
        """生成长期规划指导"""
        position = self.get_chapter_position(chapter_number)
        
        if "error" in position:
            return position["error"]
        
        arc = position["arc"]
        sub_phase = position["sub_phase"]
        
        guidance = []
        guidance.append("=" * 60)
        guidance.append("📚 长期故事规划")
        guidance.append("=" * 60)
        
        # 当前弧线信息
        guidance.append(f"\n🎬 当前故事弧线: {arc['arc_name']} (第{arc['arc_number']}部)")
        guidance.append(f"   章节范围: 第{arc['start_chapter']}-{arc['end_chapter']}章")
        guidance.append(f"   当前进度: {position['progress']*100:.1f}% ({chapter_number}/{arc['end_chapter']})")
        guidance.append(f"   弧线类型: {arc['arc_type']}")
        guidance.append(f"   主题: {arc['main_theme']}")
        guidance.append(f"   基调: {arc['tone']}")
        
        # 子阶段信息
        if sub_phase:
            guidance.append(f"\n📍 当前子阶段: {sub_phase['phase']}")
            guidance.append(f"   章节范围: 第{sub_phase['chapters'][0]}-{sub_phase['chapters'][-1]}章")
            guidance.append(f"   重点: {sub_phase['focus']}")
        
        # 关键事件
        guidance.append(f"\n🎯 本弧线关键事件:")
        for i, event in enumerate(arc['key_events'], 1):
            guidance.append(f"   {i}. {event}")
        
        # 主要角色
        guidance.append(f"\n👥 聚焦角色: {', '.join(arc['character_focus'])}")
        guidance.append(f"🏛️ 主要场景: {arc['setting']}")
        
        # 节奏建议
        guidance.append(f"\n⏱️ 建议节奏: {position['pacing']}")
        guidance.append(f"📍 在弧线中的位置: {position['position']}")
        
        # 接下来应该写什么
        guidance.append(f"\n💡 接下来应该:")
        if position['position'] == 'opening':
            guidance.append("   - 建立新环境和新冲突")
            guidance.append("   - 引入新角色或回归老角色")
            guidance.append("   - 铺垫后续情节")
        elif position['position'] == 'development':
            guidance.append("   - 推进主要情节线")
            guidance.append("   - 深化角色关系")
            guidance.append("   - 埋下伏笔")
        elif position['position'] == 'climax_building':
            guidance.append("   - 冲突升级")
            guidance.append("   - 增加紧张感")
            guidance.append("   - 准备高潮")
        else:
            guidance.append("   - 推向高潮或结局")
            guidance.append("   - 解决主要冲突")
            guidance.append("   - 为下一弧线铺垫")
        
        # 剩余章节提醒
        remaining = position['chapters_remaining_in_arc']
        guidance.append(f"\n⚠️ 本弧线还剩约 {remaining} 章，请注意:")
        if remaining > 10:
            guidance.append("   - 可以从容展开情节")
            guidance.append("   - 注意日常与情节的平衡")
        elif remaining > 5:
            guidance.append("   - 逐步推进到关键事件")
            guidance.append("   - 开始收束部分支线")
        else:
            guidance.append("   - 加快节奏，推向本弧线高潮")
            guidance.append("   - 准备弧线结束和过渡")
        
        # 下一弧线预告
        next_arc = self._get_next_arc(arc['arc_number'])
        if next_arc:
            guidance.append(f"\n🔮 下一弧线预告: {next_arc['arc_name']}")
            guidance.append(f"   将进入: {next_arc['setting']}")
            guidance.append(f"   主题: {next_arc['main_theme']}")
        
        guidance.append("\n" + "=" * 60)
        
        return "\n".join(guidance)
    
    def _get_next_arc(self, current_arc_number: int) -> Optional[Dict[str, Any]]:
        """获取下一个故事弧线"""
        for arc in self.arcs:
            if arc['arc_number'] == current_arc_number + 1:
                return arc
        return None
    
    def suggest_next_chapter_direction(self, chapter_number: int) -> Dict[str, Any]:
        """建议下一章的方向"""
        position = self.get_chapter_position(chapter_number)
        
        if "error" in position:
            return {"error": position["error"]}
        
        arc = position["arc"]
        sub_phase = position["sub_phase"]
        
        # 基于当前位置给出具体建议
        suggestion = {
            "chapter_number": chapter_number,
            "arc_context": f"{arc['arc_name']} - {sub_phase['phase'] if sub_phase else '进行中'}",
            "pacing": position["pacing"],
            "focus_suggestion": sub_phase["focus"] if sub_phase else arc["main_theme"],
            "tone": arc["tone"],
            "key_characters": arc["character_focus"],
            "setting": arc["setting"],
        }
        
        # 具体内容建议
        if chapter_number == 26:
            suggestion["content_suggestion"] = """
第26章建议：放暑假前的日常

⚠️ 重要基调：这只是**大一暑假回国**，不是生离死别！
- 轻松日常的基调，不要太文艺感伤
- 秋季还会回来上学，只是放假2-3个月

重点内容：
1. 学期结束的轻松日常（考试结束、收拾行李）
2. 路明非决定回国（或收到家里通知）
3. 与室友芬格尔的搞怪互动
4. 与诺诺的简单告别（暗示感情线，但别太沉重）
5. 对回国的复杂心情（想家但也有点怂）

人物性格把握：
【路明非】
- ✅ 废柴属性：自嘲、吐槽、嘴贫
- ✅ 网络用语：多用"GG了"、"秀逗了"、"NB"等
- ✅ 内心OS：大量内心吐槽和碎碎念
- ✅ 怂但温柔：表面怂，但关键时刻有温情
- ❌ 避免：太文艺、太感伤、太深沉

【芬格尔】
- ✅ 无厘头：说话不按套路，很搞怪
- ✅ 损友：会损路明非，但也关心他
- ✅ 搞怪礼物：送的礼物要奇葩（过期零食、盗版碟、游戏币等）
- ❌ 避免：正经的礼物（龙族徽章太正经了！）

注意事项：
- 节奏轻松，像普通大学生放假
- 多一些搞笑和吐槽，少一些伤感
- 突出双重身份的矛盾（屠龙英雄 vs 回家见爸妈的怂包）
- 埋下回国后的伏笔（家人、高中同学、陈雯雯）
- 路鸣泽的契约阴影可以暗示，但不要太重
"""
        elif chapter_number == 27:
            suggestion["content_suggestion"] = """
第27章建议：离别与启程

重点内容：
1. 与室友芬格尔告别
2. 与楚子航、恺撒等人告别
3. 诺诺送别的场景（深化感情线）
4. 机场或车站的场景
5. 回国途中的心理活动

注意事项：
- 展现路明非对学院的不舍
- 与朋友们的感情深化
- 对即将面对的"普通生活"的忐忑
"""
        elif 29 <= chapter_number <= 32:
            suggestion["content_suggestion"] = f"""
第{chapter_number}章建议：回国与家庭篇

重点内容：
1. 与父母/叔叔婶婶的相处
2. 双重身份的矛盾（不能说的秘密）
3. 家庭琐事中的格格不入
4. 对"普通生活"的重新认识
5. 暗示龙族世界并未远离

注意事项：
- 江南式的日常描写
- 亲情的温暖与隔阂并存
- 幽默与悲凉的基调
"""
        elif 33 <= chapter_number <= 35:
            suggestion["content_suggestion"] = f"""
第{chapter_number}章建议：同学聚会篇

重点内容：
1. 高中同学聚会
2. 见到陈雯雯（已有男友？）
3. 赵孟华的炫耀
4. 路明非的心境对比（已经不同了）
5. 对青春与成长的感慨

注意事项：
- 展现路明非的成长
- 对比卡塞尔学院与高中生活
- 陈雯雯不再是唯一的光
- 诺诺的身影时常浮现
"""
        
        return suggestion
    
    def export_arc_plan(self, filepath: str = None):
        """导出故事弧线规划"""
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "story_arc_plan.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.arcs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 故事弧线规划已导出: {filepath}")

# ==================== 测试 ====================

def test_story_arc_planner():
    """测试故事弧线规划器"""
    planner = StoryArcPlanner()
    
    print("\n" + "=" * 80)
    print("🎬 故事弧线规划系统测试")
    print("=" * 80)
    
    # 测试第26章
    print("\n📖 测试第26章的规划:")
    print("-" * 80)
    guidance = planner.generate_long_term_guidance(26)
    print(guidance)
    
    print("\n💡 第26章具体建议:")
    print("-" * 80)
    suggestion = planner.suggest_next_chapter_direction(26)
    print(f"弧线: {suggestion['arc_context']}")
    print(f"节奏: {suggestion['pacing']}")
    print(f"重点: {suggestion['focus_suggestion']}")
    print(f"基调: {suggestion['tone']}")
    print(f"场景: {suggestion['setting']}")
    print(suggestion['content_suggestion'])
    
    # 导出规划
    planner.export_arc_plan()
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_story_arc_planner()

