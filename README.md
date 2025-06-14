# 🧠 Fintelli - Finanças Inteligentes com IA

Esta é uma aplicação full-stack para gerenciamento de finanças pessoais com inteligência artificial, totalmente containerizada com Docker e instrumentada com **OpenTelemetry** para observabilidade completa.

## 🏗️ Diagrama de Arquitetura

```mermaid
graph TD
    subgraph "Ambiente Externo"
        User[<i class="fa fa-user"></i> Utilizador via Browser]
    end

    subgraph "Cluster Kubernetes"
        Ingress[<i class="fa fa-route"></i> Ingress Controller]

        subgraph "Aplicações Principais"
            direction LR
            Frontend[<i class="fa fa-window-maximize"></i> Frontend<br>(Nginx Pods)]
            Backend[<i class="fa fa-server"></i> Backend<br>(FastAPI Pods)]
        end

        subgraph "Camada de Dados"
            direction LR
            Postgres[<i class="fa fa-database"></i> PostgreSQL<br>(StatefulSet)]
            Redis[<i class="fa fa-memory"></i> Redis<br>(StatefulSet)]
        end

        subgraph "Pilha de Observabilidade"
            direction TB
            OTel[<i class="fa fa-satellite-dish"></i> OTel Collector<br>(Deployment)]
            
            subgraph "Visualização"
                direction LR
                Jaeger[<i class="fa fa-search-plus"></i> Jaeger<br>(Traces)]
                Grafana[<i class="fa fa-chart-bar"></i> Grafana<br>(Dashboards)]
            end
            
            Prometheus[<i class="fa fa-tachometer-alt"></i> Prometheus<br>(Métricas)]
        end

        Secrets[<i class="fa fa-key"></i> Kubernetes Secrets<br>(Postgres & Gemini API Key)]
    end

    %% Ligações de Tráfego Principal
    User -- HTTPS Request --> Ingress
    Ingress -- Encaminhamento de Tráfego<br>finance.local --> Frontend
    Ingress -- /api/* --> Backend

    %% Interações Internas da Aplicação
    Frontend -- "API Calls<br>(/api)" --> Backend
    Backend -- "Leitura/Escrita" --> Postgres
    Backend -- "Cache" --> Redis
    Secrets -- "Injeta Senhas e Chaves" --> Backend
    Secrets -- "Injeta Senha" --> Postgres

    %% Fluxo de Telemetria (OpenTelemetry)
    Frontend -.-> |"OTel Traces (HTTP)"| Ingress
    Ingress -.-> |"/v1/traces"| OTel
    Backend  -.-> |"OTel Traces & Métricas (gRPC)"| OTel
    
    OTel -- "Exporta Traces" --> Jaeger
    Prometheus -- "Recolhe Métricas" --> OTel
    Grafana -- "Consulta Métricas" --> Prometheus

    %% Estilos
    style User fill:#cde4ff,stroke:#66aaff,stroke-width:2px
    style Ingress fill:#fff2cc,stroke:#ffd966,stroke-width:2px
    style Frontend fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style Backend fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style Postgres fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
    style Redis fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
    style Secrets fill:#f8cecc,stroke:#b85450,stroke-width:2px
    style OTel fill:#e1d5e7,stroke:#9673a6,stroke-width:2px
    style Jaeger fill:#f5f5f5,stroke:#666,stroke-width:1px
    style Prometheus fill:#f5f5f5,stroke:#666,stroke-width:1px
    style Grafana fill:#f5f5f5,stroke:#666,stroke-width:1px
```

## 📋 Arquitetura

- **Frontend**: Nginx servindo um site estático (HTML, CSS, JS) instrumentado com OTel JS SDK
- **Backend**: API RESTful com FastAPI (Python), instrumentada com OTel Python SDK
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **Orquestração**: Docker Compose

### 🔍 Pilha de Observabilidade

- **OTel Collector**: Recebe telemetria do frontend e backend
- **Jaeger**: Armazena e visualiza traces distribuídos
- **Prometheus**: Coleta e armazena métricas
- **Grafana**: Cria dashboards para visualizar as métricas

## 📁 Estrutura de Diretórios

```
fintelli/
├── backend/
│   ├── app/
│   │   ├── instrumentation.py  # Configuração do OpenTelemetry
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── telemetry.js            # Instrumentação OTel do Frontend
│   ├── Dockerfile
│   └── nginx.conf
├── charts/
│   └── fintelli/               # Helm Chart para Kubernetes
├── config/
│   ├── otel-collector-config.yml  # Configuração do Collector
│   └── prometheus.yml             # Configuração do Prometheus
├── .env
└── docker-compose.yml
```

## 🛠️ Pré-requisitos

- **Docker**
- **Docker Compose**

## 🚀 Como Configurar e Executar

### 1. Crie os arquivos e diretórios
Garanta que a estrutura de diretórios e todos os arquivos abaixo estejam criados.

### 2. Crie e configure o arquivo `.env`
Na raiz do projeto, crie o arquivo `.env` com suas credenciais e adicione a chave da API do Gemini:

```bash
# Credenciais do Banco de Dados Postgres
POSTGRES_DB=finance_db
POSTGRES_USER=finance_user
POSTGRES_PASSWORD=your_strong_password

# Chave da API do Gemini (Google AI) - OBRIGATÓRIO
GEMINI_API_KEY="SUA_CHAVE_API_AQUI"
```

### 3. Construa e inicie os contêineres
No terminal, na raiz do projeto, execute:

```bash
docker-compose up --build
```

### 4. Acesse os Serviços

| Serviço                   | URL                    | Descrição                       |
| ------------------------- | ---------------------- | ------------------------------- |
| **Aplicação de Finanças** | http://localhost:8080  | Interface principal             |
| **Backend API**           | http://localhost:8001  | API FastAPI                     |
| **Jaeger (Traces)**       | http://localhost:16687 | Visualização de traces          |
| **Prometheus (Métricas)** | http://localhost:9091  | Coleta de métricas              |
| **Grafana (Dashboards)**  | http://localhost:3000  | Dashboards (login: admin/admin) |

## 📊 Como Usar a Observabilidade

### 1. Use a aplicação
Adicione e remova algumas transações para gerar dados.

### 2. Visualize Traces no Jaeger

1. Abra o **Jaeger**
2. No menu "Service", selecione `finance-backend` ou `finance-frontend`
3. Clique em "Find Traces"
4. Você verá as requisições, desde o clique no navegador até a consulta no banco de dados

### 3. Explore Métricas no Grafana

1. Abra o **Grafana** e faça login
2. Vá em "Connections" > "Data sources" e adicione o Prometheus (URL: `http://prometheus:9090`)
3. Vá em "Dashboards" > "New dashboard" para criar painéis com as métricas disponíveis
   - Exemplos: `http_server_duration_seconds`, `transactions_created_total`

