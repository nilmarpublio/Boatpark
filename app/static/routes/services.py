from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import MarinaService, ServiceRequest, Marina, Berth, Payment, User, Subscription, UserServiceSelection
from app.extensions import db
from app.services import AsaasService
from app.utils.permissions import (
    superadmin_required, admin_required, marina_admin_required, permission_required, PermissionManager
)
from datetime import datetime, timedelta
from sqlalchemy import func
import json
from functools import wraps

bp = Blueprint('services', __name__, url_prefix='/services')

def admin_required(f):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Verificar se o usuário tem uma assinatura ativa
        active_subscription = current_user.get_active_subscription()
        if not active_subscription:
            flash('❌ Acesso Negado: Você precisa ter uma assinatura ativa para acessar os serviços da marina. Entre em contato conosco para contratar um plano.', 'error')
            return redirect(url_for('services.no_subscription'))
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROTAS ADMIN ====================

@bp.route('/admin')
@login_required
@admin_required
def admin_index():
    """Dashboard de serviços para administradores"""
    # Estatísticas
    total_services = MarinaService.query.count()
    total_requests = ServiceRequest.query.count()
    pending_requests = ServiceRequest.query.filter_by(status='requested').count()
    scheduled_requests = ServiceRequest.query.filter_by(status='scheduled').count()
    
    # Receita total de serviços
    total_revenue = db.session.query(func.sum(ServiceRequest.final_price)).filter_by(
        status='completed',
        payment_status='paid'
    ).scalar() or 0
    
    # Serviços recentes
    recent_requests = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).limit(10).all()
    
    return render_template('services/admin/dashboard.html',
                         total_services=total_services,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         scheduled_requests=scheduled_requests,
                         total_revenue=total_revenue,
                         recent_requests=recent_requests)

@bp.route('/admin/services')
@login_required
@admin_required
def admin_services():
    """Lista de tipos de serviços"""
    services = MarinaService.query.all()
    return render_template('services/admin/services.html', services=services)

