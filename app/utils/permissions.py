from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from app.models import SystemConfig

class PermissionManager:
    """Gerenciador de permissões do sistema"""
    
    # Permissões do Superadmin (administração do sistema)
    SUPERADMIN_PERMISSIONS = {
        'system_config': 'Configuração do Sistema',
        'subscription_plans': 'Planos de Assinatura',
        'all_marinas': 'Todas as Marinas',
        'all_users': 'Todos os Usuários',
        'all_subscriptions': 'Todas as Assinaturas',
        'all_payments': 'Todos os Pagamentos',
        'audit_logs': 'Logs de Auditoria',
        'system_reports': 'Relatórios do Sistema',
        'user_management': 'Gestão de Usuários',
        'superadmin_management': 'Gestão de Superadmins'
    }
    
    # Permissões do Admin (administração da marina)
    ADMIN_PERMISSIONS = {
        'marina_management': 'Gestão da Marina',
        'berth_management': 'Gestão de Vagas',
        'service_management': 'Gestão de Serviços',
        'service_requests': 'Solicitações de Serviço',
        'marina_users': 'Usuários da Marina',
        'marina_subscriptions': 'Assinaturas da Marina',
        'marina_payments': 'Pagamentos da Marina',
        'marina_reports': 'Relatórios da Marina',
        'notifications': 'Notificações',
        'documents': 'Documentos'
    }
    
    # Permissões do Usuário
    USER_PERMISSIONS = {
        'profile_management': 'Gestão do Perfil',
        'vessel_management': 'Gestão de Embarcações',
        'service_requests': 'Solicitações de Serviço',
        'subscription_management': 'Gestão de Assinatura',
        'document_upload': 'Upload de Documentos'
    }
    
    @staticmethod
    def get_user_permissions(user):
        """Retorna as permissões de um usuário"""
        if user.is_superadmin:
            return PermissionManager.SUPERADMIN_PERMISSIONS
        elif user.is_regular_admin:
            return PermissionManager.ADMIN_PERMISSIONS
        else:
            return PermissionManager.USER_PERMISSIONS
    
    @staticmethod
    def has_permission(user, permission):
        """Verifica se um usuário tem uma permissão específica"""
        if user.is_superadmin:
            return True  # Superadmin tem todas as permissões
        
        if user.is_regular_admin:
            return permission in PermissionManager.ADMIN_PERMISSIONS
        
        return permission in PermissionManager.USER_PERMISSIONS
    
    @staticmethod
    def can_access_marina(user, marina_id=None):
        """Verifica se um usuário pode acessar uma marina específica"""
        if user.is_superadmin:
            return True  # Superadmin pode acessar todas as marinas
        
        if user.is_regular_admin:
            # Admin só pode acessar a marina que administra
            # Aqui você pode implementar a lógica específica
            # Por exemplo, verificar se o admin está associado à marina
            return True  # Por enquanto, permitir acesso
        
        return False  # Usuários regulares não podem acessar área administrativa
    
    @staticmethod
    def can_manage_user(user, target_user):
        """Verifica se um usuário pode gerenciar outro usuário"""
        if user.is_superadmin:
            return True  # Superadmin pode gerenciar qualquer usuário
        
        if user.is_regular_admin:
            # Admin só pode gerenciar usuários da sua marina
            # e não pode gerenciar superadmins ou outros admins
            if target_user.is_superadmin or target_user.is_regular_admin:
                return False
            return True  # Por enquanto, permitir
        
        return False

def superadmin_required(f):
    """Decorator para rotas que requerem superadmin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Faça login para acessar esta área.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_superadmin:
            flash('Acesso negado. Apenas Super Administradores podem acessar esta área.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para rotas que requerem admin (superadmin ou admin regular)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"DEBUG: admin_required decorator executado")
        print(f"DEBUG: current_user.is_authenticated: {current_user.is_authenticated}")
        print(f"DEBUG: current_user: {current_user}")
        
        if not current_user.is_authenticated:
            print(f"DEBUG: Usuário não autenticado, redirecionando para login")
            flash('Faça login para acessar esta área.', 'warning')
            return redirect(url_for('auth.login'))
        
        print(f"DEBUG: current_user.is_superadmin: {current_user.is_superadmin}")
        print(f"DEBUG: current_user.is_regular_admin: {current_user.is_regular_admin}")
        
        if not (current_user.is_superadmin or current_user.is_regular_admin):
            print(f"DEBUG: Usuário não é admin, redirecionando para dashboard")
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        print(f"DEBUG: Usuário autorizado, executando função")
        return f(*args, **kwargs)
    return decorated_function

def marina_admin_required(f):
    """Decorator para rotas que requerem admin de marina (não superadmin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Faça login para acessar esta área.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_regular_admin:
            flash('Acesso negado. Apenas administradores de marina podem acessar esta área.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """Decorator para verificar permissão específica"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Faça login para acessar esta área.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not PermissionManager.has_permission(current_user, permission):
                flash('Acesso negado. Você não tem permissão para acessar esta área.', 'danger')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_accessible_marinas(user):
    """Retorna as marinas que um usuário pode acessar"""
    from app.models import Marina
    
    if user.is_superadmin:
        return Marina.query.all()
    elif user.is_regular_admin:
        # Admin só pode ver a marina que administra
        # Implementar lógica específica aqui
        return Marina.query.all()  # Por enquanto, retornar todas
    else:
        return []

def get_accessible_users(user):
    """Retorna os usuários que um usuário pode gerenciar"""
    from app.models import User
    
    if user.is_superadmin:
        return User.query.all()
    elif user.is_regular_admin:
        # Admin só pode gerenciar usuários da sua marina
        # e não pode gerenciar superadmins ou outros admins
        return User.query.filter(
            User.user_type == 'user'
        ).all()
    else:
        return [] 