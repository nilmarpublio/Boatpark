from functools import wraps
from flask import request, jsonify, current_app
from app.models import User

def token_required(f):
    """Decorator para verificar token de autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Verificar se o token está no header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token é obrigatório'}), 401
        
        try:
            # Decodificar token
            parts = token.split('.')
            if len(parts) != 2:
                return jsonify({'error': 'Token inválido'}), 401
            
            user_id = int(parts[0])
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 401
            
            if not user.verify_auth_token(token):
                return jsonify({'error': 'Token expirado ou inválido'}), 401
            
            # Adicionar usuário ao request
            request.current_user = user
            
        except Exception as e:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_token_required(f):
    """Decorator para verificar token de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Verificar se o token está no header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token é obrigatório'}), 401
        
        try:
            # Decodificar token
            parts = token.split('.')
            if len(parts) != 2:
                return jsonify({'error': 'Token inválido'}), 401
            
            user_id = int(parts[0])
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 401
            
            if not user.verify_auth_token(token):
                return jsonify({'error': 'Token expirado ou inválido'}), 401
            
            if not user.is_admin:
                return jsonify({'error': 'Acesso negado - Administrador requerido'}), 403
            
            # Adicionar usuário ao request
            request.current_user = user
            
        except Exception as e:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function 