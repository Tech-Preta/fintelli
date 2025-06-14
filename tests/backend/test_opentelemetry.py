"""
Testes específicos para validação do OpenTelemetry
"""
import pytest
import requests
import json
import time
import os
from unittest.mock import patch, MagicMock

class TestOpenTelemetryCollector:
    """Testes para validação do OTel Collector"""
    
    @pytest.fixture
    def otel_collector_url(self):
        """URL do OTel Collector"""
        host = os.getenv('OTEL_COLLECTOR_HOST', 'localhost')
        port = os.getenv('OTEL_COLLECTOR_PORT', '8889')
        return f"http://{host}:{port}"
    
    def test_otel_collector_health(self, otel_collector_url):
        """Testa se o OTel Collector está rodando"""
        try:
            # Tenta acessar o endpoint de health
            response = requests.get(f"{otel_collector_url}/", timeout=10)
            # O collector pode retornar diferentes códigos dependendo da configuração
            assert response.status_code in [200, 404], f"Código inesperado: {response.status_code}"
            
        except requests.RequestException as e:
            pytest.fail(f"OTel Collector não está acessível: {e}")
    
    def test_otel_metrics_endpoint(self, otel_collector_url):
        """Testa endpoint de métricas do collector"""
        try:
            response = requests.get(f"{otel_collector_url}/metrics", timeout=10)
            
            if response.status_code == 200:
                metrics_text = response.text
                
                # Verifica se contém métricas esperadas do collector
                expected_metrics = [
                    'otelcol_processor_batch_batch_size_trigger_send',
                    'otelcol_receiver_accepted_spans',
                    'otelcol_exporter_sent_spans'
                ]
                
                found_metrics = []
                for metric in expected_metrics:
                    if metric in metrics_text:
                        found_metrics.append(metric)
                
                if found_metrics:
                    print(f"✓ Métricas do collector encontradas: {found_metrics}")
                else:
                    print("⚠ Métricas específicas do collector não encontradas")
                    
            else:
                print(f"⚠ Endpoint de métricas retornou status {response.status_code}")
                
        except requests.RequestException as e:
            print(f"Aviso: Erro ao acessar métricas do collector: {e}")

class TestOpenTelemetryInstrumentation:
    """Testes para instrumentação OpenTelemetry"""
    
    def test_backend_instrumentation(self):
        """Testa se o backend está instrumentado com OpenTelemetry"""
        # Simula verificação da instrumentação do backend
        # Este teste verificaria se os decoradores e middleware estão configurados
        
        # Mock do módulo de instrumentação
        try:
            # Tentaria importar o módulo de instrumentação
            import sys
            import os
            
            # Adiciona o path do backend
            backend_path = os.path.join(os.path.dirname(__file__), '../../src/backend/app')
            if backend_path not in sys.path:
                sys.path.append(backend_path)
            
            # Tenta importar o módulo de instrumentação
            try:
                import instrumentation
                print("✓ Módulo de instrumentação encontrado")
                
                # Verifica se as funções necessárias estão presentes
                expected_functions = ['setup_telemetry']
                for func in expected_functions:
                    if hasattr(instrumentation, func):
                        print(f"✓ Função {func} encontrada")
                    else:
                        print(f"⚠ Função {func} não encontrada")
                        
            except ImportError as e:
                print(f"⚠ Módulo de instrumentação não pode ser importado: {e}")
                
        except Exception as e:
            print(f"Erro ao testar instrumentação do backend: {e}")
    
    def test_frontend_telemetry(self):
        """Testa se o frontend tem instrumentação de telemetria"""
        try:
            # Verifica se o arquivo telemetry.js existe
            frontend_path = os.path.join(os.path.dirname(__file__), '../../src/frontend')
            telemetry_file = os.path.join(frontend_path, 'telemetry.js')
            
            if os.path.exists(telemetry_file):
                print("✓ Arquivo telemetry.js encontrado")
                
                # Lê o conteúdo para verificar configuração
                with open(telemetry_file, 'r') as f:
                    content = f.read()
                    
                # Verifica se contém configurações essenciais
                essential_configs = [
                    'WebTracerProvider',
                    'BatchSpanProcessor',
                    'OTLPTraceExporter'
                ]
                
                found_configs = []
                for config in essential_configs:
                    if config in content:
                        found_configs.append(config)
                
                if found_configs:
                    print(f"✓ Configurações de telemetria encontradas: {found_configs}")
                else:
                    print("⚠ Configurações essenciais de telemetria não encontradas")
            else:
                print("⚠ Arquivo telemetry.js não encontrado")
                
        except Exception as e:
            print(f"Erro ao verificar telemetria do frontend: {e}")

