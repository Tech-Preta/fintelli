# 🎯 Service Performance Monitoring (SPM) - Guia do Usuário

## Visão Geral

O Service Performance Monitoring (SPM) é uma funcionalidade avançada do Jaeger que deriva automaticamente **métricas de performance dos traces distribuídos**. No Fintelli, o SPM fornece insights instantâneos sobre a performance dos serviços sem necessidade de instrumentação manual adicional.

## 🚀 Como Funciona

### Arquitetura SPM no Fintelli

```
📱 Frontend (React) 
    ↓ (traces via OTLP)
🔄 OTel Collector
    ↓ (spanmetrics processor)
📊 Métricas SPM → Prometheus
    ↓
🎨 Grafana Dashboards
    ↓
🚨 Alertas Automáticos
```

### Pipeline de Dados

1. **Coleta**: Aplicações enviam traces para OTel Collector
2. **Processamento**: SpanMetrics processor analisa spans e gera métricas
3. **Armazenamento**: Métricas são enviadas para Prometheus
4. **Visualização**: Grafana cria dashboards automáticos
5. **Alertas**: Thresholds de performance acionam notificações

## 📊 Métricas Disponíveis

### Métricas RED (Rate, Errors, Duration)

#### 1. **Rate (Taxa de Requisições)**
```promql
# Requisições por segundo do backend
rate(calls_total{service_name="fintelli-backend"}[5m])

# Requisições por endpoint específico
rate(calls_total{operation="/api/transactions"}[5m])

# Por método HTTP
rate(calls_total{http_method="POST"}[5m])
```

#### 2. **Errors (Taxa de Erros)**
```promql
# Taxa de erro geral
rate(calls_total{status_code=~"5.."}[5m]) / rate(calls_total[5m])

# Erros por endpoint
rate(calls_total{operation="/api/transactions",status_code=~"5.."}[5m])

# Disponibilidade do serviço (uptime)
(1 - rate(calls_total{status_code=~"5.."}[5m]) / rate(calls_total[5m])) * 100
```

#### 3. **Duration (Latência)**
```promql
# Latência P95 do serviço
histogram_quantile(0.95, rate(duration_bucket{service_name="fintelli-backend"}[5m]))

# Latência média por operação
rate(duration_sum{operation="/api/transactions"}[5m]) / rate(duration_count{operation="/api/transactions"}[5m])

# Distribuição de latência
histogram_quantile(0.50, rate(duration_bucket[5m])) # P50
histogram_quantile(0.90, rate(duration_bucket[5m])) # P90
histogram_quantile(0.99, rate(duration_bucket[5m])) # P99
```

## 🎨 Dashboards SPM

### Dashboard Principal: Fintelli SPM Overview

**Painéis Inclusos:**
- 📈 **Taxa de Transações (TPS)**: Throughput em tempo real
- ⏱️ **Latência P95**: Performance crítica do sistema
- ❌ **Taxa de Erro**: Percentual de falhas
- 🛡️ **Disponibilidade**: Uptime do serviço
- 📊 **Latência por Endpoint**: Breakdown detalhado
- 🔗 **Performance de Dependências**: PostgreSQL e Redis

### Acessando os Dashboards

1. **Grafana**: http://localhost:3000
2. **Login**: admin/admin
3. **Navegar**: Dashboards → Fintelli SPM

## 🚨 Alertas Configurados

### Alertas Críticos

#### 1. **Latência Alta**
```yaml
alert: HighTransactionLatency
condition: P95 > 500ms por 2 minutos
severity: warning
action: Investigar gargalos, otimizar queries
```

#### 2. **Taxa de Erro Elevada**
```yaml
alert: HighErrorRate
condition: Taxa de erro > 1% por 1 minuto
severity: critical
action: Rollback, investigação urgente
```

#### 3. **Disponibilidade Baixa**
```yaml
alert: LowServiceAvailability
condition: Uptime < 99.9% por 5 minutos
severity: critical
action: Escalação para on-call
```

#### 4. **Throughput Baixo**
```yaml
alert: LowThroughput
condition: TPS < 10 req/s por 5 minutos
severity: warning
action: Verificar capacidade, auto-scaling
```

## 🔧 Comandos Úteis

### Verificação Rápida

```bash
# Status dos serviços SPM
./scripts/validate_spm.sh

# Métricas direto do OTel Collector
curl http://localhost:8890/metrics | grep calls_total

# Query Prometheus
curl 'http://localhost:9091/api/v1/query?query=calls_total{service_name="fintelli-backend"}'
```

### Troubleshooting

```bash
# Logs do OTel Collector
docker logs fintelli_otel_collector

# Verificar configuração
docker exec fintelli_otel_collector cat /etc/otelcol-contrib/config.yaml

# Restart componentes SPM
docker-compose restart otel-collector jaeger prometheus
```

## 📈 Casos de Uso Específicos

### 1. **Monitoramento de SLA**

**Objetivo**: Garantir 99.9% de disponibilidade e latência P95 < 500ms

**Query Grafana**:
```promql
# SLA de Disponibilidade
(1 - rate(calls_total{service_name="fintelli-backend",status_code=~"5.."}[5m]) / rate(calls_total{service_name="fintelli-backend"}[5m])) * 100

# SLA de Latência
histogram_quantile(0.95, rate(duration_bucket{service_name="fintelli-backend"}[5m]))
```

### 2. **Análise de Performance por Feature**

**Objetivo**: Comparar performance entre diferentes funcionalidades

**Query Grafana**:
```promql
# Latência por endpoint
rate(duration_sum[5m]) by (operation) / rate(duration_count[5m]) by (operation)

# Throughput por feature
rate(calls_total[5m]) by (operation)
```

### 3. **Detecção de Degradação**

**Objetivo**: Identificar automaticamente quando performance degrada

**Alert Manager**:
```yaml
# Latência crescente
increase(histogram_quantile(0.95, rate(duration_bucket[5m]))[10m:1m]) > 0.1

# Throughput decrescente  
decrease(rate(calls_total[5m])[10m:1m]) > 10
```

### 4. **Correlação com Deploy**

**Objetivo**: Verificar impacto de deploys na performance

**Processo**:
1. Anotar timestamp do deploy no Grafana
2. Comparar métricas before/after
3. Rollback automático se degradação > threshold

## 🎯 Próximos Passos

### Otimizações Futuras

1. **Machine Learning**: Detecção de anomalias baseada em ML
2. **Distributed Tracing**: Correlação entre SPM e traces específicos
3. **Business Metrics**: KPIs de negócio derivados de SPM
4. **Auto-scaling**: Ações automáticas baseadas em métricas SPM

### Integrações Avançadas

1. **Slack/Teams**: Notificações de alertas
2. **PagerDuty**: Escalação automática
3. **Jira**: Criação automática de tickets
4. **CI/CD**: Gates de qualidade baseados em SPM

## 📚 Referências

- [OpenTelemetry SpanMetrics Processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/spanmetricsprocessor)
- [Jaeger SPM Documentation](https://www.jaegertracing.io/docs/1.35/spm/)
- [Prometheus Recording Rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)

---

**🚀 Com SPM habilitado, o Fintelli agora possui observabilidade de classe enterprise, permitindo detectar e resolver problemas de performance antes que impactem os usuários!**
