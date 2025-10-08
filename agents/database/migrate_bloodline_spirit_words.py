"""
血统和言灵数据迁移脚本
添加角色血统等级和言灵信息到数据库
"""

import sys
import os
import sqlite3
sys.path.append(os.path.dirname(__file__))

from character_database import CharacterDatabase

def migrate_bloodline_and_spirit_words():
    """迁移血统和言灵数据"""
    
    # 创建数据库实例，使用database目录下的数据库
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "dragon_characters.db")
    db = CharacterDatabase(db_path)
    
    print("正在迁移血统和言灵数据...")
    
    # 添加言灵库
    print("正在添加言灵库...")
    
    # 青铜与火之王系列言灵
    db.add_spirit_word("君焰", 89, "青铜与火之王", 
                      "产生极高温度的火焰，能够熔化金属",
                      "产生数千度高温的火焰，范围可达数十米",
                      "需要大量体力，过度使用会导致血统暴走",
                      "高危")
    
    db.add_spirit_word("烛龙", 90, "青铜与火之王",
                      "召唤烛龙虚影，释放毁灭性的龙炎",
                      "召唤巨大的龙形火焰，威力足以摧毁建筑",
                      "需要极高血统纯度，使用后极度虚弱",
                      "高危")
    
    db.add_spirit_word("炽日", 91, "青铜与火之王",
                      "在掌心凝聚高温火球",
                      "产生小型但极高温度的火球",
                      "需要精确控制，否则会伤及自身",
                      "高危")
    
    # 大地与山之王系列言灵
    db.add_spirit_word("王权", 92, "大地与山之王",
                      "控制重力，使目标承受巨大压力",
                      "增加目标周围的重力，使其无法移动",
                      "对使用者也有反作用力",
                      "高危")
    
    db.add_spirit_word("青铜御座", 93, "大地与山之王",
                      "强化身体，获得超人的力量和防御",
                      "身体变得如青铜般坚硬，力量大幅提升",
                      "持续时间有限，过度使用会损害身体",
                      "高危")
    
    # 天空与风之王系列言灵
    db.add_spirit_word("风王之瞳", 94, "天空与风之王",
                      "控制周围的风元素",
                      "可以产生强风、龙卷风等风系攻击",
                      "需要良好的空气流通环境",
                      "高危")
    
    db.add_spirit_word("无尘之地", 95, "天空与风之王",
                      "创造无尘的纯净空间",
                      "在周围创造真空环境，阻挡一切物质",
                      "消耗巨大，无法维持长时间",
                      "高危")
    
    # 海洋与水之王系列言灵
    db.add_spirit_word("深潜者", 96, "海洋与水之王",
                      "控制水流，在水中有极强优势",
                      "可以控制水流方向、速度，在水中行动自如",
                      "在水中效果最佳，陆地效果减弱",
                      "高危")
    
    db.add_spirit_word("归墟", 97, "海洋与水之王",
                      "创造巨大的漩涡",
                      "产生强大的水流漩涡，可以吞噬一切",
                      "需要大量水源，在干燥环境无效",
                      "高危")
    
    # 一些常见的低序列言灵
    db.add_spirit_word("蛇", 16, "未知龙王",
                      "增强感知能力，可以感知周围的生命体",
                      "扩大感知范围，发现隐藏的敌人",
                      "感知范围有限，容易被干扰",
                      "普通")
    
    db.add_spirit_word("镰鼬", 59, "天空与风之王",
                      "增强听觉，可以听到极细微的声音",
                      "听力大幅增强，可以听到很远的对话",
                      "在嘈杂环境中效果会受影响",
                      "普通")
    
    db.add_spirit_word("言灵·镜瞳", 5, "未知龙王",
                      "增强视觉，可以看清极远距离",
                      "视力大幅增强，可以看清远距离的细节",
                      "强光环境可能造成眼睛不适",
                      "普通")
    
    # 添加角色血统信息
    print("正在添加角色血统信息...")
    # 先删除旧的血统信息
    with sqlite3.connect(db.db_path) as conn:
        conn.execute("DELETE FROM character_bloodline")
        conn.commit()
    
    # 路明非血统
    db.add_bloodline_info("路明非", "S级", 50, "黑王血统",
                         "拥有极高的龙族血统纯度，但被封印，平时表现普通")
    
    # 路鸣泽血统（第一部设定：身份未公开）
    db.add_bloodline_info("路鸣泽", "S级", 90, "未知龙王血统",
                         "极高纯度血统，但真实身份在第一部中尚未揭示")
    
    # 凯撒血统
    db.add_bloodline_info("凯撒", "A级", 75, "未知龙王血统",
                         "来自加图索家族的高纯度血统，具有强大的战斗能力")
    
    # 诺诺血统
    db.add_bloodline_info("诺诺", "A级", 80, "未知龙王血统",
                         "神秘的高纯度血统，拥有特殊的感知能力")
    
    # 楚子航血统
    db.add_bloodline_info("楚子航", "A级", 70, "大地与山之王血统",
                         "高纯度血统，在剑道方面有特殊天赋")
    
    # 陈雯雯血统
    db.add_bloodline_info("陈雯雯", "普通人", 0, "无龙族血统",
                         "完全的人类，没有任何龙族血统")
    
    # 夏弥血统（第一部设定：身份未公开）
    db.add_bloodline_info("夏弥", "A级", 85, "未知龙王血统",
                         "高纯度血统，但真实身份在第一部中尚未揭示")
    
    # 为角色添加言灵
    print("正在为角色添加言灵...")
    
    # 路明非的言灵
    db.add_character_spirit_word("路明非", "蛇", 3, "情绪激动时", "主要感知言灵")
    db.add_character_spirit_word("路明非", "言灵·镜瞳", 2, "专注时", "辅助视觉言灵")
    
    # 路鸣泽的言灵
    db.add_character_spirit_word("路鸣泽", "君焰", 5, "愤怒时", "主要攻击言灵")
    db.add_character_spirit_word("路鸣泽", "烛龙", 4, "极度愤怒时", "终极言灵")
    db.add_character_spirit_word("路鸣泽", "炽日", 5, "战斗时", "精确控制言灵")
    
    # 凯撒的言灵
    db.add_character_spirit_word("凯撒", "镰鼬", 4, "需要时", "感知类言灵")
    db.add_character_spirit_word("凯撒", "青铜御座", 3, "战斗时", "强化身体言灵")
    
    # 诺诺的言灵
    db.add_character_spirit_word("诺诺", "蛇", 4, "需要时", "主要感知言灵")
    db.add_character_spirit_word("诺诺", "言灵·镜瞳", 3, "专注时", "视觉增强言灵")
    
    # 楚子航的言灵
    db.add_character_spirit_word("楚子航", "王权", 4, "战斗时", "主要攻击言灵")
    db.add_character_spirit_word("楚子航", "青铜御座", 3, "需要强化时", "身体强化言灵")
    
    # 夏弥的言灵（第一部设定：隐藏真实实力）
    db.add_character_spirit_word("夏弥", "蛇", 3, "探测时", "辅助探测言灵")
    db.add_character_spirit_word("夏弥", "言灵·镜瞳", 2, "观察时", "观察分析言灵")
    
    # 注意：陈雯雯是普通人，没有言灵
    
    print("血统和言灵数据迁移完成！")
    
    # 显示统计信息
    stats = db.get_database_stats()
    print(f"\n数据库统计信息:")
    print(f"- 角色数量: {stats['character_count']}")
    print(f"- 血统记录: {stats['bloodline_count']}")
    print(f"- 言灵数量: {stats['spirit_word_count']}")
    print(f"- 角色言灵关联: {stats['character_spirit_word_count']}")
    
    return db

