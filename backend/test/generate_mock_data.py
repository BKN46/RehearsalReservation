#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成Mock数据脚本
创建随机的用户、设备和预约数据用于测试
"""

import sys
import os
import random
from datetime import datetime, timedelta, date

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, User, Campus, Reservation, Equipment, KeyManager, EquipmentBorrow, UnavailableTime

# 中文姓氏和名字用于生成随机姓名
SURNAMES = [
    '王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
    '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
    '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧'
]

GIVEN_NAMES = [
    '伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
    '洋', '勇', '艳', '杰', '涛', '明', '超', '秀兰', '霞', '平',
    '刚', '桂英', '萍', '华', '鹏', '玲', '浩', '宇', '欣', '婷',
    '雪', '晨', '凯', '瑞', '轩', '悦', '文', '博', '雨', '欢'
]

# 设备类型和名称
EQUIPMENT_TYPES = {
    '吉他': ['Fender电吉他', 'Gibson Les Paul', 'Yamaha民谣吉他', 'Ibanez电吉他', 'Martin民谣吉他', 'Taylor吉他'],
    '键盘': ['Yamaha电钢琴', 'Roland合成器', 'Korg键盘', 'Nord Stage', 'Casio电子琴'],
    '鼓': ['Pearl鼓组', 'Yamaha电鼓', 'Tama鼓组', 'Roland电子鼓', 'DW鼓组'],
    '贝斯': ['Fender Jazz Bass', 'Ibanez贝斯', 'Music Man贝斯', 'Yamaha贝斯'],
    '音箱': ['Marshall音箱', 'Fender音箱', 'Orange音箱', 'Vox音箱', 'Roland音箱'],
    '效果器': ['Boss GT-1000', 'Line 6 HX Stomp', 'Zoom G5n', 'TC Electronic'],
    '麦克风': ['Shure SM58', 'AKG C214', 'Audio-Technica AT2020', 'Rode NT1-A'],
    '调音台': ['Yamaha MG16XU', 'Behringer X32', 'Allen & Heath ZED-10FX', 'Mackie ProFX16v3']
}

LOCATIONS = [
    '排练室A', '排练室B', '排练室C', '排练室D', 
    '音乐厅储物间', '乐队排练间1', '乐队排练间2', '录音棚',
    '一楼器材室', '二楼储物柜', '三楼练习室', '地下室排练厅'
]

def generate_random_name():
    """生成随机中文姓名"""
    surname = random.choice(SURNAMES)
    given_name = random.choice(GIVEN_NAMES)
    if random.random() > 0.5:
        given_name += random.choice(GIVEN_NAMES)
    return surname + given_name

def generate_student_id(year_offset=0):
    """生成学号 (格式: XXXXXXXX)"""
    year = datetime.now().year - year_offset
    number = random.randint(10000, 799999)
    return f"{year % 100:02d}{number:06d}"[:10]

def generate_phone():
    """生成手机号"""
    prefixes = ['130', '131', '132', '133', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158', '159',
                '180', '181', '182', '183', '185', '186', '187', '188', '189']
    prefix = random.choice(prefixes)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return prefix + suffix

def generate_email(name, student_id):
    """生成邮箱"""
    # 使用学号作为邮箱前缀
    domains = ['buaa.edu.cn', 'stu.buaa.edu.cn']
    return f"{student_id.lower()}@{random.choice(domains)}"

def clear_database():
    """清空所有数据（保留校区）"""
    print("清空现有数据...")
    EquipmentBorrow.query.delete()
    Equipment.query.delete()
    Reservation.query.delete()
    UnavailableTime.query.delete()
    KeyManager.query.delete()
    User.query.delete()
    db.session.commit()
    print("✓ 数据已清空")

def create_campuses():
    """创建校区（如果不存在）"""
    print("\n检查校区...")
    campuses = Campus.query.all()
    if not campuses:
        campuses = [
            Campus(name='学院路校区'),
            Campus(name='沙河校区')
        ]
        for campus in campuses:
            db.session.add(campus)
        db.session.commit()
        print("✓ 已创建校区")
    else:
        print(f"✓ 校区已存在: {', '.join([c.name for c in campuses])}")
    return campuses

def create_admins():
    """创建3个管理员账号"""
    print("\n创建管理员账号...")
    admins_data = [
        {
            'student_id': 'admin001',
            'name': '张管理',
            'email': 'admin001@buaa.edu.cn',
            'phone': '13800138001',
            'password': 'admin123'
        },
        {
            'student_id': 'admin002',
            'name': '李管理',
            'email': 'admin002@buaa.edu.cn',
            'phone': '13800138002',
            'password': 'admin123'
        },
        {
            'student_id': 'admin003',
            'name': '王管理',
            'email': 'admin003@buaa.edu.cn',
            'phone': '13800138003',
            'password': 'admin123'
        }
    ]
    
    admins = []
    for admin_data in admins_data:
        admin = User(
            student_id=admin_data['student_id'],
            name=admin_data['name'],
            email=admin_data['email'],
            phone=admin_data['phone'],
            is_admin=True
        )
        admin.set_password(admin_data['password'])
        db.session.add(admin)
        admins.append(admin)
    
    db.session.commit()
    print(f"✓ 已创建 {len(admins)} 个管理员账号")
    for admin in admins:
        print(f"  - {admin.name} ({admin.student_id}) / 密码: admin123")
    return admins

def create_students(count=30):
    """创建随机学生账号"""
    print(f"\n创建 {count} 个学生账号...")
    students = []
    
    for i in range(count):
        name = generate_random_name()
        year_offset = random.randint(0, 4)  # 0-4年前入学
        student_id = generate_student_id(year_offset)
        email = generate_email(name, student_id)
        phone = generate_phone()
        
        student = User(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            is_admin=False
        )
        student.set_password('123456')  # 统一密码
        db.session.add(student)
        students.append(student)
    
    db.session.commit()
    print(f"✓ 已创建 {len(students)} 个学生账号 (默认密码: 123456)")
    print(f"  示例: {students[0].name} ({students[0].student_id})")
    return students

def create_key_managers(campuses):
    """创建钥匙管理员"""
    print("\n创建钥匙管理员...")
    managers_data = [
        {'name': '张大爷', 'contact': '13800001111'},
        {'name': '李阿姨', 'contact': '13800002222'},
        {'name': '王师傅', 'contact': '13800003333'},
    ]
    
    managers = []
    for campus in campuses:
        for manager_data in random.sample(managers_data, 2):  # 每个校区2个管理员
            manager = KeyManager(
                campus_id=campus.id,
                name=manager_data['name'],
                contact=manager_data['contact'],
                is_active=True
            )
            db.session.add(manager)
            managers.append(manager)
    
    db.session.commit()
    print(f"✓ 已创建 {len(managers)} 个钥匙管理员")
    return managers

def create_equipment(students, campuses, count=20):
    """创建随机设备"""
    print(f"\n创建 {count} 个设备...")
    equipment_list = []
    
    for i in range(count):
        equipment_type = random.choice(list(EQUIPMENT_TYPES.keys()))
        equipment_name = random.choice(EQUIPMENT_TYPES[equipment_type])
        
        owner = random.choice(students)
        campus = random.choice(campuses)
        location = random.choice(LOCATIONS)
        is_shared = random.random() > 0.4  # 60%概率共享
        
        notes_options = [
            None,
            '保养良好，欢迎使用',
            '请轻拿轻放',
            '使用后请归位',
            '需要提前预约',
            '仅限有经验者使用',
            ''
        ]
        
        equipment = Equipment(
            user_id=owner.id,
            campus_id=campus.id,
            equipment_type=equipment_type,
            equipment_name=equipment_name,
            location=location,
            is_shared=is_shared,
            contact=owner.phone,
            notes=random.choice(notes_options),
            placed_at=datetime.now() - timedelta(days=random.randint(1, 180))
        )
        db.session.add(equipment)
        equipment_list.append(equipment)
    
    db.session.commit()
    print(f"✓ 已创建 {len(equipment_list)} 个设备")
    shared_count = sum(1 for e in equipment_list if e.is_shared)
    print(f"  - 共享设备: {shared_count} 个")
    print(f"  - 私有设备: {len(equipment_list) - shared_count} 个")
    return equipment_list

def create_reservations(students, campuses, days_range=14):
    """创建随机预约"""
    print(f"\n创建预约记录 (未来{days_range}天)...")
    
    reservations = []
    today = date.today()
    
    # 为每个校区生成预约
    for campus in campuses:
        # 随机生成预约
        reservation_count = random.randint(20, 40)
        
        for _ in range(reservation_count):
            # 随机日期（今天到未来days_range天）
            days_offset = random.randint(0, days_range)
            reservation_date = today + timedelta(days=days_offset)
            
            # 定义可用的时间段（避开12-13和18-19）
            # 上午: 7-12, 下午: 13-18, 晚上: 19-22
            time_slots = [
                (7, 12),   # 上午段
                (13, 18),  # 下午段
                (19, 22),  # 晚上段
            ]
            
            # 随机选择一个时间段
            slot_start, slot_end = random.choice(time_slots)
            
            # 在选定的时间段内随机生成预约
            duration = random.choice([1, 2, 3, 4])  # 1-4小时
            max_start = slot_end - duration
            if max_start < slot_start:
                max_start = slot_start
            
            start_hour = random.randint(slot_start, max_start)
            end_hour = min(start_hour + duration, slot_end)
            
            # 随机用户
            user = random.choice(students)
            
            # 检查是否有冲突（简单检查，不完全准确）
            conflict = any(
                r.campus_id == campus.id and 
                r.date == reservation_date and
                not (r.end_hour <= start_hour or r.start_hour >= end_hour)
                for r in reservations
            )
            
            if conflict:
                continue
            
            # 创建预约
            key_picked_up = False
            key_pickup_time = None
            
            # 如果是今天之前的预约，有80%概率已取钥匙
            if reservation_date < today:
                if random.random() > 0.2:
                    key_picked_up = True
                    # 预约日期当天早上取钥匙
                    key_pickup_time = datetime.combine(
                        reservation_date, 
                        datetime.min.time()
                    ) + timedelta(hours=start_hour - 1, minutes=random.randint(0, 59))
            # 今天的预约，已开始的有50%概率取了钥匙
            elif reservation_date == today and start_hour <= datetime.now().hour:
                if random.random() > 0.5:
                    key_picked_up = True
                    key_pickup_time = datetime.now() - timedelta(hours=random.randint(0, 2))
            
            reservation = Reservation(
                user_id=user.id,
                campus_id=campus.id,
                date=reservation_date,
                start_hour=start_hour,
                end_hour=end_hour,
                status='active',
                key_picked_up=key_picked_up,
                key_pickup_time=key_pickup_time,
                created_at=datetime.now() - timedelta(days=days_offset, hours=random.randint(1, 24))
            )
            db.session.add(reservation)
            reservations.append(reservation)
    
    db.session.commit()
    print(f"✓ 已创建 {len(reservations)} 个预约")
    
    # 统计信息
    picked_up = sum(1 for r in reservations if r.key_picked_up)
    print(f"  - 已取钥匙: {picked_up} 个")
    print(f"  - 未取钥匙: {len(reservations) - picked_up} 个")
    
    return reservations

def create_equipment_borrows(students, equipment_list):
    """创建设备借用记录"""
    print("\n创建设备借用记录...")
    
    borrows = []
    borrow_count = random.randint(10, 20)
    
    for _ in range(borrow_count):
        user = random.choice(students)
        
        # 70%从已登记设备借，30%借用未登记的器材
        if random.random() > 0.3 and equipment_list:
            equipment = random.choice(equipment_list)
            equipment_name = equipment.equipment_name
            equipment_type = equipment.equipment_type
        else:
            equipment_type = random.choice(list(EQUIPMENT_TYPES.keys()))
            equipment_name = random.choice(EQUIPMENT_TYPES[equipment_type])
        
        # 借用时间
        borrow_time = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23)
        )
        
        # 50%已归还
        status = random.choice(['borrowed', 'returned'])
        return_time = None
        
        if status == 'returned':
            return_time = borrow_time + timedelta(
                days=random.randint(1, 7),
                hours=random.randint(0, 23)
            )
        
        notes_options = [
            None,
            '用于乐队排练',
            '个人练习使用',
            '演出使用',
            '录音使用',
            ''
        ]
        
        borrow = EquipmentBorrow(
            user_id=user.id,
            equipment_name=equipment_name,
            equipment_type=equipment_type,
            borrow_time=borrow_time,
            return_time=return_time,
            status=status,
            notes=random.choice(notes_options)
        )
        db.session.add(borrow)
        borrows.append(borrow)
    
    db.session.commit()
    print(f"✓ 已创建 {len(borrows)} 个借用记录")
    borrowed = sum(1 for b in borrows if b.status == 'borrowed')
    print(f"  - 借用中: {borrowed} 个")
    print(f"  - 已归还: {len(borrows) - borrowed} 个")
    return borrows

def create_unavailable_times(campuses):
    """创建不可预约时间"""
    print("\n创建不可预约时间规则...")
    
    unavailable_times = []
    
    for campus in campuses:
        # 午餐时间 (周一到周日 12:00-13:00)
        lunch_time = UnavailableTime(
            campus_id=campus.id,
            date=None,  # 所有日期
            day_of_week=None,
            start_hour=12,
            end_hour=13,
            reason='午餐时间'
        )
        db.session.add(lunch_time)
        unavailable_times.append(lunch_time)
        
        # 晚餐时间 (周一到周日 18:00-19:00)
        dinner_time = UnavailableTime(
            campus_id=campus.id,
            date=None,  # 所有日期
            day_of_week=None,
            start_hour=18,
            end_hour=19,
            reason='晚餐时间'
        )
        db.session.add(dinner_time)
        unavailable_times.append(dinner_time)
        
        # 周一上午维护 (每周一 7:00-11:00)
        if random.random() > 0.5:  # 50%概率
            monday_maintenance = UnavailableTime(
                campus_id=campus.id,
                date=None,
                day_of_week=1,  # 周一
                start_hour=7,
                end_hour=11,
                reason='设备维护'
            )
            db.session.add(monday_maintenance)
            unavailable_times.append(monday_maintenance)
    
    db.session.commit()
    print(f"✓ 已创建 {len(unavailable_times)} 个不可预约时间规则")
    return unavailable_times

def print_summary(admins, students, equipment_list, reservations, borrows):
    """打印统计摘要"""
    print("\n" + "="*60)
    print("Mock数据生成完成！")
    print("="*60)
    print(f"\n用户账号:")
    print(f"  - 管理员: {len(admins)} 个")
    print(f"  - 学生: {len(students)} 个")
    print(f"\n设备:")
    print(f"  - 总数: {len(equipment_list)} 个")
    print(f"\n预约:")
    print(f"  - 总数: {len(reservations)} 个")
    print(f"\n借用记录:")
    print(f"  - 总数: {len(borrows)} 个")
    print(f"\n登录信息:")
    print(f"  管理员账号: admin001 / admin123")
    print(f"  学生账号示例: {students[0].student_id} / 123456")
    print("="*60)

def main():
    """主函数"""
    print("="*60)
    print("开始生成Mock数据...")
    print("="*60)
    
    with app.app_context():
        # 清空数据
        clear_database()
        
        # 创建基础数据
        campuses = create_campuses()
        
        # 创建用户
        admins = create_admins()
        students = create_students(30)
        
        # 创建钥匙管理员
        create_key_managers(campuses)
        
        # 创建设备
        equipment_list = create_equipment(students, campuses, 20)
        
        # 创建预约
        reservations = create_reservations(students, campuses, days_range=14)
        
        # 创建借用记录
        borrows = create_equipment_borrows(students, equipment_list)
        
        # 创建不可预约时间
        create_unavailable_times(campuses)
        
        # 打印摘要
        print_summary(admins, students, equipment_list, reservations, borrows)

if __name__ == '__main__':
    main()
