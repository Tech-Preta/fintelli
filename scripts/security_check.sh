#!/bin/bash

# Script de validação de segurança para Fintelli
# Verifica se os secrets estão seguros e se as configurações de segurança estão corretas

echo "🔍 VALIDAÇÃO DE SEGURANÇA - FINTELLI"
echo "===================================="
echo

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
security_issues=0
warnings=0
checks_passed=0

# Função para imprimir status
print_status() {
    local status=$1
    local message=$2
    
    case $status in
        "PASS")
            echo -e "${GREEN}✅ PASS${NC}: $message"
            ((checks_passed++))
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL${NC}: $message"
            ((security_issues++))
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️  WARN${NC}: $message"
            ((warnings++))
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  INFO${NC}: $message"
            ;;
    esac
}

# Verificar se arquivo .env existe
echo "🔐 VERIFICANDO ARQUIVO .ENV"
echo "============================="

if [ ! -f ".env" ]; then
    print_status "FAIL" "Arquivo .env não encontrado"
    echo "   Crie o arquivo .env usando: cp .env.example .env"
    exit 1
else
    print_status "PASS" "Arquivo .env encontrado"
fi

# Verificar se .env está no .gitignore
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    print_status "PASS" "Arquivo .env está no .gitignore"
else
    print_status "FAIL" "Arquivo .env NÃO está no .gitignore"
fi

echo

# Verificar secrets inseguros
echo "🔒 VERIFICANDO SECRETS"
echo "====================="

# Verificar senha do PostgreSQL
postgres_pass=$(grep "^POSTGRES_PASSWORD=" .env 2>/dev/null | cut -d'=' -f2)
if [ "$postgres_pass" = "supersecretpassword" ]; then
    print_status "FAIL" "Senha do PostgreSQL ainda é a padrão insegura"
