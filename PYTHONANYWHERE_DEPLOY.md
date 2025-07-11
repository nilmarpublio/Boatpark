# 🚀 Deploy no PythonAnywhere - Guia Completo

## 📋 Pré-requisitos
- Conta no PythonAnywhere (gratuita ou paga)
- Repositório no GitHub: https://github.com/nilmarpublio/boatpark

## 🔧 Passo a Passo

### 1. Acessar o PythonAnywhere
- Vá para [www.pythonanywhere.com](https://www.pythonanywhere.com)
- Faça login na sua conta

### 2. Clonar o Repositório
No **Bash Console** do PythonAnywhere:
```bash
cd ~
git clone https://github.com/nilmarpublio/boatpark.git
cd boatpark
```

### 3. Configurar o Ambiente Virtual
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar o Banco de Dados MySQL
1. Vá para a aba **Databases** no PythonAnywhere
2. Crie um novo banco MySQL:
   - **Database name**: `nilmarpublio$boatpark`
   - **Username**: `nilmarpublio`
   - **Password**: (escolha uma senha forte)

### 5. Configurar Variáveis de Ambiente
Crie um arquivo `.env` no diretório do projeto:
```bash
nano .env
```

Conteúdo do arquivo `.env`:
```env
# Configurações do Banco de Dados
DATABASE_URL=mysql://nilmarpublio:SUA_SENHA@nilmarpublio.mysql.pythonanywhere-services.com/nilmarpublio$boatpark

# Chave Secreta
SECRET_KEY=sua-chave-secreta-muito-segura-aqui

# Configurações de Email (opcional)
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app

# Configurações do PythonAnywhere
FLASK_ENV=production
FLASK_APP=app.py
```

### 6. Inicializar o Banco de Dados
```bash
# Ativar ambiente virtual (se não estiver ativo)
source venv/bin/activate

# Executar migrações
flask db upgrade

# Inicializar dados (opcional)
python init_db_with_data.py
```

### 7. Configurar o WSGI
1. Vá para a aba **Web** no PythonAnywhere
2. Clique em **Add a new web app**
3. Escolha **Flask** e **Python 3.9** (ou versão mais recente)
4. Configure o caminho: `/home/nilmarpublio/boatpark`
5. Edite o arquivo WSGI e substitua o conteúdo por:

```python
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
```

### 8. Configurar o Domínio
1. Na aba **Web**, configure:
   - **Domain**: `nilmarpublio.pythonanywhere.com`
   - **Source code**: `/home/nilmarpublio/boatpark`
   - **Working directory**: `/home/nilmarpublio/boatpark`

### 9. Configurar Arquivos Estáticos
1. Na aba **Web**, vá em **Static files**
2. Adicione:
   - **URL**: `/static/`
   - **Directory**: `/home/nilmarpublio/boatpark/app/static`

### 10. Criar Diretórios Necessários
```bash
# Criar diretório de uploads
mkdir -p uploads/documents

# Criar diretório de logs
mkdir -p logs

# Definir permissões
chmod 755 uploads
chmod 755 logs
```

### 11. Testar a Aplicação
1. Clique em **Reload** na aba **Web**
2. Acesse: `https://nilmarpublio.pythonanywhere.com`
3. Teste o health check: `https://nilmarpublio.pythonanywhere.com/health`

## 🔧 Solução de Problemas

### Erro de Importação
Se houver erro de importação, verifique:
- Ambiente virtual ativado
- Dependências instaladas
- Caminho correto no WSGI

### Erro de Banco de Dados
Se houver erro de conexão:
- Verifique as credenciais no `.env`
- Confirme se o banco foi criado
- Teste a conexão manualmente

### Erro de Permissão
```bash
# Dar permissões necessárias
chmod -R 755 /home/nilmarpublio/boatpark
chmod 644 /home/nilmarpublio/boatpark/.env
```

## 📝 Logs e Debug
- **Logs de erro**: Aba **Web** → **Error log**
- **Logs do servidor**: Aba **Web** → **Server log**
- **Console**: Aba **Consoles** → **Bash**

## 🔄 Atualizações
Para atualizar o projeto:
```bash
cd ~/boatpark
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
# Recarregar no PythonAnywhere
```

## 🌐 Domínio Personalizado (Opcional)
Para usar um domínio personalizado:
1. Configure o DNS para apontar para o PythonAnywhere
2. Adicione o domínio na aba **Web**
3. Configure SSL se necessário

## 📞 Suporte
- **PythonAnywhere**: [help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Documentação Flask**: [flask.palletsprojects.com](https://flask.palletsprojects.com)

---
**🎉 Parabéns! Seu sistema Boatpark está online!** 