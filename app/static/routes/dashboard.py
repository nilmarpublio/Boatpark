from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import MarinaService, ServiceRequest, Marina, Berth, User, Subscription, Payment

bp = Blueprint("dashboard", __name__)

@bp.route("/")
@login_required
def index():
    if current_user.is_admin:
        # Dados para administradores
        context = {
            'user': current_user,
            'total_marinas': Marina.query.count(),
            'total_users': User.query.filter_by(is_admin=False).count(),
            'total_berths': Berth.query.count(),
            'active_subscriptions': Subscription.query.filter_by(is_active=True).count(),
            'pending_payments': Payment.query.filter_by(status='pending').count(),
            'recent_services': ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).limit(5).all()
        }
    else:
        # Dados para clientes
        user_services = ServiceRequest.query.filter_by(user_id=current_user.id).all()
        user_subscriptions = Subscription.query.filter_by(user_id=current_user.id, is_active=True).all()
        pending_payments = Payment.query.join(Subscription).filter(
            Subscription.user_id == current_user.id,
            Payment.status == 'pending'
        ).all()
        
        context = {
            'user': current_user,
            'total_vessels': len(current_user.vessels),
            'total_services': len(user_services),
            'pending_payments': len(pending_payments),
            'active_berths': len(user_subscriptions),
            'recent_services': user_services[:5]  # Últimos 5 serviços
        }
    
    return render_template("dashboard.html", **context)

@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
