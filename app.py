#!/usr/bin/env python3
"""
BOATHOUSE V1 - Sistema de Gerenciamento de Marinas
Arquivo principal para execução da aplicação
"""

from app import create_app

# Criar a aplicação Flask
app = create_app()

if __name__ == "__main__":
    print("🚤 BOATHOUSE V1 - Sistema de Gerenciamento de Marinas")
    print("=" * 60)
    print("Iniciando aplicação...")
    print("Acesse: http://localhost:5000")
    print("Login padrão: admin@boathouse.com / admin123")
    print("Para parar: Ctrl + C")
    print("=" * 60)
    print()
    
    # Executar a aplicação em modo debug
    app.run(debug=True, host='0.0.0.0', port=5000) 