#!/usr/bin/env python3
"""
BOATHOUSE V1 - Sistema de Gerenciamento de Marinas
Arquivo principal para execução da aplicação
"""

import logging
import sys
from app import create_app

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Criar a aplicação Flask
app = create_app()

# Forçar debug mode
app.debug = True
app.config['DEBUG'] = True

if __name__ == "__main__":
    print("🚤 BOATHOUSE V1 - Sistema de Gerenciamento de Marinas")
    print("=" * 60)
    print("Iniciando aplicação...")
    print("Acesse: http://localhost:5000")
    print()
    print("📋 LOGINS PARA TESTE:")
    print("=" * 40)
    print("🔑 SUPERADMIN (Administração do Sistema):")
    print("   Email: admin@boathouse.com")
    print("   Senha: admin123")
    print("   Funções: Todas as marinas, planos, configurações, logs")
    print()
    print("👨‍💼 ADMIN (Administração da Marina):")
    print("   Email: marina@boathouse.com")
    print("   Senha: marina123")
    print("   Funções: Apenas sua marina, usuários, serviços")
    print()
    print("👤 USUÁRIO (Cliente):")
    print("   Email: user@boathouse.com")
    print("   Senha: user123")
    print("   Funções: Perfil, embarcações, solicitações")
    print()
    print("Para parar: Ctrl + C")
    print("=" * 60)
    print()
    
    # Executar a aplicação em modo debug
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True) 