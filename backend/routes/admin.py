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
    
    unavailable_times = query.order_by(UnavailableTime.date.desc()).all()
    
    return jsonify([ut.to_dict() for ut in unavailable_times]), 200

@admin_bp.route('/unavailable-times', methods=['POST'])
@admin_required
def create_unavailable_time():
    """创建不可预约时间段"""
    data = request.get_json()
    
    required_fields = ['campus_id', 'date', 'start_hour', 'end_hour']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    campus_id = data['campus_id']
    date_str = data['date']
    start_hour = data['start_hour']
    end_hour = data['end_hour']
    reason = data.get('reason', '')
    
    # 验证校区
    campus = Campus.query.get(campus_id)
    if not campus:
        return jsonify({'error': 'Campus not found'}), 404
    
    # 验证日期
    try:
        unavailable_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # 验证时间
    if start_hour >= end_hour or start_hour < 8 or end_hour > 22:
        return jsonify({'error': 'Invalid time range'}), 400
    
    try:
        unavailable_time = UnavailableTime(
            campus_id=campus_id,
            date=unavailable_date,
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
    """获取所有用户"""
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_user_active(user_id):
    """启用/禁用用户"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # 不能禁用自己
    current_user_id = int(get_jwt_identity())
    if user_id == current_user_id:
        return jsonify({'error': 'Cannot disable yourself'}), 400
    
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
