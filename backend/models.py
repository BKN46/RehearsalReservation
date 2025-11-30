from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    equipment_borrows = db.relationship('EquipmentBorrow', backref='user', lazy=True)
    equipment_registrations = db.relationship('Equipment', backref='owner', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Campus(db.Model):
    __tablename__ = 'campuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    reservations = db.relationship('Reservation', backref='campus', lazy=True)
    unavailable_times = db.relationship('UnavailableTime', backref='campus', lazy=True)
    key_managers = db.relationship('KeyManager', backref='campus', lazy=True)
    equipment = db.relationship('Equipment', backref='campus', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_hour = db.Column(db.Integer, nullable=False)  # 8-22
    end_hour = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, cancelled
    key_picked_up = db.Column(db.Boolean, default=False)
    key_pickup_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_reservation_date_campus', 'date', 'campus_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'student_id': self.user.student_id,
            'campus_id': self.campus_id,
            'campus_name': self.campus.name,
            'date': self.date.isoformat(),
            'start_hour': self.start_hour,
            'end_hour': self.end_hour,
            'status': self.status,
            'key_picked_up': self.key_picked_up,
            'key_pickup_time': self.key_pickup_time.isoformat() if self.key_pickup_time else None,
            'created_at': self.created_at.isoformat()
        }

class UnavailableTime(db.Model):
    __tablename__ = 'unavailable_times'
    
    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_hour = db.Column(db.Integer, nullable=False)
    end_hour = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'campus_id': self.campus_id,
            'campus_name': self.campus.name,
            'date': self.date.isoformat(),
            'start_hour': self.start_hour,
            'end_hour': self.end_hour,
            'reason': self.reason,
            'created_at': self.created_at.isoformat()
        }

class KeyManager(db.Model):
    __tablename__ = 'key_managers'
    
    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'campus_id': self.campus_id,
            'campus_name': self.campus.name,
            'name': self.name,
            'contact': self.contact,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)  # 吉他、键盘、鼓等
    equipment_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_shared = db.Column(db.Boolean, default=False)
    contact = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'owner_name': self.owner.name,
            'campus_id': self.campus_id,
            'campus_name': self.campus.name,
            'equipment_type': self.equipment_type,
            'equipment_name': self.equipment_name,
            'location': self.location,
            'is_shared': self.is_shared,
            'contact': self.contact,
            'notes': self.notes,
            'placed_at': self.placed_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }

class EquipmentBorrow(db.Model):
    __tablename__ = 'equipment_borrows'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    equipment_name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50))
    borrow_time = db.Column(db.DateTime, default=datetime.utcnow)
    return_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')  # borrowed, returned
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'student_id': self.user.student_id,
            'equipment_name': self.equipment_name,
            'equipment_type': self.equipment_type,
            'borrow_time': self.borrow_time.isoformat(),
            'return_time': self.return_time.isoformat() if self.return_time else None,
            'status': self.status,
            'notes': self.notes
        }

def init_db():
    """Initialize database with default data"""
    db.create_all()
    
    # Create campuses if they don't exist
    if Campus.query.count() == 0:
        campuses = [
            Campus(name='学院路校区'),
            Campus(name='沙河校区')
        ]
        for campus in campuses:
            db.session.add(campus)
        db.session.commit()
        print('Campuses initialized')
    
    # Create default admin user if none exists
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            student_id='admin',
            name='管理员',
            email='admin@buaa.edu.cn',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Default admin created: admin@buaa.edu.cn / admin123')
