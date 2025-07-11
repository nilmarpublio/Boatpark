from app.extensions import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import hashlib
import secrets
from flask import current_app

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True)
    
    # Endereço completo
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(10))
    country = db.Column(db.String(50), default='Brasil')
    
    # Tipo de usuário: 'user', 'admin', 'superadmin'
    user_type = db.Column(db.String(20), default='user', nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100))
    reset_password_token = db.Column(db.String(100))
    reset_password_expires = db.Column(db.DateTime)
    asaas_customer_id = db.Column(db.String(50))  # ID do cliente no ASAAS
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relacionamentos
    documents = db.relationship('Document', backref='user', lazy=True)
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='user', lazy=True)
    subscriptions = db.relationship('Subscription', lazy=True)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        """Retorna o endereço completo formatado"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        if self.country and self.country != 'Brasil':
            parts.append(self.country)
        
        return ', '.join(parts) if parts else 'Endereço não informado'
    
    @property
    def is_subscriber(self):
        """Verifica se o usuário tem uma assinatura ativa"""
        from app.models.subscription import Subscription
        return Subscription.query.filter_by(user_id=self.id, is_active=True).first() is not None
    
    @property
    def active_subscription(self):
        """Retorna a assinatura ativa do usuário"""
        from app.models.subscription import Subscription
        return Subscription.query.filter_by(user_id=self.id, is_active=True).first()
    
    def get_active_subscription(self):
        """Retorna a assinatura ativa do usuário"""
        from app.models.subscription import Subscription
        return Subscription.query.filter_by(user_id=self.id, is_active=True).first()
    
    def generate_auth_token(self):
        """Gera um token de autenticação simples"""
        token_data = f"{self.id}:{self.email}:{datetime.utcnow().timestamp()}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        return f"{self.id}.{token_hash}"
    
    def verify_auth_token(self, token):
        """Verifica se um token é válido"""
        try:
            parts = token.split('.')
            if len(parts) != 2:
                return False
            
            user_id, token_hash = parts
            if int(user_id) != self.id:
                return False
            
            # Verificar se o token ainda é válido (24 horas)
            token_data = f"{self.id}:{self.email}:{datetime.utcnow().timestamp()}"
            expected_hash = hashlib.sha256(token_data.encode()).hexdigest()
            
            return token_hash == expected_hash
        except:
            return False
    
    def set_password(self, password):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_verified(self):
        """Alias para email_verified"""
        return self.email_verified
    
    @property
    def is_superadmin(self):
        """Verifica se o usuário é superadmin"""
        return self.user_type == 'superadmin'
    
    @property
    def is_regular_admin(self):
        """Verifica se o usuário é admin regular (não superadmin)"""
        return self.user_type == 'admin'
    
    @property
    def is_regular_user(self):
        """Verifica se o usuário é usuário regular"""
        return self.user_type == 'user'
    
    @property
    def role_display_name(self):
        """Retorna o nome de exibição do papel do usuário"""
        role_names = {
            'user': 'Usuário',
            'admin': 'Administrador',
            'superadmin': 'Super Administrador'
        }
        return role_names.get(self.user_type, 'Desconhecido')
    
    def has_permission(self, permission):
        """Verifica se o usuário tem uma determinada permissão"""
        # Superadmin tem todas as permissões
        if self.is_superadmin:
            return True
        
        # Admin tem permissões administrativas
        if self.is_regular_admin and permission in ['admin_access', 'user_management', 'marina_management']:
            return True
        
        # Usuário regular tem permissões básicas
        if self.is_regular_user and permission in ['basic_access', 'service_request']:
            return True
        
        return False
    
    def __repr__(self):
        return f'<User {self.email} ({self.user_type})>' 