@bp.route('/admin/services/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_new_service():
    """Criar novo tipo de serviço"""
    if request.method == 'POST':
        service = MarinaService(
            marina_id=request.form['marina_id'],
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            price_type=request.form.get('price_type', 'fixed'),
            is_active='is_active' in request.form
        )
        db.session.add(service)
        db.session.commit()
        flash('Serviço criado com sucesso!', 'success')
        return redirect(url_for('services.admin_services'))
    marinas = Marina.query.all()
    return render_template('services/admin/service_form.html', marinas=marinas)

@bp.route('/admin/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_service(service_id):
    """Editar tipo de serviço"""
    service = MarinaService.query.get_or_404(service_id)
    if request.method == 'POST':
        service.marina_id = request.form['marina_id']
        service.name = request.form['name']
        service.description = request.form['description']
        service.price = float(request.form['price'])
        service.price_type = request.form.get('price_type', 'fixed')
        service.is_active = 'is_active' in request.form
        db.session.commit()
        flash('Serviço atualizado com sucesso!', 'success')
        return redirect(url_for('services.admin_services'))
    marinas = Marina.query.all()
    return render_template('services/admin/service_form.html', service=service, marinas=marinas)

@bp.route('/admin/requests')
@login_required
@admin_required
def admin_requests():
    """Lista de solicitações de serviços"""
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    query = ServiceRequest.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(ServiceRequest.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('services/admin/requests.html', requests=requests, status_filter=status_filter)

@bp.route('/admin/requests/<int:request_id>')
@login_required
@admin_required
def admin_request_detail(request_id):
    """Detalhes de uma solicitação de serviço"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    return render_template('services/admin/request_detail.html', service_request=service_request)

@bp.route('/admin/requests/<int:request_id>/schedule', methods=['POST'])
@login_required
@admin_required
def admin_schedule_request(request_id):
    """Agendar uma solicitação de serviço"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Converter formato ISO 8601 (2025-07-16T10:45) para datetime
    date_str = request.form['scheduled_date']
    if 'T' in date_str:
        scheduled_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
    else:
        scheduled_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
    
    admin_notes = request.form.get('admin_notes', '')
    
    service_request.schedule(scheduled_date, admin_notes)
    db.session.commit()
    
    flash('Serviço agendado com sucesso!', 'success')
    return redirect(url_for('services.admin_request_detail', request_id=request_id))

@bp.route('/admin/requests/<int:request_id>/start', methods=['POST'])
@login_required
@admin_required
def admin_start_request(request_id):
    """Iniciar um serviço"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    service_request.start_service()
    db.session.commit()
    
    flash('Serviço iniciado!', 'success')
    return redirect(url_for('services.admin_request_detail', request_id=request_id))

@bp.route('/admin/requests/<int:request_id>/complete', methods=['POST'])
@login_required
@admin_required
def admin_complete_request(request_id):
    """Concluir um serviço"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    final_price = float(request.form['final_price']) if request.form.get('final_price') else None
    admin_notes = request.form.get('admin_notes', '')
    
    service_request.complete_service(final_price, admin_notes)
    db.session.commit()
    
    flash('Serviço concluído com sucesso!', 'success')
    return redirect(url_for('services.admin_request_detail', request_id=request_id))

@bp.route('/admin/requests/<int:request_id>/cancel', methods=['POST'])
@login_required
@admin_required
def admin_cancel_request(request_id):
    """Cancelar um serviço"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    admin_notes = request.form.get('admin_notes', '')
    service_request.cancel_service(admin_notes)
    db.session.commit()
    
    flash('Serviço cancelado.', 'warning')
    return redirect(url_for('services.admin_request_detail', request_id=request_id))

@bp.route('/admin/requests/<int:request_id>/update-status', methods=['POST'])
@login_required
@admin_required
def admin_update_status(request_id):
    """Atualizar status de uma solicitação"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    status = request.form['status']
    admin_notes = request.form.get('admin_notes', '')
    
    if status == 'in_progress':
        service_request.start_service()
    elif status == 'completed':
        service_request.complete_service(service_request.original_price, admin_notes)
    elif status == 'cancelled':
        service_request.cancel_service(admin_notes)
    
    db.session.commit()
    
    flash(f'Status atualizado para {service_request.status_display}', 'success')
    return redirect(url_for('services.admin_request_detail', request_id=request_id))

@bp.route('/admin/requests/<int:request_id>/add-notes', methods=['POST'])
@login_required
@admin_required
def admin_add_notes(request_id):
    """Adicionar observações a uma solicitação"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    admin_notes = request.form.get('admin_notes', '')
    service_request.admin_notes = admin_notes
    
    db.session.commit()
    
    flash('Observações salvas com sucesso!', 'success')
    return redirect(url_for('services.admin_request_detail', request_id=request_id))

# ==================== ROTAS CLIENTE ====================

@bp.route('/no-subscription')
@login_required
def no_subscription():
    """Página para usuários sem assinatura ativa"""
    return render_template('services/no_subscription.html')

@bp.route('/')
@login_required
@subscription_required
def index():
    """Página principal de serviços - seleção por categoria"""
    # Buscar assinatura ativa do usuário
    active_subscription = current_user.get_active_subscription()
    if not active_subscription:
        flash('Nenhuma assinatura ativa encontrada.', 'error')
        return redirect(url_for('services.no_subscription'))
    
    # Buscar serviços da marina da assinatura
    marina_services = MarinaService.query.filter_by(
        marina_id=active_subscription.marina_id,
        is_active=True
    ).order_by(MarinaService.category, MarinaService.name).all()
    
    # Agrupar serviços por categoria
    services_by_category = {}
    for service in marina_services:
        if service.category not in services_by_category:
            services_by_category[service.category] = []
        services_by_category[service.category].append(service)
    
    # Buscar serviços já selecionados pelo usuário
    selected_services = UserServiceSelection.query.filter_by(
        user_id=current_user.id,
        subscription_id=active_subscription.id,
        is_selected=True
    ).all()
    selected_service_ids = [ss.marina_service_id for ss in selected_services]
    
    return render_template('services/index.html', 
                         services_by_category=services_by_category,
                         selected_service_ids=selected_service_ids,
                         subscription=active_subscription)

@bp.route('/select', methods=['POST'])
@login_required
@subscription_required
def select_services():
    """Selecionar/deselecionar serviços"""
    active_subscription = current_user.get_active_subscription()
    if not active_subscription:
        flash('❌ Nenhuma assinatura ativa encontrada. Entre em contato conosco para contratar um plano.', 'error')
        return redirect(url_for('services.no_subscription'))
    
    # Obter serviços selecionados do formulário
    selected_service_ids = request.form.getlist('selected_services')
    
    # Limpar seleções anteriores
    UserServiceSelection.query.filter_by(
        user_id=current_user.id,
        subscription_id=active_subscription.id
    ).delete()
    
    # Criar novas seleções
    for service_id in selected_service_ids:
        selection = UserServiceSelection(
            user_id=current_user.id,
            marina_service_id=int(service_id),
            subscription_id=active_subscription.id,
            is_selected=True
        )
        db.session.add(selection)
    
    db.session.commit()
    flash(f'✅ {len(selected_service_ids)} serviços selecionados com sucesso!', 'success')
    
    return redirect(url_for('services.my_selections'))

@bp.route('/my-selections')
@login_required
@subscription_required
def my_selections():
    """Página dos serviços selecionados pelo usuário"""
    active_subscription = current_user.get_active_subscription()
    if not active_subscription:
        flash('❌ Nenhuma assinatura ativa encontrada. Entre em contato conosco para contratar um plano.', 'error')
        return redirect(url_for('services.no_subscription'))
    
    # Buscar serviços selecionados
    selections = UserServiceSelection.query.filter_by(
        user_id=current_user.id,
        subscription_id=active_subscription.id,
        is_selected=True
    ).all()
    
    return render_template('services/my_selections.html', 
                         selections=selections,
                         subscription=active_subscription)

@bp.route('/remove/<int:selection_id>', methods=['POST'])
@login_required
@subscription_required
def remove_selection(selection_id):
    """Remover um serviço da seleção"""
    selection = UserServiceSelection.query.get_or_404(selection_id)
    
    # Verificar se pertence ao usuário atual
    if selection.user_id != current_user.id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('services.my_selections'))
    
    service_name = selection.marina_service.name
    db.session.delete(selection)
    db.session.commit()
    
    flash(f'Serviço "{service_name}" removido da sua seleção.', 'success')
    return redirect(url_for('services.my_selections'))

@bp.route('/details/<int:service_id>')
@login_required
@subscription_required
def service_details(service_id):
    """Detalhes de um serviço específico"""
    service = MarinaService.query.get_or_404(service_id)
    active_subscription = current_user.get_active_subscription()
    
    # Verificar se o serviço pertence à marina da assinatura
    if service.marina_id != active_subscription.marina_id:
        flash('Serviço não disponível para sua assinatura.', 'error')
        return redirect(url_for('services.index'))
    
    # Verificar se já está selecionado
    is_selected = UserServiceSelection.query.filter_by(
        user_id=current_user.id,
        marina_service_id=service_id,
        subscription_id=active_subscription.id,
        is_selected=True
    ).first() is not None
    
    return render_template('services/details.html', 
                         service=service,
                         is_selected=is_selected,
                         subscription=active_subscription)

@bp.route('/request/<int:service_id>', methods=['GET', 'POST'])
@login_required
@subscription_required
def request_service(service_id):
    """Solicitar um serviço"""
    service = MarinaService.query.get_or_404(service_id)
    if request.method == 'POST':
        user_subscription = current_user.get_active_subscription()
        if not user_subscription or user_subscription.berth.marina_id != service.marina_id:
            flash('❌ Você precisa ter uma assinatura ativa nesta marina para solicitar serviços. Entre em contato conosco para contratar um plano.', 'error')
            return redirect(url_for('services.no_subscription'))
        service_request = ServiceRequest(
            user_id=current_user.id,
            marina_service_id=service.id,
            marina_id=service.marina_id,
            berth_id=user_subscription.berth_id,
            vessel_name=request.form['vessel_name'],
            vessel_type=request.form['vessel_type'],
            vessel_length=float(request.form['vessel_length']) if request.form['vessel_length'] else None,
            preferred_date=datetime.strptime(request.form['preferred_date'], '%Y-%m-%d').date(),
            preferred_time=datetime.strptime(request.form['preferred_time'], '%H:%M').time(),
            notes=request.form.get('notes', ''),
            original_price=service.price
        )
        db.session.add(service_request)
        db.session.commit()
        flash('✅ Solicitação de serviço enviada com sucesso!', 'success')
        return redirect(url_for('services.my_requests'))
    return render_template('services/client/request_form.html', service=service)

@bp.route('/my-requests')
@login_required
@subscription_required
def my_requests():
    """Lista de solicitações do usuário"""
    page = request.args.get('page', 1, type=int)
    requests = ServiceRequest.query.filter_by(user_id=current_user.id).order_by(
        ServiceRequest.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('services/client/my_requests.html', requests=requests)

@bp.route('/my-requests/<int:request_id>')
@login_required
@subscription_required
def my_request_detail(request_id):
    """Detalhes de uma solicitação do usuário"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Verificar se o usuário é o dono da solicitação
    if service_request.user_id != current_user.id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('services.my_requests'))
    
    return render_template('services/client/request_detail.html', service_request=service_request)

@bp.route('/my-requests/<int:request_id>/cancel', methods=['POST'])
@login_required
@subscription_required
def cancel_my_request(request_id):
    """Cancelar uma solicitação do usuário"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Verificar se o usuário é o dono da solicitação
    if service_request.user_id != current_user.id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('services.my_requests'))
    
    # Só pode cancelar se ainda não foi agendado
    if service_request.status not in ['requested']:
        flash('Não é possível cancelar este serviço.', 'error')
        return redirect(url_for('services.my_request_detail', request_id=request_id))
    
    service_request.cancel_service('Cancelado pelo cliente')
    db.session.commit()
    
    flash('Solicitação cancelada com sucesso.', 'success')
    return redirect(url_for('services.my_requests'))

# ==================== API PARA PAGAMENTOS ====================

@bp.route('/api/requests/<int:request_id>/create-payment', methods=['POST'])
@login_required
def create_payment(request_id):
    """Criar cobrança para um serviço via ASAAS"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Verificar se o usuário é o dono da solicitação
    if service_request.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Criar cobrança no ASAAS
        payment_data = {
            'customer': current_user.asaas_customer_id,
            'billingType': 'PIX',
            'value': float(service_request.final_price or service_request.original_price),
            'dueDate': datetime.now().strftime('%Y-%m-%d'),
            'description': f'Serviço: {service_request.service.name} - {service_request.vessel_name}',
            'externalReference': f'SR-{service_request.id}'
        }
        
        asaas_response = AsaasService.create_payment(payment_data)
        
        if asaas_response.get('success'):
            # Criar registro de pagamento
            payment = Payment(
                subscription_id=current_user.get_active_subscription().id,
                amount=payment_data['value'],
                status='pending',
                payment_method='pix',
                due_date=datetime.utcnow(),
                description=payment_data['description'],
                external_reference=f'SR-{service_request.id}',
                asaas_payment_id=asaas_response['data']['id']
            )
            
            db.session.add(payment)
            service_request.payment_id = payment.id
            db.session.commit()
            
            return jsonify({
                'success': True,
                'payment_id': payment.id,
                'pix_code': asaas_response['data'].get('pixCode'),
                'pix_qr_code': asaas_response['data'].get('pixQrCode')
            })
        else:
            return jsonify({'error': 'Erro ao criar cobrança'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500 