#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do BOATHOUSE
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User

def init_database():
    """Inicializa o banco de dados e cria um usuário administrador"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Inicializando banco de dados...")
        
        # Verificar qual banco está sendo usado
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if 'sqlite' in db_uri:
            print("📁 Usando SQLite (desenvolvimento)")
        else:
            print("🐘 Usando PostgreSQL (produção)")
        
        # Criar todas as tabelas
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar se já existe um usuário administrador
        admin_user = User.query.filter_by(is_admin=True).first()
        
        if not admin_user:
            print("👤 Criando usuário administrador...")
            
            # Criar usuário administrador padrão
            admin_email = "admin@boathouse.com"
            admin_password = "admin123"
            
            hashed_password = generate_password_hash(admin_password)
            admin_user = User(
                email=admin_email,
                password_hash=hashed_password,
                first_name="Administrador",
                last_name="BOATHOUSE",
                is_admin=True
            )
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Usuário administrador criado com sucesso!")
                print(f"📧 Email: {admin_email}")
                print(f"🔑 Senha: {admin_password}")
                print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
            except Exception as e:
                print(f"❌ Erro ao criar usuário administrador: {e}")
                db.session.rollback()
        else:
            print("✅ Usuário administrador já existe!")
        
        # Contar usuários
        total_users = User.query.count()
        print(f"📊 Total de usuários no sistema: {total_users}")
        
        print("\n🎉 Inicialização concluída!")
        print("🚀 Execute 'python run.py' para iniciar o servidor")
        
        if 'sqlite' in db_uri:
            print("💡 Dica: O arquivo do banco SQLite foi criado como 'boathouse.db'")

if __name__ == "__main__":
    init_database() 