elif [ ${#postgres_pass} -lt 16 ]; then
    print_status "FAIL" "Senha do PostgreSQL muito curta (mínimo 16 caracteres)"
elif [ "$postgres_pass" = "CHANGE_ME_TO_STRONG_PASSWORD_32_CHARS_MIN" ]; then
    print_status "FAIL" "Senha do PostgreSQL não foi alterada do template"
else
    print_status "PASS" "Senha do PostgreSQL parece adequada"
fi

# Verificar APP_SECRET_KEY
app_secret=$(grep "^APP_SECRET_KEY=" .env 2>/dev/null | cut -d'=' -f2)
if [ "$app_secret" = "your-secret-key-here" ]; then
    print_status "FAIL" "APP_SECRET_KEY ainda é o valor padrão"
elif [ "$app_secret" = "GENERATE_SECURE_SECRET_KEY_HERE" ]; then
    print_status "FAIL" "APP_SECRET_KEY não foi alterada do template"
elif [ ${#app_secret} -lt 32 ]; then
    print_status "FAIL" "APP_SECRET_KEY muito curta (mínimo 32 caracteres)"
else
    print_status "PASS" "APP_SECRET_KEY parece adequada"
fi

# Verificar chave do Gemini
gemini_key=$(grep "^GEMINI_API_KEY=" .env 2>/dev/null | cut -d'=' -f2 | tr -d "'\"")
if [ "$gemini_key" = "YOUR_REAL_GEMINI_API_KEY_HERE" ]; then
    print_status "WARN" "Chave do Gemini AI precisa ser configurada"
elif [[ "$gemini_key" =~ ^AIza[0-9A-Za-z-_]{35}$ ]]; then
    print_status "PASS" "Formato da chave Gemini AI parece correto"
else
    print_status "WARN" "Formato da chave Gemini AI pode estar incorreto"
fi

# Verificar DEBUG
debug_mode=$(grep "^DEBUG=" .env 2>/dev/null | cut -d'=' -f2)
if [ "$debug_mode" = "True" ] || [ "$debug_mode" = "true" ]; then
    print_status "WARN" "Modo DEBUG está ativado (desabilite em produção)"
else
    print_status "PASS" "Modo DEBUG está desabilitado"
fi

echo

# Verificar configurações de Docker
echo "🐳 VERIFICANDO CONFIGURAÇÕES DOCKER"
echo "==================================="

if [ -f "docker-compose.yml" ]; then
    print_status "PASS" "docker-compose.yml encontrado"
    
    # Verificar se há senhas hard-coded
    if grep -q "password.*=" docker-compose.yml 2>/dev/null; then
        print_status "WARN" "Possíveis senhas hard-coded em docker-compose.yml"
    else
        print_status "PASS" "Nenhuma senha hard-coded encontrada em docker-compose.yml"
    fi
    
    # Verificar se portas sensíveis estão expostas
    if grep -q "ports:" docker-compose.yml; then
        exposed_ports=$(grep -A 1 "ports:" docker-compose.yml | grep -E ":[0-9]+" | wc -l)
        if [ $exposed_ports -gt 5 ]; then
            print_status "WARN" "Muitas portas expostas ($exposed_ports) - revisar necessidade"
        else
            print_status "PASS" "Número de portas expostas parece adequado"
        fi
    fi
else
    print_status "FAIL" "docker-compose.yml não encontrado"
fi

echo

# Verificar arquivos de configuração sensíveis
echo "📋 VERIFICANDO ARQUIVOS DE CONFIGURAÇÃO"
echo "======================================="

# Verificar se há arquivos com extensões perigosas
dangerous_files=$(find . -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "*.jks" 2>/dev/null | wc -l)
if [ $dangerous_files -gt 0 ]; then
    print_status "WARN" "Arquivos com extensões sensíveis encontrados ($dangerous_files)"
    find . -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "*.jks" 2>/dev/null | head -5
else
    print_status "PASS" "Nenhum arquivo com extensão sensível encontrado"
fi

# Verificar permissões do .env
if [ -f ".env" ]; then
    env_perms=$(stat -c "%a" .env 2>/dev/null)
    if [ "$env_perms" = "600" ] || [ "$env_perms" = "644" ]; then
        print_status "PASS" "Permissões do .env adequadas ($env_perms)"
    else
        print_status "WARN" "Permissões do .env podem ser muito abertas ($env_perms)"
    fi
fi

echo

# Verificar dependências com vulnerabilidades conhecidas
echo "📦 VERIFICANDO DEPENDÊNCIAS"
echo "==========================="

# Backend Python
if [ -f "src/backend/requirements.txt" ]; then
    print_status "INFO" "Verificando dependências Python..."
    
    # Verificar se pip-audit está disponível
    if command -v pip-audit >/dev/null 2>&1; then
        echo "   Executando auditoria de segurança..."
        cd src/backend
        pip-audit -r requirements.txt --format=text 2>/dev/null || print_status "WARN" "Auditoria de segurança falhou"
        cd ../..
    else
        print_status "WARN" "pip-audit não instalado (instale com: pip install pip-audit)"
    fi
fi

# Frontend Node.js
if [ -f "src/frontend/package.json" ]; then
    print_status "INFO" "Verificando dependências Node.js..."
    
    if command -v npm >/dev/null 2>&1; then
        cd src/frontend
        if [ -d "node_modules" ]; then
            npm audit --audit-level moderate 2>/dev/null || print_status "WARN" "Vulnerabilidades encontradas em dependências Node.js"
        else
            print_status "INFO" "node_modules não encontrado - execute npm install primeiro"
        fi
        cd ../..
    else
        print_status "WARN" "npm não está instalado"
    fi
fi

echo

# Verificar configurações de observabilidade
echo "📊 VERIFICANDO OBSERVABILIDADE"
echo "=============================="

# Verificar se métricas de segurança estão configuradas
if [ -f "config/prometheus.yml" ]; then
    if grep -q "security" config/prometheus.yml 2>/dev/null; then
        print_status "PASS" "Métricas de segurança configuradas"
    else
        print_status "WARN" "Métricas de segurança não configuradas explicitamente"
    fi
fi

# Verificar alertas de segurança
if [ -f "config/fintelli-enhanced-alerts.yml" ]; then
    security_alerts=$(grep -c "alert:" config/fintelli-enhanced-alerts.yml 2>/dev/null)
    if [ $security_alerts -gt 0 ]; then
        print_status "PASS" "Alertas de segurança configurados ($security_alerts alertas)"
    else
        print_status "WARN" "Nenhum alerta de segurança encontrado"
    fi
fi

echo

# Resumo final
echo "📊 RESUMO DA VALIDAÇÃO"
echo "====================="
echo -e "${GREEN}✅ Verificações aprovadas: $checks_passed${NC}"
echo -e "${YELLOW}⚠️  Avisos: $warnings${NC}"
echo -e "${RED}❌ Problemas críticos: $security_issues${NC}"
echo

# Recomendações baseadas nos resultados
if [ $security_issues -gt 0 ]; then
    echo -e "${RED}🚨 AÇÃO NECESSÁRIA:${NC}"
    echo "   - Corrija os problemas críticos imediatamente"
    echo "   - Execute: ./scripts/generate_secrets.sh"
    echo "   - Revise as configurações de segurança"
elif [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}⚠️  RECOMENDAÇÕES:${NC}"
    echo "   - Revise os avisos para melhorar a segurança"
    echo "   - Configure chaves de API adequadamente"
    echo "   - Considere implementar as melhorias sugeridas"
else
    echo -e "${GREEN}🎉 EXCELENTE!${NC}"
    echo "   - Configuração de segurança está adequada"
    echo "   - Continue monitorando e atualizando regularmente"
fi

echo
echo "📚 Para mais informações, consulte:"
echo "   - SECURITY_RECOMMENDATIONS.md"
echo "   - docs/EBOOK_TECNOLOGIAS_FINTELLI.md"

# Exit code baseado no número de problemas críticos
exit $security_issues
