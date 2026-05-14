#!/usr/bin/env python3
"""
更新路明非与叔叔婶婶的关系描述
强调寄人篱下、疏离、不被重视的感觉（类似哈利波特）
"""

import sys
import os
sys.path.append('.')

from database.character_database import CharacterDatabase
import sqlite3

def update_family_relationships():
    """更新家庭关系描述"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "database", "dragon_characters.db")
    
    # 首先确保叔叔婶婶在数据库中
    db = CharacterDatabase(db_path)
    
    # 添加叔叔（如果不存在）
    叔叔_background = """路明非的叔叔，一个讲究"品位"的中年男人。喜欢高仿名牌（万宝龙表、仿名牌衣服），经常在饭桌上强调"手机、手表、打火机三件套是男人的身份"。

对路明非算不上苛刻，但也谈不上关心。他更关心路明非父母寄来的钱，以及这笔钱能给他买什么（比如心心念念的N96手机）。对自己的儿子路鸣泽更加重视，态度上的差别很明显。

他是个比较随和的家伙，只要不触及利益，对路明非还算客气。但这种客气更多是出于"你爸妈给钱"的考虑，而非真正的亲情。"""
    
    婶婶_background = """路明非的婶婶，一个精于算计的中年女性。她对路明非的态度复杂：一方面享受着路明非父母寄来的钱（花旗银行托管账户，每月定期到账），另一方面又嫌弃这个"吃白饭的"侄子。

她总是拿路明非和亲生儿子路鸣泽对比，逢人就说"鸣泽成绩好都是我们家的基因，看你家基因就是不行！"她对路明非的态度更像是对一个寄宿生，而非家人。

让路明非申请出国，一方面是想"给路鸣泽踩出一条路"（让路明非先试错），另一方面也希望路明非"待在大洋彼岸别让婶婶看见"。她对路明非爸妈的钱很上心，对路明非这个人却很冷淡。

她给路明非买东西（如申请学校的费用）时总会强调"花了多少钱"，让路明非时刻记得自己欠了人情。"""
    
    try:
        # 添加叔叔（如果不存在）
        try:
            db.add_character("叔叔", 叔叔_background, "路明非的监护人，讲究品位的中年男人")
            print("✅ 添加了叔叔角色")
        except:
            # 如果已存在，更新
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE characters SET background_story = ? WHERE name = ?', 
                             (叔叔_background, "叔叔"))
                conn.commit()
            print("✅ 更新了叔叔角色")
        
        # 添加婶婶（如果不存在）
        try:
            db.add_character("婶婶", 婶婶_background, "路明非的监护人，精于算计的中年女性")
            print("✅ 添加了婶婶角色")
        except:
            # 如果已存在，更新
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE characters SET background_story = ? WHERE name = ?', 
                             (婶婶_background, "婶婶"))
                conn.commit()
            print("✅ 更新了婶婶角色")
        
        # 更新路明非与他们的关系
        lumingfei_id = db.get_character_id("路明非")
        
        # 删除旧关系（如果有）
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM character_relationships 
                WHERE character_id = ? AND related_character_name IN ('叔叔', '婶婶')
            ''', (lumingfei_id,))
            conn.commit()
        
        # 添加新关系
        db.add_relationship(
            "路明非", 
            "叔叔", 
            "监护人", 
            "客气但疏离的监护关系。叔叔对路明非算不上苛刻，但也谈不上关心，更在意路明非父母寄来的钱。路明非在这个家里像个寄宿生，没有真正的归属感。", 
            4  # 重要性较低
        )
        
        db.add_relationship(
            "路明非",
            "婶婶",
            "监护人",
            "冷淡且算计的监护关系。婶婶总是拿路明非和路鸣泽对比，让路明非感觉自己是'吃白饭的'、多余的负担。她希望路明非'待在大洋彼岸别让婶婶看见'，对路明非父母的钱比对路明非这个人更感兴趣。类似哈利波特与佩妮姨妈的关系。",
            3  # 重要性很低，但影响路明非性格
        )
        
        print("✅ 更新了与叔叔婶婶的关系")
        
        # 添加路明非的心理状态注释
        db.add_personality_traits(lumingfei_id, [
            "在家中感觉寄人篱下",
            "习惯被忽视",
            "对家人保持距离",
            "不期待被关心"
        ])
        
        print("✅ 添加了心理状态特征")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 更新路明非与叔叔婶婶的关系...")
    print("=" * 60)
    update_family_relationships()
    print("=" * 60)
    print("✅ 数据库更新完成！")

