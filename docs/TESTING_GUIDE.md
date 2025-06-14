# 📚 Guia Completo de Testes e Validações - Fintelli

Este documento fornece um guia abrangente para testar e validar todos os componentes da aplicação Fintelli.

## 📋 Índice

1. [Testes de Frontend](#frontend)
2. [Testes de Backend](#backend)
3. [Validações PostgreSQL](#postgresql)
4. [Validações Redis](#redis)
5. [Validações Prometheus](#prometheus)
6. [Validações Jaeger](#jaeger)
7. [Validações OpenTelemetry](#opentelemetry)
8. [Build com Docker Compose](#docker)
9. [Consulta de Logs](#logs)
10. [Testes JavaScript](#javascript)

---

## 🎨 Frontend {#frontend}

### Configuração dos Testes

```bash
cd tests/frontend
npm install
```

### Executando Testes Unitários

```bash
# Executar todos os testes
npm test

# Executar com watch mode
npm run test:watch

# Gerar relatório de cobertura
npm run test:coverage
```

### Testes E2E com Cypress

```bash
# Abrir interface do Cypress
npm run test:e2e:open

# Executar testes headless
npm run test:e2e
```

### Exemplo de Teste Manual do Frontend

```bash
# 1. Acessar a aplicação
curl -I http://localhost:8080

# 2. Verificar se assets estão carregando
curl -I http://localhost:8080/assets/index-*.js

# 3. Testar proxy da API
curl http://localhost:8080/api/summary

# 4. Testar formulário via browser
# - Abra http://localhost:8080
# - Preencha o formulário "Adicionar Lançamento"
# - Verifique se a transação aparece na lista
```

---

## ⚙️ Backend {#backend}

### Configuração dos Testes

```bash
cd tests/backend
pip install -r requirements.txt
```

### Executando Testes

```bash
# Executar todos os testes
pytest test_api.py -v

# Executar com cobertura
pytest test_api.py --cov=main --cov-report=html

# Executar testes específicos
pytest test_api.py::TestTransactionsAPI::test_add_transaction_success -v
```

### Testes Manuais da API

```bash
# 1. Verificar documentação
curl http://localhost:8001/docs

# 2. Testar endpoint de resumo
curl http://localhost:8001/api/summary

# 3. Listar transações
curl http://localhost:8001/api/transactions

# 4. Criar nova transação
curl -X POST http://localhost:8001/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Teste API",
    "amount": 100.00,
    "transaction_date": "2024-06-14"
  }'

# 5. Criar gasto fixo
curl -X POST http://localhost:8001/api/fixed-expenses \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Internet",
    "amount": 100.00
  }'

# 6. Deletar transação (substitua 1 pelo ID real)
curl -X DELETE http://localhost:8001/api/transactions/1
```

---

## 🗄️ PostgreSQL {#postgresql}

### Conectar ao Banco

```bash
# Via Docker
docker exec -it fintelli_db psql -U finance_user -d finance_db

# Via cliente local (se instalado)
psql -h localhost -p 5433 -U finance_user -d finance_db
```

### Validações no PostgreSQL

```sql
-- 1. Verificar estrutura das tabelas
\dt

-- 2. Verificar estrutura da tabela transactions
\d transactions

-- 3. Verificar estrutura da tabela fixed_expenses
\d fixed_expenses

-- 4. Contar registros
SELECT COUNT(*) FROM transactions;
SELECT COUNT(*) FROM fixed_expenses;

-- 5. Verificar últimas transações
SELECT id, description, amount, transaction_date 
FROM transactions 
ORDER BY id DESC 
LIMIT 5;

-- 6. Calcular resumo manualmente
SELECT 
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
    SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as expense,
    SUM(amount) as balance
FROM transactions;

-- 7. Verificar integridade dos dados
SELECT * FROM transactions WHERE amount IS NULL OR description IS NULL;

-- 8. Performance - verificar índices
\d+ transactions

-- 9. Verificar conexões ativas
SELECT application_name, state, query_start 
FROM pg_stat_activity 
WHERE datname = 'finance_db';

-- 10. Backup de teste
pg_dump -h localhost -p 5433 -U finance_user finance_db > backup_test.sql
```

### Scripts de Validação

```bash
# Script para validar dados
docker exec fintelli_db psql -U finance_user -d finance_db -c "
SELECT 
    'Transações: ' || COUNT(*) as transactions_count
FROM transactions
UNION ALL
SELECT 
    'Gastos Fixos: ' || COUNT(*) as fixed_expenses_count  
FROM fixed_expenses;
"
```

---

## ⚡ Redis {#redis}

### Conectar ao Redis

```bash
# Via Docker
docker exec -it fintelli_cache redis-cli

# Via cliente local
redis-cli -h localhost -p 6380
```

### Validações no Redis

```bash
# 1. Testar conectividade
docker exec fintelli_cache redis-cli ping

# 2. Ver informações do servidor
docker exec fintelli_cache redis-cli info server

# 3. Verificar memória utilizada
docker exec fintelli_cache redis-cli info memory

# 4. Listar todas as chaves
docker exec fintelli_cache redis-cli keys "*"

# 5. Verificar cache do resumo financeiro
docker exec fintelli_cache redis-cli get "financial_summary"

# 6. Verificar TTL do cache
docker exec fintelli_cache redis-cli ttl "financial_summary"

# 7. Estatísticas de comandos
docker exec fintelli_cache redis-cli info commandstats

# 8. Monitorar comandos em tempo real
docker exec fintelli_cache redis-cli monitor

# 9. Testar operações básicas
docker exec fintelli_cache redis-cli set "test_key" "test_value"
docker exec fintelli_cache redis-cli get "test_key"
docker exec fintelli_cache redis-cli del "test_key"

# 10. Verificar configuração
docker exec fintelli_cache redis-cli config get "*"
```

### Script de Teste de Cache

```bash
#!/bin/bash
echo "Testando invalidação de cache..."

# 1. Fazer requisição para popular cache
echo "Populando cache..."
curl -s http://localhost:8001/api/summary > /dev/null

# 2. Verificar se cache foi criado
echo "Cache criado:"
docker exec fintelli_cache redis-cli get "financial_summary"

# 3. Criar nova transação (deve invalidar cache)
echo "Criando transação..."
curl -s -X POST http://localhost:8001/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"description": "Teste Cache", "amount": 50, "transaction_date": "2024-06-14"}' > /dev/null

# 4. Verificar se cache foi invalidado
echo "Cache após invalidação:"
docker exec fintelli_cache redis-cli get "financial_summary"
```

---

## 📈 Prometheus {#prometheus}

### Acessar Prometheus

- **Web UI**: http://localhost:9091
- **API**: http://localhost:9091/api/v1/

### Validações no Prometheus

```bash
# 1. Verificar status dos targets
curl http://localhost:9091/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# 2. Listar todas as métricas disponíveis
curl http://localhost:9091/api/v1/label/__name__/values | jq '.data[]' | head -20

# 3. Consultar métrica específica
curl "http://localhost:9091/api/v1/query?query=transactions_created_total" | jq '.data.result'

# 4. Consultar métricas HTTP
curl "http://localhost:9091/api/v1/query?query=http_server_duration_milliseconds_count" | jq '.data.result'

# 5. Ver últimos valores de uma métrica
curl "http://localhost:9091/api/v1/query?query=up" | jq '.data.result'

# 6. Consultar range de tempo
curl "http://localhost:9091/api/v1/query_range?query=transactions_created_total&start=$(date -d '1 hour ago' +%s)&end=$(date +%s)&step=60" | jq '.data.result'
```

### Queries Úteis no Prometheus

```promql
# 1. Verificar se o backend está up
up{job="fintelli-backend"}

# 2. Taxa de requisições por segundo
rate(http_server_duration_milliseconds_count[5m])

# 3. Latência média das requisições
rate(http_server_duration_milliseconds_sum[5m]) / rate(http_server_duration_milliseconds_count[5m])

# 4. Número total de transações criadas
transactions_created_total

# 5. Requisições por status code
sum by (http_status_code) (http_server_duration_milliseconds_count)

# 6. Top 5 endpoints mais chamados
topk(5, sum by (http_target) (rate(http_server_duration_milliseconds_count[5m])))
```

### Script de Validação do Prometheus

```bash
#!/bin/bash
echo "Validando Prometheus..."

# Verificar se está coletando métricas
METRICS_COUNT=$(curl -s "http://localhost:9091/api/v1/query?query=up" | jq '.data.result | length')
echo "Número de targets monitorados: $METRICS_COUNT"

# Verificar métrica customizada
CUSTOM_METRIC=$(curl -s "http://localhost:9091/api/v1/query?query=transactions_created_total" | jq '.data.result[0].value[1]' 2>/dev/null)
if [ "$CUSTOM_METRIC" != "null" ] && [ "$CUSTOM_METRIC" != "" ]; then
    echo "Métrica customizada funcionando: $CUSTOM_METRIC transações criadas"
else
    echo "Métrica customizada não encontrada"
fi
```

---

## 🔍 Jaeger {#jaeger}

### Acessar Jaeger

- **Web UI**: http://localhost:16687
- **API**: http://localhost:16687/api/

### Validações no Jaeger

```bash
# 1. Listar serviços rastreados
curl http://localhost:16687/api/services | jq '.'

# 2. Buscar traces do backend
curl "http://localhost:16687/api/traces?service=fintelli-backend&limit=10" | jq '.data[] | {traceID: .traceID, spans: (.spans | length)}'

# 3. Verificar operações disponíveis
curl "http://localhost:16687/api/operations?service=fintelli-backend" | jq '.data[]'

# 4. Buscar traces por tag
curl "http://localhost:16687/api/traces?service=fintelli-backend&tag=http.method:POST" | jq '.data | length'

# 5. Estatísticas de dependências
curl "http://localhost:16687/api/dependencies?endTs=$(date +%s)000&lookback=3600000" | jq '.'
```

### Script de Teste de Traces

```bash
#!/bin/bash
echo "Gerando traces para teste..."

# Fazer várias requisições para gerar traces
for i in {1..5}; do
    echo "Requisição $i"
    curl -s http://localhost:8001/api/summary > /dev/null
    curl -s http://localhost:8001/api/transactions > /dev/null
    sleep 1
done

# Aguardar processamento
sleep 5

# Verificar se traces foram gerados
TRACES_COUNT=$(curl -s "http://localhost:16687/api/traces?service=fintelli-backend&limit=100" | jq '.data | length')
echo "Traces encontrados: $TRACES_COUNT"

if [ "$TRACES_COUNT" -gt 0 ]; then
    echo "✅ Jaeger está coletando traces corretamente"
else
    echo "❌ Nenhum trace encontrado"
fi
```

---

## 📡 OpenTelemetry {#opentelemetry}

### Validações do OTel Collector

```bash
# 1. Verificar métricas do collector
curl http://localhost:8888/metrics | grep otelcol

# 2. Ver estatísticas de spans recebidos
curl http://localhost:8888/metrics | grep otelcol_receiver_accepted_spans_total

# 3. Ver estatísticas de métricas recebidas
curl http://localhost:8888/metrics | grep otelcol_receiver_accepted_metric_points_total

# 4. Verificar exporters
curl http://localhost:8888/metrics | grep otelcol_exporter

# 5. Ver logs do collector
docker logs fintelli_otel_collector --tail 20
```

### Validar Instrumentação

```bash
# 1. Verificar se o backend está enviando telemetria
echo "Fazendo requisições para gerar telemetria..."
for i in {1..3}; do
    curl -s -X POST http://localhost:8001/api/transactions \
      -H "Content-Type: application/json" \
      -d "{\"description\": \"Test $i\", \"amount\": $((i * 100)), \"transaction_date\": \"$(date +%Y-%m-%d)\"}" > /dev/null
done

# 2. Verificar métricas customizadas
sleep 5
CUSTOM_METRIC_VALUE=$(curl -s "http://localhost:9091/api/v1/query?query=transactions_created_total" | jq '.data.result[0].value[1]' 2>/dev/null)
echo "Métrica customizada: $CUSTOM_METRIC_VALUE"

# 3. Verificar traces
RECENT_TRACES=$(curl -s "http://localhost:16687/api/traces?service=fintelli-backend&limit=5" | jq '.data | length')
echo "Traces recentes: $RECENT_TRACES"
```

---

## 🐳 Build com Docker Compose {#docker}

### Comandos Básicos

```bash
# 1. Build completo
docker compose build

# 2. Build sem cache
docker compose build --no-cache

# 3. Build serviço específico
docker compose build backend

# 4. Subir todos os serviços
docker compose up -d

# 5. Subir com rebuild
docker compose up --build -d

# 6. Ver logs de build
docker compose build --progress=plain

# 7. Verificar status
docker compose ps

# 8. Parar todos os serviços
docker compose down

# 9. Parar e remover volumes
docker compose down -v

# 10. Restart serviço específico
docker compose restart backend
```

### Script de Deploy Completo

```bash
#!/bin/bash
echo "🚀 Deploy completo do Fintelli..."

# 1. Parar serviços existentes
echo "Parando serviços..."
docker compose down

# 2. Remover imagens antigas
echo "Limpando imagens antigas..."
docker compose build --no-cache

# 3. Subir novamente
echo "Subindo serviços..."
docker compose up -d

# 4. Aguardar serviços ficarem prontos
echo "Aguardando serviços..."
sleep 30

# 5. Executar testes
echo "Executando testes de integração..."
./tests/integration/run_tests.sh

echo "✅ Deploy concluído!"
```

### Validações de Containers

```bash
# 1. Verificar se todos estão rodando
docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"

# 2. Verificar uso de recursos
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 3. Verificar redes
docker network ls | grep fintelli

# 4. Verificar volumes
docker volume ls | grep fintelli

# 5. Verificar health checks
docker inspect fintelli_backend | jq '.[].State.Health'
```

---

## 📊 Consulta de Logs {#logs}

### Logs do Frontend

```bash
# Ver logs em tempo real
docker logs -f fintelli_frontend

# Últimas 50 linhas
docker logs --tail 50 fintelli_frontend

# Logs com timestamp
docker logs -t fintelli_frontend

# Logs de um período específico
docker logs --since="2024-06-14T10:00:00" fintelli_frontend
```

### Logs do Backend

```bash
# Logs do backend
docker logs -f fintelli_backend

# Filtrar por nível de log
docker logs fintelli_backend 2>&1 | grep ERROR

# Logs de acesso HTTP
docker logs fintelli_backend 2>&1 | grep "POST\|GET\|DELETE"
```

### Logs Agregados

```bash
# Ver logs de todos os serviços
docker compose logs -f

# Logs específicos
docker compose logs -f backend frontend

# Logs com timestamp
docker compose logs -t --tail 100
```

### Script de Monitoramento de Logs

```bash
#!/bin/bash
echo "🔍 Monitoramento de Logs Fintelli"

# Função para colorir logs
color_logs() {
    sed 's/ERROR/\x1b[31mERROR\x1b[0m/g; s/INFO/\x1b[32mINFO\x1b[0m/g; s/WARNING/\x1b[33mWARNING\x1b[0m/g'
}

# Mostrar logs dos últimos 5 minutos
echo "📱 Frontend (últimos 5 min):"
docker logs --since="5m" fintelli_frontend 2>&1 | tail -10 | color_logs

echo -e "\n⚙️  Backend (últimos 5 min):"
docker logs --since="5m" fintelli_backend 2>&1 | tail -10 | color_logs

echo -e "\n📡 OTel Collector (últimos 5 min):"
docker logs --since="5m" fintelli_otel_collector 2>&1 | tail -10 | color_logs
```

---

## 🧪 Testes JavaScript {#javascript}

### Configuração do Ambiente de Testes

```bash
# Instalar dependências de teste no frontend
cd src/frontend
npm install --save-dev \
  @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event \
  jest \
  jest-environment-jsdom \
  @types/jest
```

### Configurar Jest

```json
// src/frontend/jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/main.tsx',
    '!src/vite-env.d.ts'
  ],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{ts,tsx}'
  ]
};
```

### Exemplos de Testes

```typescript
// Teste do serviço API
import { getSummary, addTransaction } from '../services/api';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Service', () => {
  test('getSummary retorna dados corretos', async () => {
    const mockData = { income: 1000, expense: -500, balance: 500 };
    mockedAxios.create.mockReturnValue({
      get: jest.fn().mockResolvedValue({ data: mockData })
    } as any);

    const result = await getSummary();
    expect(result).toEqual(mockData);
  });
});
```

### Executar Testes

```bash
# Executar todos os testes
npm test

# Com cobertura
npm test -- --coverage

# Watch mode
npm test -- --watch

# Testes específicos
npm test -- TransactionForm.test.tsx
```

---

## 🚀 Executando Testes Completos

### Script Principal de Testes

```bash
# Executar todos os testes de uma vez
./tests/integration/run_tests.sh
```

Este script executará automaticamente:
- ✅ Verificação de containers
- ✅ Testes de API
- ✅ Validações de banco de dados
- ✅ Verificações de cache
- ✅ Testes de observabilidade
- ✅ Teste end-to-end completo

### Relatório de Cobertura

```bash
# Gerar relatório completo
echo "Gerando relatório de cobertura..."

# Frontend
cd src/frontend && npm run test:coverage

# Backend
cd ../../tests/backend && pytest --cov=main --cov-report=html

echo "Relatórios gerados em:"
echo "- Frontend: src/frontend/coverage/"
echo "- Backend: tests/backend/htmlcov/"
```

---

## 📝 Checklist de Validação

### ✅ Pré-Deploy
- [ ] Todos os containers estão rodando
- [ ] Banco de dados está acessível
- [ ] Cache Redis está funcionando
- [ ] API responde corretamente
- [ ] Frontend carrega sem erros

### ✅ Pós-Deploy
- [ ] Testes de integração passam
- [ ] Métricas estão sendo coletadas
- [ ] Traces aparecem no Jaeger
- [ ] Dashboards do Grafana funcionam
- [ ] Logs não mostram erros críticos

### ✅ Performance
- [ ] Tempo de resposta da API < 500ms
- [ ] Frontend carrega < 3s
- [ ] Cache hit rate > 80%
- [ ] Uso de CPU < 70%
- [ ] Uso de memória < 80%

---

Este guia garante que todos os componentes do Fintelli estejam funcionando corretamente em produção! 🎯
