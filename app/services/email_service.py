import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template
from datetime import datetime

class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self):
        self.smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = current_app.config.get('SMTP_PORT', 587)
        self.smtp_username = current_app.config.get('SMTP_USERNAME')
        self.smtp_password = current_app.config.get('SMTP_PASSWORD')
        self.from_email = current_app.config.get('FROM_EMAIL', 'noreply@boathouse.com')
        self.from_name = current_app.config.get('FROM_NAME', 'BOATHOUSE')
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Envia um email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Adicionar conteúdo HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Adicionar conteúdo texto se fornecido
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def send_welcome_email(self, user):
        """Envia email de boas-vindas"""
        subject = "Bem-vindo ao BOATHOUSE!"
        html_content = render_template('emails/welcome.html', user=user)
        text_content = f"Olá {user.first_name}, bem-vindo ao BOATHOUSE!"
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def send_verification_email(self, user, verification_url):
        """Envia email de verificação"""
        subject = "Verifique seu email - BOATHOUSE"
        html_content = render_template('emails/verification.html', 
                                     user=user, verification_url=verification_url)
        text_content = f"Clique no link para verificar seu email: {verification_url}"
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def send_password_reset_email(self, user, reset_url):
        """Envia email de redefinição de senha"""
        subject = "Redefinir senha - BOATHOUSE"
        html_content = render_template('emails/password_reset.html', 
                                     user=user, reset_url=reset_url)
        text_content = f"Clique no link para redefinir sua senha: {reset_url}"
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def send_payment_reminder(self, payment):
        """Envia lembrete de pagamento"""
        subject = "Lembrete de pagamento - BOATHOUSE"
        html_content = render_template('emails/payment_reminder.html', payment=payment)
        text_content = f"Seu pagamento vence em {payment.due_date.strftime('%d/%m/%Y')}"
        
        return self.send_email(payment.subscription.user.email, subject, html_content, text_content)
    
    def send_payment_confirmation(self, payment):
        """Envia confirmação de pagamento"""
        subject = "Pagamento confirmado - BOATHOUSE"
        html_content = render_template('emails/payment_confirmation.html', payment=payment)
        text_content = f"Seu pagamento de R$ {payment.amount} foi confirmado"
        
        return self.send_email(payment.subscription.user.email, subject, html_content, text_content)
    
    def send_subscription_expiry_warning(self, subscription):
        """Envia aviso de expiração de assinatura"""
        subject = "Sua assinatura expira em breve - BOATHOUSE"
        html_content = render_template('emails/subscription_expiry.html', subscription=subscription)
        text_content = f"Sua assinatura expira em {subscription.days_until_expiry} dias"
        
        return self.send_email(subscription.user.email, subject, html_content, text_content) 