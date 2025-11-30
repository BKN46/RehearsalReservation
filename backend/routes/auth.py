from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
import re

auth_bp = Blueprint('auth', __name__)

def validate_buaa_email(email):
    """验证是否为BUAA邮箱"""
    return email.endswith('@buaa.edu.cn')

def validate_student_id(student_id):
    """验证学号格式"""
    return len(student_id) > 0 and len(student_id) <= 20

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['student_id', 'name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    student_id = data['student_id']
    name = data['name']
    email = data['email']
    password = data['password']
    phone = data.get('phone')
    
    # 验证邮箱格式
    if not validate_buaa_email(email):
        return jsonify({'error': 'Email must end with @buaa.edu.cn'}), 400
    
    # 验证学号格式
    if not validate_student_id(student_id):
        return jsonify({'error': 'Invalid student ID'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(student_id=student_id).first():
        return jsonify({'error': 'Student ID already registered'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # 创建新用户
    user = User(
        student_id=student_id,
        name=name,
        email=email,
        phone=phone
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # 创建访问令牌
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # 查找用户
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # 检查用户是否被禁用
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    # 创建访问令牌
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前登录用户信息"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # 可更新的字段
    if 'name' in data:
        user.name = data['name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
