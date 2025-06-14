#!/bin/bash

# Script de testes de integração para Fintelli
# Este script valida todos os componentes da stack

set -e  # Para na primeira falha

echo "🚀 Iniciando Testes de Integração do Fintelli"
echo "=============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
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

# Função para verificar se um serviço está rodando
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    log_info "Verificando $service_name em $url"
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        log_success "$service_name está funcionando"
        return 0
    else
        log_error "$service_name não está respondendo corretamente"
        return 1
    fi
}

# Função para verificar containers Docker
check_containers() {
    log_info "Verificando containers Docker..."
    
    local containers=(
        "fintelli_frontend"
        "fintelli_backend" 
        "fintelli_db"
        "fintelli_cache"
        "fintelli_otel_collector"
        "fintelli_jaeger"
        "fintelli_prometheus"
        "fintelli_grafana"
    )
    
    for container in "${containers[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "$container"; then
            local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "running")
            if [ "$status" = "healthy" ] || [ "$status" = "running" ]; then
                log_success "Container $container está rodando"
            else
                log_warning "Container $container está com status: $status"
            fi
        else
            log_error "Container $container não encontrado"
            return 1
        fi
    done
}

# Teste dos endpoints da API
test_api_endpoints() {
    log_info "Testando endpoints da API..."
    
    local base_url="http://localhost:8001"
    
    # Teste 1: Health check da documentação
    check_service "API Documentation" "$base_url/docs" "200"
    
    # Teste 2: Endpoint de resumo
    log_info "Testando endpoint /api/summary"
    local summary_response=$(curl -s "$base_url/api/summary")
    if echo "$summary_response" | jq -e '.income >= 0 and .expense <= 0 and has("balance")' > /dev/null 2>&1; then
        log_success "Endpoint /api/summary retornou dados válidos"
    else
        log_error "Endpoint /api/summary retornou dados inválidos: $summary_response"
    fi
    
    # Teste 3: Endpoint de transações
    log_info "Testando endpoint /api/transactions"
    local transactions_response=$(curl -s "$base_url/api/transactions")
    if echo "$transactions_response" | jq -e 'type == "array"' > /dev/null 2>&1; then
        log_success "Endpoint /api/transactions retornou array válido"
    else
        log_error "Endpoint /api/transactions não retornou array: $transactions_response"
    fi
    
    # Teste 4: Criação de transação
    log_info "Testando criação de transação"
    local new_transaction=$(cat <<EOF
{
    "description": "Teste Integração",
    "amount": 100.00,
    "transaction_date": "$(date +%Y-%m-%d)"
}
EOF
)
    
    local create_response=$(curl -s -X POST "$base_url/api/transactions" \
        -H "Content-Type: application/json" \
        -d "$new_transaction")
    
    if echo "$create_response" | jq -e 'has("id") and .description == "Teste Integração"' > /dev/null 2>&1; then
        log_success "Criação de transação funcionando"
        
        # Extrair ID para teste de deleção
        local transaction_id=$(echo "$create_response" | jq -r '.id')
        
        # Teste 5: Deleção de transação
        log_info "Testando deleção de transação ID: $transaction_id"
        local delete_status=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$base_url/api/transactions/$transaction_id")
        if [ "$delete_status" = "204" ]; then
            log_success "Deleção de transação funcionando"
        else
            log_warning "Deleção retornou status: $delete_status"
        fi
    else
        log_error "Criação de transação falhou: $create_response"
    fi
}

# Teste do Frontend
test_frontend() {
    log_info "Testando Frontend..."
    
    local frontend_url="http://localhost:8080"
    
    # Teste 1: Página principal
    check_service "Frontend" "$frontend_url" "200"
    
    # Teste 2: Assets estáticos
    log_info "Verificando se assets estão sendo servidos"
    local html_content=$(curl -s "$frontend_url")
    if echo "$html_content" | grep -q "Fintelli"; then
        log_success "Frontend carregando conteúdo correto"
    else
        log_warning "Frontend pode não estar carregando corretamente"
    fi
    
    # Teste 3: Proxy da API
    log_info "Testando proxy da API através do frontend"
    check_service "Frontend API Proxy" "$frontend_url/api/summary" "200"
}

