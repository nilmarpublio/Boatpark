from flask import Blueprint, request, jsonify, current_app
from app.models import (
    User, Marina, Berth, Subscription, SubscriptionPlan, Payment, 
    ServiceRequest, Document, Vessel, Notification, SystemConfig
)
from app.extensions import db
from app.services.asaas_service import AsaasService
from app.services.notification_service import NotificationService
from datetime import datetime, timedelta
import json

bp = Blueprint('api', __name__, url_prefix='/api/v1')

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

@bp.route('/auth/login', methods=['POST'])
def login():
    """Login do usuário"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not user.email_verified:
            return jsonify({'error': 'Email não verificado'}), 403
        
        # Gerar token de acesso
        token = user.generate_auth_token()
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/auth/register', methods=['POST'])
def register():
    """Registro de usuário"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['email', 'password', 'full_name', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Separar nome completo
        full_name_parts = data['full_name'].split()
        first_name = full_name_parts[0] if full_name_parts else ''
        last_name = ' '.join(full_name_parts[1:]) if len(full_name_parts) > 1 else ''
        
        # Criar usuário
        user = User(
            email=data['email'],
            first_name=first_name,
            last_name=last_name,
            phone=data['phone'],
            cpf=data.get('cpf'),
            email_verified=True  # Para mobile, assumir verificado
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Gerar token
        token = user.generate_auth_token()
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'is_admin': user.is_admin
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PERFIL E DOCUMENTOS
# ============================================================================

@bp.route('/profile', methods=['GET'])
def get_profile():
    """Obter perfil do usuário"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        # Decodificar token
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        # Buscar assinaturas ativas
        active_subscriptions = Subscription.query.filter_by(
            user_id=user.id, status='active', is_active=True
        ).all()
        
        # Buscar documentos
        documents = Document.query.filter_by(user_id=user.id).all()
        
        # Buscar embarcações
        vessels = Vessel.query.filter_by(user_id=user.id).all()
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'cpf': user.cpf,
                'address': {
                    'street': user.address,
                    'city': user.city,
                    'state': user.state,
                    'zip_code': user.zip_code
                },
                'asaas_customer_id': user.asaas_customer_id
            },
            'subscriptions': [{
                'id': sub.id,
                'plan_name': sub.plan_name,
                'marina_name': sub.marina.name,
                'berth_number': sub.berth.number,
                'status': sub.status,
                'amount': float(sub.amount),
                'next_billing_date': sub.next_billing_date.isoformat() if sub.next_billing_date else None
            } for sub in active_subscriptions],
            'documents': [{
                'id': doc.id,
                'title': doc.document_name,
                'type': doc.document_type,
                'number': doc.document_number,
                'status': doc.status,
                'expiry_date': doc.expiry_date.isoformat() if doc.expiry_date else None
            } for doc in documents],
            'vessels': [{
                'id': vessel.id,
                'name': vessel.name,
                'type': vessel.type,
                'brand': vessel.brand,
                'model': vessel.model,
                'registration_number': vessel.registration_number
            } for vessel in vessels]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
def update_profile():
    """Atualizar perfil do usuário"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'full_name' in data:
            full_name_parts = data['full_name'].split()
            user.first_name = full_name_parts[0] if full_name_parts else ''
            user.last_name = ' '.join(full_name_parts[1:]) if len(full_name_parts) > 1 else ''
        if 'phone' in data:
            user.phone = data['phone']
        if 'cpf' in data:
            user.cpf = data['cpf']
        if 'address' in data:
            user.address = data['address'].get('street')
            user.city = data['address'].get('city')
            user.state = data['address'].get('state')
            user.zip_code = data['address'].get('zip_code')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MARINAS E VAGAS
# ============================================================================

@bp.route('/marinas', methods=['GET'])
def get_marinas():
    """Listar marinas"""
    try:
        marinas = Marina.query.filter_by(is_active=True).all()
        
        return jsonify({
            'marinas': [{
                'id': marina.id,
                'name': marina.name,
                'description': marina.description,
                'address': marina.address,
                'city': marina.city,
                'state': marina.state,
                'phone': marina.phone,
                'email': marina.email,
                'website': marina.website,
                'coordinates': {
                    'latitude': marina.latitude,
                    'longitude': marina.longitude
                },
                'total_berths': marina.berths.count(),
                'available_berths': marina.berths.filter_by(status='available').count(),
                'photos': marina.photos_list if marina.photos else []
            } for marina in marinas]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/marinas/<int:marina_id>', methods=['GET'])
def get_marina_detail(marina_id):
    """Detalhes da marina"""
    try:
        marina = Marina.query.get_or_404(marina_id)
        
        # Buscar vagas disponíveis
        available_berths = Berth.query.filter_by(
            marina_id=marina_id, status='available'
        ).all()
        
        return jsonify({
            'marina': {
                'id': marina.id,
                'name': marina.name,
                'description': marina.description,
                'address': marina.address,
                'city': marina.city,
                'state': marina.state,
                'phone': marina.phone,
                'email': marina.email,
                'website': marina.website,
                'coordinates': {
                    'latitude': marina.latitude,
                    'longitude': marina.longitude
                },
                'amenities': marina.amenities_list if marina.amenities else [],
                'services': marina.services_list if marina.services else [],
                'hours': marina.hours_list if marina.hours else [],
                'rules': marina.rules_list if marina.rules else [],
                'photos': marina.photos_list if marina.photos else []
            },
            'available_berths': [{
                'id': berth.id,
                'number': berth.number,
                'type': berth.type,
                'length': berth.length,
                'width': berth.width,
                'depth': berth.depth,
                'price': float(berth.price) if berth.price else None,
                'features': berth.features_list if berth.features else []
            } for berth in available_berths]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/marinas/<int:marina_id>/berths', methods=['GET'])
def get_marina_berths(marina_id):
    """Listar vagas de uma marina"""
    try:
        status = request.args.get('status', 'available')
        berths = Berth.query.filter_by(marina_id=marina_id, status=status).all()
        
        return jsonify({
            'berths': [{
                'id': berth.id,
                'number': berth.number,
                'type': berth.type,
                'length': berth.length,
                'width': berth.width,
                'depth': berth.depth,
                'price': float(berth.price) if berth.price else None,
                'status': berth.status,
                'features': berth.features_list if berth.features else []
            } for berth in berths]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PLANOS E ASSINATURAS
# ============================================================================

@bp.route('/plans', methods=['GET'])
def get_plans():
    """Listar planos disponíveis"""
    try:
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        
        return jsonify({
            'plans': [{
                'id': plan.id,
                'name': plan.name,
                'display_name': plan.display_name,
                'description': plan.description,
                'monthly_price': float(plan.monthly_price),
                'yearly_price': float(plan.yearly_price) if plan.yearly_price else None,
                'features': plan.features_list,
                'max_berths': plan.max_berths,
                'max_services_per_month': plan.max_services_per_month,
                'max_documents': plan.max_documents,
                'is_featured': plan.is_featured
            } for plan in plans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    """Listar assinaturas do usuário"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        subscriptions = Subscription.query.filter_by(user_id=user.id).all()
        
        return jsonify({
            'subscriptions': [{
                'id': sub.id,
                'plan_name': sub.plan_name,
                'marina_name': sub.marina.name,
                'berth_number': sub.berth.number,
                'status': sub.status,
                'amount': float(sub.amount),
                'start_date': sub.start_date.isoformat(),
                'end_date': sub.end_date.isoformat() if sub.end_date else None,
                'next_billing_date': sub.next_billing_date.isoformat() if sub.next_billing_date else None,
                'auto_renew': sub.auto_renew,
                'asaas_subscription_id': sub.asaas_subscription_id
            } for sub in subscriptions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    """Criar nova assinatura"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['marina_id', 'berth_id', 'plan_id', 'billing_cycle']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se a vaga está disponível
        berth = Berth.query.get_or_404(data['berth_id'])
        if berth.status != 'available':
            return jsonify({'error': 'Vaga não está disponível'}), 409
        
        # Obter plano
        plan = SubscriptionPlan.query.get_or_404(data['plan_id'])
        
        # Calcular valor
        if data['billing_cycle'] == 'monthly':
            amount = plan.monthly_price
        elif data['billing_cycle'] == 'yearly' and plan.yearly_price:
            amount = plan.yearly_price
        else:
            return jsonify({'error': 'Ciclo de cobrança inválido'}), 400
        
        # Criar assinatura
        subscription = Subscription(
            user_id=user.id,
            marina_id=data['marina_id'],
            berth_id=data['berth_id'],
            plan_id=data['plan_id'],
            plan_type=data['billing_cycle'],
            plan_name=f"{plan.display_name} - {data['billing_cycle'].title()}",
            amount=amount,
            start_date=datetime.utcnow(),
            billing_cycle=data['billing_cycle'],
            auto_renew=True
        )
        
        # Calcular datas
        if data['billing_cycle'] == 'monthly':
            subscription.end_date = subscription.start_date + timedelta(days=30)
        elif data['billing_cycle'] == 'yearly':
            subscription.end_date = subscription.start_date + timedelta(days=365)
        
        subscription.calculate_next_billing_date()
        
        db.session.add(subscription)
        db.session.commit()
        
        # Integração ASAAS
        try:
            asaas_service = AsaasService()
            
            # Criar cliente se não existir
            if not user.asaas_customer_id:
                asaas_service.create_customer(user)
                db.session.commit()
            
            # Criar assinatura ASAAS
            asaas_result = asaas_service.create_subscription(subscription)
            db.session.commit()
            
        except Exception as e:
            # Log do erro mas não falha a criação
            current_app.logger.error(f"Erro ASAAS: {e}")
        
        # Atualizar status da vaga
        berth.status = 'occupied'
        berth.subscription_id = subscription.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'subscription': {
                'id': subscription.id,
                'plan_name': subscription.plan_name,
                'amount': float(subscription.amount),
                'status': subscription.status
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PAGAMENTOS E FATURAS
# ============================================================================

@bp.route('/payments', methods=['GET'])
def get_payments():
    """Listar pagamentos do usuário"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        # Buscar pagamentos das assinaturas do usuário
        user_subscriptions = Subscription.query.filter_by(user_id=user.id).all()
        subscription_ids = [sub.id for sub in user_subscriptions]
        
        payments = Payment.query.filter(Payment.subscription_id.in_(subscription_ids)).all()
        
        return jsonify({
            'payments': [{
                'id': payment.id,
                'amount': float(payment.amount),
                'status': payment.status,
                'payment_method': payment.payment_method,
                'due_date': payment.due_date.isoformat(),
                'paid_date': payment.paid_date.isoformat() if payment.paid_date else None,
                'description': payment.description,
                'payment_url': payment.payment_url,
                'subscription': {
                    'plan_name': payment.subscription.plan_name,
                    'marina_name': payment.subscription.marina.name
                }
            } for payment in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment_detail(payment_id):
    """Detalhes do pagamento"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        payment = Payment.query.get_or_404(payment_id)
        
        # Verificar se o pagamento pertence ao usuário
        if payment.subscription.user_id != user.id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify({
            'payment': {
                'id': payment.id,
                'amount': float(payment.amount),
                'status': payment.status,
                'payment_method': payment.payment_method,
                'due_date': payment.due_date.isoformat(),
                'paid_date': payment.paid_date.isoformat() if payment.paid_date else None,
                'description': payment.description,
                'payment_url': payment.payment_url,
                'asaas_payment_id': payment.asaas_payment_id,
                'subscription': {
                    'plan_name': payment.subscription.plan_name,
                    'marina_name': payment.subscription.marina.name,
                    'berth_number': payment.subscription.berth.number
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# NOTIFICAÇÕES
# ============================================================================

@bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Listar notificações do usuário"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        notifications = Notification.query.filter_by(
            user_id=user.id
        ).order_by(Notification.created_at.desc()).limit(50).all()
        
        return jsonify({
            'notifications': [{
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat()
            } for notification in notifications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Marcar notificação como lida"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        notification = Notification.query.get_or_404(notification_id)
        
        if notification.user_id != user.id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SUPORTE E CHAT
# ============================================================================

@bp.route('/support/contact', methods=['POST'])
def contact_support():
    """Enviar mensagem para suporte"""
    try:
        # Verificar token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token obrigatório'}), 401
        
        parts = token.split('.')
        if len(parts) != 2:
            return jsonify({'error': 'Token inválido'}), 401
        
        user_id = int(parts[0])
        user = User.query.get(user_id)
        
        if not user or not user.verify_auth_token(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        
        if not data.get('message'):
            return jsonify({'error': 'Mensagem é obrigatória'}), 400
        
        # Criar notificação para administradores
        admin_users = User.query.filter_by(is_admin=True).all()
        
        for admin in admin_users:
            notification = Notification(
                user_id=admin.id,
                title=f"Suporte - {user.full_name}",
                message=f"Usuário: {user.email}\n\nMensagem: {data['message']}",
                type='support',
                created_by=user.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Mensagem enviada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CONFIGURAÇÕES DO APP
# ============================================================================

@bp.route('/config', methods=['GET'])
def get_app_config():
    """Obter configurações do app"""
    try:
        config = SystemConfig.get_config()
        
        return jsonify({
            'app_name': 'BoatHouse',
            'version': '1.0.0',
            'payment_overdue_days': config.payment_overdue_days,
            'support_email': config.support_email,
            'support_phone': config.support_phone
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 