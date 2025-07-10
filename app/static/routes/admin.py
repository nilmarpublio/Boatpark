from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import login_required, current_user
from functools import wraps
from app.models import MarinaService, ServiceRequest, SystemConfig, Document, Notification, AuditLog, User, Marina, Berth, Subscription, Payment
from app.extensions import db
from app.utils.audit_middleware import log_admin_action
from datetime import datetime, timedelta
import json

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    """Admin Dashboard Overview"""
    # Get statistics
    total_users = User.query.count()
    total_marinas = Marina.query.count()
    total_berths = Berth.query.count()
    total_subscriptions = Subscription.query.count()
    total_payments = Payment.query.count()
    total_services = MarinaService.query.count()
    total_service_requests = ServiceRequest.query.count()
    
    # Recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
    recent_services = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).limit(5).all()
    
    # Revenue statistics
    total_revenue_result = db.session.query(db.func.sum(Payment.amount)).filter(Payment.status == 'paid').scalar()
    total_revenue = total_revenue_result if total_revenue_result is not None else 0
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    monthly_revenue_result = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == 'paid',
        Payment.created_at >= thirty_days_ago
    ).scalar()
    monthly_revenue = monthly_revenue_result if monthly_revenue_result is not None else 0
    
    context = {
        'total_users': total_users,
        'total_marinas': total_marinas,
        'total_berths': total_berths,
        'total_subscriptions': total_subscriptions,
        'total_payments': total_payments,
        'total_services': total_services,
        'total_service_requests': total_service_requests,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_services': recent_services
    }
    
    return render_template('admin/dashboard.html', **context)

# User Management
@bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """User detail view"""
    user = User.query.get_or_404(user_id)
    subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    
    # Buscar pagamentos através das assinaturas do usuário
    subscription_ids = [sub.id for sub in subscriptions]
    payments = Payment.query.filter(Payment.subscription_id.in_(subscription_ids)).all() if subscription_ids else []
    
    service_requests = ServiceRequest.query.filter_by(user_id=user_id).all()
    
    return render_template('admin/user_detail.html', 
                         user=user, 
                         subscriptions=subscriptions,
                         payments=payments,
                         service_requests=service_requests)

@bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def user_new():
    """Create new user"""
    if request.method == 'POST':
        # Verificar se o email já existe
        existing_user = User.query.filter_by(email=request.form['email']).first()
        if existing_user:
            flash('Email já cadastrado!', 'error')
            return render_template('admin/user_form.html', user=None)
        
        # Verificar se o CPF já existe
        if request.form.get('cpf'):
            existing_cpf = User.query.filter_by(cpf=request.form['cpf']).first()
            if existing_cpf:
                flash('CPF já cadastrado!', 'error')
                return render_template('admin/user_form.html', user=None)
        
        # Determinar o tipo de usuário
        user_type = request.form.get('user_type', 'user')
        
        user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form.get('phone'),
            cpf=request.form.get('cpf'),
            user_type=user_type,
            is_admin='is_admin' in request.form,
            is_active='is_active' in request.form
        )
        user.password = request.form['password']
        
        db.session.add(user)
        db.session.commit()
        
        # Log da criação
        log_admin_action(
            action='USER_CREATE',
            description=f'Usuário criado: {user.full_name} ({user.email})',
            record_id=user.id,
            new_values={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'cpf': user.cpf,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            }
        )
        
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    return render_template('admin/user_form.html', user=None)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Verificar se o email já existe (exceto para o próprio usuário)
        existing_user = User.query.filter_by(email=request.form['email']).first()
        if existing_user and existing_user.id != user.id:
            flash('Email já cadastrado!', 'error')
            return render_template('admin/user_form.html', user=user)
        
        # Verificar se o CPF já existe (exceto para o próprio usuário)
        if request.form.get('cpf'):
            existing_cpf = User.query.filter_by(cpf=request.form['cpf']).first()
            if existing_cpf and existing_cpf.id != user.id:
                flash('CPF já cadastrado!', 'error')
                return render_template('admin/user_form.html', user=user)
        
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.phone = request.form.get('phone')
        user.cpf = request.form.get('cpf')
        user.user_type = request.form.get('user_type', 'user')
        user.is_admin = 'is_admin' in request.form
        user.is_active = 'is_active' in request.form
        
        # Atualizar senha apenas se fornecida
        if request.form.get('password'):
            user.password = request.form['password']
        
        # Capturar valores antigos para o log
        old_values = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'cpf': user.cpf,
            'is_admin': user.is_admin,
            'is_active': user.is_active
        }
        
        db.session.commit()
        
        # Log da atualização
        log_admin_action(
            action='USER_UPDATE',
            description=f'Usuário atualizado: {user.full_name} ({user.email})',
            record_id=user.id,
            old_values=old_values,
            new_values={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'cpf': user.cpf,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            }
        )
        
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    return render_template('admin/user_form.html', user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    # Verificar se não é o próprio usuário logado
    if user.id == current_user.id:
        flash('Não é possível excluir seu próprio usuário!', 'error')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    # Verificar se é o único administrador
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Não é possível excluir o único administrador do sistema!', 'error')
            return redirect(url_for('admin.user_detail', user_id=user.id))
    
    # Excluir assinaturas do usuário
    subscriptions = Subscription.query.filter_by(user_id=user.id).all()
    for subscription in subscriptions:
        # Liberar a vaga
        if subscription.berth:
            subscription.berth.status = 'available'
            subscription.berth.add_occupancy_record(
                status='available',
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                reason='Assinatura encerrada',
                notes='Liberação automática após exclusão de assinatura'
            )
        db.session.delete(subscription)
    
    # Excluir solicitações de serviço
    service_requests = ServiceRequest.query.filter_by(user_id=user.id).all()
    for request in service_requests:
        db.session.delete(request)
    
    # Excluir documentos
    documents = Document.query.filter_by(user_id=user.id).all()
    for document in documents:
        db.session.delete(document)
    
    # Excluir notificações
    notifications = Notification.query.filter_by(user_id=user.id).all()
    for notification in notifications:
        db.session.delete(notification)
    
    # Capturar informações do usuário antes da exclusão
    user_info = {
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'is_admin': user.is_admin
    }
    
    # Excluir o usuário
    db.session.delete(user)
    db.session.commit()
    
    # Log da exclusão
    log_admin_action(
        action='USER_DELETE',
        description=f'Usuário excluído: {user_info["full_name"]} ({user_info["email"]})',
        record_id=user_info['id'],
        old_values=user_info
    )
    
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/users/<int:user_id>/subscription/new', methods=['GET', 'POST'])
@login_required
@admin_required
def user_subscription_new(user_id):
    """Create new subscription for user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        plan_id = request.form.get('plan_id')
        marina_id = request.form.get('marina_id')
        berth_id = request.form.get('berth_id')
        
        if not all([plan_id, marina_id, berth_id]):
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('admin.user_subscription_new', user_id=user.id))
        
        plan = SubscriptionPlan.query.get(plan_id)
        marina = Marina.query.get(marina_id)
        berth = Berth.query.get(berth_id)
        
        if not all([plan, marina, berth]):
            flash('Dados inválidos!', 'error')
            return redirect(url_for('admin.user_subscription_new', user_id=user.id))
        
        # Verificar se a vaga está disponível
        if berth.status != 'available':
            flash('Vaga não está disponível!', 'error')
            return redirect(url_for('admin.user_subscription_new', user_id=user.id))
        
        # Criar assinatura
        subscription = Subscription(
            user_id=user.id,
            marina_id=marina.id,
            berth_id=berth.id,
            plan_id=plan.id,
            plan_type='monthly',
            plan_name=plan.display_name,
            amount=plan.monthly_price,
            status='active',
            is_active=True,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            next_billing_date=datetime.utcnow() + timedelta(days=30),
            billing_cycle='monthly',
            auto_renew=True
        )
        
        # Marcar vaga como ocupada
        berth.status = 'occupied'
        berth.add_occupancy_record(
            status='occupied',
            user_id=user.id,
            subscription_id=None,  # será atualizado após commit
            reason='Assinatura criada',
            notes=f'Plano: {plan.display_name}'
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        flash('Assinatura criada com sucesso!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    marinas = Marina.query.filter_by(is_active=True).all()
    berths = Berth.query.filter_by(status='available').all()
    
    return render_template('admin/user_subscription_form.html', 
                         user=user, 
                         plans=plans, 
                         marinas=marinas, 
                         berths=berths)

# Marina Management
@bp.route('/marinas')
@login_required
@admin_required
def marinas():
    """List all marinas"""
    marinas = Marina.query.all()
    return render_template('admin/marinas.html', marinas=marinas)

@bp.route('/marinas/<int:marina_id>')
@login_required
@admin_required
def marina_detail(marina_id):
    """Marina detail view"""
    marina = Marina.query.get_or_404(marina_id)
    berths = Berth.query.filter_by(marina_id=marina_id).all()
    subscriptions = Subscription.query.join(Berth).filter(Berth.marina_id == marina_id).all()
    
    return render_template('admin/marina_detail.html', 
                         marina=marina, 
                         berths=berths,
                         subscriptions=subscriptions)

@bp.route('/marinas/new', methods=['GET', 'POST'])
@login_required
@admin_required
def marina_new():
    """Create new marina"""
    if request.method == 'POST':
        # Process opening hours
        opening_hours = {}
        days = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        for day in days:
            hours = request.form.get(f'opening_hours_{day}')
            if hours:
                opening_hours[day] = hours
        
        # Process amenities and services
        amenities = [item for item in request.form.getlist('amenities[]') if item.strip()]
        services = [item for item in request.form.getlist('services[]') if item.strip()]
        
        # Process photos
        photos_text = request.form.get('photos', '')
        photos = [url.strip() for url in photos_text.split('\n') if url.strip()]
        
        marina = Marina(
            name=request.form['name'],
            description=request.form.get('description'),
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            zip_code=request.form.get('zip_code'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            website=request.form.get('website'),
            contact_person=request.form.get('contact_person'),
            emergency_phone=request.form.get('emergency_phone'),
            latitude=float(request.form.get('latitude', 0)) if request.form.get('latitude') else None,
            longitude=float(request.form.get('longitude', 0)) if request.form.get('longitude') else None,
            map_zoom=int(request.form.get('map_zoom', 15)),
            is_active=request.form.get('is_active') == 'on',
            max_berths=int(request.form.get('max_berths', 0)),
            opening_hours=json.dumps(opening_hours),
            services=json.dumps(services),
            photos=json.dumps(photos),
            cover_photo_url=request.form.get('cover_photo_url'),
            amenities=json.dumps(amenities),
            rules=request.form.get('rules')
        )
        db.session.add(marina)
        db.session.commit()
        flash('Marina criada com sucesso!', 'success')
        return redirect(url_for('admin.marinas'))
    
    return render_template('admin/marina_form.html', marina=None)

@bp.route('/marinas/<int:marina_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def marina_edit(marina_id):
    """Edit marina"""
    marina = Marina.query.get_or_404(marina_id)
    
    if request.method == 'POST':
        # Process opening hours
        opening_hours = {}
        days = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        for day in days:
            hours = request.form.get(f'opening_hours_{day}')
            if hours:
                opening_hours[day] = hours
        
        # Process amenities and services
        amenities = [item for item in request.form.getlist('amenities[]') if item.strip()]
        services = [item for item in request.form.getlist('services[]') if item.strip()]
        
        # Process photos
        photos_text = request.form.get('photos', '')
        photos = [url.strip() for url in photos_text.split('\n') if url.strip()]
        
        marina.name = request.form['name']
        marina.description = request.form.get('description')
        marina.address = request.form['address']
        marina.city = request.form['city']
        marina.state = request.form['state']
        marina.zip_code = request.form.get('zip_code')
        marina.phone = request.form.get('phone')
        marina.email = request.form.get('email')
        marina.website = request.form.get('website')
        marina.contact_person = request.form.get('contact_person')
        marina.emergency_phone = request.form.get('emergency_phone')
        marina.latitude = float(request.form.get('latitude', 0)) if request.form.get('latitude') else None
        marina.longitude = float(request.form.get('longitude', 0)) if request.form.get('longitude') else None
        marina.map_zoom = int(request.form.get('map_zoom', 15))
        marina.is_active = request.form.get('is_active') == 'on'
        marina.max_berths = int(request.form.get('max_berths', 0))
        marina.opening_hours = json.dumps(opening_hours)
        marina.services = json.dumps(services)
        marina.photos = json.dumps(photos)
        marina.cover_photo_url = request.form.get('cover_photo_url')
        marina.amenities = json.dumps(amenities)
        marina.rules = request.form.get('rules')
        
        db.session.commit()
        flash('Marina atualizada com sucesso!', 'success')
        return redirect(url_for('admin.marina_detail', marina_id=marina.id))
    
    return render_template('admin/marina_form.html', marina=marina)

# Berth Management
@bp.route('/berths')
@login_required
@admin_required
def berths():
    """List all berths"""
    berths = Berth.query.all()
    return render_template('admin/berths.html', berths=berths)

@bp.route('/berths/new', methods=['GET', 'POST'])
@login_required
@admin_required
def berth_new():
    """Create new berth"""
    marinas = Marina.query.all()
    
    if request.method == 'POST':
        berth = Berth(
            berth_number=request.form['berth_number'],
            berth_type=request.form['berth_type'],
            length=float(request.form.get('length', 0)) if request.form.get('length') else None,
            width=float(request.form.get('width', 0)) if request.form.get('width') else None,
            depth=float(request.form.get('depth', 0)) if request.form.get('depth') else None,
            max_boat_length=float(request.form.get('max_boat_length', 0)) if request.form.get('max_boat_length') else None,
            daily_rate=float(request.form.get('daily_rate', 0)) if request.form.get('daily_rate') else None,
            monthly_rate=float(request.form.get('monthly_rate', 0)) if request.form.get('monthly_rate') else None,
            yearly_rate=float(request.form.get('yearly_rate', 0)) if request.form.get('yearly_rate') else None,
            status=request.form.get('status', 'available'),
            description=request.form.get('description'),
            marina_id=int(request.form['marina_id']),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(berth)
        db.session.commit()
        flash('Vaga criada com sucesso!', 'success')
        return redirect(url_for('admin.berths'))
    
    return render_template('admin/berth_form.html', berth=None, marinas=marinas)

@bp.route('/berths/<int:berth_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def berth_edit(berth_id):
    """Edit berth"""
    berth = Berth.query.get_or_404(berth_id)
    marinas = Marina.query.all()
    
    if request.method == 'POST':
        berth.berth_number = request.form['berth_number']
        berth.berth_type = request.form['berth_type']
        berth.length = float(request.form.get('length', 0)) if request.form.get('length') else None
        berth.width = float(request.form.get('width', 0)) if request.form.get('width') else None
        berth.depth = float(request.form.get('depth', 0)) if request.form.get('depth') else None
        berth.max_boat_length = float(request.form.get('max_boat_length', 0)) if request.form.get('max_boat_length') else None
        berth.daily_rate = float(request.form.get('daily_rate', 0)) if request.form.get('daily_rate') else None
        berth.monthly_rate = float(request.form.get('monthly_rate', 0)) if request.form.get('monthly_rate') else None
        berth.yearly_rate = float(request.form.get('yearly_rate', 0)) if request.form.get('yearly_rate') else None
        old_status = berth.status
        berth.status = request.form.get('status', 'available')
        if berth.status != old_status:
            berth.add_occupancy_record(
                status=berth.status,
                user_id=current_user.id if current_user.is_authenticated else None,
                reason='Alteração manual',
                notes='Alteração via painel admin'
            )
        berth.description = request.form.get('description')
        berth.marina_id = int(request.form['marina_id'])
        berth.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Vaga atualizada com sucesso!', 'success')
        return redirect(url_for('admin.berths'))
    
    return render_template('admin/berth_form.html', berth=berth, marinas=marinas)

@bp.route('/berths/<int:berth_id>')
@login_required
@admin_required
def berth_detail(berth_id):
    """Detalhe da vaga"""
    berth = Berth.query.get_or_404(berth_id)
    marina = berth.marina
    history = berth.get_occupancy_history()
    return render_template('admin/berth_detail.html', berth=berth, marina=marina, history=history)

# Subscription Plan Management
@bp.route('/subscription-plans')
@login_required
@admin_required
def subscription_plans():
    """List all subscription plans"""
    plans = SubscriptionPlan.query.all()
    print(f"DEBUG: Encontrados {len(plans)} planos de assinatura")
    for plan in plans:
        print(f"  - {plan.name}: {plan.display_name}")
    return render_template('admin/subscription_plans.html', plans=plans)

@bp.route('/subscription-plans/<int:plan_id>')
@login_required
@admin_required
def subscription_plan_detail(plan_id):
    """Subscription plan detail view"""
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    subscriptions = Subscription.query.filter_by(plan_id=plan_id).all()
    return render_template('admin/subscription_plan_detail.html', plan=plan, subscriptions=subscriptions)

@bp.route('/subscription-plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def subscription_plan_edit(plan_id):
    """Edit subscription plan"""
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # Atualizar dados do plano
        plan.display_name = request.form['display_name']
        plan.description = request.form['description']
        plan.monthly_price = float(request.form['monthly_price'])
        plan.yearly_price = float(request.form['yearly_price']) if request.form['yearly_price'] else None
        plan.max_berths = int(request.form['max_berths'])
        plan.max_services_per_month = int(request.form['max_services_per_month']) if request.form['max_services_per_month'] != '-1' else -1
        plan.max_documents = int(request.form['max_documents']) if request.form['max_documents'] != '-1' else -1
        
        # Permissões
        plan.can_create_services = 'can_create_services' in request.form
        plan.can_upload_documents = 'can_upload_documents' in request.form
        plan.can_make_payments = 'can_make_payments' in request.form
        plan.can_view_reports = 'can_view_reports' in request.form
        plan.can_access_api = 'can_access_api' in request.form
        plan.is_test_plan = 'is_test_plan' in request.form
        
        # Status
        plan.is_active = 'is_active' in request.form
        plan.is_featured = 'is_featured' in request.form
        
        db.session.commit()
        flash('Plano atualizado com sucesso!', 'success')
        return redirect(url_for('admin.subscription_plan_detail', plan_id=plan.id))
    
    return render_template('admin/subscription_plan_form.html', plan=plan)

# Subscription Management
@bp.route('/subscriptions')
@login_required
@admin_required
def subscriptions():
    """List all subscriptions"""
    subscriptions = Subscription.query.all()
    return render_template('admin/subscriptions.html', subscriptions=subscriptions)

@bp.route('/subscriptions/<int:subscription_id>')
@login_required
@admin_required
def subscription_detail(subscription_id):
    """Subscription detail view"""
    subscription = Subscription.query.get_or_404(subscription_id)
    return render_template('admin/subscription_detail.html', subscription=subscription)

# Payment Management
@bp.route('/payments')
@login_required
@admin_required
def payments():
    """List all payments with filters and pagination"""
    # Filtros
    status = request.args.get('status')
    method = request.args.get('method')
    date_from = request.args.get('dateFrom')
    date_to = request.args.get('dateTo')
    page = request.args.get('page', 1, type=int)
    
    # Construir query
    query = Payment.query.join(Subscription)
    
    if status:
        query = query.filter(Payment.status == status)
    if method:
        query = query.filter(Payment.payment_method == method)
    if date_from:
        query = query.filter(Payment.created_at >= date_from)
    if date_to:
        query = query.filter(Payment.created_at <= date_to + ' 23:59:59')
    
    # Paginação
    payments = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    
    # Estatísticas
    total_confirmed = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == 'confirmed'
    ).scalar() or 0
    
    total_pending = Payment.query.filter_by(status='pending').count()
    total_overdue = Payment.query.filter_by(status='overdue').count()
    
    # Calcular taxa de sucesso
    total_payments = Payment.query.count()
    confirmed_payments = Payment.query.filter_by(status='confirmed').count()
    success_rate = (confirmed_payments / total_payments * 100) if total_payments > 0 else 0
    
    context = {
        'payments': payments,
        'total_confirmed': total_confirmed,
        'total_pending': total_pending,
        'total_overdue': total_overdue,
        'success_rate': success_rate
    }
    
    return render_template('admin/payments.html', **context)

@bp.route('/payments/<int:payment_id>')
@login_required
@admin_required
def payment_detail(payment_id):
    """Payment detail view"""
    payment = Payment.query.get_or_404(payment_id)
    return render_template('admin/payment_detail.html', payment=payment)

# Service Management
@bp.route('/services')
@login_required
@admin_required
def services():
    """List all marina services"""
    services = MarinaService.query.all()
    return render_template('services/admin/services.html', services=services)

@bp.route('/services/new', methods=['GET', 'POST'])
@login_required
@admin_required
def service_new():
    """Create new marina service"""
    marinas = Marina.query.all()
    if request.method == 'POST':
        service = MarinaService(
            marina_id=request.form['marina_id'],
            name=request.form['name'],
            description=request.form['description'],
            category=request.form.get('category'),
            price=float(request.form['price']),
            price_type=request.form.get('price_type', 'fixed'),
            is_active='is_active' in request.form,
            requires_approval='requires_approval' in request.form,
            max_duration_hours=int(request.form.get('max_duration_hours') or 0)
        )
        db.session.add(service)
        db.session.commit()
        flash('Serviço criado com sucesso!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('services/admin/service_form.html', service=None, marinas=marinas)

@bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def service_edit(service_id):
    """Edit marina service"""
    service = MarinaService.query.get_or_404(service_id)
    marinas = Marina.query.all()
    if request.method == 'POST':
        service.marina_id = request.form['marina_id']
        service.name = request.form['name']
        service.description = request.form['description']
        service.category = request.form.get('category')
        service.price = float(request.form['price'])
        service.price_type = request.form.get('price_type', 'fixed')
        service.is_active = 'is_active' in request.form
        service.requires_approval = 'requires_approval' in request.form
        service.max_duration_hours = int(request.form.get('max_duration_hours') or 0)
        db.session.commit()
        flash('Serviço atualizado com sucesso!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('services/admin/service_form.html', service=service, marinas=marinas)

# Service Requests Management
@bp.route('/service-requests')
@login_required
@admin_required
def service_requests():
    """List all service requests"""
    requests = ServiceRequest.query.all()
    return render_template('services/admin/requests.html', requests=requests)

@bp.route('/service-requests/<int:request_id>')
@login_required
@admin_required
def service_request_detail(request_id):
    """Service request detail view"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    return render_template('services/admin/request_detail.html', request=service_request)

@bp.route('/service-requests/<int:request_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_service_request_status(request_id):
    """Update service request status"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    service_request.status = request.form['status']
    
    if request.form.get('notes'):
        service_request.admin_notes = request.form['notes']
    
    db.session.commit()
    flash('Status do serviço atualizado com sucesso!', 'success')
    return redirect(url_for('admin.service_request_detail', request_id=request_id))

# System Configuration
@bp.route('/system-config', methods=['GET', 'POST'])
@login_required
@admin_required
def system_config():
    """System configuration management"""
    config = SystemConfig.get_config()
    
    if request.method == 'POST':
        # Configurações de pagamento
        config.payment_reminder_days = int(request.form['payment_reminder_days'])
        config.payment_overdue_days = int(request.form['payment_overdue_days'])
        config.vessel_removal_days = int(request.form['vessel_removal_days'])
        
        # Mensagens
        config.payment_reminder_message = request.form['payment_reminder_message']
        config.payment_overdue_message = request.form['payment_overdue_message']
        config.vessel_removal_message = request.form['vessel_removal_message']
        
        # Configurações de notificação
        config.send_email_notifications = 'send_email_notifications' in request.form
        config.send_sms_notifications = 'send_sms_notifications' in request.form
        config.send_push_notifications = 'send_push_notifications' in request.form
        
        # Configurações gerais
        config.maintenance_mode = 'maintenance_mode' in request.form
        config.maintenance_message = request.form['maintenance_message']
        
        db.session.commit()
        flash('Configurações do sistema atualizadas com sucesso!', 'success')
        return redirect(url_for('admin.system_config'))
    
    return render_template('admin/system_config.html', config=config)

# Document Management
@bp.route('/documents')
@login_required
@admin_required
def documents():
    """List all documents"""
    # For now, return a simple message since we don't have a Document model yet
    return render_template('admin/documents.html', documents=[])

# Reports
@bp.route('/reports')
@login_required
@admin_required
def reports():
    """Reports dashboard"""
    # Filtros
    date_from = request.args.get('dateFrom')
    date_to = request.args.get('dateTo')
    marina_id = request.args.get('marina')
    plan_id = request.args.get('plan')
    
    # Construir filtros
    payment_filters = [Payment.status == 'confirmed']
    subscription_filters = []
    
    if date_from:
        payment_filters.append(Payment.created_at >= date_from)
    if date_to:
        payment_filters.append(Payment.created_at <= date_to + ' 23:59:59')
    if marina_id:
        subscription_filters.append(Subscription.marina_id == int(marina_id))
    if plan_id:
        subscription_filters.append(Subscription.plan_id == int(plan_id))
    
    # Revenue by month
    query = db.session.query(
        db.func.strftime('%Y-%m', Payment.created_at).label('month'),
        db.func.sum(Payment.amount).label('total')
    ).filter(Payment.status == 'confirmed')
    
    if date_from:
        query = query.filter(Payment.created_at >= date_from)
    if date_to:
        query = query.filter(Payment.created_at <= date_to + ' 23:59:59')
    
    monthly_revenue = query.group_by('month').order_by('month').all()
    
    # Top marinas by revenue
    marina_query = db.session.query(
        Marina.name,
        db.func.sum(Payment.amount).label('total'),
        db.func.count(Subscription.id).label('subscriptions')
    ).join(Berth).join(Subscription).join(Payment).filter(Payment.status == 'confirmed')
    
    if date_from:
        marina_query = marina_query.filter(Payment.created_at >= date_from)
    if date_to:
        marina_query = marina_query.filter(Payment.created_at <= date_to + ' 23:59:59')
    if marina_id:
        marina_query = marina_query.filter(Subscription.marina_id == int(marina_id))
    
    marina_revenue_query = marina_query.group_by(Marina.id).order_by(db.func.sum(Payment.amount).desc()).limit(10)
    
    marina_revenue = []
    for marina in marina_revenue_query.all():
        marina_revenue.append({
            'name': marina.name,
            'total': float(marina.total),
            'subscriptions': marina.subscriptions
        })
    
    # Service statistics
    service_stats = db.session.query(
        MarinaService.name,
        db.func.count(ServiceRequest.id).label('total_requests'),
        db.func.avg(ServiceRequest.final_price).label('avg_amount')
    ).outerjoin(ServiceRequest).group_by(MarinaService.id).all()
    
    # Estatísticas gerais
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(*payment_filters).scalar() or 0
    active_subscriptions = Subscription.query.filter_by(is_active=True).count()
    
    # Calcular taxa de ocupação
    total_berths = Berth.query.count()
    occupied_berths = Berth.query.filter_by(status='occupied').count()
    occupancy_rate = (occupied_berths / total_berths * 100) if total_berths > 0 else 0
    
    # Pagamentos pendentes
    pending_payments = Payment.query.filter_by(status='pending').count()
    
    # Pagamentos recentes para tabela
    recent_payments = Payment.query.join(Subscription).filter(
        *payment_filters
    ).order_by(Payment.created_at.desc()).limit(20).all()
    
    # Dados para filtros
    marinas = Marina.query.all()
    plans = SubscriptionPlan.query.all()
    
    context = {
        'monthly_revenue': monthly_revenue,
        'marina_revenue': marina_revenue,
        'service_stats': service_stats,
        'total_revenue': total_revenue,
        'active_subscriptions': active_subscriptions,
        'occupancy_rate': occupancy_rate,
        'pending_payments': pending_payments,
        'recent_payments': recent_payments,
        'marinas': marinas,
        'plans': plans
    }
    
    return render_template('admin/reports.html', **context)

# Audit Logs
@bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """List all audit logs"""
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '')
    table_filter = request.args.get('table', '')
    user_filter = request.args.get('user', '')
    
    query = AuditLog.query
    
    if action_filter:
        query = query.filter(AuditLog.action.contains(action_filter))
    if table_filter:
        query = query.filter(AuditLog.table_name.contains(table_filter))
    if user_filter:
        query = query.join(User).filter(User.full_name.contains(user_filter))
    
    logs = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/audit_logs.html', logs=logs, 
                         action_filter=action_filter, 
                         table_filter=table_filter, 
                         user_filter=user_filter)

@bp.route('/audit-logs/<int:log_id>')
@login_required
@admin_required
def audit_log_detail(log_id):
    """Audit log detail view"""
    log = AuditLog.query.get_or_404(log_id)
    return render_template('admin/audit_log_detail.html', log=log)

# Notifications Management
@bp.route('/notifications')
@login_required
@admin_required
def notifications():
    """List all notifications"""
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/notifications.html', notifications=notifications)

@bp.route('/notifications/new', methods=['GET', 'POST'])
@login_required
@admin_required
def notification_new():
    """Create new notification"""
    if request.method == 'POST':
        notification_type = request.form.get('type', 'general')
        title = request.form['title']
        message = request.form['message']
        target_users = request.form.getlist('target_users')
        
        # Criar notificação para usuários específicos ou todos
        if 'all_users' in target_users:
            users = User.query.filter_by(is_active=True).all()
        else:
            user_ids = [int(uid) for uid in target_users if uid.isdigit()]
            users = User.query.filter(User.id.in_(user_ids)).all()
        
        notifications_created = 0
        for user in users:
            notification = Notification(
                user_id=user.id,
                title=title,
                message=message,
                notification_type=notification_type,
                is_read=False,
                created_by=current_user.id
            )
            db.session.add(notification)
            notifications_created += 1
        
        db.session.commit()
        
        # Log da ação
        log_admin_action(
            action='NOTIFICATION_CREATE',
            description=f'Notificação criada: "{title}" para {notifications_created} usuários',
            new_values={
                'title': title,
                'type': notification_type,
                'target_count': notifications_created
            }
        )
        
        flash(f'Notificação enviada para {notifications_created} usuários!', 'success')
        return redirect(url_for('admin.notifications'))
    
    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('admin/notification_form.html', users=users)

@bp.route('/notifications/<int:notification_id>')
@login_required
@admin_required
def notification_detail(notification_id):
    """Notification detail view"""
    notification = Notification.query.get_or_404(notification_id)
    return render_template('admin/notification_detail.html', notification=notification)

@bp.route('/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
@admin_required
def notification_delete(notification_id):
    """Delete notification"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Log da exclusão
    log_admin_action(
        action='NOTIFICATION_DELETE',
        description=f'Notificação excluída: "{notification.title}"',
        record_id=notification.id,
        old_values={
            'title': notification.title,
            'notification_type': notification.notification_type,
            'user_id': notification.user_id
        }
    )
    
    db.session.delete(notification)
    db.session.commit()
    
    flash('Notificação excluída com sucesso!', 'success')
    return redirect(url_for('admin.notifications'))

# Bulk Messages
@bp.route('/bulk-messages')
@login_required
@admin_required
def bulk_messages():
    """Bulk messages management"""
    return render_template('admin/bulk_messages.html')

@bp.route('/bulk-messages/send', methods=['POST'])
@login_required
@admin_required
def send_bulk_message():
    """Send bulk message to users"""
    message_type = request.form.get('type', 'email')
    subject = request.form.get('subject', '')
    message_content = request.form['message']
    target_filter = request.form.get('target_filter', 'all')
    
    # Determinar usuários alvo
    if target_filter == 'all':
        users = User.query.filter_by(is_active=True).all()
    elif target_filter == 'subscribers':
        users = User.query.join(Subscription).filter(
            User.is_active == True,
            Subscription.is_active == True
        ).distinct().all()
    elif target_filter == 'admins':
        users = User.query.filter_by(is_admin=True, is_active=True).all()
    elif target_filter == 'custom':
        user_ids = request.form.getlist('custom_users')
        users = User.query.filter(User.id.in_(user_ids)).all()
    
    # Enviar mensagens
    messages_sent = 0
    for user in users:
        if message_type == 'email':
            # Aqui você pode integrar com seu serviço de email
            # Por enquanto, vamos criar uma notificação
            notification = Notification(
                user_id=user.id,
                title=subject or 'Mensagem do Sistema',
                message=message_content,
                notification_type='system_message',
                is_read=False,
                created_by=current_user.id
            )
            db.session.add(notification)
            messages_sent += 1
        elif message_type == 'notification':
            notification = Notification(
                user_id=user.id,
                title=subject or 'Notificação',
                message=message_content,
                notification_type='notification',
                is_read=False,
                created_by=current_user.id
            )
            db.session.add(notification)
            messages_sent += 1
    
    db.session.commit()
    
    # Log da ação
    log_admin_action(
        action='BULK_MESSAGE_SEND',
        description=f'Mensagem em massa enviada: "{subject}" para {messages_sent} usuários',
        new_values={
            'type': message_type,
            'subject': subject,
            'target_filter': target_filter,
            'messages_sent': messages_sent
        }
    )
    
    flash(f'Mensagem enviada para {messages_sent} usuários!', 'success')
    return redirect(url_for('admin.bulk_messages'))

# API endpoints for AJAX
@bp.route('/api/marinas/<int:marina_id>/berths')
@login_required
@admin_required
def api_marina_berths(marina_id):
    """API endpoint to get berths for a specific marina"""
    marina = Marina.query.get_or_404(marina_id)
    berths = Berth.query.filter_by(marina_id=marina_id).all()
    
    berths_data = []
    for berth in berths:
        berths_data.append({
            'id': berth.id,
            'number': berth.number,
            'type': berth.type,
            'status': berth.status,
            'length': berth.length,
            'width': berth.width,
            'depth': berth.depth
        })
    
    return jsonify({
        'marina': {
            'id': marina.id,
            'name': marina.name
        },
        'berths': berths_data
    })

@bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for dashboard statistics"""
    total_revenue_result = db.session.query(db.func.sum(Payment.amount)).filter(Payment.status == 'confirmed').scalar()
    total_revenue = total_revenue_result if total_revenue_result is not None else 0
    
    stats = {
        'total_users': User.query.count(),
        'total_marinas': Marina.query.count(),
        'total_berths': Berth.query.count(),
        'total_subscriptions': Subscription.query.count(),
        'total_revenue': total_revenue
    }
    return jsonify(stats)

@bp.route('/api/users')
@login_required
@admin_required
def api_users():
    """API endpoint for users list"""
    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return jsonify({
        'users': [
            {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'is_admin': user.is_admin
            }
            for user in users
        ]
    })

@bp.route('/api/payments/<int:payment_id>')
@login_required
@admin_required
def api_payment_detail(payment_id):
    """API endpoint for payment details"""
    payment = Payment.query.get_or_404(payment_id)
    
    html = f"""
    <div class="row">
        <div class="col-md-6">
            <h6>Informações do Pagamento</h6>
            <table class="table table-sm">
                <tr><td><strong>ID:</strong></td><td>{payment.id}</td></tr>
                <tr><td><strong>Valor:</strong></td><td>R$ {payment.amount}</td></tr>
                <tr><td><strong>Status:</strong></td><td>{payment.status}</td></tr>
                <tr><td><strong>Método:</strong></td><td>{payment.payment_method or 'N/A'}</td></tr>
                <tr><td><strong>Data de Criação:</strong></td><td>{payment.created_at.strftime('%d/%m/%Y %H:%M')}</td></tr>
                <tr><td><strong>Vencimento:</strong></td><td>{payment.due_date.strftime('%d/%m/%Y') if payment.due_date else 'N/A'}</td></tr>
            </table>
        </div>
        <div class="col-md-6">
            <h6>Informações do Usuário</h6>
            <table class="table table-sm">
                <tr><td><strong>Nome:</strong></td><td>{payment.subscription.user.full_name}</td></tr>
                <tr><td><strong>Email:</strong></td><td>{payment.subscription.user.email}</td></tr>
                <tr><td><strong>Marina:</strong></td><td>{payment.subscription.marina.name}</td></tr>
                <tr><td><strong>Vaga:</strong></td><td>{payment.subscription.berth.berth_number}</td></tr>
            </table>
        </div>
    </div>
    """
    
    return jsonify({'html': html})

@bp.route('/api/payments/<int:payment_id>/confirm', methods=['POST'])
@login_required
@admin_required
def api_confirm_payment(payment_id):
    """API endpoint to confirm payment"""
    payment = Payment.query.get_or_404(payment_id)
    
    try:
        payment.confirm_payment()
        db.session.commit()
        
        # Log da ação
        log_admin_action(
            action='PAYMENT_CONFIRM',
            description=f'Pagamento confirmado: R$ {payment.amount} - Usuário: {payment.subscription.user.full_name}',
            new_values={'payment_id': payment.id, 'status': 'confirmed'}
        )
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/export-payments')
@login_required
@admin_required
def export_payments():
    """Export payments to CSV"""
    from flask import Response
    import csv
    import io
    
    # Filtros
    status = request.args.get('status')
    method = request.args.get('method')
    date_from = request.args.get('dateFrom')
    date_to = request.args.get('dateTo')
    
    # Construir query
    query = Payment.query.join(Subscription)
    
    if status:
        query = query.filter(Payment.status == status)
    if method:
        query = query.filter(Payment.payment_method == method)
    if date_from:
        query = query.filter(Payment.created_at >= date_from)
    if date_to:
        query = query.filter(Payment.created_at <= date_to + ' 23:59:59')
    
    payments = query.order_by(Payment.created_at.desc()).all()
    
    # Criar CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        'ID', 'Data', 'Usuário', 'Email', 'Marina', 'Valor', 'Status', 
        'Método', 'Vencimento', 'ASAAS ID', 'Descrição'
    ])
    
    # Dados
    for payment in payments:
        writer.writerow([
            payment.id,
            payment.created_at.strftime('%d/%m/%Y %H:%M'),
            payment.subscription.user.full_name,
            payment.subscription.user.email,
            payment.subscription.marina.name,
            payment.amount,
            payment.status,
            payment.payment_method or 'N/A',
            payment.due_date.strftime('%d/%m/%Y') if payment.due_date else 'N/A',
            payment.asaas_payment_id or 'N/A',
            payment.description or 'N/A'
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=pagamentos.csv'}
    )

 