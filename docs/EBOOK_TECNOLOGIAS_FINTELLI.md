# 📖 E-book: Finanças pessoais com IA 

**Uma Jornada Completa Através das Tecnologias Modernas de Desenvolvimento**

---

## 📑 Sumário

1. [Introdução](#introducao)
2. [Arquitetura Geral](#arquitetura)
3. [Frontend Moderno](#frontend)
4. [Backend Robusto](#backend)
5. [Banco de Dados e Cache](#dados)
6. [Observabilidade Completa](#observabilidade)
7. [Containerização e Deploy](#deploy)
8. [Inteligência Artificial](#ia)
9. [Testes e Qualidade](#testes)
10. [Validações e Monitoramento](#validacoes)
11. [Boas Práticas](#praticas)
12. [Conclusão](#conclusao)

---

## 🚀 Introdução {#introducao}

### O que é o Fintelli?

O **Fintelli** é uma aplicação completa que demonstra como construir um sistema moderno de gestão financeira usando as melhores tecnologias disponíveis no mercado. Este projeto serve como um laboratório prático para desenvolvedores que desejam dominar tecnologias de ponta.

### Por que Este E-book?

Este e-book não é apenas uma documentação técnica, mas uma **jornada educativa** que explica:
- **Como** cada tecnologia funciona
- **Por que** escolhemos cada uma
- **Quando** usar cada ferramenta
- **Onde** aplicar na prática

### O que Você Vai Aprender

- 🎨 **Frontend Moderno**: React, TypeScript, Tailwind CSS
- ⚙️ **Backend Escalável**: FastAPI, Python, Arquitetura REST
- 💾 **Persistência de Dados**: PostgreSQL, Redis
- 📊 **Observabilidade**: OpenTelemetry, Jaeger, Prometheus, Grafana
- 🐳 **DevOps**: Docker, Docker Compose, Kubernetes
- 🤖 **IA Integrada**: Google Gemini API
- 🧪 **Qualidade**: Testes automatizados, CI/CD

---

## 🏗️ Arquitetura Geral {#arquitetura}

### Visão Macro da Aplicação

```
👤 Usuário
    ↓
🌐 Frontend (React)
    ↓
⚙️  Backend (FastAPI)
    ↓
💾 Dados (PostgreSQL + Redis)
    ↓
📊 Observabilidade (OTel + Jaeger + Prometheus)
```

### Princípios Arquiteturais

#### 1. **Separação de Responsabilidades**
- **Frontend**: Interface do usuário e experiência
- **Backend**: Lógica de negócio e APIs
- **Dados**: Persistência e cache
- **Observabilidade**: Monitoramento e métricas

#### 2. **Escalabilidade Horizontal**
- Containers Docker independentes
- Microserviços prontos para Kubernetes
- Load balancing com Nginx

#### 3. **Observabilidade por Design**
- Instrumentação desde o início
- Métricas customizadas de negócio
- Traces distribuídos completos

---

## 🎨 Frontend Moderno {#frontend}

### React 18: O Coração da Interface

#### Por que React?
- **Component-based**: Reutilização e manutenibilidade
- **Virtual DOM**: Performance otimizada
- **Ecosystem**: Vasto ecossistema de bibliotecas
- **Community**: Grande comunidade e suporte

#### Hooks Utilizados
```typescript
// Estado local
const [transactions, setTransactions] = useState<Transaction[]>([]);

// Efeitos colaterais
useEffect(() => {
    fetchTransactions();
}, []);

// Referências DOM
const formRef = useRef<HTMLFormElement>(null);
```

### TypeScript: Tipagem Estática

#### Benefícios do TypeScript
- **Type Safety**: Detecção de erros em tempo de compilação
- **IntelliSense**: Autocompletar e documentação inline
- **Refactoring**: Mudanças seguras no código
- **Documentation**: Tipos servem como documentação

#### Exemplo Prático
```typescript
interface Transaction {
    id?: number;
    description: string;
    amount: number;
    transaction_date: string;
}

interface TransactionFormProps {
    onTransactionAdded: () => void;
}

export function TransactionForm({ onTransactionAdded }: TransactionFormProps) {
    // Implementação tipada
}
```

### Tailwind CSS: Utility-First CSS

#### Filosofia do Tailwind
- **Utility Classes**: Classes pequenas e específicas
- **Customização**: Sistema de design consistente
- **Performance**: CSS otimizado automaticamente
- **Developer Experience**: Prototipagem rápida

#### Exemplo de Uso
```tsx
<div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
    <h3 className="text-xl font-bold mb-4">Adicionar Lançamento</h3>
    <button className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400">
        Adicionar
    </button>
</div>
```

### Vite: Build Tool Moderno

#### Vantagens do Vite
- **Dev Server Rápido**: Hot Module Replacement instantâneo
- **Build Otimizado**: Rollup para produção
- **Plugin Ecosystem**: Extensível com plugins
- **TypeScript**: Suporte nativo

#### Configuração do Vite
```typescript
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/api': {
                target: 'http://backend:8000',
                changeOrigin: true,
            }
        }
    }
});
```

### Axios: HTTP Client

#### Por que Axios?
- **Promise-based**: Sintaxe moderna com async/await
- **Interceptors**: Middleware para requests/responses
- **Error Handling**: Tratamento robusto de erros
- **TypeScript**: Tipagem completa

#### Implementação da API
```typescript
const apiClient = axios.create({
    baseURL: '/api',
});

export const addTransaction = async (transaction: Omit<Transaction, 'id'>) => {
    const response = await apiClient.post<Transaction>('/transactions', transaction);
    return response.data;
};
```

### Chart.js: Visualização de Dados

#### Recursos do Chart.js
- **Responsive**: Gráficos adaptáveis
- **Interactive**: Tooltips e animações
- **Customizable**: Altamente configurável
- **Performance**: Otimizado para grandes datasets

---

## ⚙️ Backend Robusto {#backend}

### FastAPI: Framework Web Moderno

#### Por que FastAPI?
- **Performance**: Uma das mais rápidas em Python
- **Type Hints**: Validação automática com Python types
- **OpenAPI**: Documentação automática
- **Async Support**: Programação assíncrona nativa

#### Exemplo de Endpoint
```python
@app.post("/api/transactions", response_model=Transaction, status_code=201)
def add_transaction(transaction: Transaction):
    # Validação automática pelo Pydantic
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("INSERT INTO transactions (description, amount, transaction_date) VALUES (%s, %s, %s) RETURNING id", 
                (transaction.description, transaction.amount, transaction.transaction_date))
    
    new_id = cur.fetchone()['id']
    transaction.id = new_id
    
    # Incrementa métrica customizada
    transactions_created_counter.add(1)
    
    return transaction
```

### Pydantic: Validação de Dados

#### Modelos de Dados
```python
class Transaction(BaseModel):
    id: Optional[int] = None
    description: str
    amount: float
    transaction_date: str
    
    @validator('amount')
    def amount_must_not_be_zero(cls, v):
        if v == 0:
            raise ValueError('Amount cannot be zero')
        return v
```

### Uvicorn: Servidor ASGI

#### Características do Uvicorn
- **ASGI Server**: Suporte completo a aplicações assíncronas
- **Performance**: Baseado em uvloop para máxima performance
- **Hot Reload**: Desenvolvimento ágil com reload automático
- **Production Ready**: Pronto para produção

### psycopg2: Driver PostgreSQL

#### Uso Otimizado
```python
def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host="db"
    )
    return conn

# Uso de cursor factory para resultados como dicionário
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
```

---

## 💾 Banco de Dados e Cache {#dados}

### PostgreSQL: Banco Relacional Robusto

#### Por que PostgreSQL?
- **ACID Compliance**: Transações seguras
- **JSON Support**: Dados estruturados e não-estruturados
- **Performance**: Otimizações avançadas
- **Extensibility**: Extensões como PostGIS

#### Schema do Fintelli
```sql
-- Tabela de transações
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de gastos fixos
CREATE TABLE fixed_expenses (
    id SERIAL PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_amount ON transactions(amount);
```

#### Consultas Otimizadas
```sql
-- Resumo financeiro otimizado
SELECT 
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
    SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as expense,
    SUM(amount) as balance
FROM transactions;

-- Análise por período
SELECT 
    DATE_TRUNC('month', transaction_date) as month,
    SUM(amount) as total
FROM transactions 
WHERE transaction_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY month
ORDER BY month;
```

### Redis: Cache de Alta Performance

#### Casos de Uso no Fintelli
- **Cache de Resumos**: Dados calculados frequentemente
- **Session Storage**: Sessões de usuário
- **Rate Limiting**: Controle de taxa de requisições
- **Pub/Sub**: Notificações em tempo real

#### Implementação de Cache
```python
def get_summary():
    # Verifica cache primeiro
    cached_summary = redis_client.get("financial_summary")
    if cached_summary: 
        return json.loads(cached_summary)
    
    # Calcula e armazena no cache
    summary = calculate_summary_from_db()
    redis_client.set("financial_summary", json.dumps(summary), ex=3600)
    return summary

def invalidate_summary_cache():
    """Invalida cache quando dados mudam"""
    redis_client.delete("financial_summary")
```

#### Padrões de Cache
- **Cache-Aside**: Aplicação gerencia o cache
- **Write-Through**: Escreve no cache e DB simultaneamente
- **Write-Behind**: Escreve no cache primeiro, DB depois
- **TTL (Time To Live)**: Expiração automática

---

## 📊 Observabilidade Completa {#observabilidade}

### OpenTelemetry: Observabilidade Unificada

#### Os Três Pilares da Observabilidade
1. **Metrics**: Dados quantitativos sobre o sistema
2. **Traces**: Jornada de uma requisição através dos serviços
3. **Logs**: Eventos discretos com contexto

#### Instrumentação Automática
```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def setup_opentelemetry(app):
    # Instrumenta FastAPI automaticamente
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    
    # Instrumenta PostgreSQL
    Psycopg2Instrumentor().instrument(tracer_provider=tracer_provider)
    
    # Instrumenta Redis
    RedisInstrumentor().instrument(tracer_provider=tracer_provider)
```

#### Métricas Customizadas
```python
from opentelemetry import metrics

# Criar meter
meter = metrics.get_meter("fintelli.api.meter")

# Contador de transações
transactions_created_counter = meter.create_counter(
    name="transactions_created_total",
    description="Conta o número total de transações criadas",
    unit="1"
)

# Uso da métrica
transactions_created_counter.add(1)
```

### Jaeger: Distributed Tracing

#### Como Funciona
- **Spans**: Unidades de trabalho em um trace
- **Trace**: Coleção de spans representando uma operação
- **Sampling**: Coleta estatística para reduzir overhead
- **Baggage**: Dados que acompanham o trace

#### Anatomia de um Trace
```
Trace: Criar Transação
├── Span: HTTP POST /api/transactions
├── Span: Validar Dados
├── Span: Conectar ao PostgreSQL
├── Span: INSERT INTO transactions
├── Span: Invalidar Cache Redis
└── Span: Retornar Resposta
```

### Prometheus: Coleta de Métricas

#### Tipos de Métricas
- **Counter**: Sempre cresce (ex: requests_total)
- **Gauge**: Pode subir/descer (ex: memory_usage)
- **Histogram**: Distribuição de valores (ex: request_duration)
- **Summary**: Similiar ao histogram com quantis

#### Queries Úteis
```promql
# Taxa de requisições por segundo
rate(http_requests_total[5m])

# Latência P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Crescimento de transações
increase(transactions_created_total[1h])

# Alerta de alta latência
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]) > 0.5
```

### Grafana: Visualização e Alertas

#### Tipos de Painéis
- **Time Series**: Métricas ao longo do tempo
- **Stat**: Valores únicos importantes
- **Bar Gauge**: Comparação de valores
- **Table**: Dados tabulares
- **Heatmap**: Distribuições de densidade

#### Dashboard Essencial para Fintech
```json
{
  "dashboard": {
    "title": "Fintelli - Visão Geral",
    "panels": [
      {
        "title": "Transações por Hora",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(transactions_created_total[1h])"
          }
        ]
      },
      {
        "title": "Latência da API",
        "type": "graph", 
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

---

## 🐳 Containerização e Deploy {#deploy}

### Docker: Containerização de Aplicações

#### Dockerfile do Backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile do Frontend
```dockerfile
# Estágio de build
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Estágio de produção
FROM nginx:1.21.3-alpine

# Remover configuração padrão
RUN rm /etc/nginx/conf.d/default.conf

# Copiar configuração customizada
COPY nginx.conf /etc/nginx/conf.d/

# Copiar arquivos buildados
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
```

### Docker Compose: Orquestração Local

#### Vantagens do Docker Compose
- **Multi-Container**: Gerencia múltiplos serviços
- **Networking**: Rede isolada entre containers
- **Volumes**: Persistência de dados
- **Environment**: Variáveis de ambiente centralizadas

#### Configuração Completa
```yaml
services:
  backend:
    build: ./src/backend
    environment:
      - OTEL_SERVICE_NAME=fintelli-backend
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
    depends_on:
      - db
      - cache
      - otel-collector
    volumes:
      - ./src/backend/app:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=finance_db
      - POSTGRES_USER=finance_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  cache:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
```

### Nginx: Proxy Reverso e Load Balancer

#### Configuração para SPA
```nginx
server {
    listen 80;
    
    # Servir arquivos estáticos
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy para API
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Kubernetes: Orquestração em Produção

#### Deployment do Backend
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fintelli-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fintelli-backend
  template:
    metadata:
      labels:
        app: fintelli-backend
    spec:
      containers:
      - name: backend
        image: fintelli-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fintelli-secrets
              key: postgres-password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### Service e Ingress
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fintelli-backend-service
spec:
  selector:
    app: fintelli-backend
  ports:
  - port: 8000
    targetPort: 8000

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fintelli-ingress
spec:
  rules:
  - host: fintelli.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: fintelli-backend-service
            port:
              number: 8000
```

---

## 🤖 Inteligência Artificial {#ia}

### Google Gemini API: IA Generativa

#### Integração com FastAPI
```python
import google.generativeai as genai

@app.post("/api/analyze-invoice")
async def analyze_invoice(file: UploadFile = File(...)):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Ler arquivo PDF
    pdf_content = await file.read()
    
    # Prompt estruturado
    prompt = """
    Analise esta fatura e extraia as seguintes informações em formato JSON:
    {
        "fornecedor": "Nome do fornecedor",
        "valor_total": 0.00,
        "data_vencimento": "YYYY-MM-DD",
        "itens": [
            {"descricao": "Item", "valor": 0.00}
        ]
    }
    """
    
    response = model.generate_content([
        prompt,
        {"mime_type": "application/pdf", "data": pdf_content}
    ])
    
    # Parse da resposta
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_response)
```

#### Casos de Uso em Fintech
- **Análise de Documentos**: Extrair dados de faturas, recibos
- **Categorização Automática**: Classificar transações
- **Detecção de Anomalias**: Identificar gastos suspeitos
- **Assistente Virtual**: Responder perguntas sobre finanças

### Prompt Engineering

#### Boas Práticas
- **Seja Específico**: Defina claramente o formato esperado
- **Use Exemplos**: Forneça exemplos do output desejado
- **Estruture o Contexto**: Organize informações hierarquicamente
- **Valide Respostas**: Sempre valide a saída da IA

---

## 🧪 Testes e Qualidade {#testes}

### Pirâmide de Testes

```
    /\
   /  \  E2E Tests (Poucos, Lentos, Caros)
  /____\
 /      \  Integration Tests (Médios)
/________\
\        / Unit Tests (Muitos, Rápidos, Baratos)
 \______/
```

### Testes de Frontend com React Testing Library

#### Filosofia
- **Teste como Usuário**: Foque na interação do usuário
- **Evite Detalhes de Implementação**: Teste comportamento, não código
- **Accessibility**: Encontre elementos como usuários com deficiência

#### Exemplo Prático
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TransactionForm } from './TransactionForm';

test('submete formulário com dados corretos', async () => {
    const user = userEvent.setup();
    const mockOnAdd = jest.fn();
    
    render(<TransactionForm onTransactionAdded={mockOnAdd} />);
    
    // Simula interação do usuário
    await user.type(screen.getByLabelText(/descrição/i), 'Salário');
    await user.type(screen.getByLabelText(/valor/i), '5000');
    await user.click(screen.getByRole('button', { name: /adicionar/i }));
    
    // Verifica resultado
    await waitFor(() => {
        expect(mockOnAdd).toHaveBeenCalled();
    });
});
```

### Testes de Backend com Pytest

#### Estrutura de Testes
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

class TestTransactionsAPI:
    """Testes para endpoints de transações"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_add_transaction_success(self, client):
        """Testa adição de transação com sucesso"""
        with patch('main.get_db_connection') as mock_db:
            # Setup do mock
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = {'id': 1}
            mock_db.return_value = mock_conn
            
            # Dados de teste
            transaction_data = {
                "description": "Salário",
                "amount": 5000.00,
                "transaction_date": "2024-06-14"
            }
            
            # Executar teste
            response = client.post("/api/transactions", json=transaction_data)
            
            # Verificações
            assert response.status_code == 201
            data = response.json()
            assert data["description"] == "Salário"
            assert data["amount"] == 5000.00
```

### Testes de Integração

#### Docker para Testes
```bash
#!/bin/bash
# Script de teste de integração

# Subir ambiente de teste
docker-compose -f docker-compose.test.yml up -d

# Aguardar serviços
sleep 30

# Executar testes
pytest tests/integration/ -v

# Limpar ambiente
docker-compose -f docker-compose.test.yml down -v
```

### Testes de Performance

#### K6 para Load Testing
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
    stages: [
        { duration: '2m', target: 100 }, // Ramp up
        { duration: '5m', target: 100 }, // Stay at 100 users
        { duration: '2m', target: 0 },   // Ramp down
    ],
};

export default function() {
    // Teste de criação de transação
    let payload = JSON.stringify({
        description: 'Load Test',
        amount: 100.00,
        transaction_date: '2024-06-14'
    });
    
    let response = http.post('http://localhost:8001/api/transactions', payload, {
        headers: { 'Content-Type': 'application/json' },
    });
    
    check(response, {
        'status is 201': (r) => r.status === 201,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
}
```

---

## 🧪 Validações e Monitoramento {#validacoes}

### Guia Completo de Testes e Validações

Esta seção fornece um overview completo de como testar e validar cada componente do Fintelli, garantindo que todos os sistemas estejam funcionando corretamente.

---

### 🎨 Testes de Frontend

#### Configuração do Ambiente de Testes

O frontend utiliza **Jest** e **React Testing Library** para testes unitários:

```bash
cd tests/frontend
npm install
npm test
```

#### Estrutura de Testes Frontend

```
tests/frontend/
├── src/
│   ├── components/          # Testes de componentes
│   │   ├── TransactionForm.test.tsx
│   │   ├── TransactionList.test.tsx
│   │   └── SummaryCard.test.tsx
│   ├── utils/               # Testes de utilitários
│   │   └── javascript.test.ts
│   └── setupTests.ts        # Configuração global
├── integration/             # Testes de integração
│   └── api.test.ts         # Testes de API
└── package.json
```

#### Exemplo de Teste de Componente

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { TransactionForm } from '../../../src/frontend/src/components/TransactionForm';

describe('TransactionForm', () => {
    test('renderiza o formulário corretamente', () => {
        render(<TransactionForm onTransactionAdded={jest.fn()} />);
        
        expect(screen.getByText('Adicionar Lançamento')).toBeInTheDocument();
        expect(screen.getByLabelText(/tipo/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/descrição/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/valor/i)).toBeInTheDocument();
    });
    
    test('valida dados antes do envio', async () => {
        const mockCallback = jest.fn();
        render(<TransactionForm onTransactionAdded={mockCallback} />);
        
        const submitButton = screen.getByRole('button', { name: /adicionar/i });
        fireEvent.click(submitButton);
        
        // Verifica se validação impede envio com dados vazios
        expect(mockCallback).not.toHaveBeenCalled();
    });
});
```

#### Comandos de Teste Frontend

```bash
# Executar todos os testes
npm test

# Modo watch (desenvolvimento)
npm run test:watch

# Relatório de cobertura
npm run test:coverage

# Testes específicos
npm run test:unit         # Apenas testes unitários
npm run test:integration  # Apenas testes de integração
```

---

### ⚙️ Testes de Backend

#### Configuração do Ambiente Backend

O backend utiliza **pytest** para testes:

```bash
cd tests/backend
pip install -r requirements.txt
pytest
```

#### Estrutura de Testes Backend

```
tests/backend/
├── test_api.py           # Testes de API
├── test_database.py      # Testes de banco de dados
├── test_redis.py         # Testes de cache
├── test_prometheus.py    # Testes de métricas
├── test_jaeger.py        # Testes de traces
├── test_opentelemetry.py # Testes de telemetria
├── test_docker.py        # Testes de containerização
└── requirements.txt
```

#### Exemplo de Teste de API

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestTransactionsAPI:
    def test_get_summary_empty_database(self):
        """Testa o resumo com banco vazio"""
        response = client.get("/api/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data == {"income": 0, "expense": 0, "balance": 0}
    
    def test_create_transaction(self):
        """Testa criação de transação"""
        transaction_data = {
            "type": "income",
            "description": "Salário",
            "amount": 5000,
            "date": "2024-01-15"
        }
        
        response = client.post("/api/transactions", json=transaction_data)
        assert response.status_code == 201
        
        created = response.json()
        assert created["type"] == transaction_data["type"]
        assert created["amount"] == transaction_data["amount"]
```

#### Comandos de Teste Backend

```bash
# Executar todos os testes
pytest

# Teste específico
pytest test_api.py

# Relatório de cobertura
pytest --cov=app --cov-report=html

# Testes em paralelo
pytest -n auto
```

---

### 🔍 Consultas de Endpoint na API

#### Testando Endpoints Manualmente

```bash
# Health check
curl http://localhost:8001/health

# Resumo financeiro
curl http://localhost:8001/api/summary

# Lista de transações
curl http://localhost:8001/api/transactions

# Criar transação
curl -X POST http://localhost:8001/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"income","description":"Teste","amount":100,"date":"2024-01-15"}'

# Deletar transação
curl -X DELETE http://localhost:8001/api/transactions/1
```

#### Testando com HTTPie (mais legível)

```bash
# Instalar HTTPie
pip install httpie

# Consultas
http GET localhost:8001/api/summary
http GET localhost:8001/api/transactions

# Criar transação
http POST localhost:8001/api/transactions \
  type=income description="Freelance" amount:=1500 date="2024-01-15"
```

#### Documentação Interativa

Acesse a documentação automática da API:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

### 🗄️ Validações no PostgreSQL

#### Conexão Manual com o Banco

```bash
# Via Docker
docker exec -it fintelli_db psql -U finance_user -d finance_db

# Via cliente local (se instalado)
psql -h localhost -p 5432 -U finance_user -d finance_db
```

#### Consultas de Validação

```sql
-- Verificar estrutura das tabelas
\dt

-- Verificar dados de transações
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;

-- Verificar resumo financeiro
SELECT 
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
    SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as expense,
    SUM(amount) as balance
FROM transactions;

-- Verificar integridade dos dados
SELECT 
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN amount > 0 THEN 1 END) as income_count,
    COUNT(CASE WHEN amount < 0 THEN 1 END) as expense_count
FROM transactions;

-- Verificar performance
EXPLAIN ANALYZE SELECT * FROM transactions WHERE date >= '2024-01-01';
```

#### Teste de Backup e Restore

```bash
# Criar backup
docker exec fintelli_db pg_dump -U finance_user finance_db > backup.sql

# Restaurar backup
docker exec -i fintelli_db psql -U finance_user finance_db < backup.sql
```

---

### ⚡ Validações no Redis

#### Conexão Manual com Redis

```bash
# Via Docker
docker exec -it fintelli_cache redis-cli

# Via cliente local
redis-cli -h localhost -p 6379
```

#### Comandos de Validação Redis

```bash
# Verificar status
INFO server

# Verificar memória
INFO memory

# Listar todas as chaves
KEYS *

# Verificar chaves do Fintelli
KEYS fintelli:*

# Verificar valor de cache
GET fintelli:summary

# Verificar TTL (time to live)
TTL fintelli:summary

# Verificar estatísticas
INFO stats

# Limpar cache (cuidado!)
FLUSHDB
```

#### Teste de Performance Redis

```bash
# Benchmark básico
redis-benchmark -h localhost -p 6379 -n 10000 -c 50

# Teste de latência
redis-cli --latency -h localhost -p 6379
```

---

### 📈 Validações no Prometheus

#### Acessando o Prometheus

**URL**: http://localhost:9091

#### Consultas de Validação (PromQL)

```promql
# Verificar se serviços estão up
up

# Métricas HTTP do backend
http_server_duration_seconds

# Contadores de transações criadas
transactions_created_total

# Taxa de criação de transações (por minuto)
rate(transactions_created_total[1m])

# Uso de memória do processo Python
process_resident_memory_bytes

# Conexões ativas do banco
database_connections_active

# Latência P95 das requisições HTTP
histogram_quantile(0.95, http_server_duration_seconds_bucket)
```

#### Testando Alerts

```promql
# Alta latência (> 1 segundo)
histogram_quantile(0.95, http_server_duration_seconds_bucket) > 1

# Muitas requisições com erro
rate(http_server_requests_total{status=~"5.."}[5m]) > 0.1

# Serviço down
up == 0
```

#### Verificação de Targets

1. Acesse: http://localhost:9091/targets
2. Verifique se todos os endpoints estão **UP**
3. Confirme última coleta de métricas

---

### 🔍 Validações no Jaeger

#### Acessando o Jaeger

**URL**: http://localhost:16687

#### Validações de Traces

1. **Serviços Disponíveis**
   - Acesse "Services" no menu
   - Verifique se `fintelli-backend` e `fintelli-frontend` aparecem

2. **Buscar Traces**
   - Selecione um serviço
   - Defina intervalo de tempo (últimas 1h)
   - Clique em "Find Traces"

3. **Analisar Trace Individual**
   - Clique em um trace
   - Verifique spans
   - Confirme propagação entre serviços

#### Consultas de Validação via API

```bash
# Listar serviços
curl http://localhost:16687/api/services

# Buscar traces dos últimos 1 hora
curl "http://localhost:16687/api/traces?service=fintelli-backend&start=$(date -d '1 hour ago' +%s)000000&end=$(date +%s)000000"

# Obter operações de um serviço
curl http://localhost:16687/api/services/fintelli-backend/operations
```

#### Métricas de Qualidade dos Traces

- **Completude**: Todos os spans necessários presentes
- **Precisão**: Timestamps e durações corretos
- **Context Propagation**: Headers de trace propagados
- **Error Tracking**: Erros marcados nos spans

---

### 🛠️ Validações do OpenTelemetry

#### Verificando o OTel Collector

```bash
# Status do collector
curl http://localhost:8889/metrics

# Verificar configuração
docker exec fintelli_otel_collector cat /etc/otel-collector-config.yml
```

#### Métricas do Collector

```bash
# Spans recebidos
curl -s http://localhost:8889/metrics | grep "otelcol_receiver_accepted_spans"

# Spans enviados
curl -s http://localhost:8889/metrics | grep "otelcol_exporter_sent_spans"

# Spans rejeitados
curl -s http://localhost:8889/metrics | grep "otelcol_processor_refused_spans"
```

#### Testando Instrumentação

##### Backend (Python)
```python
# Verificar se instrumentação está ativa
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
print(f"Tracer ativo: {tracer}")

# Criar span manualmente
with tracer.start_as_current_span("test_span") as span:
    span.set_attribute("test.key", "test.value")
    print("Span criado com sucesso")
```

##### Frontend (JavaScript)
```javascript
// Verificar se telemetria está carregada
console.log(window.opentelemetry);

// Verificar provider de traces
console.log(window.opentelemetry?.trace?.getActiveTracer());
```

---

### 🐳 Build com Docker Compose

#### Comandos de Validação

```bash
# Verificar sintaxe
docker-compose config

# Build completo
docker-compose build --no-cache

# Subir serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Verificar logs
docker-compose logs -f

# Verificar recursos
docker stats

# Parar e limpar
docker-compose down -v
```

#### Troubleshooting Docker

```bash
# Verificar imagens
docker images | grep fintelli

# Verificar volumes
docker volume ls | grep fintelli

# Verificar redes
docker network ls | grep fintelli

# Limpar recursos órfãos
docker system prune -f

# Verificar uso de disco
docker system df
```

#### Health Checks

```bash
# Verificar health de todos os containers
docker-compose ps --services --filter "status=running" | xargs -I {} docker inspect --format='{{.Name}}: {{.State.Health.Status}}' fintelli_{}
```

---

### 📋 Consulta de Logs do Frontend e Backend

#### Logs do Frontend (Nginx)

```bash
# Logs em tempo real
docker-compose logs -f frontend

# Logs específicos do nginx
docker exec fintelli_frontend cat /var/log/nginx/access.log
docker exec fintelli_frontend cat /var/log/nginx/error.log

# Filtrar por código de status
docker-compose logs frontend | grep " 404 "
docker-compose logs frontend | grep " 500 "
```

#### Logs do Backend (Python/FastAPI)

```bash
# Logs em tempo real
docker-compose logs -f backend

# Logs de aplicação
docker exec fintelli_backend cat /app/logs/application.log

# Filtrar por nível de log
docker-compose logs backend | grep ERROR
docker-compose logs backend | grep WARNING
```

#### Análise de Logs

```bash
# Contagem de requisições por endpoint
docker-compose logs backend | grep "GET\|POST\|PUT\|DELETE" | awk '{print $NF}' | sort | uniq -c

# Requisições mais lentas
docker-compose logs backend | grep "duration" | sort -k5 -nr | head -10

# Erros mais frequentes
docker-compose logs backend | grep ERROR | awk '{print $NF}' | sort | uniq -c | sort -nr
```

#### Configuração de Log Rotation

```bash
# Verificar tamanho dos logs
docker exec fintelli_backend du -sh /var/log/

# Configurar logrotate (se necessário)
echo '/var/log/nginx/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 nginx nginx
    postrotate
        nginx -s reload
    endscript
}' > /etc/logrotate.d/nginx
```

---

### 🎯 Testes de JavaScript

#### Testes de Utilitários

```javascript
// Formatação de moeda
test('formatCurrency', () => {
    expect(formatCurrency(1000)).toBe('R$ 1.000,00');
    expect(formatCurrency(-500)).toBe('-R$ 500,00');
    expect(formatCurrency(0)).toBe('R$ 0,00');
});

// Validação de transação
test('validateTransaction', () => {
    const valid = {
        type: 'income',
        description: 'Salário',
        amount: 5000,
        date: '2024-01-15'
    };
    
    expect(validateTransaction(valid).isValid).toBe(true);
    
    const invalid = {
        type: 'income',
        description: '',
        amount: -5000,
        date: '2024-01-32'
    };
    
    expect(validateTransaction(invalid).isValid).toBe(false);
});

// Cálculo de resumo
test('calculateSummary', () => {
    const transactions = [
        { type: 'income', amount: 1000 },
        { type: 'expense', amount: -300 }
    ];
    
    const summary = calculateSummary(transactions);
    expect(summary.balance).toBe(700);
    expect(summary.income).toBe(1000);
    expect(summary.expense).toBe(300);
});
```

#### Testes de Integração API

```javascript
test('API Integration', async () => {
    // Teste de health check
    const health = await fetch('http://localhost:8001/health');
    expect(health.status).toBe(200);
    
    // Teste de endpoint de resumo
    const summary = await fetch('http://localhost:8001/api/summary');
    const data = await summary.json();
    
    expect(data).toHaveProperty('income');
    expect(data).toHaveProperty('expense');
    expect(data).toHaveProperty('balance');
    
    // Teste de criação de transação
    const transaction = await fetch('http://localhost:8001/api/transactions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: 'income',
            description: 'Teste',
            amount: 100,
            date: '2024-01-15'
        }),
    });
    
    const transactionData = await transaction.json();
    expect(transaction.status).toBe(201);
    expect(transactionData).toHaveProperty('id');
});
```

#### Performance Testing

```javascript
test('Performance Test', async () => {
    const start = Date.now();
    
    // Múltiplas requisições paralelas
    const promises = Array(10).fill().map(() => 
        fetch('http://localhost:8001/api/summary')
    );
    
    await Promise.all(promises);
    
    const duration = Date.now() - start;
    expect(duration).toBeLessThan(5000); // 5 segundos
});
```

---

### 🚀 Script de Testes Automatizados

#### Executando Todos os Testes

```bash
# Script principal de integração
./tests/integration/run_tests.sh

# Testes individuais
./tests/integration/run_tests.sh test_frontend
./tests/integration/run_tests.sh test_backend
./tests/integration/run_tests.sh test_database
```

#### Relatório de Testes

O script gera um relatório completo incluindo:

- ✅ **Status dos Containers**: Todos os serviços rodando
- ✅ **Health Checks**: APIs respondendo corretamente
- ✅ **Conectividade**: Comunicação entre serviços
- ✅ **Persistência**: Banco de dados operacional
- ✅ **Cache**: Redis funcionando
- ✅ **Observabilidade**: Métricas e traces sendo coletados
- ✅ **Frontend**: Interface carregando corretamente
- ✅ **Logs**: Acessibilidade e análise de logs

#### Exemplo de Saída

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

[INFO] Testando PostgreSQL...
[SUCCESS] Conexão com PostgreSQL estabelecida
[SUCCESS] Tabelas existem e estão acessíveis

[INFO] Testando Redis...
[SUCCESS] Redis está funcionando corretamente

[INFO] Testando OpenTelemetry...
[SUCCESS] Métricas do OTel Collector encontradas
[SUCCESS] Serviços encontrados no Jaeger

==============================================
[SUCCESS] Todos os testes de integração passaram! 🎉
Fintelli está funcionando perfeitamente!
==============================================
```

---

### 📊 Monitoramento Contínuo

#### Dashboards Grafana

Acesse http://localhost:3000 (admin/admin) e configure dashboards para:

1. **Métricas de Aplicação**
   - Taxa de requisições
   - Latência P95
   - Taxa de erro
   - Throughput

2. **Métricas de Sistema**
   - CPU e memória
   - Disk I/O
   - Network I/O
   - Container health

3. **Métricas de Negócio**
   - Transações criadas por período
   - Volume financeiro processado
   - Usuários ativos
   - Operações por tipo

#### Alertas

Configure alertas para:
- Latência alta (> 1s)
- Taxa de erro alta (> 5%)
- Serviços down
- Uso de memória alto (> 80%)
- Disk space baixo (< 10%)

---

## 💡 Dicas de Troubleshooting

### Problemas Comuns

#### 1. Container não sobe
```bash
# Verificar logs
docker-compose logs [nome_do_servico]

# Verificar recursos
docker system df

# Limpar e rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### 2. API não responde
```bash
# Verificar se porta está livre
netstat -tulpn | grep :8001

# Verificar logs do backend
docker-compose logs backend

# Testar conectividade
curl -v http://localhost:8001/health
```

#### 3. Banco de dados inacessível
```bash
# Verificar container
docker-compose ps db

# Verificar logs
docker-compose logs db

# Testar conexão
docker exec -it fintelli_db psql -U finance_user -d finance_db
```

#### 4. Observabilidade não funciona
```bash
# Verificar OTel Collector
curl http://localhost:8889/metrics

# Verificar Jaeger
curl http://localhost:16687/api/services

# Verificar Prometheus
curl http://localhost:9091/api/v1/query?query=up
```

---
