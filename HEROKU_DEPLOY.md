# 🚀 Deploy no Heroku - Guia Completo

## 📋 Pré-requisitos
- Conta no Heroku (gratuita)
- Repositório no GitHub: https://github.com/nilmarpublio/Boatpark

## 🔧 Passo a Passo

### 1. Criar Conta no Heroku
- Acesse [heroku.com](https://heroku.com)
- Crie uma conta gratuita
- Faça login no dashboard

### 2. Criar Novo App
1. Clique em **"New"** → **"Create new app"**
2. **App name**: `boatpark-app` (ou o nome que preferir)
3. **Region**: United States
4. Clique em **"Create app"**

### 3. Conectar ao GitHub
1. Na aba **"Deploy"**, clique em **"Connect to GitHub"**
2. Autorize o Heroku a acessar seu GitHub
3. Procure por `nilmarpublio/Boatpark`
4. Clique em **"Connect"**

### 4. Configurar Variáveis de Ambiente
Na aba **"Settings"** → **"Config Vars"**, adicione:

```
SECRET_KEY = boatpark-secret-key-2024-muito-segura
FLASK_ENV = production
FLASK_APP = app.py
```

### 5. Adicionar Banco PostgreSQL
1. Na aba **"Resources"**
2. Clique em **"Find more add-ons"**
3. Procure por **"Heroku Postgres"**
4. Selecione **"Hobby Dev"** (gratuito)
5. Clique em **"Submit Order Form"**

### 6. Deploy Automático
1. Na aba **"Deploy"**
2. Selecione a branch **"main"**
3. Clique em **"Deploy Branch"**
4. Aguarde o deploy (2-3 minutos)

### 7. Executar Migrações
Após o deploy, execute no **Heroku CLI** ou **Console**:

```bash
# Via Heroku CLI
heroku run flask db upgrade

# Ou via Console do Heroku
# Vá em "More" → "Run console"
# Digite: flask db upgrade
```

### 8. Inicializar Dados (Opcional)
```bash
heroku run python init_db_with_data.py
```

## 🌐 Acessar a Aplicação
- URL: `https://boatpark-app.herokuapp.com`
- Health check: `https://boatpark-app.herokuapp.com/health`

## 🔧 Configurações Avançadas

### Domínio Personalizado
1. Na aba **"Settings"**
2. Clique em **"Add domain"**
3. Adicione seu domínio

### SSL Automático
- Heroku fornece SSL automático
- Não precisa configurar nada

### Logs
- Aba **"More"** → **"View logs"**
- Ou via CLI: `heroku logs --tail`

## 🔄 Atualizações
Para atualizar:
1. Faça push para o GitHub
2. O Heroku fará deploy automático
3. Execute migrações se necessário: `heroku run flask db upgrade`

## 📊 Monitoramento
- **Metrics**: Aba **"Metrics"**
- **Logs**: Aba **"More"** → **"View logs"**
- **Status**: Aba **"Activity"**

## 🆘 Solução de Problemas

### Erro de Deploy
- Verifique os logs: `heroku logs --tail`
- Confirme se todas as dependências estão no `requirements.txt`

### Erro de Banco
- Verifique se o PostgreSQL foi adicionado
- Confirme as variáveis de ambiente

### Erro de Migração
```bash
heroku run flask db upgrade
heroku run flask db migrate -m "Fix migration"
```

## 💡 Dicas
- Heroku dorme após 30 minutos de inatividade (conta gratuita)
- Use `heroku logs --tail` para ver logs em tempo real
- Configure alertas de erro no dashboard

---
**🎉 Parabéns! Seu sistema Boatpark está no Heroku!**

**URL Final**: https://boatpark-app.herokuapp.com 