from flask import request, g
from flask_login import current_user
from app.models import AuditLog
import json

class AuditMiddleware:
    """Middleware para capturar informações de auditoria"""
    
    def __init__(self, app):
        self.app = app
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Executado antes de cada requisição"""
        # Capturar informações do usuário e IP
        g.audit_user_id = current_user.id if current_user.is_authenticated else None
        g.audit_ip_address = request.remote_addr
        g.audit_user_agent = request.headers.get('User-Agent')
    
    def after_request(self, response):
        """Executado após cada requisição"""
        # Log de login/logout
        if request.endpoint == 'auth.login' and response.status_code == 302:
            AuditLog.log_user_action(
                action='LOGIN',
                description=f'Login realizado via {request.form.get("email", "email desconhecido")}',
                user_id=g.audit_user_id,
                ip_address=g.audit_ip_address,
                user_agent=g.audit_user_agent
            )
        elif request.endpoint == 'auth.logout':
            AuditLog.log_user_action(
                action='LOGOUT',
                description='Logout realizado',
                user_id=g.audit_user_id,
                ip_address=g.audit_ip_address,
                user_agent=g.audit_user_agent
            )
        
        return response

def log_admin_action(action, description, record_id=None, old_values=None, new_values=None):
    """Função helper para logar ações administrativas"""
    from flask import g, request
    
    AuditLog.log_action(
        action=action,
        table_name='admin_actions',
        record_id=record_id,
        old_values=json.dumps(old_values) if old_values else None,
        new_values=json.dumps(new_values) if new_values else None,
        description=description,
        user_id=g.audit_user_id if hasattr(g, 'audit_user_id') else None,
        ip_address=g.audit_ip_address if hasattr(g, 'audit_ip_address') else None,
        user_agent=g.audit_user_agent if hasattr(g, 'audit_user_agent') else None
    ) 