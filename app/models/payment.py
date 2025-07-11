from app.extensions import db
from datetime import datetime
import uuid

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    
    # Informações do pagamento
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='BRL')
    payment_method = db.Column(db.String(50))  # credit_card, bank_slip, pix, etc.
    
    # Status do pagamento
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, overdue, refunded
    due_date = db.Column(db.DateTime, nullable=False)
    paid_date = db.Column(db.DateTime)
    
    # Integração ASAAS
    asaas_payment_id = db.Column(db.String(50), unique=True)
    asaas_invoice_url = db.Column(db.String(500))
    asaas_bank_slip_url = db.Column(db.String(500))
    asaas_pix_qr_code = db.Column(db.Text)
    asaas_pix_qr_code_url = db.Column(db.String(500))
    
    # Informações adicionais
    description = db.Column(db.Text)
    external_reference = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_overdue(self):
        """Verifica se o pagamento está vencido"""
        return datetime.utcnow() > self.due_date and self.status == 'pending'
    
    @property
    def days_overdue(self):
        """Retorna os dias de atraso"""
        if not self.is_overdue:
            return 0
        delta = datetime.utcnow() - self.due_date
        return delta.days
    
    @property
    def payment_url(self):
        """Retorna a URL de pagamento baseada no método"""
        if self.payment_method == 'bank_slip' and self.asaas_bank_slip_url:
            return self.asaas_bank_slip_url
        elif self.payment_method == 'pix' and self.asaas_pix_qr_code_url:
            return self.asaas_pix_qr_code_url
        elif self.asaas_invoice_url:
            return self.asaas_invoice_url
        return None
    
    def confirm_payment(self, paid_date=None):
        """Confirma o pagamento"""
        self.status = 'confirmed'
        self.paid_date = paid_date or datetime.utcnow()
    
    def cancel_payment(self):
        """Cancela o pagamento"""
        self.status = 'cancelled'
    
    def mark_as_overdue(self):
        """Marca o pagamento como vencido"""
        self.status = 'overdue'
    
    def check_overdue_and_suspend(self):
        """Verifica se o pagamento está vencido e suspende a assinatura se necessário"""
        from app.models import SystemConfig
        from datetime import timedelta
        
        if self.status != 'pending':
            return False
        
        config = SystemConfig.get_config()
        overdue_date = self.due_date + timedelta(days=config.payment_overdue_days)
        
        if datetime.utcnow() > overdue_date:
            # Suspender assinatura
            if self.subscription:
                self.subscription.suspend()
                self.status = 'overdue'
                
                # Enviar notificação
                from app.services.notification_service import NotificationService
                NotificationService.send_payment_overdue_notification(self)
                
                return True
        
        return False
    
    def __repr__(self):
        return f'<Payment {self.amount} - {self.status}>' 