def test_bloodline_and_spirit_words():
    """测试血统和言灵功能"""
    print("\n=== 测试血统和言灵功能 ===")
    
    # 使用与迁移函数相同的数据库路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "dragon_characters.db")
    db = CharacterDatabase(db_path)
    
    # 测试角色血统查询
    print("\n🧬 角色血统信息:")
    characters = ["路明非", "路鸣泽", "凯撒", "诺诺", "楚子航"]
    for name in characters:
        bloodline = db.get_character_bloodline(name)
        if bloodline:
            print(f"{name}: {bloodline['bloodline_level']} ({bloodline['bloodline_percentage']}%)")
        else:
            print(f"{name}: 无血统记录")
    
    # 测试角色言灵查询
    print("\n⚡ 角色言灵信息:")
    for name in characters:
        spirit_words = db.get_character_spirit_words(name)
        if spirit_words:
            print(f"\n{name}:")
            for sw in spirit_words:
                print(f"  - {sw['name']} (序列{sw['sequence_number']}, 等级{sw['mastery_level']})")
        else:
            print(f"{name}: 无言灵记录")
    
    # 测试言灵库查询
    print("\n📚 言灵库统计:")
    all_spirit_words = db.get_all_spirit_words()
    print(f"总言灵数量: {len(all_spirit_words)}")
    
    # 按龙王分类
    dragon_counts = {}
    for sw in all_spirit_words:
        dragon = sw['dragon_name']
        dragon_counts[dragon] = dragon_counts.get(dragon, 0) + 1
    
    print("按龙王分类:")
    for dragon, count in dragon_counts.items():
        print(f"  {dragon}: {count}个言灵")
    
    # 测试言灵搜索
    print("\n🔍 言灵搜索测试:")
    search_terms = ["火", "风", "大地", "水"]
    for term in search_terms:
        results = db.search_spirit_words(term)
        names = [sw['name'] for sw in results]
        print(f"搜索 '{term}': {', '.join(names) if names else '无结果'}")

if __name__ == "__main__":
    db = migrate_bloodline_and_spirit_words()
    test_bloodline_and_spirit_words()
