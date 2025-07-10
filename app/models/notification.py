from app.extensions import db
from datetime import datetime
import uuid

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informações da notificação
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')  # info, success, warning, error
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    
    # Rastreamento
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Dados adicionais
    data = db.Column(db.Text)  # JSON string com dados extras
    action_url = db.Column(db.String(500))  # URL para ação
    action_text = db.Column(db.String(100))  # Texto do botão de ação
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    
    # Relacionamentos
    created_by_user = db.relationship('User', foreign_keys=[created_by], backref='created_notifications', lazy=True)
    
    def mark_as_read(self):
        """Marca a notificação como lida"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def mark_as_sent(self):
        """Marca a notificação como enviada"""
        self.is_sent = True
        self.sent_at = datetime.utcnow()
    
    @property
    def is_recent(self):
        """Verifica se a notificação é recente (últimas 24h)"""
        delta = datetime.utcnow() - self.created_at
        return delta.days == 0
    
    @property
    def type_icon(self):
        """Retorna o ícone baseado no tipo de notificação"""
        icons = {
            'info': 'fas fa-info-circle',
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times-circle'
        }
        return icons.get(self.notification_type, 'fas fa-bell')
    
    @property
    def type_color(self):
        """Retorna a cor baseada no tipo de notificação"""
        colors = {
            'info': 'info',
            'success': 'success',
            'warning': 'warning',
            'error': 'danger'
        }
        return colors.get(self.notification_type, 'secondary')
    
    def __repr__(self):
        return f'<Notification {self.title} - {self.user_id}>' 