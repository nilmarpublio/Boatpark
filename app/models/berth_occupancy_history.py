from app.extensions import db
from datetime import datetime
import uuid

class BerthOccupancyHistory(db.Model):
    __tablename__ = 'berth_occupancy_history'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    berth_id = db.Column(db.Integer, db.ForeignKey('berths.id'), nullable=False)
    
    # Status da ocupação
    status = db.Column(db.String(20), nullable=False)  # available, occupied, maintenance, reserved
    
    # Informações da ocupação
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Usuário que ocupou
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))  # Assinatura relacionada
    
    # Período da ocupação
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)  # Null se ainda ativo
    
    # Informações adicionais
    reason = db.Column(db.String(200))  # Motivo da mudança de status
    notes = db.Column(db.Text)  # Observações adicionais
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    berth = db.relationship('Berth', backref='occupancy_history')
    user = db.relationship('User', backref='berth_occupancy_history')
    subscription = db.relationship('Subscription', backref='occupancy_history')
    
    @property
    def duration_days(self):
        """Retorna a duração da ocupação em dias"""
        if self.end_date:
            return (self.end_date - self.start_date).days
        else:
            return (datetime.utcnow() - self.start_date).days
    
    @property
    def is_active(self):
        """Verifica se a ocupação está ativa"""
        return self.end_date is None
    
    @property
    def status_display(self):
        """Retorna o status formatado para exibição"""
        status_map = {
            'available': 'Disponível',
            'occupied': 'Ocupada',
            'maintenance': 'Manutenção',
            'reserved': 'Reservada'
        }
        return status_map.get(self.status, self.status)
    
    def __repr__(self):
        return f'<BerthOccupancyHistory {self.berth_id} - {self.status} - {self.start_date}>' 