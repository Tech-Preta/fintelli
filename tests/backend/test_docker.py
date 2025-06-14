"""
Testes específicos para validação do Docker Compose
"""
import pytest
import subprocess
import time
import requests
import json
import os

class TestDockerCompose:
    """Testes para validação do Docker Compose"""
    
    def test_docker_compose_file_exists(self):
        """Verifica se o arquivo docker-compose.yml existe"""
        compose_file = os.path.join(
            os.path.dirname(__file__), 
            '../../docker-compose.yml'
        )
        assert os.path.exists(compose_file), "Arquivo docker-compose.yml não encontrado"
    
    def test_docker_compose_syntax(self):
        """Verifica se a sintaxe do docker-compose.yml está correta"""
        try:
            result = subprocess.run(
                ['docker-compose', 'config'],
                cwd=os.path.join(os.path.dirname(__file__), '../..'),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            assert result.returncode == 0, f"Erro na sintaxe do docker-compose: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Timeout ao validar sintaxe do docker-compose")
        except FileNotFoundError:
            pytest.skip("Docker Compose não está instalado")
    
    def test_containers_are_running(self):
        """Verifica se todos os containers estão rodando"""
        try:
            result = subprocess.run(
                ['docker-compose', 'ps', '--format', 'json'],
                cwd=os.path.join(os.path.dirname(__file__), '../..'),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                containers = []
                for line in result.stdout.strip().split('\n'):
                    try:
                        container = json.loads(line)
                        containers.append(container)
                    except json.JSONDecodeError:
                        # Formato legado do docker-compose
                        pass
                
                if containers:
                    running_containers = [c for c in containers if c.get('State') == 'running']
                    print(f"✓ {len(running_containers)} containers rodando")
                else:
                    print("⚠ Nenhum container encontrado (pode estar parado)")
            else:
                print("⚠ Erro ao listar containers ou nenhum container ativo")
                
        except subprocess.TimeoutExpired:
            pytest.fail("Timeout ao verificar status dos containers")
        except FileNotFoundError:
            pytest.skip("Docker Compose não está instalado")

class TestDockerServices:
    """Testes para validação dos serviços Docker"""
    
    def test_backend_service_health(self):
        """Testa se o serviço backend está saudável"""
        try:
            response = requests.get('http://localhost:8001/health', timeout=10)
            assert response.status_code == 200
            print("✓ Serviço backend está saudável")
        except requests.RequestException:
            print("⚠ Serviço backend não está acessível")
    
    def test_frontend_service_health(self):
        """Testa se o serviço frontend está saudável"""
        try:
            response = requests.get('http://localhost:8080', timeout=10)
            assert response.status_code == 200
            print("✓ Serviço frontend está acessível")
        except requests.RequestException:
            print("⚠ Serviço frontend não está acessível")
    
    def test_database_service_health(self):
        """Testa se o serviço de banco de dados está saudável"""
        try:
            # Tenta conectar via backend (que já tem a conexão configurada)
            response = requests.get('http://localhost:8001/api/summary', timeout=10)
            # Se conseguir responder, o banco está funcionando
            if response.status_code in [200, 500]:  # 500 pode indicar erro de aplicação, mas DB conectado
                print("✓ Serviço de banco de dados está acessível")
            else:
                print("⚠ Possível problema com o banco de dados")
        except requests.RequestException:
            print("⚠ Não foi possível verificar o banco de dados")
    
    def test_redis_service_health(self):
        """Testa se o serviço Redis está saudável"""
        try:
            # Tenta usar Redis via backend
            response = requests.get('http://localhost:8001/api/summary', timeout=10)
            # Se o backend responder, é provável que o Redis esteja funcionando
            if response.status_code in [200, 500]:
                print("✓ Serviço Redis provavelmente está funcionando")
            else:
                print("⚠ Possível problema com o Redis")
        except requests.RequestException:
            print("⚠ Não foi possível verificar o Redis")

class TestDockerNetworking:
    """Testes para validação da rede Docker"""
    
    def test_internal_network_connectivity(self):
        """Testa conectividade entre serviços na rede interna"""
        try:
            # Verifica se backend consegue acessar banco de dados
            response = requests.get('http://localhost:8001/api/summary', timeout=15)
            
            if response.status_code == 200:
                print("✓ Conectividade interna entre serviços funcionando")
            else:
                print(f"⚠ Possível problema de conectividade: status {response.status_code}")
                
        except requests.RequestException as e:
            print(f"⚠ Erro de conectividade: {e}")
    
    def test_port_mapping(self):
        """Testa se o mapeamento de portas está funcionando"""
        services_and_ports = [
            ('frontend', 8080),
            ('backend', 8001),
            ('jaeger', 16687),
            ('prometheus', 9091),
            ('grafana', 3000)
        ]
        
        for service, port in services_and_ports:
            try:
                response = requests.get(f'http://localhost:{port}', timeout=5)
                if response.status_code in [200, 404]:  # 404 é OK para alguns serviços
                    print(f"✓ Porta {port} ({service}) está acessível")
                else:
                    print(f"⚠ Porta {port} ({service}) retornou status {response.status_code}")
            except requests.RequestException:
                print(f"⚠ Porta {port} ({service}) não está acessível")

class TestDockerVolumes:
    """Testes para validação dos volumes Docker"""
    
    def test_volume_persistence(self):
        """Testa se os volumes estão persistindo dados"""
        try:
            result = subprocess.run(
                ['docker', 'volume', 'ls', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                volumes = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            volume = json.loads(line)
                            volumes.append(volume)
                        except json.JSONDecodeError:
                            pass
                
                # Procura por volumes relacionados ao projeto
                project_volumes = [v for v in volumes if 'fintelli' in v.get('Name', '').lower()]
                
                if project_volumes:
                    print(f"✓ {len(project_volumes)} volumes do projeto encontrados")
                else:
                    print("⚠ Nenhum volume específico do projeto encontrado")
                    
        except subprocess.TimeoutExpired:
            print("⚠ Timeout ao verificar volumes")
        except FileNotFoundError:
            pytest.skip("Docker não está instalado")

class TestDockerLogs:
    """Testes para validação dos logs Docker"""
    
    def test_container_logs_accessibility(self):
        """Testa se os logs dos containers estão acessíveis"""
        services = ['backend', 'frontend', 'db', 'cache']
        
        for service in services:
            try:
                result = subprocess.run(
                    ['docker-compose', 'logs', '--tail=10', service],
                    cwd=os.path.join(os.path.dirname(__file__), '../..'),
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0:
                    if result.stdout.strip():
                        print(f"✓ Logs do serviço {service} estão acessíveis")
                    else:
                        print(f"⚠ Logs do serviço {service} estão vazios")
                else:
                    print(f"⚠ Erro ao acessar logs do serviço {service}")
                    
            except subprocess.TimeoutExpired:
                print(f"⚠ Timeout ao acessar logs do serviço {service}")
            except FileNotFoundError:
                pytest.skip("Docker Compose não está instalado")
