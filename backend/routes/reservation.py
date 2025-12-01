from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Reservation, Campus, User, UnavailableTime
from datetime import datetime, timedelta, date
from sqlalchemy import and_, or_

reservation_bp = Blueprint('reservation', __name__)

# 定义可预约时间段
TIME_SLOTS = {
    'morning': (8, 12),
    'afternoon': (13, 18),
    'evening': (19, 22)
}

def validate_time_slot(start_hour, end_hour):
    """验证时间段是否有效"""
    if start_hour >= end_hour:
        return False
    if start_hour < 8 or end_hour > 22:
        return False
    # 验证是否在允许的时间段内
    valid_ranges = [(8, 12), (13, 18), (19, 22)]
    for start, end in valid_ranges:
        if start_hour >= start and end_hour <= end:
            return True
    return False

def check_time_conflict(campus_id, date, start_hour, end_hour, exclude_id=None):
    """检查时间冲突（带数据库锁）"""
    query = Reservation.query.filter(
        Reservation.campus_id == campus_id,
        Reservation.date == date,
        Reservation.status == 'active',
        or_(
            and_(Reservation.start_hour < end_hour, Reservation.end_hour > start_hour)
        )
    )
    
    if exclude_id:
        query = query.filter(Reservation.id != exclude_id)
    
    # 使用悲观锁防止并发问题
    return query.with_for_update().first() is not None

def check_unavailable_time(campus_id, date, start_hour, end_hour):
    """检查是否在不可预约时间段内，返回(是否不可用, 原因)"""
    # 获取星期几 (0=周一, 6=周日) -> 转换为 (0=周日, 1=周一, ..., 6=周六)
    day_of_week = (date.weekday() + 1) % 7
    
    # 检查三种类型的不可预约时间：
    # 1. 特定日期
    # 2. 固定周几
    # 3. 所有日期
    unavailable = UnavailableTime.query.filter(
        UnavailableTime.campus_id == campus_id,
        or_(
            UnavailableTime.date == date,  # 特定日期
            UnavailableTime.day_of_week == day_of_week,  # 固定周几
            and_(UnavailableTime.date.is_(None), UnavailableTime.day_of_week.is_(None))  # 所有日期
        ),
        or_(
            and_(UnavailableTime.start_hour < end_hour, UnavailableTime.end_hour > start_hour)
        )
    ).first()
    
    if unavailable:
        reason = unavailable.reason if unavailable.reason else '该时间段不可预约'
        return True, reason
    
    return False, None

@reservation_bp.route('/campuses', methods=['GET'])
def get_campuses():
    """获取所有校区"""
    campuses = Campus.query.all()
    return jsonify([c.to_dict() for c in campuses]), 200

