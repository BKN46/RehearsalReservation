from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Equipment, EquipmentBorrow, User, Campus
from datetime import datetime

equipment_bp = Blueprint('equipment', __name__)

# 设备借用相关

@equipment_bp.route('/borrow', methods=['POST'])
@jwt_required()
def borrow_equipment():
    """登记借用设备"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    required_fields = ['equipment_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    equipment_name = data['equipment_name']
    equipment_type = data.get('equipment_type', '')
    notes = data.get('notes', '')
    
    try:
        borrow = EquipmentBorrow(
            user_id=user_id,
            equipment_name=equipment_name,
            equipment_type=equipment_type,
            notes=notes
        )
        
        db.session.add(borrow)
        db.session.commit()
        
        return jsonify({
            'message': 'Equipment borrow registered successfully',
            'borrow': borrow.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/borrow/<int:borrow_id>/return', methods=['POST'])
@jwt_required()
def return_equipment(borrow_id):
    """确认归还设备"""
    user_id = int(get_jwt_identity())
    
    borrow = EquipmentBorrow.query.get(borrow_id)
    
    if not borrow:
        return jsonify({'error': 'Borrow record not found'}), 404
    
    # 只有借用者可以确认归还
    if borrow.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if borrow.status == 'returned':
        return jsonify({'error': 'Equipment already returned'}), 400
    
    try:
        borrow.status = 'returned'
        borrow.return_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Equipment return confirmed successfully',
            'borrow': borrow.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/borrows', methods=['GET'])
def get_equipment_borrows():
    """获取设备借用记录"""
    status = request.args.get('status', 'borrowed')
    
    borrows = EquipmentBorrow.query.filter_by(status=status).order_by(
        EquipmentBorrow.borrow_time.desc()
    ).limit(100).all()
    
    return jsonify([b.to_dict() for b in borrows]), 200

@equipment_bp.route('/my-borrows', methods=['GET'])
@jwt_required()
def get_my_borrows():
    """获取我的借用记录"""
    user_id = int(get_jwt_identity())
    
    borrows = EquipmentBorrow.query.filter_by(user_id=user_id).order_by(
        EquipmentBorrow.borrow_time.desc()
    ).all()
    
    return jsonify([b.to_dict() for b in borrows]), 200

# 设备登记相关

@equipment_bp.route('/register', methods=['POST'])
@jwt_required()
def register_equipment():
    """登记设备"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    required_fields = ['campus_id', 'equipment_type', 'equipment_name', 'location', 'contact']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    campus_id = data['campus_id']
    equipment_type = data['equipment_type']
    equipment_name = data['equipment_name']
    location = data['location']
    is_shared = data.get('is_shared', False)
    contact = data['contact']
    notes = data.get('notes', '')
    
    # 验证校区
    campus = Campus.query.get(campus_id)
    if not campus:
        return jsonify({'error': 'Campus not found'}), 404
    
    # 解析放置时间
    placed_at = datetime.utcnow()
    if 'placed_at' in data:
        try:
            placed_at = datetime.fromisoformat(data['placed_at'])
        except ValueError:
            pass
    
    try:
        equipment = Equipment(
            user_id=user_id,
            campus_id=campus_id,
            equipment_type=equipment_type,
            equipment_name=equipment_name,
            location=location,
            is_shared=is_shared,
            contact=contact,
            notes=notes,
            placed_at=placed_at
        )
        
        db.session.add(equipment)
        db.session.commit()
        
        return jsonify({
            'message': 'Equipment registered successfully',
            'equipment': equipment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/list', methods=['GET'])
def get_equipment_list():
    """获取设备列表"""
    campus_id = request.args.get('campus_id', type=int)
    is_shared = request.args.get('is_shared', type=lambda x: x.lower() == 'true')
    equipment_type = request.args.get('equipment_type')
    
    query = Equipment.query
    
    if campus_id:
        query = query.filter_by(campus_id=campus_id)
    
    if is_shared is not None:
        query = query.filter_by(is_shared=is_shared)
    
    if equipment_type:
        query = query.filter_by(equipment_type=equipment_type)
    
    equipment_list = query.order_by(Equipment.placed_at.desc()).all()
    
    return jsonify([e.to_dict() for e in equipment_list]), 200

@equipment_bp.route('/my-equipment', methods=['GET'])
@jwt_required()
def get_my_equipment():
    """获取我的设备"""
    user_id = int(get_jwt_identity())
    
    equipment_list = Equipment.query.filter_by(user_id=user_id).order_by(
        Equipment.placed_at.desc()
    ).all()
    
    return jsonify([e.to_dict() for e in equipment_list]), 200

@equipment_bp.route('/<int:equipment_id>', methods=['PUT'])
@jwt_required()
def update_equipment(equipment_id):
    """更新设备信息"""
    user_id = int(get_jwt_identity())
    
    equipment = Equipment.query.get(equipment_id)
    
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    # 只有设备所有者可以更新
    if equipment.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # 可更新的字段
    if 'equipment_type' in data:
        equipment.equipment_type = data['equipment_type']
    if 'equipment_name' in data:
        equipment.equipment_name = data['equipment_name']
    if 'location' in data:
        equipment.location = data['location']
    if 'is_shared' in data:
        equipment.is_shared = data['is_shared']
    if 'contact' in data:
        equipment.contact = data['contact']
    if 'notes' in data:
        equipment.notes = data['notes']
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Equipment updated successfully',
            'equipment': equipment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>', methods=['DELETE'])
@jwt_required()
def delete_equipment(equipment_id):
    """删除设备"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    equipment = Equipment.query.get(equipment_id)
    
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    # 只有设备所有者或管理员可以删除
    if equipment.user_id != user_id and not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(equipment)
        db.session.commit()
        
        return jsonify({'message': 'Equipment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/types', methods=['GET'])
def get_equipment_types():
    """获取设备类型列表"""
    # 从数据库中获取所有不同的设备类型
    types = db.session.query(Equipment.equipment_type).distinct().all()
    
    return jsonify([t[0] for t in types if t[0]]), 200
