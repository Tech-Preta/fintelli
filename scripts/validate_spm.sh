#!/bin/bash

# Script de Validação do Service Performance Monitoring (SPM)
# Este script verifica se todas as componentes do SPM estão funcionando corretamente

echo "🔍 VALIDAÇÃO DO SPM (Service Performance Monitoring) - Fintelli"
echo "================================================================="

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para checar se um serviço está respondendo
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "📡 Checking $service_name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Função para checar métricas específicas
check_metrics() {
    local metrics_name=$1
    local query=$2
    local endpoint=$3
    
    echo -n "📊 Checking $metrics_name... "
    
    response=$(curl -s "$endpoint/api/v1/query?query=$query")
    
    if echo "$response" | grep -q '"status":"success"'; then
        result_count=$(echo "$response" | jq -r '.data.result | length')
        if [ "$result_count" -gt 0 ]; then
            echo -e "${GREEN}✅ OK ($result_count metrics found)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  No data yet${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

echo ""
echo "🔧 1. VERIFICANDO INFRAESTRUTURA BASE"
echo "------------------------------------"

# Verificar se os serviços estão rodando
check_service "OTel Collector" "http://localhost:8888/metrics"
check_service "Jaeger UI" "http://localhost:16687"
check_service "Jaeger Admin" "http://localhost:14269/metrics"
check_service "Prometheus" "http://localhost:9091"
check_service "Grafana" "http://localhost:3001/api/health"

echo ""
echo "📊 2. VERIFICANDO MÉTRICAS SPM"
echo "------------------------------"

# Verificar se métricas SPM estão sendo geradas
check_metrics "SPM Calls Total" "calls_total" "http://localhost:9091"
check_metrics "SPM Duration Histogram" "duration_bucket" "http://localhost:9091"
check_metrics "SPM Latency" "duration_sum" "http://localhost:9091"

echo ""
echo "🎯 3. VERIFICANDO MÉTRICAS ESPECÍFICAS DO FINTELLI"
echo "-------------------------------------------------"

# Verificar métricas específicas dos serviços do Fintelli
check_metrics "Backend Service Metrics" "calls_total{service_name=\"fintelli-backend\"}" "http://localhost:9091"
check_metrics "Transaction Endpoint Metrics" "calls_total{operation=~\".*transaction.*\"}" "http://localhost:9091"
check_metrics "HTTP Method Breakdown" "calls_total{http_method!=\"\"}" "http://localhost:9091"
check_metrics "Status Code Distribution" "calls_total{status_code!=\"\"}" "http://localhost:9091"

echo ""
echo "🚀 4. TESTE DE GERAÇÃO DE TRÁFEGO"
echo "--------------------------------"

echo "📤 Gerando tráfego de teste para o backend..."

# Gerar algumas requisições de teste para criar dados SPM
for i in {1..5}; do
    echo -n "  Request $i... "
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001/docs" | grep -q "200"; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
    fi
    sleep 1
done

echo ""
echo "⏳ Aguardando 30 segundos para métricas serem processadas..."
sleep 30

echo ""
echo "📈 5. VALIDAÇÃO FINAL DAS MÉTRICAS SPM"
echo "------------------------------------"

# Verificar novamente se as métricas foram coletadas
check_metrics "Backend Calls After Traffic" "calls_total{service_name=\"fintelli-backend\"}" "http://localhost:9091"
check_metrics "Request Duration Metrics" "duration_bucket{service_name=\"fintelli-backend\"}" "http://localhost:9091"

echo ""
echo "🎨 6. VERIFICANDO DASHBOARDS"
echo "---------------------------"

# Verificar se dashboard SPM pode ser acessado
check_service "Grafana Dashboard API" "http://localhost:3000/api/dashboards/uid/fintelli-spm" 404

echo ""
echo "📋 7. RELATÓRIO DE VALIDAÇÃO"
echo "----------------------------"

# Coletar algumas métricas para relatório
echo "📊 Coletando métricas atuais..."

calls_total=$(curl -s "http://localhost:9091/api/v1/query?query=sum(calls_total)" | jq -r '.data.result[0].value[1] // "0"')
duration_avg=$(curl -s "http://localhost:9091/api/v1/query?query=rate(duration_sum[5m])/rate(duration_count[5m])" | jq -r '.data.result[0].value[1] // "0"')

echo ""
echo -e "${GREEN}✅ RELATÓRIO SPM${NC}"
echo "=================="
echo "📞 Total de Calls: $calls_total"
echo "⏱️  Latência Média: ${duration_avg}s"
echo "🕐 Timestamp: $(date)"

echo ""
echo "🔗 LINKS ÚTEIS:"
echo "---------------"
echo "🎯 Jaeger UI: http://localhost:16687"
echo "📊 Prometheus: http://localhost:9091"
echo "🎨 Grafana: http://localhost:3001"
echo "📈 OTel Metrics: http://localhost:8888/metrics"

echo ""
echo "📚 COMANDOS DE TROUBLESHOOTING:"
echo "------------------------------"
echo "# Ver logs do OTel Collector:"
echo "docker logs fintelli_otel_collector"
echo ""
echo "# Ver métricas SPM direto do collector:"
echo "curl http://localhost:8890/metrics | grep -E 'calls_total|duration_'"
echo ""
echo "# Query Prometheus para debugging:"
echo "curl 'http://localhost:9091/api/v1/query?query=calls_total'"
echo ""
echo "# Restart dos serviços se necessário:"
echo "docker-compose restart otel-collector jaeger prometheus"

echo ""
echo -e "${GREEN}🎉 VALIDAÇÃO DO SPM CONCLUÍDA!${NC}"
