import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")
    # Usar SQLite para desenvolvimento (mais simples)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///boathouse.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações ASAAS
    ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "your_asaas_api_key_here")
    ASAAS_BASE_URL = os.getenv("ASAAS_BASE_URL", "https://sandbox.asaas.com/api/v3")
    ASAAS_WEBHOOK_TOKEN = os.getenv("ASAAS_WEBHOOK_TOKEN", "your_webhook_token_here")
    
    # Configurações de pagamento
    PAYMENT_METHODS = ['BOLETO', 'CREDIT_CARD', 'PIX']
    DEFAULT_PAYMENT_METHOD = 'BOLETO'
    
    # Configurações de Email
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your_email@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@boathouse.com")
    FROM_NAME = os.getenv("FROM_NAME", "BOATHOUSE")
    
    # Configurações de segurança
    EMAIL_VERIFICATION_EXPIRES = 24  # horas
    PASSWORD_RESET_EXPIRES = 1  # hora
