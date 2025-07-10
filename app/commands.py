import click
from flask.cli import with_appcontext
from app import create_app, db
from app.models import Payment, SystemConfig
from app.services.notification_service import NotificationService
from datetime import datetime, timedelta

@click.command('check-overdue-payments')
@with_appcontext
def check_overdue_payments():
    """Verifica pagamentos vencidos e suspende assinaturas"""
    app = create_app()
    
    with app.app_context():
        print("Verificando pagamentos vencidos...")
        
        # Buscar pagamentos pendentes
        pending_payments = Payment.query.filter_by(status='pending').all()
        
        suspended_count = 0
        for payment in pending_payments:
            if payment.check_overdue_and_suspend():
                suspended_count += 1
                print(f"Assinatura suspensa para pagamento {payment.id}")
        
        db.session.commit()
        print(f"Verificação concluída. {suspended_count} assinaturas suspensas.")

@click.command('send-payment-reminders')
@with_appcontext
def send_payment_reminders():
    """Envia lembretes de pagamento"""
    app = create_app()
    
    with app.app_context():
        print("Enviando lembretes de pagamento...")
        
        config = SystemConfig.get_config()
        reminder_date = datetime.utcnow() + timedelta(days=config.payment_reminder_days)
        
        # Buscar pagamentos que vencem em X dias
        upcoming_payments = Payment.query.filter(
            Payment.status == 'pending',
            Payment.due_date <= reminder_date,
            Payment.due_date > datetime.utcnow()
        ).all()
        
        sent_count = 0
        for payment in upcoming_payments:
            try:
                NotificationService.send_payment_reminder(payment)
                sent_count += 1
                print(f"Lembrete enviado para pagamento {payment.id}")
            except Exception as e:
                print(f"Erro ao enviar lembrete para pagamento {payment.id}: {e}")
        
        print(f"Lembretes enviados: {sent_count}")

@click.command('send-vessel-removal-notices')
@with_appcontext
def send_vessel_removal_notices():
    """Envia avisos de retirada de embarcação"""
    app = create_app()
    
    with app.app_context():
        print("Enviando avisos de retirada de embarcação...")
        
        config = SystemConfig.get_config()
        removal_date = datetime.utcnow() + timedelta(days=config.vessel_removal_days)
        
        # Buscar pagamentos vencidos há X dias
        overdue_payments = Payment.query.filter(
            Payment.status == 'overdue',
            Payment.due_date <= removal_date
        ).all()
        
        sent_count = 0
        for payment in overdue_payments:
            try:
                NotificationService.send_vessel_removal_notification(payment)
                sent_count += 1
                print(f"Aviso de retirada enviado para pagamento {payment.id}")
            except Exception as e:
                print(f"Erro ao enviar aviso de retirada para pagamento {payment.id}: {e}")
        
        print(f"Avisos de retirada enviados: {sent_count}")

def register_commands(app):
    """Registra os comandos personalizados"""
    app.cli.add_command(check_overdue_payments)
    app.cli.add_command(send_payment_reminders)
    app.cli.add_command(send_vessel_removal_notices) 