from app.extensions import db
from datetime import datetime

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    marina_service_id = db.Column(db.Integer, db.ForeignKey('marina_services.id'), nullable=False)
    marina_id = db.Column(db.Integer, db.ForeignKey('marinas.id'), nullable=False)
    berth_id = db.Column(db.Integer, db.ForeignKey('berths.id'), nullable=True)
    
    # Informações da embarcação
    vessel_name = db.Column(db.String(100), nullable=False)
    vessel_type = db.Column(db.String(50))  # Iate, Lancha, Veleiro, etc.
    vessel_length = db.Column(db.Numeric(5, 2))  # Comprimento em metros
    
    # Agendamento
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.Time, nullable=False)
    scheduled_date = db.Column(db.DateTime)  # Data/hora confirmada pelo admin
    completed_date = db.Column(db.DateTime)  # Data/hora de conclusão
    
    # Status e observações
    status = db.Column(db.String(20), default='requested')  # requested, scheduled, in_progress, completed, cancelled
    notes = db.Column(db.Text)  # Observações do cliente
    admin_notes = db.Column(db.Text)  # Observações do administrador
    
    # Preços
    original_price = db.Column(db.Numeric(10, 2), nullable=False)
    final_price = db.Column(db.Numeric(10, 2))  # Preço final após ajustes
    
    # Pagamento
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)
    
    # Fotos (opcional)
    before_photos = db.Column(db.Text)  # JSON com URLs das fotos
    after_photos = db.Column(db.Text)  # JSON com URLs das fotos
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='service_requests')
    marina_service = db.relationship('MarinaService', foreign_keys=[marina_service_id])
    marina = db.relationship('Marina', backref='service_requests')
    berth = db.relationship('Berth', backref='service_requests')
    payment = db.relationship('Payment', backref='service_request')
    
    @property
    def status_display(self):
        """Retorna o status em português"""
        status_map = {
            'requested': 'Solicitado',
            'scheduled': 'Agendado',
            'in_progress': 'Em Andamento',
            'completed': 'Concluído',
            'cancelled': 'Cancelado'
        }
        return status_map.get(self.status, self.status)
    
    @property
    def payment_status_display(self):
        """Retorna o status do pagamento em português"""
        status_map = {
            'pending': 'Pendente',
            'paid': 'Pago',
            'cancelled': 'Cancelado'
        }
        return status_map.get(self.payment_status, self.payment_status)
    
    def schedule(self, scheduled_date, admin_notes=None):
        """Agendar o serviço"""
        self.status = 'scheduled'
        self.scheduled_date = scheduled_date
        if admin_notes:
            self.admin_notes = admin_notes
    
    def start_service(self):
        """Iniciar o serviço"""
        self.status = 'in_progress'
    
    def complete_service(self, final_price=None, admin_notes=None):
        """Concluir o serviço"""
        self.status = 'completed'
        self.completed_date = datetime.utcnow()
        if final_price:
            self.final_price = final_price
        if admin_notes:
            self.admin_notes = admin_notes
    
    def cancel_service(self, admin_notes=None):
        """Cancelar o serviço"""
        self.status = 'cancelled'
        if admin_notes:
            self.admin_notes = admin_notes
    
    def __repr__(self):
        return f'<ServiceRequest {self.id} - {self.marina_service.name} - {self.status}>' 