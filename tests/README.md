# 🧪 Guia Completo de Testes - Fintelli

Este documento fornece instruções detalhadas para executar todos os tipos de testes disponíveis no projeto Fintelli.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Testes de Frontend](#testes-de-frontend)
- [Testes de Backend](#testes-de-backend)
- [Testes de Integração](#testes-de-integração)
- [Validações de Componentes](#validações-de-componentes)
- [Scripts Automatizados](#scripts-automatizados)
- [Troubleshooting](#troubleshooting)

## 🔍 Visão Geral

O Fintelli possui uma suíte completa de testes que cobre:

- ✅ **Frontend**: Jest, React Testing Library, Cypress
- ✅ **Backend**: Pytest, FastAPI TestClient
- ✅ **APIs**: Testes de endpoint, validação de dados
- ✅ **Banco de Dados**: PostgreSQL, integridade de dados
- ✅ **Cache**: Redis, performance e persistência
- ✅ **Observabilidade**: Prometheus, Jaeger, OpenTelemetry
- ✅ **Docker**: Containers, networking, volumes
- ✅ **Integração**: Testes end-to-end
- ✅ **JavaScript**: Utilitários, validações, performance

## 🛠️ Pré-requisitos

### Software Necessário

```bash
# Node.js e npm (para testes frontend)
node --version   # >= 16.0.0
npm --version    # >= 8.0.0

# Python e pip (para testes backend)
python --version # >= 3.9
pip --version    # >= 21.0

# Docker e Docker Compose
docker --version          # >= 20.0.0
docker-compose --version  # >= 1.29.0

# Ferramentas adicionais
curl --version   # Para testes de API
jq --version     # Para parsing JSON
```

### Ambiente de Desenvolvimento

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/fintelli.git
cd fintelli

# 2. Configure o ambiente
cp .env_sample .env
# Edite .env com suas configurações

# 3. Suba a aplicação
docker-compose up -d

# 4. Aguarde todos os serviços ficarem prontos (2-3 minutos)
docker-compose ps
```

## 🎨 Testes de Frontend

### Configuração

```bash
cd tests/frontend
npm install
```

### Executando Testes

```bash
# Todos os testes
npm test

# Testes em modo watch (desenvolvimento)
npm run test:watch

# Relatório de cobertura
npm run test:coverage

# Testes unitários apenas
npm run test:unit

# Testes de integração apenas
npm run test:integration

# Testes E2E com Cypress
npm run test:e2e:open  # Interface gráfica
npm run test:e2e       # Headless
```

### Estrutura dos Testes Frontend

```
tests/frontend/
├── src/
│   ├── components/           # Testes de componentes React
│   │   ├── TransactionForm.test.tsx
│   │   ├── TransactionList.test.tsx
│   │   └── SummaryCard.test.tsx
│   ├── utils/               # Testes de utilitários JS
│   │   └── javascript.test.ts
│   └── setupTests.ts        # Configuração global
├── integration/             # Testes de integração
│   └── api.test.ts         # Testes de API
├── cypress/                # Testes E2E (se configurado)
│   ├── fixtures/
│   ├── integration/
│   └── support/
├── package.json
└── jest.config.js
```

### Comandos Úteis

```bash
# Executar teste específico
npm test TransactionForm.test.tsx

# Debug de testes
npm test -- --verbose

# Atualizar snapshots
npm test -- --updateSnapshot

# Executar com coverage específico
npm test -- --collectCoverageFrom="src/components/**/*.{ts,tsx}"
```

## ⚙️ Testes de Backend

### Configuração

```bash
cd tests/backend
pip install -r requirements.txt
```

### Executando Testes

```bash
# Todos os testes
pytest

# Teste específico
pytest test_api.py

# Com cobertura
pytest --cov=app --cov-report=html

# Paralelo (mais rápido)
pytest -n auto

# Verboso
pytest -v

# Parar no primeiro erro
pytest -x

# Testes por categoria
pytest -m "unit"        # Testes unitários
pytest -m "integration" # Testes de integração
```

### Estrutura dos Testes Backend

```
tests/backend/
├── test_api.py           # Testes de endpoints FastAPI
├── test_database.py      # Testes PostgreSQL
├── test_redis.py         # Testes Redis
├── test_prometheus.py    # Testes de métricas
├── test_jaeger.py        # Testes de traces
├── test_opentelemetry.py # Testes de telemetria
├── test_docker.py        # Testes de containerização
├── conftest.py          # Fixtures compartilhadas
└── requirements.txt     # Dependências de teste
```

### Executando Testes Específicos

```bash
# Testes de API
pytest test_api.py::TestTransactionsAPI::test_create_transaction

# Testes de banco
pytest test_database.py -v

# Testes de cache
pytest test_redis.py::TestRedisValidation

# Testes de observabilidade
pytest test_prometheus.py test_jaeger.py
```

## 🔗 Testes de Integração

### Script Principal

O script `tests/integration/run_tests.sh` executa uma validação completa de toda a stack:

```bash
# Executar todos os testes de integração
./tests/integration/run_tests.sh

# Executar com logs detalhados
./tests/integration/run_tests.sh --verbose

# Executar testes específicos
./tests/integration/run_tests.sh --only="frontend,backend,database"
```

### O que o Script Testa

1. **Containers Docker**
   - Status de todos os containers
   - Health checks
   - Conectividade entre serviços

2. **APIs e Endpoints**
   - Health checks de APIs
   - Validação de dados retornados
   - Performance básica

3. **Banco de Dados**
   - Conectividade PostgreSQL
   - Integridade de tabelas
   - Operações CRUD

4. **Cache Redis**
   - Conectividade
   - Operações básicas
   - Performance

5. **Observabilidade**
   - OpenTelemetry Collector
   - Prometheus métricas
   - Jaeger traces

6. **Frontend**
   - Carregamento da página
   - Assets JavaScript
   - Integração com backend

### Exemplo de Saída

```
🚀 Iniciando Testes de Integração do Fintelli
==============================================

[INFO] Verificando containers Docker...
[SUCCESS] Container fintelli_frontend está rodando
[SUCCESS] Container fintelli_backend está rodando
[SUCCESS] Container fintelli_db está rodando
[SUCCESS] Container fintelli_cache está rodando

[INFO] Testando Frontend em http://localhost:8080
[SUCCESS] Frontend está funcionando

[INFO] Testando endpoints da API...
[SUCCESS] Endpoint /api/summary retornou dados válidos
[SUCCESS] Endpoint /api/transactions retornou dados válidos

==============================================
[SUCCESS] Todos os testes de integração passaram! 🎉
==============================================
```

## 🔍 Validações de Componentes

### PostgreSQL

```bash
# Conectar ao banco
docker exec -it fintelli_db psql -U finance_user -d finance_db

# Verificar dados
SELECT COUNT(*) FROM transactions;
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5;

# Verificar performance
EXPLAIN ANALYZE SELECT * FROM transactions WHERE date >= '2024-01-01';
```

### Redis

```bash
# Conectar ao Redis
docker exec -it fintelli_cache redis-cli

# Verificar chaves
KEYS fintelli:*

# Verificar cache de summary
GET fintelli:summary

# Verificar estatísticas
INFO stats
```

### Prometheus

```bash
# Acessar métricas via API
curl http://localhost:9091/api/v1/query?query=up

# Verificar targets
curl http://localhost:9091/api/v1/targets

# Métricas customizadas
curl http://localhost:9091/api/v1/query?query=transactions_created_total
```

### Jaeger

```bash
# Listar serviços
curl http://localhost:16687/api/services

# Buscar traces
curl "http://localhost:16687/api/traces?service=fintelli-backend&limit=10"
```

### APIs

```bash
# Health check
curl http://localhost:8001/health

# Resumo financeiro
curl http://localhost:8001/api/summary

# Criar transação
curl -X POST http://localhost:8001/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"income","description":"Teste","amount":100,"date":"2024-01-15"}'
```

## 🤖 Scripts Automatizados

### Script Master de Testes

Criamos um script que executa TODOS os testes:

```bash
#!/bin/bash
# run_all_tests.sh

echo "🧪 Executando TODOS os testes do Fintelli"
echo "========================================="

# 1. Testes de Backend
echo "⚙️ Executando testes de backend..."
cd tests/backend
pytest -v --cov=app
cd ../..

# 2. Testes de Frontend
echo "🎨 Executando testes de frontend..."
cd tests/frontend
npm test -- --coverage --watchAll=false
cd ../..

# 3. Testes de Integração
echo "🔗 Executando testes de integração..."
./tests/integration/run_tests.sh

echo "✅ Todos os testes concluídos!"
```

### Scripts de Validação Específicos

```bash
# Validação rápida (apenas health checks)
./scripts/quick_health_check.sh

# Validação de performance
./scripts/performance_test.sh

# Validação de segurança
./scripts/security_scan.sh

# Validação de compliance
./scripts/compliance_check.sh
```

## 🎯 Comandos de Teste por Categoria

### Testes Unitários

```bash
# Frontend
npm test -- --testNamePattern="unit"

# Backend
pytest -m unit
```

### Testes de Integração

```bash
# Frontend + Backend
npm run test:integration

# Docker + Services
./tests/integration/run_tests.sh
```

### Testes E2E

```bash
# Cypress (se configurado)
npm run test:e2e

# Manual via curl
./scripts/e2e_manual_test.sh
```

### Testes de Performance

```bash
# Backend
pytest test_performance.py

# Redis
redis-benchmark -h localhost -p 6379

# Database
pgbench -h localhost -p 5432 -U finance_user finance_db
```

## 📊 Relatórios de Teste

### Coverage Reports

```bash
# Frontend Coverage
cd tests/frontend
npm run test:coverage
open coverage/lcov-report/index.html

# Backend Coverage
cd tests/backend
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Reports

```bash
# JUnit XML (CI/CD)
pytest --junitxml=test-results.xml

# JSON Report
pytest --json-report --json-report-file=test-report.json
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Testes de Frontend Falham

```bash
# Limpar cache do Jest
npm test -- --clearCache

# Reinstalar dependências
rm -rf node_modules package-lock.json
npm install

# Verificar versões
node --version
npm --version
```

#### 2. Testes de Backend Falham

```bash
# Verificar dependências Python
pip install -r requirements.txt --upgrade

# Verificar variáveis de ambiente
echo $DATABASE_URL
echo $REDIS_URL

# Verificar conexão com serviços
curl http://localhost:8001/health
```

#### 3. Serviços Não Respondem

```bash
# Verificar containers
docker-compose ps

# Restart dos serviços
docker-compose restart

# Logs detalhados
docker-compose logs -f
```

#### 4. Problemas de Performance

```bash
# Verificar recursos
docker stats

# Verificar disk space
df -h

# Verificar memory
free -h
```

### Logs de Debug

```bash
# Backend detalhado
docker-compose logs backend | grep ERROR

# Frontend detalhado
docker-compose logs frontend | grep nginx

# Database detalhado
docker-compose logs db | tail -50
```

## 📝 Boas Práticas

### 1. **Sempre Execute Testes Antes de Commit**

```bash
# Git hook recomendado (pre-commit)
#!/bin/bash
npm test --watchAll=false
pytest
./tests/integration/run_tests.sh --quick
```

### 2. **Mantenha Dados de Teste Limpos**

```bash
# Limpar dados entre testes
docker-compose down -v
docker-compose up -d
```

### 3. **Use Mocks Apropriados**

```javascript
// Frontend
jest.mock('../services/api');

// Backend
@pytest.fixture
def mock_database():
    return MagicMock()
```

### 4. **Monitore Coverage**

```bash
# Manter coverage > 80%
pytest --cov=app --cov-fail-under=80
```

### 5. **Automatize no CI/CD**

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Integration Tests
        run: ./tests/integration/run_tests.sh
```

## 🚀 Próximos Passos

### Expansão dos Testes

1. **Testes de Carga**: k6, Artillery
2. **Testes de Segurança**: OWASP ZAP, Bandit
3. **Testes de Acessibilidade**: axe-core
4. **Testes Visuais**: Percy, Chromatic

### Automação

1. **CI/CD Pipeline**: GitHub Actions, GitLab CI
2. **Quality Gates**: SonarQube
3. **Deployment Testing**: Smoke tests
4. **Monitoring**: Alertas baseados em métricas

---

## 📚 Recursos Adicionais

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Docker Testing Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

*Este guia está em constante evolução. Contribuições são bem-vindas!* 🤝
