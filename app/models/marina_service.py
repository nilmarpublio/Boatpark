from app.extensions import db
from datetime import datetime

class MarinaService(db.Model):
    """Serviços oferecidos pela marina"""
    __tablename__ = 'marina_services'
    
    id = db.Column(db.Integer, primary_key=True)
    marina_id = db.Column(db.Integer, db.ForeignKey('marinas.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Limpeza, Manutenção, Segurança, etc.
    price = db.Column(db.Numeric(10, 2), nullable=False)
    price_type = db.Column(db.String(20), default='fixed')  # fixed, hourly, daily, monthly
    is_active = db.Column(db.Boolean, default=True)
    requires_approval = db.Column(db.Boolean, default=False)
    max_duration_hours = db.Column(db.Integer)  # Para serviços por hora
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    marina = db.relationship('Marina', backref='marina_services')
    service_requests = db.relationship('ServiceRequest', backref='service', lazy=True)
    
    def __repr__(self):
        return f'<MarinaService {self.name} - R$ {self.price}>'
    
    @property
    def formatted_price(self):
        """Retorna o preço formatado com tipo"""
        if self.price_type == 'hourly':
            return f"R$ {float(self.price):.2f}/hora"
        elif self.price_type == 'daily':
            return f"R$ {float(self.price):.2f}/dia"
        elif self.price_type == 'monthly':
            return f"R$ {float(self.price):.2f}/mês"
        else:
            return f"R$ {float(self.price):.2f}"

class UserServiceSelection(db.Model):
    """Serviços selecionados pelo usuário"""
    __tablename__ = 'user_service_selections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    marina_service_id = db.Column(db.Integer, db.ForeignKey('marina_services.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    is_selected = db.Column(db.Boolean, default=False)
    custom_price = db.Column(db.Numeric(10, 2))  # Preço personalizado se aplicável
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='service_selections')
    marina_service = db.relationship('MarinaService')
    subscription = db.relationship('Subscription', backref='service_selections')
    
    def __repr__(self):
        return f'<UserServiceSelection {self.user.email} - {self.marina_service.name}>' 