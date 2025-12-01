#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加 key_returned 和 key_return_time 字段到 Reservation 表
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
        try:
            with db.engine.connect() as conn:
                # 检查列是否已存在
                result = conn.execute(db.text("PRAGMA table_info(reservations)"))
                columns = [row[1] for row in result]
                
                # 添加 key_returned 列
                if 'key_returned' not in columns:
                    print("添加 key_returned 列到 reservations 表...")
                    conn.execute(db.text(
                        "ALTER TABLE reservations ADD COLUMN key_returned BOOLEAN DEFAULT 0"
                    ))
                    conn.commit()
                    print("✓ key_returned 列添加成功")
                else:
                    print("✓ key_returned 列已存在，跳过")
                
                # 添加 key_return_time 列
                if 'key_return_time' not in columns:
                    print("添加 key_return_time 列到 reservations 表...")
                    conn.execute(db.text(
                        "ALTER TABLE reservations ADD COLUMN key_return_time DATETIME"
                    ))
                    conn.commit()
                    print("✓ key_return_time 列添加成功")
                else:
                    print("✓ key_return_time 列已存在，跳过")
                    
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
