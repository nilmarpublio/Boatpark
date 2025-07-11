# ========================================
# WSGI CONFIGURAÇÃO PYTHONANYWHERE
# ========================================

import sys
import os

# Adiciona o diretório do projeto ao path
path = '/home/nilmarpublio/boatpark'
if path not in sys.path:
    sys.path.append(path)

# Configura as variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = 'app.py'

# Importa a aplicação Flask
from app import create_app

# Cria a aplicação
application = create_app()

# Para debug local (opcional)
if __name__ == '__main__':
    application.run() 