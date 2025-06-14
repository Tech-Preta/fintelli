# Helm Chart - Fintelli (Finanças Inteligentes com IA)

Este Helm chart provisiona a stack completa da aplicação Fintelli em um cluster Kubernetes.

## 📋 Stack de Aplicação

- **Frontend**: Nginx
- **Backend**: API FastAPI em Python
- **Banco de Dados**: PostgreSQL (pode usar o chart do Bitnami como dependência)
- **Cache**: Redis (pode usar o chart do Bitnami como dependência)

### Observabilidade

- **OpenTelemetry Collector**
- **Prometheus** (via kube-prometheus-stack)
- **Grafana** (via kube-prometheus-stack)
- **Jaeger** (via jaeger-operator)

## 🛠️ Pré-requisitos

- Cluster Kubernetes >= 1.20
- Helm >= 3.2

## 🚀 Como Instalar o Chart

### 1. Adicione os Repositórios de Dependências

O chart depende de outros charts da comunidade para a pilha de observabilidade. Adicione os repositórios necessários:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update
```

### 2. Crie os Segredos do Kubernetes

O chart espera que segredos para o banco de dados e a API do Gemini já existam no cluster. Crie-os no namespace desejado (ex: default):

```bash
# Segredo para a senha do PostgreSQL
kubectl create secret generic postgres-secret --from-literal=postgres-password='your_strong_password'

# Segredo para a chave da API do Gemini
kubectl create secret generic gemini-secret --from-literal=api-key='SUA_CHAVE_API_AQUI'
```

### 3. Instale o Chart

Execute o comando a seguir a partir do diretório raiz do chart (fintelli/), personalizando os valores se necessário:

```bash
helm install my-finance-release . \
  --set postgresql.auth.password=$(kubectl get secret postgres-secret -o jsonpath='{.data.postgres-password}' | base64 --decode) \
  --set backend.config.geminiApiKey=$(kubectl get secret gemini-secret -o jsonpath='{.data.api-key}' | base64 --decode)
```

## ⚙️ Configuração

Os principais parâmetros configuráveis estão no arquivo `values.yaml`. Você pode criar um arquivo `my-values.yaml` customizado e usá-lo na instalação:

```bash
helm install my-finance-release . -f my-values.yaml
```

### Parâmetros Principais

| Parâmetro                   | Descrição                                     | Valor Padrão                 |
| --------------------------- | --------------------------------------------- | ---------------------------- |
| `replicaCount`              | Número de réplicas para frontend e backend    | `1`                          |
| `backend.image.repository`  | Imagem Docker do backend                      | `your-repo/finance-backend`  |
| `frontend.image.repository` | Imagem Docker do frontend                     | `your-repo/finance-frontend` |
| `ingress.enabled`           | Habilita ou desabilita o Ingress              | `true`                       |
| `ingress.hosts`             | Configuração de hosts para o Ingress          | `chart-example.local`        |
| `postgresql.enabled`        | Provisiona o PostgreSQL como parte do release | `true`                       |
| `redis.enabled`             | Provisiona o Redis como parte do release      | `true`                       |
| `prometheus-stack.enabled`  | Provisiona a stack do Prometheus/Grafana      | `true`                       |
| `jaeger.enabled`            | Provisiona o Jaeger                           | `true`                       |

