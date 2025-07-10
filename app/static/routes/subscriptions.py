from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Subscription, SubscriptionPlan, User, Marina, Berth, Payment
from app.extensions import db
from app.services.asaas_service import AsaasService
from app.static.routes.admin import admin_required
from datetime import datetime, timedelta
import json

bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

@bp.route('/')
@login_required
def index():
    """Lista de assinaturas do usuário"""
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).order_by(Subscription.created_at.desc()).all()
    return render_template('subscriptions/index.html', subscriptions=subscriptions)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Nova assinatura"""
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            marina_id = int(request.form['marina_id'])
            berth_id = int(request.form['berth_id'])
            plan_id = int(request.form['plan_id'])
            billing_cycle = request.form['billing_cycle']
            
            # Verificar se a vaga está disponível
            berth = Berth.query.get_or_404(berth_id)
            if berth.status != 'available':
                flash('Vaga não está disponível!', 'error')
                return redirect(request.url)
            
            # Obter plano
            plan = SubscriptionPlan.query.get_or_404(plan_id)
            
            # Calcular valor baseado no ciclo de cobrança
            if billing_cycle == 'monthly':
                amount = plan.monthly_price
            elif billing_cycle == 'yearly' and plan.yearly_price:
                amount = plan.yearly_price
            else:
                flash('Ciclo de cobrança inválido!', 'error')
                return redirect(request.url)
            
            # Criar assinatura
            subscription = Subscription(
                user_id=current_user.id,
                marina_id=marina_id,
                berth_id=berth_id,
                plan_id=plan_id,
                plan_type=billing_cycle,
                plan_name=f"{plan.display_name} - {billing_cycle.title()}",
                amount=amount,
                start_date=datetime.utcnow(),
                billing_cycle=billing_cycle,
                auto_renew=True
            )
            
            # Calcular data de término
            if billing_cycle == 'monthly':
                subscription.end_date = subscription.start_date + timedelta(days=30)
            elif billing_cycle == 'yearly':
                subscription.end_date = subscription.start_date + timedelta(days=365)
            
            # Calcular próxima data de cobrança
            subscription.calculate_next_billing_date()
            
            db.session.add(subscription)
            db.session.commit()
            
            # Integração com ASAAS
            try:
                asaas_service = AsaasService()
                
                # Criar cliente ASAAS se não existir
                if not current_user.asaas_customer_id:
                    asaas_service.create_customer(current_user)
                    db.session.commit()
                
                # Criar assinatura ASAAS
                asaas_result = asaas_service.create_subscription(subscription)
                db.session.commit()
                
                flash('Assinatura criada com sucesso e integrada ao ASAAS!', 'success')
                
            except Exception as e:
                flash(f'Assinatura criada, mas erro na integração ASAAS: {str(e)}', 'warning')
            
            # Atualizar status da vaga
            berth.status = 'occupied'
            berth.subscription_id = subscription.id
            db.session.commit()
            
            return redirect(url_for('subscriptions.detail', subscription_id=subscription.id))
            
        except Exception as e:
            flash(f'Erro ao criar assinatura: {str(e)}', 'error')
            return redirect(request.url)
    
    # Obter dados para o formulário
    marinas = Marina.query.filter_by(is_active=True).all()
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    
    return render_template('subscriptions/form.html', 
                         marinas=marinas, 
                         plans=plans, 
                         subscription=None)

@bp.route('/<int:subscription_id>')
@login_required
def detail(subscription_id):
    """Detalhes da assinatura"""
    subscription = Subscription.query.filter_by(id=subscription_id, user_id=current_user.id).first_or_404()
    return render_template('subscriptions/detail.html', subscription=subscription)

@bp.route('/<int:subscription_id>/cancel', methods=['POST'])
@login_required
def cancel(subscription_id):
    """Cancelar assinatura"""
    subscription = Subscription.query.filter_by(id=subscription_id, user_id=current_user.id).first_or_404()
    
    try:
        # Cancelar no ASAAS se existir
        if subscription.asaas_subscription_id:
            asaas_service = AsaasService()
            asaas_service.cancel_subscription(subscription)
        
        # Cancelar localmente
        subscription.cancel()
        
        # Liberar vaga
        if subscription.berth:
            subscription.berth.status = 'available'
            subscription.berth.subscription_id = None
        
        db.session.commit()
        
        flash('Assinatura cancelada com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao cancelar assinatura: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.index'))

@bp.route('/<int:subscription_id>/reactivate', methods=['POST'])
@login_required
def reactivate(subscription_id):
    """Reativar assinatura"""
    subscription = Subscription.query.filter_by(id=subscription_id, user_id=current_user.id).first_or_404()
    
    try:
        subscription.activate()
        db.session.commit()
        flash('Assinatura reativada com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao reativar assinatura: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.detail', subscription_id=subscription.id))

# Rotas administrativas
@bp.route('/admin')
@login_required
@admin_required
def admin_index():
    """Lista de todas as assinaturas (admin)"""
    subscriptions = Subscription.query.order_by(Subscription.created_at.desc()).all()
    return render_template('subscriptions/admin/index.html', subscriptions=subscriptions)

@bp.route('/admin/<int:subscription_id>')
@login_required
@admin_required
def admin_detail(subscription_id):
    """Detalhes da assinatura (admin)"""
    subscription = Subscription.query.get_or_404(subscription_id)
    return render_template('subscriptions/admin/detail.html', subscription=subscription)

@bp.route('/admin/<int:subscription_id>/suspend', methods=['POST'])
@login_required
@admin_required
def admin_suspend(subscription_id):
    """Suspender assinatura (admin)"""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    try:
        subscription.suspend()
        db.session.commit()
        flash('Assinatura suspensa com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao suspender assinatura: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.admin_detail', subscription_id=subscription.id))

@bp.route('/admin/<int:subscription_id>/activate', methods=['POST'])
@login_required
@admin_required
def admin_activate(subscription_id):
    """Ativar assinatura (admin)"""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    try:
        subscription.activate()
        db.session.commit()
        flash('Assinatura ativada com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao ativar assinatura: {str(e)}', 'error')
    
    return redirect(url_for('subscriptions.admin_detail', subscription_id=subscription.id))

# API para obter vagas de uma marina
@bp.route('/api/marinas/<int:marina_id>/berths')
@login_required
def api_marina_berths(marina_id):
    """API para obter vagas disponíveis de uma marina"""
    berths = Berth.query.filter_by(marina_id=marina_id, status='available').all()
    
    berths_data = []
    for berth in berths:
        berths_data.append({
            'id': berth.id,
            'number': berth.number,
            'type': berth.type,
            'length': berth.length,
            'width': berth.width,
            'depth': berth.depth,
            'price': float(berth.price) if berth.price else None
        })
    
    return jsonify({'berths': berths_data}) 