@reservation_bp.route('/create', methods=['POST'])
@jwt_required()
def create_reservation():
    """创建预约（处理并发）"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # 检查用户是否被禁用
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({'error': 'Account is disabled. Please contact administrator.'}), 403
    
    # 验证必填字段
    required_fields = ['campus_id', 'date', 'start_hour', 'end_hour']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    campus_id = data['campus_id']
    date_str = data['date']
    start_hour = data['start_hour']
    end_hour = data['end_hour']
    
    # 验证校区
    campus = Campus.query.get(campus_id)
    if not campus:
        return jsonify({'error': 'Campus not found'}), 404
    
    # 验证日期
    try:
        reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # 计算预约窗口：上周日22:00至本周日22:00
    now = datetime.now()
    current_hour = now.hour
    day_of_week = now.weekday()  # 0=周一, 6=周日
    today = now.date()
    
    # 计算上周日
    days_to_last_sunday = day_of_week + 1 if day_of_week < 6 else 0
    last_sunday = today - timedelta(days=days_to_last_sunday)
    
    # 如果当前是周日且时间>=22:00，上周日就是今天
    if day_of_week == 6 and current_hour >= 22:
        last_sunday = today
    
    # 计算本周日
    days_to_this_sunday = 6 - day_of_week if day_of_week < 6 else 0
    this_sunday = today + timedelta(days=days_to_this_sunday)
    
    # 如果当前是周日且时间>=22:00，本周日就是下周日
    if day_of_week == 6 and current_hour >= 22:
        this_sunday = today + timedelta(days=7)
    
    # 检查预约日期是否在窗口内（上周日22:00之后，本周日22:00之前）
    # 简化为日期检查：必须在上周日（含）到本周日（含）之间
    if reservation_date < last_sunday or reservation_date > this_sunday:
        return jsonify({
            'error': f'Reservation date must be between {last_sunday.isoformat()} and {this_sunday.isoformat()}'
        }), 400
    
    # 验证时间段
    if not validate_time_slot(start_hour, end_hour):
        return jsonify({'error': 'Invalid time slot'}), 400
    
    # 检查本周预约时长限制（6小时）
    # 使用与窗口相同的逻辑：上周日到本周日
    weekly_reservations = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.date >= last_sunday,
        Reservation.date <= this_sunday,
        Reservation.status == 'active'
    ).all()
    
    total_hours = sum(r.end_hour - r.start_hour for r in weekly_reservations)
    new_hours = end_hour - start_hour
    
    if total_hours + new_hours > 6:
        return jsonify({
            'error': f'Weekly reservation limit exceeded. You have used {total_hours} hours this week. Limit is 6 hours.'
        }), 400
    
    # 使用事务和锁处理并发
    try:
        # 开始事务
        db.session.begin_nested()
        
        # 检查不可预约时间段
        is_unavailable, unavailable_reason = check_unavailable_time(campus_id, reservation_date, start_hour, end_hour)
        if is_unavailable:
            db.session.rollback()
            return jsonify({'error': f'该时间段不可预约：{unavailable_reason}'}), 400
        
        # 检查时间冲突（带锁）
        if check_time_conflict(campus_id, reservation_date, start_hour, end_hour):
            db.session.rollback()
            return jsonify({'error': 'Time slot already reserved'}), 409
        
        # 创建预约
        reservation = Reservation(
            user_id=user_id,
            campus_id=campus_id,
            date=reservation_date,
            start_hour=start_hour,
            end_hour=end_hour
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation created successfully',
            'reservation': reservation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Reservation failed: {str(e)}'}), 500

@reservation_bp.route('/my-reservations', methods=['GET'])
@jwt_required()
def get_my_reservations():
    """获取当前用户的预约"""
    user_id = int(get_jwt_identity())
    
    reservations = Reservation.query.filter_by(
        user_id=user_id,
        status='active'
    ).order_by(Reservation.date.desc(), Reservation.start_hour.desc()).all()
    
    return jsonify([r.to_dict() for r in reservations]), 200

@reservation_bp.route('/weekly', methods=['GET'])
def get_weekly_reservations():
    """获取本周预约情况（周日22:00后显示下周）"""
    campus_id = request.args.get('campus_id', type=int)
    
    if not campus_id:
        return jsonify({'error': 'campus_id is required'}), 400
    
    # 获取当前时间
    now = datetime.now()
    current_hour = now.hour
    day_of_week = now.weekday()  # 0=周一, 6=周日
    
    # 计算本周的开始和结束日期
    today = now.date()
    
    # 如果是周日(6)且时间>=22:00，显示下周
    if day_of_week == 6 and current_hour >= 22:
        # 跳到下周一
        start_of_week = today + timedelta(days=1)
    else:
        # 本周一
        start_of_week = today - timedelta(days=day_of_week)
    
    end_of_week = start_of_week + timedelta(days=6)
    
    reservations = Reservation.query.filter(
        Reservation.campus_id == campus_id,
        Reservation.date >= start_of_week,
        Reservation.date <= end_of_week,
        Reservation.status == 'active'
    ).order_by(Reservation.date, Reservation.start_hour).all()
    
    return jsonify({
        'start_date': start_of_week.isoformat(),
        'end_date': end_of_week.isoformat(),
        'reservations': [r.to_dict() for r in reservations]
    }), 200

@reservation_bp.route('/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def cancel_reservation(reservation_id):
    """取消预约"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    reservation = Reservation.query.get(reservation_id)
    
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    # 只有预约用户或管理员可以取消
    if reservation.user_id != user_id and not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        reservation.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'message': 'Reservation cancelled successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reservation_bp.route('/date/<date_str>', methods=['GET'])
def get_reservations_by_date(date_str):
    """获取指定日期的预约"""
    campus_id = request.args.get('campus_id', type=int)
    
    if not campus_id:
        return jsonify({'error': 'campus_id is required'}), 400
    
    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    reservations = Reservation.query.filter(
        Reservation.campus_id == campus_id,
        Reservation.date == query_date,
        Reservation.status == 'active'
    ).order_by(Reservation.start_hour).all()
    
    return jsonify([r.to_dict() for r in reservations]), 200
