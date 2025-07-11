from app.extensions import db
from datetime import datetime
import uuid

class Berth(db.Model):
    __tablename__ = 'berths'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    marina_id = db.Column(db.Integer, db.ForeignKey('marinas.id'), nullable=False)
    
    # Identificação da vaga
    berth_number = db.Column(db.String(20), nullable=False)
    berth_type = db.Column(db.String(50), nullable=False)  # flutuante, píer, box, etc.
    
    # Características
    length = db.Column(db.Float)  # Comprimento em metros
    width = db.Column(db.Float)   # Largura em metros
    depth = db.Column(db.Float)   # Profundidade em metros
    max_boat_length = db.Column(db.Float)  # Comprimento máximo da embarcação
    
    # Status e disponibilidade
    status = db.Column(db.String(20), default='available')  # available, occupied, maintenance, reserved
    is_active = db.Column(db.Boolean, default=True)
    
    # Preços
    daily_rate = db.Column(db.Numeric(10, 2))
    monthly_rate = db.Column(db.Numeric(10, 2))
    yearly_rate = db.Column(db.Numeric(10, 2))
    
    # Informações adicionais
    description = db.Column(db.Text)
    amenities = db.Column(db.Text)  # JSON string com comodidades
    restrictions = db.Column(db.Text)  # Restrições específicas
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_available(self):
        """Verifica se a vaga está disponível"""
        return self.status == 'available' and self.is_active
    
    @property
    def current_subscription(self):
        """Retorna a assinatura ativa desta vaga"""
        from app.models.subscription import Subscription
        return Subscription.query.filter_by(berth_id=self.id, is_active=True).first()
    
    @property
    def dimensions(self):
        """Retorna as dimensões formatadas"""
        if self.length and self.width:
            return f"{self.length}m x {self.width}m"
        return "Não informado"
    
    def get_occupancy_history(self):
        """Retorna o histórico de ocupação da vaga"""
        from app.models.berth_occupancy_history import BerthOccupancyHistory
        return BerthOccupancyHistory.query.filter_by(berth_id=self.id).order_by(BerthOccupancyHistory.start_date.desc()).all()
    
    def add_occupancy_record(self, status, user_id=None, subscription_id=None, reason=None, notes=None):
        """Adiciona um registro ao histórico de ocupação"""
        from app.models.berth_occupancy_history import BerthOccupancyHistory
        
        # Finalizar registro ativo anterior se existir
        active_record = BerthOccupancyHistory.query.filter_by(
            berth_id=self.id, 
            end_date=None
        ).first()
        
        if active_record:
            active_record.end_date = datetime.utcnow()
        
        # Criar novo registro
        new_record = BerthOccupancyHistory(
            berth_id=self.id,
            status=status,
            user_id=user_id,
            subscription_id=subscription_id,
            start_date=datetime.utcnow(),
            reason=reason,
            notes=notes
        )
        
        db.session.add(new_record)
        return new_record
    
    def get_current_occupancy(self):
        """Retorna o registro de ocupação atual"""
        from app.models.berth_occupancy_history import BerthOccupancyHistory
        return BerthOccupancyHistory.query.filter_by(
            berth_id=self.id, 
            end_date=None
        ).first()
    
    def get_status_display(self):
        """Retorna o nome de exibição do status"""
        status_names = {
            'available': 'Disponível',
            'occupied': 'Ocupada',
            'maintenance': 'Manutenção',
            'reserved': 'Reservada',
            'inactive': 'Inativa'
        }
        return status_names.get(self.status, 'Desconhecido')
    
    def __repr__(self):
        return f'<Berth {self.berth_number} - {self.marina_id}>' 