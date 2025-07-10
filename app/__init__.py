from flask import Flask, render_template
from .config import Config
from .extensions import db, login_manager, migrate

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

    @app.errorhandler(404)
    def page_not_found(e):
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
