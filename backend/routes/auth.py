from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from datetime import datetime, timedelta
import secrets
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
    
    # 创建新用户（默认禁用状态，需要管理员启用）
    user = User(
        student_id=student_id,
        name=name,
        email=email,
        phone=phone,
        is_active=False  # 新用户默认禁用
    )
    user.set_password(password)
    
    # 如果启用了邮箱验证，生成验证令牌并发送邮件
    email_verification_enabled = current_app.config.get('EMAIL_VERIFICATION_ENABLED', False)
    email_sent = False
    
    if email_verification_enabled:
        try:
            from email_service import send_verification_email
            
            # 生成验证令牌
            verification_token = secrets.token_urlsafe(32)
            user.verification_token = verification_token
            user.verification_token_expires = datetime.utcnow() + timedelta(minutes=30)
            
            # 发送验证邮件
            email_sent = send_verification_email(email, name, verification_token)
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
    
    try:
        db.session.add(user)
        db.session.commit()
        
        response_data = {
            'user': user.to_dict(),
            'requires_activation': True
        }
        
        if email_verification_enabled:
            if email_sent:
                response_data['message'] = 'Registration successful. Please check your email to verify your account.'
                response_data['email_sent'] = True
            else:
                response_data['message'] = 'Registration successful but failed to send verification email. Your account needs to be activated by an administrator.'
                response_data['email_sent'] = False
        else:
            response_data['message'] = 'Registration successful. Your account needs to be activated by an administrator.'
        
        return jsonify(response_data), 201
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
    if 'preferred_campus_id' in data:
        user.preferred_campus_id = data['preferred_campus_id']
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

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """验证邮箱"""
    if not current_app.config.get('EMAIL_VERIFICATION_ENABLED', False):
        return jsonify({'error': 'Email verification is not enabled'}), 400
    
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Verification token is required'}), 400
    
    # 查找用户
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid verification token'}), 400
    
    # 检查令牌是否过期
    if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
        return jsonify({'error': 'Verification token has expired'}), 400
    
    # 验证邮箱
    user.email_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    # 邮箱验证后自动激活账户
    user.is_active = True
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Email verified successfully. Your account is now active.',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """重新发送验证邮件"""
    if not current_app.config.get('EMAIL_VERIFICATION_ENABLED', False):
        return jsonify({'error': 'Email verification is not enabled'}), 400
    
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.email_verified:
        return jsonify({'error': 'Email already verified'}), 400
    
    try:
        from email_service import send_verification_email
        
        # 生成新的验证令牌
        verification_token = secrets.token_urlsafe(32)
        user.verification_token = verification_token
        user.verification_token_expires = datetime.utcnow() + timedelta(minutes=30)
        
        db.session.commit()
        
        # 发送验证邮件
        email_sent = send_verification_email(email, user.name, verification_token)
        
        if email_sent:
            return jsonify({
                'message': 'Verification email sent successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send verification email'
            }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/check-verification-status', methods=['GET'])
@jwt_required()
def check_verification_status():
    """检查当前用户的邮箱验证状态"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'email_verified': user.email_verified,
        'email_verification_enabled': current_app.config.get('EMAIL_VERIFICATION_ENABLED', False)
    }), 200
