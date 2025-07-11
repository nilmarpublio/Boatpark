from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import MarinaService, ServiceRequest, Marina, Berth, User, Subscription, Payment
from app.services.weather_service import WeatherService

bp = Blueprint("dashboard", __name__)

@bp.route("/")
@login_required
def index():
    # Obter dados do tempo baseado na localização
    weather_service = WeatherService()
    
    # Determinar localização para o clima
    lat = None
    lon = None
    city = None
    
    if current_user.is_regular_admin:
        # Para admin regular, usar a primeira marina (Marina Santos)
        marina = Marina.query.first()
        if marina and marina.latitude and marina.longitude:
            lat = marina.latitude
            lon = marina.longitude
            city = marina.city
    elif current_user.is_superadmin:
        # Para superadmin, usar coordenadas padrão (São Paulo)
        lat = -23.5505
        lon = -46.6333
        city = "São Paulo"
    else:
        # Para usuários regulares, usar coordenadas padrão
        lat = -23.5505
        lon = -46.6333
        city = "São Paulo"
    
    # Obter dados do tempo com as coordenadas corretas
    current_weather = weather_service.get_current_weather(lat=lat, lon=lon, city=city)
    weather_forecast = weather_service.get_forecast(lat=lat, lon=lon, city=city, days=3)
    
    if current_user.is_admin:
        # Dados para administradores
        context = {
            'user': current_user,
            'total_marinas': Marina.query.count(),
            'total_users': User.query.filter_by(is_admin=False).count(),
            'total_berths': Berth.query.count(),
            'active_subscriptions': Subscription.query.filter_by(is_active=True).count(),
            'pending_payments': Payment.query.filter_by(status='pending').count(),
            'recent_services': ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).limit(5).all(),
            'current_weather': current_weather,
            'weather_forecast': weather_forecast
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
            'recent_services': user_services[:5],  # Últimos 5 serviços
            'current_weather': current_weather,
            'weather_forecast': weather_forecast
        }
    
    return render_template("dashboard.html", **context)

@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
