from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Reservation, KeyManager
from datetime import datetime

key_bp = Blueprint('key', __name__)

@key_bp.route('/pickup/<int:reservation_id>', methods=['POST'])
@jwt_required()
def pickup_key(reservation_id):
    """登记取钥匙"""
    user_id = int(get_jwt_identity())
    
    reservation = Reservation.query.get(reservation_id)
    
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    # 只有预约用户可以登记
    if reservation.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # 检查预约是否有效
    if reservation.status != 'active':
        return jsonify({'error': 'Reservation is not active'}), 400
    
    # 检查是否已经登记
    if reservation.key_picked_up:
        return jsonify({'error': 'Key already picked up'}), 400
    
    try:
        reservation.key_picked_up = True
        reservation.key_pickup_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Key pickup registered successfully',
            'reservation': reservation.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@key_bp.route('/pickups', methods=['GET'])
def get_key_pickups():
    """获取钥匙领取情况"""
    campus_id = request.args.get('campus_id', type=int)
    
    if not campus_id:
        return jsonify({'error': 'campus_id is required'}), 400
    
    # 获取已领取钥匙的预约
    reservations = Reservation.query.filter(
        Reservation.campus_id == campus_id,
        Reservation.key_picked_up == True,
        Reservation.status == 'active'
    ).order_by(Reservation.key_pickup_time.desc()).limit(50).all()
    
    return jsonify([r.to_dict() for r in reservations]), 200

@key_bp.route('/managers/<int:campus_id>', methods=['GET'])
def get_current_key_managers(campus_id):
    """获取当前钥匙管理员"""
    managers = KeyManager.query.filter_by(
        campus_id=campus_id,
        is_active=True
    ).all()
    
    return jsonify([m.to_dict() for m in managers]), 200
