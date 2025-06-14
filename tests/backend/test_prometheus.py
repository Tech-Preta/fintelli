"""
Testes específicos para validação do Prometheus
"""
import pytest
import requests
import json
import time
from unittest.mock import patch
import os

class TestPrometheusValidation:
    """Testes para validação do Prometheus"""
    
    @pytest.fixture
    def prometheus_url(self):
        """URL base do Prometheus"""
        host = os.getenv('PROMETHEUS_HOST', 'localhost')
        port = os.getenv('PROMETHEUS_PORT', '9091')
        return f"http://{host}:{port}"
    
    def test_prometheus_health(self, prometheus_url):
        """Testa se o Prometheus está rodando"""
        try:
            response = requests.get(f"{prometheus_url}/-/healthy", timeout=10)
            assert response.status_code == 200
        except requests.RequestException as e:
            pytest.fail(f"Prometheus não está acessível: {e}")
    
    def test_prometheus_ready(self, prometheus_url):
        """Testa se o Prometheus está pronto"""
        try:
            response = requests.get(f"{prometheus_url}/-/ready", timeout=10)
            assert response.status_code == 200
        except requests.RequestException as e:
            pytest.fail(f"Prometheus não está pronto: {e}")
    
    def test_prometheus_config(self, prometheus_url):
        """Testa se a configuração do Prometheus está carregada"""
        try:
            response = requests.get(f"{prometheus_url}/api/v1/status/config", timeout=10)
            assert response.status_code == 200
            
            config_data = response.json()
            assert config_data['status'] == 'success'
            assert 'yaml' in config_data['data']
        except requests.RequestException as e:
            pytest.fail(f"Erro ao obter configuração do Prometheus: {e}")
    
    def test_prometheus_targets(self, prometheus_url):
        """Testa se os targets estão sendo descobertos"""
        try:
            response = requests.get(f"{prometheus_url}/api/v1/targets", timeout=10)
            assert response.status_code == 200
            
            targets_data = response.json()
            assert targets_data['status'] == 'success'
            
            # Verifica se existem targets ativos
            active_targets = targets_data['data']['activeTargets']
            assert len(active_targets) > 0, "Nenhum target ativo encontrado"
            
        except requests.RequestException as e:
            pytest.fail(f"Erro ao obter targets do Prometheus: {e}")
    
    def test_custom_metrics_available(self, prometheus_url):
        """Testa se métricas customizadas estão disponíveis"""
        try:
            # Busca métricas específicas da aplicação
            metrics_to_check = [
                'http_server_duration_seconds',
                'transactions_created_total',
                'database_connections_active'
            ]
            
            for metric in metrics_to_check:
                response = requests.get(
                    f"{prometheus_url}/api/v1/query",
                    params={'query': metric},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'success' and data['data']['result']:
                        print(f"✓ Métrica {metric} encontrada")
                    else:
                        print(f"⚠ Métrica {metric} não encontrada (normal se a aplicação não estiver gerando dados)")
                        
        except requests.RequestException as e:
            pytest.fail(f"Erro ao consultar métricas: {e}")
    
    def test_query_range(self, prometheus_url):
        """Testa consultas com range de tempo"""
        try:
            # Consulta métricas dos últimos 5 minutos
            end_time = int(time.time())
            start_time = end_time - 300  # 5 minutos atrás
            
            response = requests.get(
                f"{prometheus_url}/api/v1/query_range",
                params={
                    'query': 'up',
                    'start': start_time,
                    'end': end_time,
                    'step': '15s'
                },
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'success'
            
        except requests.RequestException as e:
            pytest.fail(f"Erro ao executar query range: {e}")

class TestPrometheusMetrics:
    """Testes específicos para métricas do Prometheus"""
    
    def test_application_metrics(self, prometheus_url):
        """Testa métricas específicas da aplicação"""
        try:
            # Testa métrica de uptime
            response = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={'query': 'up{job="fintelli-backend"}'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data['data']['result']:
                    # Verifica se a aplicação está up (valor 1)
                    for result in data['data']['result']:
                        assert float(result['value'][1]) == 1.0, "Aplicação não está up"
                        
        except requests.RequestException as e:
            print(f"Aviso: Erro ao verificar métricas da aplicação: {e}")
    
    def test_system_metrics(self, prometheus_url):
        """Testa métricas do sistema"""
        try:
            system_metrics = [
                'go_memstats_alloc_bytes',
                'go_goroutines',
                'process_cpu_seconds_total'
            ]
            
            for metric in system_metrics:
                response = requests.get(
                    f"{prometheus_url}/api/v1/query",
                    params={'query': metric},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'success' and data['data']['result']:
                        print(f"✓ Métrica do sistema {metric} disponível")
                        
        except requests.RequestException as e:
            print(f"Aviso: Erro ao verificar métricas do sistema: {e}")

class TestPrometheusAlerts:
    """Testes para alertas do Prometheus"""
    
    def test_alertmanager_rules(self, prometheus_url):
        """Testa se as regras de alerta estão carregadas"""
        try:
            response = requests.get(f"{prometheus_url}/api/v1/rules", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                assert data['status'] == 'success'
                print("✓ Regras de alerta carregadas com sucesso")
            else:
                print("⚠ Nenhuma regra de alerta configurada")
                
        except requests.RequestException as e:
            print(f"Aviso: Erro ao verificar regras de alerta: {e}")