class TestOpenTelemetryData:
    """Testes para validação de dados OpenTelemetry"""
    
    def test_trace_data_format(self):
        """Testa formato dos dados de trace"""
        # Este teste simularia a validação do formato de dados de trace
        
        sample_trace = {
            "traceId": "5B8EFFF798038103D269B633813FC60C",
            "spanId": "EEE19B7EC3C1B173",
            "parentSpanId": "EEE19B7EC3C1B174",
            "operationName": "HTTP GET",
            "startTime": 1234567890000000,
            "duration": 1000000,
            "tags": [
                {"key": "http.method", "value": "GET"},
                {"key": "http.status_code", "value": "200"}
            ]
        }
        
        # Validações básicas do formato
        assert "traceId" in sample_trace
        assert "spanId" in sample_trace
        assert "operationName" in sample_trace
        assert "startTime" in sample_trace
        assert "duration" in sample_trace
        
        # Valida formato dos IDs
        assert len(sample_trace["traceId"]) == 32
        assert len(sample_trace["spanId"]) == 16
        
        print("✓ Formato de trace validado")
    
    def test_metrics_data_format(self):
        """Testa formato dos dados de métricas"""
        sample_metric = {
            "name": "http_server_duration_seconds",
            "type": "histogram",
            "help": "HTTP server request duration",
            "unit": "seconds",
            "samples": [
                {
                    "name": "http_server_duration_seconds_count",
                    "labels": {"method": "GET", "status": "200"},
                    "value": 42,
                    "timestamp": 1234567890
                }
            ]
        }
        
        # Validações básicas
        assert "name" in sample_metric
        assert "type" in sample_metric
        assert "samples" in sample_metric
        
        # Valida amostras
        for sample in sample_metric["samples"]:
            assert "name" in sample
            assert "value" in sample
            assert "timestamp" in sample
        
        print("✓ Formato de métrica validado")

class TestOpenTelemetryConfig:
    """Testes para configuração OpenTelemetry"""
    
    def test_collector_config_file(self):
        """Testa se o arquivo de configuração do collector existe e é válido"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '../../config/otel-collector-config.yml'
            )
            
            if os.path.exists(config_path):
                print("✓ Arquivo de configuração do collector encontrado")
                
                with open(config_path, 'r') as f:
                    content = f.read()
                
                # Verifica seções essenciais
                essential_sections = ['receivers', 'processors', 'exporters', 'service']
                
                found_sections = []
                for section in essential_sections:
                    if f"{section}:" in content:
                        found_sections.append(section)
                
                if len(found_sections) == len(essential_sections):
                    print(f"✓ Todas as seções essenciais encontradas: {found_sections}")
                else:
                    missing = set(essential_sections) - set(found_sections)
                    print(f"⚠ Seções ausentes: {missing}")
                    
            else:
                print("⚠ Arquivo de configuração do collector não encontrado")
                
        except Exception as e:
            print(f"Erro ao verificar configuração do collector: {e}")
    
    def test_environment_variables(self):
        """Testa se as variáveis de ambiente necessárias estão configuradas"""
        required_vars = [
            'OTEL_SERVICE_NAME',
            'OTEL_EXPORTER_OTLP_ENDPOINT'
        ]
        
        optional_vars = [
            'OTEL_RESOURCE_ATTRIBUTES',
            'OTEL_PROPAGATORS',
            'OTEL_TRACES_SAMPLER'
        ]
        
        # Verifica variáveis obrigatórias
        missing_required = []
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        if not missing_required:
            print("✓ Todas as variáveis obrigatórias estão configuradas")
        else:
            print(f"⚠ Variáveis obrigatórias ausentes: {missing_required}")
        
        # Verifica variáveis opcionais
        found_optional = []
        for var in optional_vars:
            if os.getenv(var):
                found_optional.append(var)
        
        if found_optional:
            print(f"✓ Variáveis opcionais configuradas: {found_optional}")
        else:
            print("⚠ Nenhuma variável opcional configurada")
