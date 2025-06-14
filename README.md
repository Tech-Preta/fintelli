# 🧠 Fintelli - Finanças Inteligentes com IA

Esta é uma aplicação full-stack para gerenciamento de finanças pessoais com inteligência artificial, totalmente containerizada com Docker e instrumentada com **OpenTelemetry** para observabilidade completa.

## 🏗️ Diagrama de Arquitetura

```mermaid
graph TD
    subgraph External["🌐 AMBIENTE EXTERNO"]
        User["👤 Usuário via Browser"]
    end

    subgraph Docker["🐳 DOCKER ENVIRONMENT"]
        subgraph FrontendLayer["📱 FRONTEND LAYER"]
            Frontend["🌐 Frontend<br/>(React + Nginx)"]
        end

        subgraph BackendLayer["⚙️ BACKEND LAYER"]
            Backend["🔧 Backend<br/>(FastAPI + Python)"]
        end

        subgraph DataLayer["💾 DATA LAYER"]
            Postgres["🗄️ PostgreSQL<br/>(Database)"]
            Redis["⚡ Redis<br/>(Cache)"]
        end

        subgraph ObsStack["📊 OBSERVABILITY STACK"]
            OTel["📡 OTel Collector<br/>(Telemetry)"]
            
            subgraph Monitoring["📈 MONITORING TOOLS"]
                Jaeger["🔍 Jaeger<br/>(Traces)"]
                Grafana["📊 Grafana<br/>(Dashboards)"]
                Prometheus["📈 Prometheus<br/>(Metrics)"]
            end
        end
    end

    %% User Flow
    User -->|HTTP Request| Frontend
    Frontend -->|API Calls| Backend
    
    %% Data Flow
    Backend -->|Read/Write| Postgres
    Backend -->|Cache| Redis
    
    %% Telemetry Flow
    Frontend -.->|Traces| OTel
    Backend -.->|Traces & Metrics| OTel
    OTel -->|Export Traces| Jaeger
    OTel -->|Export Metrics| Prometheus
    Grafana -->|Query| Prometheus

    %% High Contrast Styles
    classDef userStyle fill:#ffffff,stroke:#000000,stroke-width:3px,color:#000000
    classDef frontendStyle fill:#c8e6c9,stroke:#1b5e20,stroke-width:3px,color:#000000
    classDef backendStyle fill:#ffcc80,stroke:#bf360c,stroke-width:3px,color:#000000
    classDef dataStyle fill:#ce93d8,stroke:#4a148c,stroke-width:3px,color:#000000
    classDef obsStyle fill:#f8bbd9,stroke:#880e4f,stroke-width:3px,color:#000000
    
    class User userStyle
    class Frontend frontendStyle
    class Backend backendStyle
    class Postgres,Redis dataStyle
    class OTel,Jaeger,Grafana,Prometheus obsStyle
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

## 🛠️ Tecnologias Utilizadas

### 🎯 **FRONTEND**
#### **Framework & Biblioteca Principal**
- ![React](https://img.shields.io/badge/React-18.2.0-61dafb?logo=react&logoColor=white) - Biblioteca para interfaces de usuário
- ![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-3178c6?logo=typescript&logoColor=white) - Superset do JavaScript com tipagem estática
- ![Vite](https://img.shields.io/badge/Vite-6.3.5-646cff?logo=vite&logoColor=white) - Build tool e bundler moderno

#### **UI & Estilização**
- ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.3.5-06b6d4?logo=tailwindcss&logoColor=white) - Framework CSS utility-first
- ![PostCSS](https://img.shields.io/badge/PostCSS-8.4.31-dd3a0a?logo=postcss&logoColor=white) - Processador CSS
- ![React Icons](https://img.shields.io/badge/React_Icons-5.5.0-e91e63?logo=react&logoColor=white) - Biblioteca de ícones

#### **Gráficos & HTTP**
- ![Chart.js](https://img.shields.io/badge/Chart.js-4.4.0-ff6384?logo=chartdotjs&logoColor=white) - Biblioteca de gráficos
- ![Axios](https://img.shields.io/badge/Axios-1.6.0-5a29e4?logo=axios&logoColor=white) - Cliente HTTP para chamadas de API

### 🔧 **BACKEND**
#### **Framework & Runtime**
- ![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi&logoColor=white) - Framework web moderno para Python
- ![Python](https://img.shields.io/badge/Python-latest-3776ab?logo=python&logoColor=white) - Linguagem de programação principal
- ![Uvicorn](https://img.shields.io/badge/Uvicorn-standard-499848?logo=uvicorn&logoColor=white) - Servidor ASGI de alta performance

#### **Banco de Dados & Cache**
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql&logoColor=white) - Banco de dados relacional
- ![Redis](https://img.shields.io/badge/Redis-7-dc382d?logo=redis&logoColor=white) - Cache em memória e broker de mensagens

#### **Inteligência Artificial**
- ![Google AI](https://img.shields.io/badge/Google_Gemini-AI-4285f4?logo=google&logoColor=white) - API do Gemini para análise de documentos

### 📊 **OBSERVABILIDADE & MONITORAMENTO**
#### **OpenTelemetry Stack**
- ![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-latest-425cc7?logo=opentelemetry&logoColor=white) - Observabilidade unificada
- ![Jaeger](https://img.shields.io/badge/Jaeger-1.38-66d9ef?logo=jaeger&logoColor=white) - Distributed tracing
- ![Prometheus](https://img.shields.io/badge/Prometheus-v2.37.0-e6522c?logo=prometheus&logoColor=white) - Coleta de métricas
- ![Grafana](https://img.shields.io/badge/Grafana-9.1.0-f46800?logo=grafana&logoColor=white) - Dashboards e visualizações

### 🐳 **CONTAINERIZAÇÃO & DEPLOY**
- ![Docker](https://img.shields.io/badge/Docker-latest-2496ed?logo=docker&logoColor=white) - Containerização de aplicações
- ![Docker Compose](https://img.shields.io/badge/Docker_Compose-latest-2496ed?logo=docker&logoColor=white) - Orquestração de múltiplos containers
- ![Nginx](https://img.shields.io/badge/Nginx-1.21.3-009639?logo=nginx&logoColor=white) - Servidor web e proxy reverso

### ☸️ **KUBERNETES (OPCIONAL)**
- ![Kubernetes](https://img.shields.io/badge/Kubernetes-latest-326ce5?logo=kubernetes&logoColor=white) - Orquestração de containers
- ![Helm](https://img.shields.io/badge/Helm-latest-0f1689?logo=helm&logoColor=white) - Gerenciador de pacotes Kubernetes

### 🔐 **SEGURANÇA & CONFIGURAÇÃO**
- ![Environment Variables](https://img.shields.io/badge/Environment_Variables-Security-green) - Configuração segura
- ![CORS](https://img.shields.io/badge/CORS-Enabled-blue) - Cross-Origin Resource Sharing

---

### 📊 **RESUMO POR CATEGORIA:**

| **Categoria**         | **Tecnologias Principais**                    |
| --------------------- | --------------------------------------------- |
| **🎨 Frontend**        | React + TypeScript + Tailwind + Vite          |
| **⚙️ Backend**         | FastAPI + Python + PostgreSQL + Redis         |
| **🤖 IA**              | Google Gemini AI                              |
| **📊 Observabilidade** | OpenTelemetry + Jaeger + Prometheus + Grafana |
| **🐳 Containerização** | Docker + Docker Compose + Nginx               |
| **☸️ Deploy**          | Kubernetes + Helm (opcional)                  |

**Total: 30+ tecnologias** integradas em uma aplicação completa de fintech! 🚀

