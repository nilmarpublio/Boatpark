from app.extensions import db
from datetime import datetime

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    marina_id = db.Column(db.Integer, db.ForeignKey('marinas.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)  # Duração estimada em minutos
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    marina = db.relationship('Marina', backref='service_types')
    service_requests = db.relationship('ServiceRequest', lazy=True)
    
    def __repr__(self):
        return f'<Service {self.name} - R$ {self.price}>' 