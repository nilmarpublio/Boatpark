from app.extensions import db
from datetime import datetime
import uuid

class SystemConfig(db.Model):
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Configurações de pagamento
    payment_reminder_days = db.Column(db.Integer, default=3)  # Dias antes do vencimento
    payment_overdue_days = db.Column(db.Integer, default=1)   # Dias após vencimento para suspensão
    vessel_removal_days = db.Column(db.Integer, default=7)    # Dias para retirada da embarcação
    
    # Mensagens de aviso
    payment_reminder_message = db.Column(db.Text, default='Seu pagamento vence em {days} dias. Evite a suspensão da sua assinatura.')
    payment_overdue_message = db.Column(db.Text, default='Seu pagamento está em atraso. Sua assinatura foi suspensa.')
    vessel_removal_message = db.Column(db.Text, default='Sua embarcação deve ser retirada em {days} dias devido ao não pagamento.')
    
    # Configurações de notificação
    send_email_notifications = db.Column(db.Boolean, default=True)
    send_sms_notifications = db.Column(db.Boolean, default=False)
    send_push_notifications = db.Column(db.Boolean, default=True)
    
    # Configurações gerais
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text, default='Sistema em manutenção. Volte em breve.')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração do sistema (cria se não existir)"""
        config = cls.query.first()
        if not config:
            config = cls()
            db.session.add(config)
            db.session.commit()
        return config
    
    def format_message(self, message_template, **kwargs):
        """Formata uma mensagem com os parâmetros fornecidos"""
        try:
            return message_template.format(**kwargs)
        except KeyError:
            return message_template
    
    def get_payment_reminder_message(self, days):
        """Retorna a mensagem de lembrete de pagamento formatada"""
        return self.format_message(self.payment_reminder_message, days=days)
    
    def get_vessel_removal_message(self, days):
        """Retorna a mensagem de retirada de embarcação formatada"""
        return self.format_message(self.vessel_removal_message, days=days)
    
    def __repr__(self):
        return f'<SystemConfig {self.id}>' 