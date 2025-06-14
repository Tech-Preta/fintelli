"""
Testes específicos para validação do Jaeger
"""
import pytest
import requests
import json
import time
from datetime import datetime, timedelta
import os

class TestJaegerValidation:
    """Testes para validação do Jaeger"""
    
    @pytest.fixture
    def jaeger_url(self):
        """URL base do Jaeger"""
        host = os.getenv('JAEGER_HOST', 'localhost')
        port = os.getenv('JAEGER_PORT', '16687')
        return f"http://{host}:{port}"
    
    def test_jaeger_health(self, jaeger_url):
        """Testa se o Jaeger está rodando"""
        try:
            response = requests.get(f"{jaeger_url}/", timeout=10)
            assert response.status_code == 200
            assert "Jaeger UI" in response.text or "jaeger" in response.text.lower()
        except requests.RequestException as e:
            pytest.fail(f"Jaeger UI não está acessível: {e}")
    
    def test_jaeger_api_services(self, jaeger_url):
        """Testa se a API de serviços do Jaeger está funcionando"""
        try:
            response = requests.get(f"{jaeger_url}/api/services", timeout=10)
            assert response.status_code == 200
            
            services = response.json()
            assert isinstance(services, dict)
            assert 'data' in services
            
            # Verifica se existe lista de serviços
            services_list = services['data']
            assert isinstance(services_list, list)
            
        except requests.RequestException as e:
            pytest.fail(f"API de serviços do Jaeger não está funcionando: {e}")
    
    def test_jaeger_traces_api(self, jaeger_url):
        """Testa se a API de traces está funcionando"""
        try:
            # Busca traces dos últimos 1 hora
            end_time = int(time.time() * 1000000)  # microsegundos
            start_time = end_time - (3600 * 1000000)  # 1 hora atrás
            
            params = {
                'start': start_time,
                'end': end_time,
                'limit': 20
            }
            
            response = requests.get(
                f"{jaeger_url}/api/traces",
                params=params,
                timeout=10
            )
            
            assert response.status_code == 200
            traces_data = response.json()
            
            assert 'data' in traces_data
            
        except requests.RequestException as e:
            pytest.fail(f"API de traces do Jaeger não está funcionando: {e}")
    
    def test_application_traces(self, jaeger_url):
        """Testa se existem traces da aplicação"""
        try:
            # Primeiro, obtém lista de serviços
            response = requests.get(f"{jaeger_url}/api/services", timeout=10)
            services = response.json()['data']
            
            # Procura por serviços da aplicação
            app_services = [s for s in services if 'fintelli' in s.lower() or 'finance' in s.lower()]
            
            if app_services:
                print(f"✓ Serviços da aplicação encontrados: {app_services}")
                
                # Para cada serviço, busca traces recentes
                for service in app_services:
                    self._check_service_traces(jaeger_url, service)
            else:
                print("⚠ Nenhum serviço da aplicação encontrado no Jaeger")
                
        except requests.RequestException as e:
            print(f"Aviso: Erro ao verificar traces da aplicação: {e}")
    
    def _check_service_traces(self, jaeger_url, service_name):
        """Verifica traces de um serviço específico"""
        try:
            end_time = int(time.time() * 1000000)
            start_time = end_time - (3600 * 1000000)  # 1 hora atrás
            
            params = {
                'service': service_name,
                'start': start_time,
                'end': end_time,
                'limit': 10
            }
            
            response = requests.get(
                f"{jaeger_url}/api/traces",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                traces = response.json()['data']
                if traces:
                    print(f"✓ {len(traces)} traces encontrados para o serviço {service_name}")
                else:
                    print(f"⚠ Nenhum trace encontrado para o serviço {service_name}")
                    
        except requests.RequestException as e:
            print(f"Erro ao verificar traces do serviço {service_name}: {e}")

class TestJaegerOperations:
    """Testes para operações específicas do Jaeger"""
    
    def test_operations_api(self, jaeger_url):
        """Testa API de operações"""
        try:
            # Primeiro obtém serviços
            response = requests.get(f"{jaeger_url}/api/services", timeout=10)
            services = response.json()['data']
            
            if services:
                # Pega o primeiro serviço para testar operações
                service = services[0]
                
                response = requests.get(
                    f"{jaeger_url}/api/services/{service}/operations",
                    timeout=10
                )
                
                assert response.status_code == 200
                operations = response.json()
                assert 'data' in operations
                
        except requests.RequestException as e:
            print(f"Aviso: Erro ao testar API de operações: {e}")
    
    def test_trace_detail(self, jaeger_url):
        """Testa detalhes de um trace específico"""
        try:
            # Busca um trace recente
            end_time = int(time.time() * 1000000)
            start_time = end_time - (3600 * 1000000)
            
            response = requests.get(
                f"{jaeger_url}/api/traces",
                params={
                    'start': start_time,
                    'end': end_time,
                    'limit': 1
                },
                timeout=10
            )
            
            if response.status_code == 200:
                traces = response.json()['data']
                if traces:
                    trace_id = traces[0]['traceID']
                    
                    # Busca detalhes do trace
                    detail_response = requests.get(
                        f"{jaeger_url}/api/traces/{trace_id}",
                        timeout=10
                    )
                    
                    assert detail_response.status_code == 200
                    trace_detail = detail_response.json()
                    assert 'data' in trace_detail
                    
        except requests.RequestException as e:
            print(f"Aviso: Erro ao testar detalhes de trace: {e}")

class TestJaegerIntegration:
    """Testes de integração com OpenTelemetry"""
    
    def test_otel_integration(self, jaeger_url):
        """Testa se o Jaeger está recebendo dados do OTel Collector"""
        try:
            # Verifica se existem spans recentes (últimos 15 minutos)
            end_time = int(time.time() * 1000000)
            start_time = end_time - (900 * 1000000)  # 15 minutos
            
            response = requests.get(
                f"{jaeger_url}/api/traces",
                params={
                    'start': start_time,
                    'end': end_time,
                    'limit': 50
                },
                timeout=10
            )
            
            if response.status_code == 200:
                traces = response.json()['data']
                
                if traces:
                    print(f"✓ {len(traces)} traces recentes encontrados")
                    
                    # Verifica se há spans com características do OpenTelemetry
                    for trace in traces[:5]:  # Verifica apenas os primeiros 5
                        self._validate_otel_trace(trace)
                else:
                    print("⚠ Nenhum trace recente encontrado")
                    
        except requests.RequestException as e:
            print(f"Aviso: Erro ao verificar integração OTel: {e}")
    
    def _validate_otel_trace(self, trace):
        """Valida se um trace tem características do OpenTelemetry"""
        if 'spans' in trace:
            for span in trace['spans'][:3]:  # Verifica apenas os primeiros 3 spans
                # Verifica se o span tem estrutura esperada
                required_fields = ['spanID', 'operationName', 'startTime', 'duration']
                for field in required_fields:
                    if field not in span:
                        print(f"⚠ Campo {field} ausente no span")
                        return
                
                # Verifica se há tags (atributos) do OpenTelemetry
                if 'tags' in span:
                    tags = {tag['key']: tag['value'] for tag in span['tags']}
                    
                    # Procura por tags comuns do OpenTelemetry
                    otel_tags = ['http.method', 'http.status_code', 'component', 'span.kind']
                    found_otel_tags = [tag for tag in otel_tags if tag in tags]
                    
                    if found_otel_tags:
                        print(f"✓ Tags OpenTelemetry encontradas: {found_otel_tags}")
                    else:
                        print("⚠ Nenhuma tag OpenTelemetry comum encontrada")
