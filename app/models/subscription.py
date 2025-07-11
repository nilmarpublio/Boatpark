from app.extensions import db
from datetime import datetime, timedelta
import uuid

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    marina_id = db.Column(db.Integer, db.ForeignKey('marinas.id'), nullable=False)
    berth_id = db.Column(db.Integer, db.ForeignKey('berths.id'), nullable=False)
    
    # Informações da assinatura
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)  # daily, monthly, yearly
    plan_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Status da assinatura
    status = db.Column(db.String(20), default='active')  # active, suspended, cancelled, expired
    is_active = db.Column(db.Boolean, default=True)
    
    # Datas importantes
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    next_billing_date = db.Column(db.DateTime)
    
    # Integração ASAAS
    asaas_subscription_id = db.Column(db.String(50))
    asaas_customer_id = db.Column(db.String(50))
    
    # Configurações de cobrança
    billing_cycle = db.Column(db.String(20), default='monthly')  # daily, weekly, monthly, yearly
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', foreign_keys=[user_id])
    marina = db.relationship('Marina', foreign_keys=[marina_id])
    berth = db.relationship('Berth', foreign_keys=[berth_id])
    subscription_plan = db.relationship('SubscriptionPlan', foreign_keys=[plan_id])
    payments = db.relationship('Payment', backref='subscription', lazy='dynamic')
    
    @property
    def plan(self):
        """Alias para subscription_plan para facilitar o acesso"""
        return self.subscription_plan
    
    @property
    def is_expired(self):
        """Verifica se a assinatura expirou"""
        if not self.end_date:
            return False
        return datetime.utcnow() > self.end_date
    
    @property
    def days_until_expiry(self):
        """Retorna os dias até a expiração"""
        if not self.end_date:
            return None
        delta = self.end_date - datetime.utcnow()
        return delta.days
    
    @property
    def total_paid(self):
        """Retorna o total pago até o momento"""
        return sum(payment.amount for payment in self.payments.all() if payment.status == 'confirmed')
    
    @property
    def next_payment_amount(self):
        """Retorna o valor do próximo pagamento"""
        return self.amount
    
    def calculate_next_billing_date(self):
        """Calcula a próxima data de cobrança"""
        if not self.next_billing_date:
            self.next_billing_date = self.start_date
        
        if self.billing_cycle == 'daily':
            self.next_billing_date += timedelta(days=1)
        elif self.billing_cycle == 'weekly':
            self.next_billing_date += timedelta(weeks=1)
        elif self.billing_cycle == 'monthly':
            # Adiciona um mês
            if self.next_billing_date.month == 12:
                self.next_billing_date = self.next_billing_date.replace(year=self.next_billing_date.year + 1, month=1)
            else:
                self.next_billing_date = self.next_billing_date.replace(month=self.next_billing_date.month + 1)
        elif self.billing_cycle == 'yearly':
            self.next_billing_date = self.next_billing_date.replace(year=self.next_billing_date.year + 1)
    
    def suspend(self):
        """Suspende a assinatura"""
        self.status = 'suspended'
        self.is_active = False
    
    def activate(self):
        """Ativa a assinatura"""
        self.status = 'active'
        self.is_active = True
    
    def cancel(self):
        """Cancela a assinatura"""
        self.status = 'cancelled'
        self.is_active = False
        self.auto_renew = False
    
    def can_perform_action(self, action):
        """Verifica se a assinatura permite uma determinada ação"""
        if not self.subscription_plan:
            return False
        return self.subscription_plan.can_perform_action(action)
    
    def check_service_limit(self, current_count):
        """Verifica se ainda pode solicitar serviços"""
        if not self.subscription_plan:
            return False
        return self.subscription_plan.check_service_limit(current_count)
    
    def check_document_limit(self, current_count):
        """Verifica se ainda pode fazer upload de documentos"""
        if not self.subscription_plan:
            return False
        return self.subscription_plan.check_document_limit(current_count)
    
    def __repr__(self):
        return f'<Subscription {self.plan_name} - {self.user_id}>' 