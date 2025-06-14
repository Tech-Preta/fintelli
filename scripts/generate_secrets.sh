#!/bin/bash

# Script para gerar secrets seguros para Fintelli
# Uso: ./generate_secrets.sh

echo "🔐 GERADOR DE SECRETS SEGUROS - FINTELLI"
echo "========================================"
echo

# Verificar dependências
check_dependency() {
    command -v $1 >/dev/null 2>&1 || {
        echo "❌ Erro: $1 não está instalado."
        echo "   Instale com: sudo apt-get install $1"
        exit 1
    }
}

echo "🔍 Verificando dependências..."
check_dependency openssl
check_dependency python3
echo "✅ Todas as dependências estão instaladas."
echo

# Função para gerar senha forte
generate_password() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Função para gerar chave hexadecimal
generate_hex_key() {
    local length=${1:-32}
    openssl rand -hex $length
}

# Função para gerar chave URL-safe
generate_url_safe_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"
}

echo "🔑 Gerando secrets seguros..."
echo

# 1. Senha do PostgreSQL
postgres_password=$(generate_password 32)
echo "1. POSTGRES_PASSWORD (32 caracteres):"
echo "   $postgres_password"
echo

# 2. Chave secreta da aplicação
app_secret=$(generate_url_safe_key)
echo "2. APP_SECRET_KEY (URL-safe):"
echo "   $app_secret"
echo

# 3. Senha do Redis
redis_password=$(generate_password 24)
echo "3. REDIS_PASSWORD (24 caracteres):"
echo "   $redis_password"
echo

# 4. JWT Secret
jwt_secret=$(generate_hex_key 64)
echo "4. JWT_SECRET (128 hex chars):"
echo "   $jwt_secret"
echo

# 5. Encryption Key
encryption_key=$(generate_hex_key 32)
echo "5. ENCRYPTION_KEY (64 hex chars):"
echo "   $encryption_key"
echo

# Gerar arquivo .env seguro
echo "📄 Gerando arquivo .env com secrets seguros..."
cat > .env.secure << EOF
# Arquivo .env gerado automaticamente com secrets seguros
# Gerado em: $(date)
# ⚠️ NUNCA commitar este arquivo!

# ===================================
# CREDENCIAIS DO BANCO DE DADOS
# ===================================
POSTGRES_DB=finance_db
POSTGRES_USER=finance_user
POSTGRES_PASSWORD=$postgres_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# ===================================
# CONFIGURAÇÕES DO REDIS
# ===================================
REDIS_HOST=cache
REDIS_PORT=6379
REDIS_PASSWORD=$redis_password

# ===================================
# API EXTERNA - GOOGLE GEMINI AI
# ===================================
# ⚠️ SUBSTITUA PELA SUA CHAVE REAL DO GEMINI
GEMINI_API_KEY=YOUR_REAL_GEMINI_API_KEY_HERE

# ===================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ===================================
APP_SECRET_KEY=$app_secret
DEBUG=False

# ===================================
# CONFIGURAÇÕES DE SEGURANÇA
# ===================================
JWT_SECRET=$jwt_secret
ENCRYPTION_KEY=$encryption_key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000

# ===================================
# CONFIGURAÇÕES DE OBSERVABILIDADE
# ===================================
SERVICE_NAME=fintelli-backend
ENVIRONMENT=development
JAEGER_ENDPOINT=http://jaeger:14268/api/traces
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

# ===================================
# CONFIGURAÇÕES GERAIS
# ===================================
LOG_LEVEL=INFO
TZ=America/Sao_Paulo
EOF

echo "✅ Arquivo '.env.secure' criado com sucesso!"
echo
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Renomeie o arquivo atual: mv .env .env.backup"
echo "2. Use o novo arquivo: mv .env.secure .env"
echo "3. Configure sua chave real do Gemini AI"
echo "4. Teste a aplicação com os novos secrets"
echo "5. Delete o backup após confirmar que tudo funciona"
echo
echo "🔒 LEMBRE-SE:"
echo "- Nunca commite o arquivo .env"
echo "- Adicione .env ao .gitignore"
echo "- Faça backup seguro dos secrets"
echo "- Rotacione os secrets periodicamente"
echo
echo "🚨 IMPORTANTE:"
echo "- A chave do Gemini AI precisa ser configurada manualmente"
echo "- Configure SSL/TLS para conexões de banco em produção"
echo "- Use um gerenciador de secrets em produção (Azure Key Vault, AWS Secrets Manager)"
