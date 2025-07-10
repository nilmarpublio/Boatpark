from app.extensions import db
from app.models import Notification
from datetime import datetime

class NotificationService:
    """Serviço para gerenciamento de notificações"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type='info', 
                          action_url=None, action_text=None, data=None):
        """Cria uma nova notificação"""
        try:
            notification = Notification(
                user_id=user.id,
                title=title,
                message=message,
                notification_type=notification_type,
                action_url=action_url,
                action_text=action_text,
                data=data
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return notification
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def send_welcome_notification(user):
        """Envia notificação de boas-vindas"""
        return NotificationService.create_notification(
            user=user,
            title="Bem-vindo ao BOATHOUSE!",
            message=f"Olá {user.first_name}, seja bem-vindo ao sistema de gerenciamento de marinas.",
            notification_type='success',
            action_url='/dashboard',
            action_text='Acessar Dashboard'
        )
    
    @staticmethod
    def send_payment_reminder(payment):
        """Envia lembrete de pagamento"""
        return NotificationService.create_notification(
            user=payment.subscription.user,
            title="Lembrete de pagamento",
            message=f"Seu pagamento de R$ {payment.amount} vence em {payment.due_date.strftime('%d/%m/%Y')}",
            notification_type='warning',
            action_url=payment.payment_url,
            action_text='Pagar agora'
        )
    
    @staticmethod
    def send_payment_confirmation(payment):
        """Envia confirmação de pagamento"""
        return NotificationService.create_notification(
            user=payment.subscription.user,
            title="Pagamento confirmado",
            message=f"Seu pagamento de R$ {payment.amount} foi confirmado com sucesso!",
            notification_type='success'
        )
    
    @staticmethod
    def send_subscription_expiry_warning(subscription):
        """Envia aviso de expiração de assinatura"""
        return NotificationService.create_notification(
            user=subscription.user,
            title="Assinatura expira em breve",
            message=f"Sua assinatura expira em {subscription.days_until_expiry} dias. Renove agora!",
            notification_type='warning',
            action_url='/subscriptions',
            action_text='Renovar assinatura'
        )
    
    @staticmethod
    def send_document_approved_notification(document):
        """Envia notificação de documento aprovado"""
        return NotificationService.create_notification(
            user=document.user,
            title="Documento aprovado",
            message=f"Seu documento {document.document_name} foi aprovado.",
            notification_type='success'
        )
    
    @staticmethod
    def send_document_rejected_notification(document):
        """Envia notificação de documento rejeitado"""
        return NotificationService.create_notification(
            user=document.user,
            title="Documento rejeitado",
            message=f"Seu documento {document.document_name} foi rejeitado. Verifique as observações.",
            notification_type='error',
            action_url='/profile',
            action_text='Ver detalhes'
        )
    
    @staticmethod
    def send_subscription_suspended_notification(subscription):
        """Envia notificação de assinatura suspensa"""
        return NotificationService.create_notification(
            user=subscription.user,
            title="Assinatura suspensa",
            message="Sua assinatura foi suspensa devido a pagamento em atraso.",
            notification_type='error',
            action_url='/payments',
            action_text='Ver pagamentos'
        )
    
    @staticmethod
    def send_payment_overdue_notification(payment):
        """Envia notificação de pagamento vencido"""
        from app.models import SystemConfig
        
        config = SystemConfig.get_config()
        message = config.payment_overdue_message
        
        return NotificationService.create_notification(
            user=payment.subscription.user,
            title="Pagamento vencido",
            message=message,
            notification_type='error',
            action_url='/payments',
            action_text='Pagar agora'
        )
    
    @staticmethod
    def send_vessel_removal_notification(payment):
        """Envia notificação de retirada de embarcação"""
        from app.models import SystemConfig
        
        config = SystemConfig.get_config()
        message = config.get_vessel_removal_message(config.vessel_removal_days)
        
        return NotificationService.create_notification(
            user=payment.subscription.user,
            title="Retirada de embarcação",
            message=message,
            notification_type='error',
            action_url='/payments',
            action_text='Ver detalhes'
        )
    
    @staticmethod
    def get_user_notifications(user, limit=10, unread_only=False):
        """Obtém notificações do usuário"""
        query = Notification.query.filter_by(user_id=user.id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Marca uma notificação como lida"""
        notification = Notification.query.filter_by(
            id=notification_id, user_id=user_id
        ).first()
        
        if notification:
            notification.mark_as_read()
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Marca todas as notificações do usuário como lidas"""
        notifications = Notification.query.filter_by(
            user_id=user_id, is_read=False
        ).all()
        
        for notification in notifications:
            notification.mark_as_read()
        
        db.session.commit()
        return len(notifications)
    
    @staticmethod
    def get_unread_count(user_id):
        """Retorna o número de notificações não lidas"""
        return Notification.query.filter_by(
            user_id=user_id, is_read=False
        ).count() 