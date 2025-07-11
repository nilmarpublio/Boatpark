from app.extensions import db
from datetime import datetime
import uuid

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Informações básicas do plano
    name = db.Column(db.String(50), nullable=False, unique=True)  # Teste, Cobre, Prata, Gold
    display_name = db.Column(db.String(100), nullable=False)  # Nome para exibição
    description = db.Column(db.Text)
    
    # Preços
    monthly_price = db.Column(db.Numeric(10, 2), nullable=False)
    yearly_price = db.Column(db.Numeric(10, 2))
    
    # Características do plano
    max_admins = db.Column(db.Integer, default=1)  # Máximo de administradores
    max_users = db.Column(db.Integer, default=1)  # Máximo de usuários
    max_vessels = db.Column(db.Integer, default=1)  # Máximo de embarcações
    max_berths = db.Column(db.Integer, default=1)  # Máximo de vagas por usuário
    max_services_per_month = db.Column(db.Integer, default=0)  # Máximo de serviços por mês
    max_documents = db.Column(db.Integer, default=0)  # Máximo de documentos
    
    # Permissões específicas
    can_create_services = db.Column(db.Boolean, default=True)
    can_upload_documents = db.Column(db.Boolean, default=True)
    can_make_payments = db.Column(db.Boolean, default=True)
    can_view_reports = db.Column(db.Boolean, default=False)
    can_access_api = db.Column(db.Boolean, default=False)
    
    # Plano de teste (apenas navegação, sem gravações)
    is_test_plan = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)  # Plano em destaque
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    subscriptions = db.relationship('Subscription', lazy=True)
    
    def __repr__(self):
        return f'<SubscriptionPlan {self.name}>'
    
    @property
    def features_list(self):
        """Retorna lista de características do plano"""
        features = []
        
        if self.max_admins > 0:
            features.append(f"Até {self.max_admins} administrador(es)")
        
        if self.max_users > 0:
            features.append(f"Até {self.max_users} usuário(s)")
        
        if self.max_vessels > 0:
            features.append(f"Até {self.max_vessels} embarcação(ões)")
        
        if self.max_berths > 0:
            features.append(f"Até {self.max_berths} vaga(s)")
        
        if self.max_services_per_month > 0:
            features.append(f"Até {self.max_services_per_month} serviços/mês")
        elif self.max_services_per_month == -1:
            features.append("Serviços ilimitados")
        
        if self.max_documents > 0:
            features.append(f"Até {self.max_documents} documentos")
        elif self.max_documents == -1:
            features.append("Documentos ilimitados")
        
        if self.can_create_services:
            features.append("Solicitar serviços")
        
        if self.can_upload_documents:
            features.append("Upload de documentos")
        
        if self.can_view_reports:
            features.append("Relatórios detalhados")
        
        if self.can_access_api:
            features.append("Acesso à API")
        
        if self.is_test_plan:
            features.append("Apenas navegação (sem gravações)")
        
        return features
    
    def can_perform_action(self, action):
        """Verifica se o plano permite uma determinada ação"""
        action_permissions = {
            'create_service': self.can_create_services,
            'upload_document': self.can_upload_documents,
            'make_payment': self.can_make_payments,
            'view_reports': self.can_view_reports,
            'access_api': self.can_access_api,
            'save_data': not self.is_test_plan  # Plano de teste não pode salvar dados
        }
        
        return action_permissions.get(action, False)
    
    def check_service_limit(self, current_count):
        """Verifica se o usuário ainda pode solicitar serviços"""
        if self.max_services_per_month == -1:  # Ilimitado
            return True
        return current_count < self.max_services_per_month
    
    def check_document_limit(self, current_count):
        """Verifica se o usuário ainda pode fazer upload de documentos"""
        if self.max_documents == -1:  # Ilimitado
            return True
        return current_count < self.max_documents 