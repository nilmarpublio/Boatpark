from flask import Blueprint, request, jsonify, current_app
from app.services.asaas_service import AsaasService
from app.models import Payment, Subscription, User
from app.extensions import db
from datetime import datetime
import hmac
import hashlib

bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

@bp.route('/asaas', methods=['POST'])
def asaas_webhook():
    """Webhook para receber notificações do ASAAS"""
    try:
        # Verificar assinatura do webhook (segurança)
        webhook_token = current_app.config.get('ASAAS_WEBHOOK_TOKEN')
        if webhook_token and webhook_token != 'your_webhook_token_here':
            signature = request.headers.get('asaas-access-token')
            if not signature or signature != webhook_token:
                current_app.logger.warning("Webhook ASAAS: Assinatura inválida")
                return jsonify({'error': 'Unauthorized'}), 401
        
        # Processar dados do webhook
        webhook_data = request.get_json()
        current_app.logger.info(f"Webhook ASAAS recebido: {webhook_data}")
        
        # Processar webhook usando o serviço ASAAS
        asaas_service = AsaasService()
        asaas_service.process_webhook(webhook_data)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao processar webhook ASAAS: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/asaas/test', methods=['GET'])
def test_asaas_webhook():
    """Rota de teste para verificar se o webhook está funcionando"""
    return jsonify({
        'status': 'success',
        'message': 'Webhook ASAAS está funcionando',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@bp.route('/asaas/events', methods=['GET'])
def list_webhook_events():
    """Lista os eventos de webhook suportados"""
    events = [
        'PAYMENT_RECEIVED',
        'PAYMENT_CONFIRMED', 
        'PAYMENT_OVERDUE',
        'PAYMENT_DELETED',
        'PAYMENT_RESTORED',
        'PAYMENT_REFUNDED',
        'PAYMENT_RECEIVED_IN_CASH_UNDONE',
        'PAYMENT_CHARGEBACK_REQUESTED',
        'PAYMENT_CHARGEBACK_DISPUTE',
        'PAYMENT_AWAITING_CHARGEBACK_REVERSAL',
        'PAYMENT_DUNNING_RECEIVED',
        'PAYMENT_DUNNING_REQUESTED',
        'SUBSCRIPTION_CREATED',
        'SUBSCRIPTION_UPDATED',
        'SUBSCRIPTION_DELETED',
        'SUBSCRIPTION_RESTORED',
        'SUBSCRIPTION_CHARGED',
        'SUBSCRIPTION_CHARGEBACK_REQUESTED',
        'SUBSCRIPTION_CHARGEBACK_DISPUTE',
        'SUBSCRIPTION_AWAITING_CHARGEBACK_REVERSAL',
        'SUBSCRIPTION_DUNNING_RECEIVED',
        'SUBSCRIPTION_DUNNING_REQUESTED'
    ]
    
    return jsonify({
        'events': events,
        'webhook_url': request.url_root.rstrip('/') + '/webhooks/asaas'
    }), 200 