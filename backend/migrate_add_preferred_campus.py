#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加 preferred_campus_id 字段到 User 表
"""

import sys
import os

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db

def migrate():
    """执行数据库迁移"""
    with app.app_context():
        # 使用 SQLite 的 ALTER TABLE 添加新列
        try:
            # 检查列是否已存在
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                if 'preferred_campus_id' not in columns:
                    print("添加 preferred_campus_id 列到 users 表...")
                    conn.execute(db.text(
                        "ALTER TABLE users ADD COLUMN preferred_campus_id INTEGER"
                    ))
                    conn.commit()
                    print("✓ 列添加成功")
                else:
                    print("✓ preferred_campus_id 列已存在，跳过迁移")
                    
        except Exception as e:
            print(f"✗ 迁移失败: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    print("="*60)
    print("开始数据库迁移...")
    print("="*60)
    
    if migrate():
        print("\n" + "="*60)
        print("迁移完成！")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("迁移失败！")
        print("="*60)
        sys.exit(1)
