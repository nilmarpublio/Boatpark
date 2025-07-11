# 🚤 BOATPARK - Sistema de Gerenciamento de Marinas

Sistema web desenvolvido em Flask para gerenciamento de marinas, embarcações e usuários.

## 🚀 Instalação Rápida

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar ambiente**:
   ```bash
   # O arquivo .env já foi criado automaticamente
   # Edite se necessário
   ```

3. **Inicializar banco de dados**:
   ```bash
   python init_db.py
   ```

4. **Executar aplicação**:
   ```bash
   python app.py
   ```

5. **Acessar**:
   - URL: http://localhost:5000
   - Login: admin@boathouse.com
   - Senha: admin123

## 📋 Funcionalidades

- ✅ Sistema de autenticação completo
- ✅ Gestão de usuários e administradores
- ✅ Sistema de marinas e vagas
- ✅ Sistema de assinaturas com ASAAS
- ✅ Sistema de pagamentos
- ✅ Sistema de serviços
- ✅ Dashboard administrativo
- ✅ Relatórios e estatísticas
- ✅ Sistema de notificações
- ✅ Upload de documentos
- ✅ API REST

## 🛠️ Tecnologias

- **Backend**: Flask (Python)
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Frontend**: Bootstrap 5, Font Awesome
- **Autenticação**: Flask-Login
- **Migrações**: Flask-Migrate

## 📁 Estrutura

```
Boatpark/
├── app/                    # Aplicação Flask
├── migrations/             # Migrações do banco
├── uploads/               # Arquivos enviados
├── instance/              # Banco de dados
├── app.py                 # Execução principal
├── requirements.txt       # Dependências
├── init_db.py            # Inicialização do banco
└── README.md             # Este arquivo
```

## 🚀 Deploy

### Heroku
```bash
heroku create boatpark-app
git push heroku main
```

### Railway
```bash
railway up
```

### Render
```bash
git push render main
```

---

**🎯 Sistema pronto para uso em produção!**
