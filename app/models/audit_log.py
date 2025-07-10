from app.extensions import db
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.orm import attributes

class AuditLog(db.Model):
    """Modelo para registrar logs de auditoria do sistema"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    table_name = db.Column(db.String(100), nullable=False)  # Nome da tabela/modelo
    record_id = db.Column(db.Integer, nullable=True)  # ID do registro afetado
    old_values = db.Column(db.Text, nullable=True)  # Valores antigos (JSON)
    new_values = db.Column(db.Text, nullable=True)  # Valores novos (JSON)
    description = db.Column(db.Text, nullable=True)  # Descrição da ação
    ip_address = db.Column(db.String(45), nullable=True)  # IP do usuário
    user_agent = db.Column(db.Text, nullable=True)  # User agent do navegador
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com usuário
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.table_name}:{self.record_id}>'
    
    @classmethod
    def log_action(cls, action, table_name, record_id=None, old_values=None, 
                   new_values=None, description=None, user_id=None, 
                   ip_address=None, user_agent=None):
        """Método para registrar uma ação no log"""
        try:
            log_entry = cls(
                user_id=user_id,
                action=action,
                table_name=table_name,
                record_id=record_id,
                old_values=old_values,
                new_values=new_values,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            # Se houver erro ao salvar o log, não quebrar a aplicação
            db.session.rollback()
            print(f"Erro ao salvar log de auditoria: {e}")
    
    @classmethod
    def log_user_action(cls, action, description=None, user_id=None, 
                       ip_address=None, user_agent=None):
        """Método específico para ações de usuário"""
        return cls.log_action(
            action=action,
            table_name='users',
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @classmethod
    def log_model_change(cls, action, model_instance, old_values=None, 
                        new_values=None, description=None, user_id=None,
                        ip_address=None, user_agent=None):
        """Método para registrar mudanças em modelos"""
        table_name = model_instance.__tablename__
        record_id = getattr(model_instance, 'id', None)
        
        return cls.log_action(
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

# Funções para capturar mudanças automaticamente
def setup_audit_logging():
    """Configura o logging automático para modelos específicos"""
    from app.models import User, Subscription, Marina, Berth, SubscriptionPlan, Payment
    
    models_to_audit = [User, Subscription, Marina, Berth, SubscriptionPlan, Payment]
    
    for model in models_to_audit:
        # Capturar inserções
        @event.listens_for(model, 'after_insert')
        def after_insert(mapper, connection, target):
            AuditLog.log_model_change(
                action='CREATE',
                model_instance=target,
                new_values=str(target.__dict__),
                description=f'Novo {target.__class__.__name__} criado'
            )
        
        # Capturar atualizações
        @event.listens_for(model, 'after_update')
        def after_update(mapper, connection, target):
            # Capturar valores antigos e novos
            state = attributes.instance_state(target)
            changes = {}
            old_values = {}
            
            for attr in state.attrs:
                if attr.history.has_changes():
                    old_values[attr.key] = attr.history.deleted[0] if attr.history.deleted else None
                    changes[attr.key] = attr.value
            
            if changes:
                AuditLog.log_model_change(
                    action='UPDATE',
                    model_instance=target,
                    old_values=str(old_values),
                    new_values=str(changes),
                    description=f'{target.__class__.__name__} atualizado'
                )
        
        # Capturar exclusões
        @event.listens_for(model, 'after_delete')
        def after_delete(mapper, connection, target):
            AuditLog.log_model_change(
                action='DELETE',
                model_instance=target,
                old_values=str(target.__dict__),
                description=f'{target.__class__.__name__} excluído'
            ) 