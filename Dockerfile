# ========================================
# DOCKERFILE - BOATHOUSE
# ========================================

# Usar Python 3.11 slim como base
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements de produção primeiro para cache
COPY requirements-production.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements-production.txt

# Copiar código da aplicação
COPY . .

# Criar usuário não-root
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando para executar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"] 