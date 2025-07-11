# ========================================
# CONFIGURAÇÃO HEROKU - BOATPARK
# ========================================

import os
from app.config import Config

class HerokuConfig(Config):
    """Configuração específica para Heroku"""
    
    # Configurações do Heroku
    DEBUG = False
    TESTING = False
    
    # URL base do Heroku (será substituída pelo domínio real)
    BASE_URL = os.environ.get('BASE_URL', 'https://boatpark-app.herokuapp.com')
    
    # Configurações de email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configurações de banco de dados (PostgreSQL no Heroku)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Configurações de segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'boatpark-secret-key-2024-muito-segura'
    
    # Configurações de upload (usar serviços externos no Heroku)
    UPLOAD_FOLDER = '/tmp/uploads'  # Temporário no Heroku
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Configurações de log
    LOG_LEVEL = 'INFO'
    
    # Configurações específicas do Heroku
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    } 