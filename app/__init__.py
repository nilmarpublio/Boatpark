from flask import Flask, render_template, request
from .config import Config
from .extensions import db, login_manager, migrate
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configurar login manager
    login_manager.login_view = 'auth.login'  # type: ignore
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Configurar sessão para expirar automaticamente
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Sessão dura 24 horas
    app.config['SESSION_COOKIE_SECURE'] = False  # True em produção com HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Configurações adicionais para debug
    app.config['SESSION_COOKIE_DOMAIN'] = None
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_MAX_AGE'] = None  # Sessão de navegador
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True

    # Definir a função user_loader
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar blueprints
    from .static.routes import auth, dashboard, admin, services, vessels, documents, webhooks, subscriptions, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(services.bp)
    app.register_blueprint(vessels.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(webhooks.bp)
    app.register_blueprint(subscriptions.bp)
    app.register_blueprint(api.bp)

    # Registrar comandos personalizados
    from .commands import register_commands
    register_commands(app)
    
    # Inicializar middleware de auditoria
    from .utils.audit_middleware import AuditMiddleware
    AuditMiddleware(app)
    
    # Inicializar middleware de sessão (temporariamente desabilitado para debug)
    # from .utils.session_middleware import SessionMiddleware
    # SessionMiddleware(app)

    @app.errorhandler(500)
    def internal_error(e):
        import traceback
        import sys
        print("=== ERRO 500 DETECTADO ===")
        print(f"Erro: {e}")
        print(f"Tipo: {type(e).__name__}")
        print("Traceback completo:")
        traceback.print_exc()
        print("=== FIM DO ERRO 500 ===")
        return f"Erro interno do servidor: {e}", 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        import sys
        print("=== EXCEÇÃO GERAL DETECTADA ===")
        print(f"Tipo de erro: {type(e).__name__}")
        print(f"Erro: {e}")
        print("Traceback completo:")
        traceback.print_exc()
        print("=== FIM DA EXCEÇÃO ===")
        return f"Erro: {str(e)}", 500

    # Handler para erros de template
    @app.errorhandler(500)
    def template_error(e):
        import traceback
        print("=== ERRO DE TEMPLATE DETECTADO ===")
        print(f"Erro: {e}")
        traceback.print_exc()
        return f"Erro de template: {str(e)}", 500

    # Handler para erros de rota
    @app.errorhandler(404)
    def not_found_error(e):
        print(f"=== ROTA NÃO ENCONTRADA: {request.url} ===")
        return render_template('404.html'), 404

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'BOATHOUSE is running'}, 200

    # Root endpoint
    @app.route('/')
    def root():
        return '''
        <html>
        <head><title>BOATHOUSE</title></head>
        <body>
            <h1>🚤 BOATHOUSE - Sistema de Gerenciamento de Marinas</h1>
            <p>Sistema funcionando corretamente!</p>
            <p><a href="/auth/login">Fazer Login</a></p>
            <p><a href="/health">Health Check</a></p>
        </body>
        </html>
        '''

    return app
