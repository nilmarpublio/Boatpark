from flask import request, session, redirect, url_for, flash
from flask_login import current_user
from functools import wraps
import time

class SessionMiddleware:
    """Middleware para gerenciar sessões e forçar logout quando necessário"""
    
    def __init__(self, app):
        self.app = app
        app.before_request(self.before_request)
    
    def before_request(self):
        """Executado antes de cada requisição"""
        # Se o usuário está logado, verificar se a sessão ainda é válida
        if current_user.is_authenticated:
            # Verificar se há timestamp de login na sessão
            if 'login_timestamp' not in session:
                # Se não há timestamp, forçar logout
                self._force_logout("Sessão inválida. Faça login novamente.")
                return
            
            # Verificar se a sessão não expirou (opcional - já configurado para expirar com navegador)
            # current_time = time.time()
            # login_time = session.get('login_timestamp', 0)
            # if current_time - login_time > 3600:  # 1 hora
            #     self._force_logout("Sessão expirada. Faça login novamente.")
            #     return
    
    def _force_logout(self, message):
        """Força o logout do usuário"""
        from flask_login import logout_user
        
        # Limpar sessão
        session.clear()
        logout_user()
        
        # Redirecionar para login
        flash(message, "warning")
        return redirect(url_for('auth.login'))

def require_fresh_session(f):
    """Decorator para forçar nova sessão a cada acesso"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            # Verificar se é uma nova sessão
            if 'session_id' not in session:
                # Gerar novo ID de sessão
                import uuid
                session['session_id'] = str(uuid.uuid4())
                session['login_timestamp'] = time.time()
            else:
                # Se já existe uma sessão, verificar se é a mesma
                # Isso força nova sessão a cada acesso
                import uuid
                session['session_id'] = str(uuid.uuid4())
                session['login_timestamp'] = time.time()
        
        return f(*args, **kwargs)
    return decorated_function 