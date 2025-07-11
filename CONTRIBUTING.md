# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o BOATHOUSE! Este documento fornece diretrizes para contribuições.

## 📋 Como Contribuir

### 1. Fork e Clone

1. Faça um fork do repositório
2. Clone seu fork localmente:
   ```bash
   git clone https://github.com/seu-usuario/BoatHouse-V1.git
   cd BoatHouse-V1
   ```

### 2. Configuração do Ambiente

Execute o script de setup:

**Linux/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows:**
```cmd
scripts\setup.bat
```

### 3. Criar uma Branch

Crie uma branch para sua feature:
```bash
git checkout -b feature/nova-funcionalidade
```

### 4. Desenvolvimento

- Siga as convenções de código
- Escreva testes para novas funcionalidades
- Mantenha commits pequenos e descritivos
- Use mensagens de commit em português

### 5. Testes

Execute os testes antes de fazer commit:
```bash
# Testes unitários (quando implementados)
python -m pytest tests/

# Verificação de estilo
flake8 app/
```

### 6. Commit e Push

```bash
git add .
git commit -m "feat: adiciona nova funcionalidade"
git push origin feature/nova-funcionalidade
```

### 7. Pull Request

1. Vá para o repositório original no GitHub
2. Clique em "New Pull Request"
3. Selecione sua branch
4. Preencha o template do PR
5. Aguarde a revisão

## 📝 Convenções de Código

### Python

- Use **snake_case** para variáveis e funções
- Use **PascalCase** para classes
- Use **UPPER_CASE** para constantes
- Máximo 127 caracteres por linha
- Use docstrings para funções e classes

### Flask

- Use blueprints para organizar rotas
- Mantenha templates simples e reutilizáveis
- Use WTForms para validação de formulários
- Implemente tratamento de erros adequado

### Banco de Dados

- Use migrações para mudanças no schema
- Mantenha nomes de tabelas em snake_case
- Use foreign keys apropriadamente
- Documente relacionamentos complexos

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py
├── test_auth.py
├── test_models.py
├── test_services.py
└── test_api.py
```

### Executando Testes

```bash
# Todos os testes
python -m pytest

# Testes específicos
python -m pytest tests/test_auth.py

# Com cobertura
python -m pytest --cov=app tests/
```

## 📋 Template de Pull Request

```markdown
## 📝 Descrição
Breve descrição das mudanças

## 🔧 Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## 🧪 Testes
- [ ] Testes unitários passando
- [ ] Testes de integração passando
- [ ] Manual testing realizado

## 📸 Screenshots (se aplicável)
Adicione screenshots aqui

## ✅ Checklist
- [ ] Código segue as convenções
- [ ] Documentação atualizada
- [ ] Testes adicionados/atualizados
- [ ] Self-review realizado
```

## 🐛 Reportando Bugs

Use o template de issue para bugs:

```markdown
## 🐛 Descrição do Bug
Descrição clara e concisa do bug

## 🔄 Passos para Reproduzir
1. Vá para '...'
2. Clique em '...'
3. Role até '...'
4. Veja o erro

## ✅ Comportamento Esperado
O que deveria acontecer

## 📸 Screenshots
Se aplicável, adicione screenshots

## 💻 Ambiente
- OS: [ex: Windows 10]
- Python: [ex: 3.11]
- Browser: [ex: Chrome 120]

## 📋 Informações Adicionais
Qualquer contexto adicional
```

## 🚀 Deploy e Release

### Processo de Release

1. **Desenvolvimento**: Branch `develop`
2. **Staging**: Branch `staging` 
3. **Produção**: Branch `main`

### Versionamento

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Mudanças incompatíveis
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

## 📞 Suporte

- **Issues**: Use o GitHub Issues
- **Discussões**: Use o GitHub Discussions
- **Email**: suporte@boathouse.com

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a licença MIT.

---

**Obrigado por contribuir com o BOATHOUSE! 🚤** 