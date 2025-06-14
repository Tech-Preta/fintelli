#!/bin/bash

# Script Master para Executar Todos os Testes do Fintelli
# Este script executa uma suíte completa de testes e validações

set -e  # Para na primeira falha (pode ser desabilitado com --continue-on-error)

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Variáveis de controle
CONTINUE_ON_ERROR=false
QUICK_MODE=false
VERBOSE=false
SKIP_FRONTEND=false
SKIP_BACKEND=false
SKIP_INTEGRATION=false

# Função para logging
log_header() {
    echo -e "\n${PURPLE}========================================${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}========================================${NC}\n"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar dependências
check_dependencies() {
    log_header "Verificando Dependências"
    
    local missing_deps=()
    
    # Verificar comandos essenciais
    for cmd in docker docker-compose curl jq; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        else
            log_success "$cmd está instalado"
        fi
    done
    
    # Verificar Node.js para testes frontend
    if ! $SKIP_FRONTEND; then
        if ! command -v node &> /dev/null; then
            missing_deps+=(node)
        else
            log_success "Node.js $(node --version) está instalado"
        fi
        
        if ! command -v npm &> /dev/null; then
            missing_deps+=(npm)
        else
            log_success "npm $(npm --version) está instalado"
        fi
    fi
    
    # Verificar Python para testes backend
    if ! $SKIP_BACKEND; then
        if ! command -v python3 &> /dev/null; then
            missing_deps+=(python3)
        else
            log_success "Python $(python3 --version) está instalado"
        fi
        
        if ! command -v pip3 &> /dev/null; then
            missing_deps+=(pip3)
        else
            log_success "pip $(pip3 --version) está instalado"
        fi
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Dependências ausentes: ${missing_deps[*]}"
        log_info "Por favor, instale as dependências ausentes antes de continuar"
        exit 1
    fi
    
    log_success "Todas as dependências estão instaladas"
}

# Função para verificar se a aplicação está rodando
check_application_status() {
    log_header "Verificando Status da Aplicação"
    
    # Verificar se containers estão rodando
    if ! docker-compose ps --services --filter "status=running" | grep -q .; then
        log_warning "Nenhum container está rodando"
        log_info "Tentando iniciar a aplicação..."
        
        docker-compose up -d
        
        log_info "Aguardando serviços ficarem prontos (30s)..."
        sleep 30
    else
        log_success "Aplicação está rodando"
    fi
    
    # Verificar endpoints principais
    local endpoints=(
        "http://localhost:8080:Frontend"
        "http://localhost:8001/health:Backend API"
        "http://localhost:9091:Prometheus"
        "http://localhost:16687:Jaeger"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r url name <<< "$endpoint_info"
        
        if curl -s --max-time 10 "$url" >/dev/null 2>&1; then
            log_success "$name está acessível"
        else
            log_warning "$name não está acessível em $url"
        fi
    done
}

# Função para testes de backend
run_backend_tests() {
    if $SKIP_BACKEND; then
        log_info "Pulando testes de backend (--skip-backend)"
        return 0
    fi
    
    log_header "Executando Testes de Backend"
    
    cd tests/backend
    
    # Verificar se dependências estão instaladas
    if [ ! -f "requirements.txt" ]; then
        log_error "Arquivo requirements.txt não encontrado"
        return 1
    fi
    
    log_info "Instalando dependências do backend..."
    pip3 install -r requirements.txt --quiet || {
        log_error "Falha ao instalar dependências do backend"
        return 1
    }
    
    # Executar testes
    local pytest_args=()
    if $VERBOSE; then
        pytest_args+=("-v")
    fi
    
    if $QUICK_MODE; then
        pytest_args+=("-x")  # Para no primeiro erro
        pytest_args+=("--tb=short")  # Traceback curto
    else
        pytest_args+=("--cov=app" "--cov-report=term-missing")
    fi
    
    log_info "Executando testes pytest..."
    python3 -m pytest "${pytest_args[@]}" || {
        log_error "Testes de backend falharam"
        cd ../..
        return 1
    }
    
    log_success "Testes de backend concluídos com sucesso"
    cd ../..
    return 0
}

# Função para testes de frontend
run_frontend_tests() {
    if $SKIP_FRONTEND; then
        log_info "Pulando testes de frontend (--skip-frontend)"
        return 0
    fi
    
    log_header "Executando Testes de Frontend"
    
    cd tests/frontend
    
    # Verificar se package.json existe
    if [ ! -f "package.json" ]; then
        log_error "Arquivo package.json não encontrado"
        return 1
    fi
    
    # Instalar dependências se node_modules não existir
    if [ ! -d "node_modules" ]; then
        log_info "Instalando dependências do frontend..."
        npm install --silent || {
            log_error "Falha ao instalar dependências do frontend"
            return 1
        }
    fi
    
    # Executar testes
    local npm_args=("--watchAll=false")
    
    if $QUICK_MODE; then
        npm_args+=("--bail")  # Para no primeiro erro
    else
        npm_args+=("--coverage")
    fi
    
    if $VERBOSE; then
        npm_args+=("--verbose")
    fi
    
    log_info "Executando testes Jest..."
    npm test -- "${npm_args[@]}" || {
        log_error "Testes de frontend falharam"
        cd ../..
        return 1
    }
    
    log_success "Testes de frontend concluídos com sucesso"
    cd ../..
    return 0
}

# Função para testes de integração
run_integration_tests() {
    if $SKIP_INTEGRATION; then
        log_info "Pulando testes de integração (--skip-integration)"
        return 0
    fi
    
    log_header "Executando Testes de Integração"
    
    # Verificar se script existe
    if [ ! -f "tests/integration/run_tests.sh" ]; then
        log_error "Script de testes de integração não encontrado"
        return 1
    fi
    
    # Tornar executável se necessário
    chmod +x tests/integration/run_tests.sh
    
    log_info "Executando script de integração..."
    ./tests/integration/run_tests.sh || {
        log_error "Testes de integração falharam"
        return 1
    }
    
    log_success "Testes de integração concluídos com sucesso"
    return 0
}

# Função para relatório final
generate_report() {
    log_header "Relatório Final de Testes"
    
    echo "📊 Resumo da Execução:"
    echo "⏰ Tempo total: $((SECONDS / 60))m $((SECONDS % 60))s"
    echo "🏗️ Aplicação: $(docker-compose ps --services --filter 'status=running' | wc -l) serviços rodando"
    
    # Verificar coverage se disponível
    if [ -f "tests/backend/htmlcov/index.html" ]; then
        echo "📈 Coverage Backend: Relatório disponível em tests/backend/htmlcov/index.html"
    fi
    
    if [ -f "tests/frontend/coverage/lcov-report/index.html" ]; then
        echo "📈 Coverage Frontend: Relatório disponível em tests/frontend/coverage/lcov-report/index.html"
    fi
    
    echo ""
    echo "✅ Testes validados:"
    echo "   🎨 Frontend: Componentes React, utilitários JavaScript"
    echo "   ⚙️ Backend: APIs, banco de dados, cache, observabilidade"
    echo "   🔗 Integração: End-to-end, Docker, networking"
    echo ""
    echo "🌐 URLs de Validação:"
    echo "   Frontend: http://localhost:8080"
    echo "   Backend API: http://localhost:8001/docs"
    echo "   Prometheus: http://localhost:9091"
    echo "   Jaeger: http://localhost:16687"
    echo "   Grafana: http://localhost:3000"
}

# Função de ajuda
show_help() {
    echo "🧪 Script Master de Testes do Fintelli"
    echo ""
    echo "USAGE:"
    echo "  $0 [options]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help              Mostra esta ajuda"
    echo "  -q, --quick             Modo rápido (para no primeiro erro)"
    echo "  -v, --verbose           Output verboso"
    echo "  -c, --continue-on-error Continua mesmo com erros"
    echo "  --skip-frontend         Pula testes de frontend"
    echo "  --skip-backend          Pula testes de backend"
    echo "  --skip-integration      Pula testes de integração"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                      # Executa todos os testes"
    echo "  $0 --quick              # Execução rápida"
    echo "  $0 --skip-frontend      # Apenas backend e integração"
    echo "  $0 -v --continue-on-error # Verboso, não para em erros"
    echo ""
    echo "ABOUT:"
    echo "  Este script executa uma suíte completa de testes para o Fintelli,"
    echo "  incluindo testes de frontend (Jest), backend (pytest) e integração."
}

# Parser de argumentos
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -q|--quick)
                QUICK_MODE=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--continue-on-error)
                CONTINUE_ON_ERROR=true
                set +e
                shift
                ;;
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --skip-backend)
                SKIP_BACKEND=true
                shift
                ;;
            --skip-integration)
                SKIP_INTEGRATION=true
                shift
                ;;
            *)
                log_error "Opção desconhecida: $1"
                echo "Use --help para ver opções disponíveis"
                exit 1
                ;;
        esac
    done
}

