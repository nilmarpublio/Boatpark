# ========================================
# CONFIGURAÇÃO PYTHONANYWHERE
# ========================================

import os
from app.config import Config

class PythonAnywhereConfig(Config):
    """Configuração específica para PythonAnywhere"""
    
    # Configurações do PythonAnywhere
    DEBUG = False
    TESTING = False
    
    # URL base do PythonAnywhere (será substituída pelo seu domínio)
    BASE_URL = 'https://nilmarpublio.pythonanywhere.com'
    
    # Configurações de email (se necessário)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configurações de banco de dados
    # PythonAnywhere oferece MySQL por padrão
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://nilmarpublio:SUA_SENHA@nilmarpublio.mysql.pythonanywhere-services.com/nilmarpublio$boatpark'
    
    # Configurações de segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-aqui'
    
    # Configurações de upload
    UPLOAD_FOLDER = '/home/nilmarpublio/boatpark/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Configurações de log
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/home/nilmarpublio/boatpark/logs/app.log' 