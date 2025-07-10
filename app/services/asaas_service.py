import requests
import json
from datetime import datetime
from flask import current_app

class AsaasService:
    """Serviço para integração com a API ASAAS"""
    
    def __init__(self):
        self.api_key = current_app.config.get('ASAAS_API_KEY')
        self.base_url = current_app.config.get('ASAAS_BASE_URL', 'https://sandbox.asaas.com/api/v3')
        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def create_customer(self, user):
        """Cria um cliente no ASAAS"""
        try:
            url = f"{self.base_url}/customers"
            data = {
                'name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'cpfCnpj': user.cpf,
                'externalReference': str(user.uuid)
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            user.asaas_customer_id = result['id']
            
            current_app.logger.info(f"Cliente ASAAS criado: {result['id']} para usuário {user.email}")
            return result
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erro ao criar cliente ASAAS: {e}")
            raise
    
    def create_subscription(self, subscription):
        """Cria uma assinatura no ASAAS"""
        try:
            url = f"{self.base_url}/subscriptions"
            data = {
                'customer': subscription.user.asaas_customer_id,
                'billingType': 'BOLETO',  # ou 'CREDIT_CARD', 'PIX'
                'value': float(subscription.amount),
                'nextDueDate': subscription.start_date.strftime('%Y-%m-%d'),
                'cycle': subscription.billing_cycle.upper(),
                'description': f"Assinatura {subscription.plan_name} - {subscription.marina.name}",
                'externalReference': str(subscription.uuid)
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            subscription.asaas_subscription_id = result['id']
            
            current_app.logger.info(f"Assinatura ASAAS criada: {result['id']} para {subscription.user.email}")
            return result
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erro ao criar assinatura ASAAS: {e}")
            raise
    
    def create_payment(self, payment):
        """Cria um pagamento no ASAAS"""
        try:
            url = f"{self.base_url}/payments"
            data = {
                'customer': payment.subscription.user.asaas_customer_id,
                'billingType': payment.payment_method.upper(),
                'value': float(payment.amount),
                'dueDate': payment.due_date.strftime('%Y-%m-%d'),
                'description': payment.description or f"Pagamento {payment.subscription.plan_name}",
                'externalReference': str(payment.uuid)
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            payment.asaas_payment_id = result['id']
            
            # Salvar URLs de pagamento
            if 'invoiceUrl' in result:
                payment.asaas_invoice_url = result['invoiceUrl']
            if 'bankSlipUrl' in result:
                payment.asaas_bank_slip_url = result['bankSlipUrl']
            if 'pixQrCode' in result:
                payment.asaas_pix_qr_code = result['pixQrCode']
            if 'pixQrCodeUrl' in result:
                payment.asaas_pix_qr_code_url = result['pixQrCodeUrl']
            
            current_app.logger.info(f"Pagamento ASAAS criado: {result['id']} para {payment.subscription.user.email}")
            return result
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erro ao criar pagamento ASAAS: {e}")
            raise
    
    def get_payment_status(self, payment):
        """Obtém o status de um pagamento no ASAAS"""
        try:
            url = f"{self.base_url}/payments/{payment.asaas_payment_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            return result['status']
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erro ao obter status do pagamento ASAAS: {e}")
            raise
    
    def cancel_subscription(self, subscription):
        """Cancela uma assinatura no ASAAS"""
        try:
            url = f"{self.base_url}/subscriptions/{subscription.asaas_subscription_id}/cancel"
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            current_app.logger.info(f"Assinatura ASAAS cancelada: {subscription.asaas_subscription_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erro ao cancelar assinatura ASAAS: {e}")
            raise
    
    def process_webhook(self, webhook_data):
        """Processa webhook do ASAAS"""
        try:
            event = webhook_data.get('event')
            payment_data = webhook_data.get('payment', {})
            
            current_app.logger.info(f"Webhook ASAAS recebido: {event}")
            
            # Buscar pagamento pelo ID do ASAAS
            from app.models import Payment
            payment = Payment.query.filter_by(asaas_payment_id=payment_data.get('id')).first()
            
            if not payment:
                current_app.logger.warning(f"Pagamento não encontrado: {payment_data.get('id')}")
                return
            
            # Atualizar status baseado no evento
            if event == 'PAYMENT_RECEIVED':
                payment.confirm_payment()
                payment.subscription.activate()
            elif event == 'PAYMENT_OVERDUE':
                payment.mark_as_overdue()
                payment.subscription.suspend()
            elif event == 'PAYMENT_DELETED':
                payment.cancel_payment()
            
            # Salvar alterações
            from app.extensions import db
            db.session.commit()
            
            current_app.logger.info(f"Webhook processado: {event} para pagamento {payment.id}")
            
        except Exception as e:
            current_app.logger.error(f"Erro ao processar webhook ASAAS: {e}")
            raise 