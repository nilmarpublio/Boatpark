from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from app.models import SystemConfig

def subscription_required(action):
    """
    Decorator para verificar se o usuário tem permissão para realizar uma ação
    baseado no seu plano de assinatura
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, faça login para acessar esta funcionalidade.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Administradores têm acesso total
            if current_user.is_admin:
                return f(*args, **kwargs)
            
            # Verificar se o usuário tem uma assinatura ativa
            active_subscription = current_user.get_active_subscription()
            if not active_subscription:
                flash('Você precisa de uma assinatura ativa para acessar esta funcionalidade.', 'warning')
                return redirect(url_for('dashboard.index'))
            
            # Verificar se o plano permite a ação
            if not active_subscription.can_perform_action(action):
                plan_name = active_subscription.plan.display_name if active_subscription.plan else 'seu plano'
                flash(f'Esta funcionalidade não está disponível no {plan_name}.', 'warning')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_service_eligibility():
    """
    Verificação completa de elegibilidade para solicitar serviços:
    1. Verifica se tem plano ativo
    2. Verifica se os pagamentos estão em dia
    3. Retorna mensagens configuradas pelo administrador
    """
    if not current_user.is_authenticated:
        return False, "Usuário não autenticado"
    
    if current_user.is_admin:
        return True, "Administrador"
    
    # Verificar se tem assinatura ativa
    active_subscription = current_user.get_active_subscription()
    if not active_subscription:
        config = SystemConfig.get_config()
        message = config.payment_overdue_message if hasattr(config, 'payment_overdue_message') else 'Você precisa de uma assinatura ativa para solicitar serviços.'
        return False, message
    
    # Verificar se a assinatura está ativa
    if not active_subscription.is_active or active_subscription.status != 'active':
        config = SystemConfig.get_config()
        message = config.payment_overdue_message if hasattr(config, 'payment_overdue_message') else 'Sua assinatura está suspensa. Entre em contato com a marina.'
        return False, message
    
    # Verificar se a assinatura não expirou
    if active_subscription.is_expired:
        config = SystemConfig.get_config()
        message = config.payment_overdue_message if hasattr(config, 'payment_overdue_message') else 'Sua assinatura expirou. Renove para continuar usando os serviços.'
        return False, message
    
    # Verificar pagamentos em dia
    from app.models import Payment
    from datetime import datetime, timedelta
    
    # Buscar pagamentos pendentes ou em atraso
    overdue_payments = Payment.query.filter_by(
        subscription_id=active_subscription.id
    ).all()
    
    for payment in overdue_payments:
        if payment.status in ['pending', 'overdue'] and payment.due_date < datetime.utcnow():
            config = SystemConfig.get_config()
            message = config.payment_overdue_message if hasattr(config, 'payment_overdue_message') else 'Você tem pagamentos em atraso. Regularize sua situação para solicitar serviços.'
            return False, message
    
    # Verificar se o plano permite solicitar serviços
    if not active_subscription.can_perform_action('create_service'):
        plan_name = active_subscription.plan.display_name if active_subscription.plan else 'seu plano'
        config = SystemConfig.get_config()
        message = f'Esta funcionalidade não está disponível no {plan_name}.'
        return False, message
    
    # Verificar limite de serviços
    from app.models import ServiceRequest
    
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    services_this_month = ServiceRequest.query.filter(
        ServiceRequest.user_id == current_user.id,
        ServiceRequest.created_at >= start_of_month
    ).count()
    
    if not active_subscription.check_service_limit(services_this_month):
        limit = active_subscription.plan.max_services_per_month if active_subscription.plan else 0
        config = SystemConfig.get_config()
        message = f'Limite de {limit} serviços/mês atingido. Aguarde o próximo ciclo ou faça upgrade do seu plano.'
        return False, message
    
    return True, "Elegível para solicitar serviços"

def check_service_limit():
    """
    Verifica se o usuário ainda pode solicitar serviços baseado no seu plano
    """
    if not current_user.is_authenticated:
        return False, "Usuário não autenticado"
    
    if current_user.is_admin:
        return True, "Administrador"
    
    active_subscription = current_user.get_active_subscription()
    if not active_subscription:
        return False, "Nenhuma assinatura ativa"
    
    # Contar serviços do mês atual
    from app.models import ServiceRequest
    from datetime import datetime, timedelta
    
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    services_this_month = ServiceRequest.query.filter(
        ServiceRequest.user_id == current_user.id,
        ServiceRequest.created_at >= start_of_month
    ).count()
    
    if not active_subscription.check_service_limit(services_this_month):
        return False, f"Limite de {active_subscription.plan.max_services_per_month} serviços/mês atingido"
    
    return True, "OK"

def check_document_limit():
    """
    Verifica se o usuário ainda pode fazer upload de documentos baseado no seu plano
    """
    if not current_user.is_authenticated:
        return False, "Usuário não autenticado"
    
    if current_user.is_admin:
        return True, "Administrador"
    
    active_subscription = current_user.get_active_subscription()
    if not active_subscription:
        return False, "Nenhuma assinatura ativa"
    
    # Contar documentos do usuário
    from app.models import Document
    
    documents_count = Document.query.filter_by(user_id=current_user.id).count()
    
    if not active_subscription.check_document_limit(documents_count):
        return False, f"Limite de {active_subscription.plan.max_documents} documentos atingido"
    
    return True, "OK"

def is_test_plan_user():
    """
    Verifica se o usuário está no plano de teste
    """
    if not current_user.is_authenticated:
        return False
    
    if current_user.is_admin:
        return False
    
    active_subscription = current_user.get_active_subscription()
    if not active_subscription or not active_subscription.plan:
        return False
    
    return active_subscription.plan.is_test_plan

def require_active_subscription(f):
    """
    Decorator para verificar se o usuário tem uma assinatura ativa
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta funcionalidade.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.is_admin:
            return f(*args, **kwargs)
        
        active_subscription = current_user.get_active_subscription()
        if not active_subscription:
            flash('Você precisa de uma assinatura ativa para acessar esta funcionalidade.', 'warning')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function 