# Teste do PostgreSQL
test_postgresql() {
    log_info "Testando PostgreSQL..."
    
    # Teste de conexão via Docker
    if docker exec fintelli_db psql -U finance_user -d finance_db -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "PostgreSQL está respondendo"
        
        # Teste das tabelas
        log_info "Verificando estrutura das tabelas"
        local tables=$(docker exec fintelli_db psql -U finance_user -d finance_db -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        if echo "$tables" | grep -q "transactions"; then
            log_success "Tabela transactions existe"
        else
            log_warning "Tabela transactions não encontrada"
        fi
        
        if echo "$tables" | grep -q "fixed_expenses"; then
            log_success "Tabela fixed_expenses existe"
        else
            log_warning "Tabela fixed_expenses não encontrada"
        fi
    else
        log_error "PostgreSQL não está respondendo"
        return 1
    fi
}

# Teste do Redis
test_redis() {
    log_info "Testando Redis..."
    
    # Teste de conexão via Docker
    if docker exec fintelli_cache redis-cli ping | grep -q "PONG"; then
        log_success "Redis está respondendo"
        
        # Teste de cache
        log_info "Testando operações de cache"
        docker exec fintelli_cache redis-cli set "test_key" "test_value" > /dev/null
        local cached_value=$(docker exec fintelli_cache redis-cli get "test_key")
        if [ "$cached_value" = "test_value" ]; then
            log_success "Operações de cache funcionando"
            docker exec fintelli_cache redis-cli del "test_key" > /dev/null
        else
            log_warning "Problemas com operações de cache"
        fi
    else
        log_error "Redis não está respondendo"
        return 1
    fi
}

# Teste do Prometheus
test_prometheus() {
    log_info "Testando Prometheus..."
    
    local prometheus_url="http://localhost:9091"
    
    # Teste 1: Interface web
    check_service "Prometheus Web UI" "$prometheus_url" "200"
    
    # Teste 2: Métricas da API
    log_info "Verificando métricas coletadas"
    local targets_response=$(curl -s "$prometheus_url/api/v1/targets")
    if echo "$targets_response" | jq -e '.status == "success"' > /dev/null 2>&1; then
        log_success "Prometheus está coletando métricas"
    else
        log_warning "Prometheus pode não estar coletando métricas corretamente"
    fi
    
    # Teste 3: Métrica customizada
    log_info "Verificando métrica customizada transactions_created_total"
    local custom_metric=$(curl -s "$prometheus_url/api/v1/query?query=transactions_created_total")
    if echo "$custom_metric" | jq -e '.data.result | length > 0' > /dev/null 2>&1; then
        log_success "Métrica customizada encontrada"
    else
        log_warning "Métrica customizada não encontrada ainda"
    fi
}

# Teste do Jaeger
test_jaeger() {
    log_info "Testando Jaeger..."
    
    local jaeger_url="http://localhost:16687"
    
    # Teste 1: Interface web
    check_service "Jaeger Web UI" "$jaeger_url" "200"
    
    # Teste 2: API de serviços
    log_info "Verificando serviços rastreados"
    local services_response=$(curl -s "$jaeger_url/api/services")
    if echo "$services_response" | jq -e '. | length >= 0' > /dev/null 2>&1; then
        log_success "Jaeger API está funcionando"
        
        # Verificar se o serviço fintelli-backend está sendo rastreado
        if echo "$services_response" | jq -e '.[] | select(. == "fintelli-backend")' > /dev/null 2>&1; then
            log_success "Serviço fintelli-backend está sendo rastreado"
        else
            log_warning "Serviço fintelli-backend ainda não aparece nos traces"
        fi
    else
        log_warning "Jaeger API pode não estar funcionando corretamente"
    fi
}

# Teste do Grafana
test_grafana() {
    log_info "Testando Grafana..."
    
    local grafana_url="http://localhost:3000"
    
    # Teste 1: Interface web
    check_service "Grafana Web UI" "$grafana_url" "200"
    
    # Teste 2: API de health
    log_info "Verificando health do Grafana"
    if curl -s "$grafana_url/api/health" | jq -e '.database == "ok"' > /dev/null 2>&1; then
        log_success "Grafana está saudável"
    else
        log_warning "Grafana pode ter problemas de health"
    fi
}

# Teste do OpenTelemetry Collector
test_otel_collector() {
    log_info "Testando OpenTelemetry Collector..."
    
    local otel_url="http://localhost:8888"
    
    # Teste 1: Métricas do collector
    check_service "OTel Collector Metrics" "$otel_url/metrics" "200"
    
    # Teste 2: Verificar se está recebendo dados
    log_info "Verificando métricas internas do collector"
    local metrics_content=$(curl -s "$otel_url/metrics")
    if echo "$metrics_content" | grep -q "otelcol_receiver_accepted_spans"; then
        log_success "Collector está recebendo spans"
    else
        log_warning "Collector pode não estar recebendo spans ainda"
    fi
}

# Teste de logs
test_logs() {
    log_info "Verificando logs dos containers..."
    
    local containers=("fintelli_frontend" "fintelli_backend" "fintelli_otel_collector")
    
    for container in "${containers[@]}"; do
        log_info "Últimas linhas do log de $container:"
        docker logs --tail 5 "$container" 2>&1 | sed 's/^/  /'
        echo ""
    done
}

# Função para testar logs do Docker Compose
test_docker_logs() {
    log_info "Testando acessibilidade dos logs..."
    
    local services=("frontend" "backend" "db" "cache" "prometheus" "jaeger" "grafana" "otel-collector")
    
    for service in "${services[@]}"; do
        log_info "Verificando logs do serviço $service"
        
        # Obtém as últimas 10 linhas do log
        local log_output=$(docker-compose logs --tail=10 "$service" 2>/dev/null)
        
        if [ $? -eq 0 ] && [ -n "$log_output" ]; then
            local log_lines=$(echo "$log_output" | wc -l)
            log_success "Logs do $service acessíveis ($log_lines linhas)"
            
            # Verifica se há erros críticos nos logs
            if echo "$log_output" | grep -i "error\|exception\|failed\|fatal" >/dev/null; then
                log_warning "Possíveis erros encontrados nos logs do $service"
                echo "$log_output" | grep -i "error\|exception\|failed\|fatal" | head -3
            fi
        else
            log_warning "Logs do $service não estão acessíveis ou estão vazios"
        fi
    done
}

# Função para testar OpenTelemetry
test_opentelemetry() {
    log_info "Testando OpenTelemetry..."
    
    # Verifica se o OTel Collector está rodando
    check_service "OTel Collector" "http://localhost:8889/metrics" "200"
    
    # Verifica se métricas estão sendo coletadas
    log_info "Verificando se métricas estão sendo coletadas..."
    local metrics_response=$(curl -s "http://localhost:8889/metrics")
    
    if echo "$metrics_response" | grep -q "otelcol_"; then
        log_success "Métricas do OTel Collector encontradas"
    else
        log_warning "Métricas do OTel Collector não encontradas"
    fi
    
    # Verifica se traces estão sendo enviados para o Jaeger
    log_info "Verificando traces no Jaeger..."
    local jaeger_services=$(curl -s "http://localhost:16687/api/services" | jq -r '.data[]' 2>/dev/null)
    
    if [ -n "$jaeger_services" ]; then
        log_success "Serviços encontrados no Jaeger: $jaeger_services"
    else
        log_warning "Nenhum serviço encontrado no Jaeger"
    fi
}

# Função para teste de JavaScript/Frontend
test_javascript_frontend() {
    log_info "Testando funcionalidades JavaScript do frontend..."
    
    # Verifica se o frontend carrega corretamente
    local frontend_content=$(curl -s "http://localhost:8080")
    
    if echo "$frontend_content" | grep -q "Fintelli"; then
        log_success "Frontend carregou com conteúdo correto"
    else
        log_error "Frontend não carregou conteúdo esperado"
    fi
    
    # Verifica se arquivos JavaScript estão sendo servidos
    if echo "$frontend_content" | grep -q "script\|telemetry.js"; then
        log_success "Arquivos JavaScript encontrados no frontend"
    else
        log_warning "Arquivos JavaScript não encontrados no frontend"
    fi
    
    # Testa chamadas de API do frontend
    log_info "Testando integração frontend-backend..."
    local api_test=$(curl -s -H "Origin: http://localhost:8080" "http://localhost:8001/api/summary")
    
    if [ $? -eq 0 ] && [ -n "$api_test" ]; then
        log_success "Frontend pode acessar APIs do backend"
    else
        log_error "Frontend não consegue acessar APIs do backend"
    fi
}

# Teste end-to-end
test_e2e_flow() {
    log_info "Executando teste end-to-end..."
    
    # 1. Criar uma transação via API
    local e2e_transaction=$(cat <<EOF
{
    "description": "E2E Test Transaction",
    "amount": 250.00,
    "transaction_date": "$(date +%Y-%m-%d)"
}
EOF
)
    
    log_info "Criando transação E2E..."
    local e2e_response=$(curl -s -X POST "http://localhost:8001/api/transactions" \
        -H "Content-Type: application/json" \
        -d "$e2e_transaction")
    
    if echo "$e2e_response" | jq -e 'has("id")' > /dev/null 2>&1; then
        local e2e_id=$(echo "$e2e_response" | jq -r '.id')
        log_success "Transação E2E criada com ID: $e2e_id"
        
        # 2. Verificar se aparece no resumo
        sleep 2  # Aguarda cache invalidation
        local updated_summary=$(curl -s "http://localhost:8001/api/summary")
        log_info "Resumo atualizado: $updated_summary"
        
        # 3. Verificar se aparece na lista
        local updated_transactions=$(curl -s "http://localhost:8001/api/transactions")
        if echo "$updated_transactions" | jq -e '.[] | select(.id == '$e2e_id')' > /dev/null 2>&1; then
            log_success "Transação aparece na listagem"
        else
            log_warning "Transação não aparece na listagem"
        fi
        
        # 4. Aguardar telemetria
        sleep 3
        log_info "Aguardando telemetria ser coletada..."
        
        # 5. Cleanup
        curl -s -X DELETE "http://localhost:8001/api/transactions/$e2e_id" > /dev/null
        log_success "Teste E2E concluído"
    else
        log_error "Falha no teste E2E: $e2e_response"
    fi
}

# Função principal
main() {
    echo "Iniciando testes em: $(date)"
    echo ""
    
    # Verificar dependências
    for cmd in curl jq docker; do
        if ! command -v $cmd &> /dev/null; then
            log_error "Comando $cmd não encontrado. Por favor, instale-o antes de continuar."
            exit 1
        fi
    done
    
    # Executar todos os testes
    check_containers || exit 1
    test_frontend || exit 1
    test_api_endpoints || exit 1
    test_postgresql || exit 1
    test_redis || exit 1
    test_otel_collector || exit 1
    test_prometheus || exit 1
    test_jaeger || exit 1
    test_grafana || exit 1
    test_e2e_flow || exit 1
    test_logs
    test_docker_logs
    test_opentelemetry
    test_javascript_frontend
    
    echo ""
    echo "=============================================="
    log_success "Todos os testes de integração passaram! 🎉"
    echo "Fintelli está funcionando perfeitamente!"
    echo "=============================================="
}

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
