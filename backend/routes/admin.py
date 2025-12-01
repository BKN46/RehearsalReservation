from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, UnavailableTime, KeyManager, Campus
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    """管理员权限装饰器"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper

@admin_bp.route('/unavailable-times', methods=['GET'])
def get_unavailable_times():
    """获取所有不可预约时间段"""
    campus_id = request.args.get('campus_id', type=int)
    
    query = UnavailableTime.query
    if campus_id:
        query = query.filter_by(campus_id=campus_id)
    
    # 排序：先按日期（降序，None在后），再按周几，最后按开始时间
    unavailable_times = query.order_by(
        UnavailableTime.date.desc().nullslast(),
        UnavailableTime.day_of_week.asc().nullslast(),
        UnavailableTime.start_hour.asc()
    ).all()
    
    return jsonify([ut.to_dict() for ut in unavailable_times]), 200

@admin_bp.route('/unavailable-times', methods=['POST'])
@admin_required
def create_unavailable_time():
    """创建不可预约时间段"""
    data = request.get_json()
    
    required_fields = ['campus_id', 'start_hour', 'end_hour']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    campus_id = data['campus_id']
    start_hour = data['start_hour']
    end_hour = data['end_hour']
    reason = data.get('reason', '')
    date = data.get('date')
    day_of_week = data.get('day_of_week')
    
    # 验证校区
    campus = Campus.query.get(campus_id)
    if not campus:
        return jsonify({'error': 'Campus not found'}), 404
    
    # 验证时间
    if start_hour >= end_hour or start_hour < 0 or end_hour > 24:
        return jsonify({'error': 'Invalid time range'}), 400
    
    # 验证日期（如果提供）
    unavailable_date = None
    if date:
        try:
            unavailable_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # 验证周几（如果提供）
    if day_of_week is not None:
        if not isinstance(day_of_week, int) or day_of_week < 0 or day_of_week > 6:
            return jsonify({'error': 'day_of_week must be an integer between 0 (Sunday) and 6 (Saturday)'}), 400
    
    try:
        unavailable_time = UnavailableTime(
            campus_id=campus_id,
            date=unavailable_date,
            day_of_week=day_of_week,
            start_hour=start_hour,
            end_hour=end_hour,
            reason=reason
        )
        
        db.session.add(unavailable_time)
        db.session.commit()
        
        return jsonify({
            'message': 'Unavailable time created successfully',
            'unavailable_time': unavailable_time.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/unavailable-times/<int:id>', methods=['DELETE'])
@admin_required
def delete_unavailable_time(id):
    """删除不可预约时间段"""
    unavailable_time = UnavailableTime.query.get(id)
    
    if not unavailable_time:
        return jsonify({'error': 'Unavailable time not found'}), 404
    
    try:
        db.session.delete(unavailable_time)
        db.session.commit()
        
        return jsonify({'message': 'Unavailable time deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/key-managers', methods=['GET'])
def get_key_managers():
    """获取所有钥匙管理员"""
    campus_id = request.args.get('campus_id', type=int)
    
    query = KeyManager.query.filter_by(is_active=True)
    if campus_id:
        query = query.filter_by(campus_id=campus_id)
    
    key_managers = query.all()
    
    return jsonify([km.to_dict() for km in key_managers]), 200

@admin_bp.route('/key-managers', methods=['POST'])
@admin_required
def create_key_manager():
    """创建钥匙管理员"""
    data = request.get_json()
    
    required_fields = ['campus_id', 'name', 'contact']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    campus_id = data['campus_id']
    name = data['name']
    contact = data['contact']
    
    # 验证校区
    campus = Campus.query.get(campus_id)
    if not campus:
        return jsonify({'error': 'Campus not found'}), 404
    
    try:
        key_manager = KeyManager(
            campus_id=campus_id,
            name=name,
            contact=contact
        )
        
        db.session.add(key_manager)
        db.session.commit()
        
        return jsonify({
            'message': 'Key manager created successfully',
            'key_manager': key_manager.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/key-managers/<int:id>', methods=['PUT'])
@admin_required
def update_key_manager(id):
    """更新钥匙管理员"""
    key_manager = KeyManager.query.get(id)
    
    if not key_manager:
        return jsonify({'error': 'Key manager not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        key_manager.name = data['name']
    if 'contact' in data:
        key_manager.contact = data['contact']
    if 'is_active' in data:
        key_manager.is_active = data['is_active']
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Key manager updated successfully',
            'key_manager': key_manager.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/key-managers/<int:id>', methods=['DELETE'])
@admin_required
def delete_key_manager(id):
    """删除钥匙管理员"""
    key_manager = KeyManager.query.get(id)
    
    if not key_manager:
        return jsonify({'error': 'Key manager not found'}), 404
    
    try:
        db.session.delete(key_manager)
        db.session.commit()
        
        return jsonify({'message': 'Key manager deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """获取所有用户（支持筛选）"""
    # 获取筛选参数
    is_active = request.args.get('is_active')  # 'true' 或 'false'
    year = request.args.get('year', type=int)  # 入学年份
    search = request.args.get('search', '')  # 搜索名称
    
    query = User.query
    
    # 按激活状态筛选
    if is_active is not None:
        if is_active.lower() == 'true':
            query = query.filter_by(is_active=True)
        elif is_active.lower() == 'false':
            query = query.filter_by(is_active=False)
    
    # 按入学年份筛选（根据学号前两位）
    if year:
        # 学号格式通常为 BYYYXXXXXXXX，其中YY是年份后两位
        year_suffix = str(year % 100).zfill(2)  # 例如 2024 -> "24"
        query = query.filter(User.student_id.like(f'%{year_suffix}%'))
    
    # 按名称搜索
    if search:
        query = query.filter(User.name.like(f'%{search}%'))
    
    users = query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_user_active(user_id):
    """启用/禁用用户"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # 不能禁用管理员（包括自己）
    current_user_id = int(get_jwt_identity())
    if user.is_admin:
        return jsonify({'error': 'Cannot disable admin users'}), 400
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/annual-reset', methods=['POST'])
@admin_required
def annual_reset_users():
    """每年1月1日重置所有普通用户为禁用状态"""
    try:
        # 只禁用非管理员用户
        result = User.query.filter_by(is_admin=False).update({'is_active': False})
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deactivated {result} non-admin users',
            'count': result
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/batch-activate', methods=['POST'])
@admin_required
def batch_activate_users():
    """批量激活用户"""
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'error': 'user_ids is required'}), 400
    
    try:
        result = User.query.filter(User.id.in_(user_ids)).update({'is_active': True}, synchronize_session=False)
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully activated {result} users',
            'count': result
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reservations', methods=['GET'])
@admin_required
def get_reservation_history():
    """获取历史预约记录（支持筛选和分页）"""
    from models import Reservation
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    # 获取筛选参数
    user_name = request.args.get('user_name', '')
    campus_id = request.args.get('campus_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 构建查询
    query = Reservation.query
    
    # 按用户名筛选 - 需要JOIN User表
    if user_name:
        query = query.join(User).filter(User.name.like(f'%{user_name}%'))
    
    # 按校区筛选
    if campus_id:
        query = query.filter(Reservation.campus_id == campus_id)
    
    # 按日期范围筛选
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Reservation.date >= start)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Reservation.date <= end)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    
    # 按创建时间倒序排列
    query = query.order_by(Reservation.created_at.desc())
    
    # 分页
    total = query.count()
    reservations = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 构建返回数据，使用to_dict()方法已经包含了用户和校区名称
    reservation_list = [r.to_dict() for r in reservations]
    
    return jsonify({
        'data': reservation_list,
        'total': total,
        'page': page,
        'page_size': page_size
    }), 200