# Função principal
main() {
    local start_time=$SECONDS
    
    echo "🧪 Script Master de Testes do Fintelli"
    echo "======================================"
    echo "⏰ Iniciado em: $(date)"
    echo "🏗️ Diretório: $(pwd)"
    
    if $QUICK_MODE; then
        echo "⚡ Modo: Rápido"
    fi
    
    if $VERBOSE; then
        echo "📝 Modo: Verboso"
    fi
    
    if $CONTINUE_ON_ERROR; then
        echo "🔄 Modo: Continuar em erros"
    fi
    
    echo ""
    
    # Executar etapas
    check_dependencies
    check_application_status
    
    local failed_tests=()
    
    # Backend tests
    if ! run_backend_tests; then
        failed_tests+=("Backend")
        if ! $CONTINUE_ON_ERROR; then
            log_error "Parando devido a falha nos testes de backend"
            exit 1
        fi
    fi
    
    # Frontend tests
    if ! run_frontend_tests; then
        failed_tests+=("Frontend")
        if ! $CONTINUE_ON_ERROR; then
            log_error "Parando devido a falha nos testes de frontend"
            exit 1
        fi
    fi
    
    # Integration tests
    if ! run_integration_tests; then
        failed_tests+=("Integração")
        if ! $CONTINUE_ON_ERROR; then
            log_error "Parando devido a falha nos testes de integração"
            exit 1
        fi
    fi
    
    # Relatório final
    generate_report
    
    # Resultado final
    if [ ${#failed_tests[@]} -eq 0 ]; then
        log_header "🎉 TODOS OS TESTES PASSARAM! 🎉"
        log_success "Fintelli está funcionando perfeitamente!"
        echo "🚀 Sistema pronto para produção!"
        exit 0
    else
        log_header "❌ ALGUNS TESTES FALHARAM"
        log_error "Testes que falharam: ${failed_tests[*]}"
        echo "🔧 Verifique os logs acima para detalhes"
        exit 1
    fi
}

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_arguments "$@"
    main
fi
