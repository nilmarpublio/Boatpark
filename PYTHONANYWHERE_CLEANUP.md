# 🧹 Limpeza de Espaço - PythonAnywhere

## 🚨 Erro: Disk quota exceeded

### 1. Verificar Uso de Disco
```bash
# Verificar espaço usado
du -sh ~

# Verificar espaço disponível
df -h

# Listar arquivos maiores
du -sh ~/* | sort -hr | head -10
```

### 2. Limpar Cache e Arquivos Temporários
```bash
# Limpar cache do pip
pip cache purge

# Limpar cache do Python
find ~/.cache -type f -delete 2>/dev/null || true

# Limpar arquivos temporários
rm -rf /tmp/* 2>/dev/null || true
```

### 3. Remover Ambientes Virtuais Antigos
```bash
# Listar ambientes virtuais
ls -la ~/ | grep venv

# Remover ambientes não utilizados
rm -rf ~/venv_old
rm -rf ~/env_old
```

### 4. Limpar Downloads e Arquivos Grandes
```bash
# Remover downloads antigos
rm -rf ~/Downloads/*

# Remover arquivos .pyc
find ~ -name "*.pyc" -delete

# Remover diretórios __pycache__
find ~ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

### 5. Verificar e Limpar Logs
```bash
# Verificar tamanho dos logs
du -sh ~/logs 2>/dev/null || echo "No logs directory"

# Limpar logs antigos
find ~/logs -name "*.log" -size +1M -delete 2>/dev/null || true
```

## 🔄 Reinstalar com Dependências Otimizadas

### Versão Lightweight do Requirements
Crie um arquivo `requirements_light.txt`:

```txt
# Flask e extensões essenciais
Flask==2.2.5
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-Migrate==4.0.5
Flask-WTF==1.1.1
Flask-Mail==0.10.0

# Banco de dados (apenas MySQL)
PyMySQL==1.1.0
SQLAlchemy==2.0.35
alembic==1.16.2

# Segurança essencial
bcrypt==4.0.1
email-validator==2.0.0

# Utilitários básicos
python-dotenv==1.0.0
requests==2.31.0

# Dependências Flask
Werkzeug==2.2.3
Jinja2==3.0.3
click==8.1.7
itsdangerous==2.1.2
blinker==1.8.2
markupsafe==2.1.3
```

### Instalar Versão Lightweight
```bash
# Remover ambiente virtual atual
rm -rf venv

# Criar novo ambiente virtual
python3 -m venv venv

# Ativar ambiente
source venv/bin/activate

# Instalar versão lightweight
pip install -r requirements_light.txt
```

## 💡 Alternativas para Pillow

### Opção A: Instalar Pillow Separadamente
```bash
# Instalar apenas Pillow
pip install Pillow==10.0.1

# Se ainda der erro, tentar versão mais antiga
pip install Pillow==9.5.0
```

### Opção B: Usar Alternativa ao Pillow
Se Pillow não for essencial, remova do requirements e use:
```bash
# Para processamento básico de imagens
pip install Pillow-SIMD  # Versão otimizada
# ou
pip install imageio  # Alternativa mais leve
```

## 🆘 Se Nada Funcionar

### 1. Upgrade da Conta PythonAnywhere
- Considere fazer upgrade para conta paga
- Mais espaço em disco disponível

### 2. Deploy Alternativo
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Heroku**: https://heroku.com

### 3. Otimizar o Projeto
- Remover arquivos desnecessários
- Comprimir imagens
- Usar CDN para arquivos estáticos

## 📊 Monitoramento de Espaço
```bash
# Script para monitorar espaço
#!/bin/bash
echo "=== USO DE DISCO ==="
df -h
echo ""
echo "=== MAIORES DIRETÓRIOS ==="
du -sh ~/* | sort -hr | head -5
echo ""
echo "=== ARQUIVOS MAIORES ==="
find ~ -type f -size +1M -exec ls -lh {} \; | head -10
```

---
**💡 Dica**: Sempre mantenha pelo menos 100MB livres no PythonAnywhere! 

## 🔧 Criar o arquivo requirements_light.txt

Execute este comando no **Bash Console** do PythonAnywhere:

```bash
# Criar o arquivo requirements_light.txt
cat > requirements_light.txt << 'EOF'
# Flask e extensões essenciais
Flask==2.2.5
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-Migrate==4.0.5
Flask-WTF==1.1.1
Flask-Mail==0.10.0

# Banco de dados (apenas MySQL)
PyMySQL==1.1.0
SQLAlchemy==2.0.35
alembic==1.16.2

# Segurança essencial
bcrypt==4.0.1
email-validator==2.0.0

# Utilitários básicos
python-dotenv==1.0.0
requests==2.31.0

# Dependências Flask
Werkzeug==2.2.3
Jinja2==3.0.3
click==8.1.7
itsdangerous==2.1.2
blinker==1.8.2
markupsafe==2.1.3
EOF
```

## ✅ Verificar se foi criado

```bash
# Verificar se o arquivo foi criado
ls -la requirements_light.txt

# Ver o conteúdo do arquivo
cat requirements_light.txt
```

## 🚀 Instalar dependências

```bash
<code_block_to_apply_changes_from>
```

## 🔍 Se der erro de quota novamente

Se ainda der erro de espaço, instale apenas as essenciais:

```bash
# Instalar apenas o essencial
pip install Flask==2.2.5
pip install Flask-SQLAlchemy==3.0.5
pip install Flask-Login==0.6.3
pip install PyMySQL==1.1.0
pip install python-dotenv==1.0.0
```

## 📋 Teste final

```bash
# Verificar instalação
pip list

# Testar Flask
python -c "import flask; print('Flask instalado com sucesso!')"
```

**Execute o primeiro comando (criar o arquivo) e me informe se funcionou!** 

## 🔍 **1. Verificar se o arquivo .env foi criado**

```bash
ls -la .env
cat .env
```

## ️ **2. Verificar se o banco MySQL existe**

No PythonAnywhere, vá para a aba **Databases** e verifique se existe um banco chamado `nilmarcastro$boatpark`.

**Se não existir, crie um:**
1. Clique em **"Create database"**
2. **Database name**: `nilmarcastro$boatpark`
3. **Username**: `nilmarcastro`
4. **Password**: `Strattus1997`

## ⚙️ **3. Configurar variáveis de ambiente**

```bash
export FLASK_APP=app.py
export FLASK_DEBUG=0
export DATABASE_URL="mysql://nilmarcastro:Strattus1997@nilmarcastro.mysql.pythonanywhere-services.com/nilmarcastro\$boatpark"
```

## 🧪 **4. Testar configuração**

```bash
<code_block_to_apply_changes_from>
```

## ️ **5. Limpar migrações antigas**

```bash
rm -rf migrations/versions/*
rm -f migrations/alembic.ini
```

## 🚀 **6. Inicializar novas migrações**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📋 **7. Testar aplicação**

```bash
python -c "from app import create_app; print('Aplicação carregada com sucesso!')"
```

**Execute os comandos em ordem e me informe o resultado de cada um!**

**Qual comando você quer executar primeiro?** 