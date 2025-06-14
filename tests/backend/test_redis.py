"""
Testes específicos para validação do Redis
"""
import pytest
import redis
import json
import time
from unittest.mock import patch
import os

class TestRedisValidation:
    """Testes para validação do Redis"""
    
    @pytest.fixture
    def redis_config(self):
        """Configuração de conexão com o Redis"""
        return {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'db': 0,
            'decode_responses': True
        }
    
    def test_redis_connection(self, redis_config):
        """Testa se é possível conectar ao Redis"""
        try:
            r = redis.Redis(**redis_config)
            # Testa ping
            assert r.ping() == True
        except redis.RedisError as e:
            pytest.fail(f"Falha na conexão com o Redis: {e}")
    
    def test_set_and_get_data(self, redis_config):
        """Testa operações básicas de set e get"""
        r = redis.Redis(**redis_config)
        
        # Testa string simples
        test_key = "test:fintelli:string"
        test_value = "valor de teste"
        
        r.set(test_key, test_value)
        retrieved_value = r.get(test_key)
        
        assert retrieved_value == test_value
        
        # Limpa dados de teste
        r.delete(test_key)
    
    def test_json_cache(self, redis_config):
        """Testa cache de dados JSON"""
        r = redis.Redis(**redis_config)
        
        test_key = "test:fintelli:json"
        test_data = {
            "total_income": 5000.00,
            "total_expense": 2000.00,
            "balance": 3000.00,
            "transactions_count": 15
        }
        
        # Armazena JSON
        r.set(test_key, json.dumps(test_data))
        
        # Recupera e decodifica JSON
        retrieved_data = json.loads(r.get(test_key))
        
        assert retrieved_data == test_data
        
        # Limpa dados de teste
        r.delete(test_key)
    
    def test_cache_expiration(self, redis_config):
        """Testa expiração de cache"""
        r = redis.Redis(**redis_config)
        
        test_key = "test:fintelli:expiry"
        test_value = "dados temporários"
        
        # Define com expiração de 2 segundos
        r.setex(test_key, 2, test_value)
        
        # Verifica se existe
        assert r.get(test_key) == test_value
        
        # Espera expirar
        time.sleep(3)
        
        # Verifica se expirou
        assert r.get(test_key) is None
    
    def test_hash_operations(self, redis_config):
        """Testa operações com hash"""
        r = redis.Redis(**redis_config)
        
        hash_key = "test:fintelli:hash"
        hash_data = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        
        # Define hash
        r.hset(hash_key, mapping=hash_data)
        
        # Recupera todos os campos
        retrieved_hash = r.hgetall(hash_key)
        
        assert retrieved_hash == hash_data
        
        # Testa recuperação de campo específico
        assert r.hget(hash_key, "field1") == "value1"
        
        # Limpa dados de teste
        r.delete(hash_key)
    
    def test_list_operations(self, redis_config):
        """Testa operações com listas"""
        r = redis.Redis(**redis_config)
        
        list_key = "test:fintelli:list"
        
        # Adiciona itens à lista
        r.lpush(list_key, "item1", "item2", "item3")
        
        # Verifica tamanho da lista
        assert r.llen(list_key) == 3
        
        # Recupera todos os itens
        items = r.lrange(list_key, 0, -1)
        assert "item1" in items
        assert "item2" in items
        assert "item3" in items
        
        # Limpa dados de teste
        r.delete(list_key)

class TestRedisPerformance:
    """Testes de performance do Redis"""
    
    def test_bulk_operations_performance(self, redis_config):
        """Testa performance de operações em lote"""
        r = redis.Redis(**redis_config)
        
        start_time = time.time()
        
        # Executa operações em lote
        pipe = r.pipeline()
        for i in range(1000):
            pipe.set(f"test:bulk:{i}", f"value:{i}")
        pipe.execute()
        
        end_time = time.time()
        operation_time = end_time - start_time
        
        assert operation_time < 2.0, f"Operações em lote muito lentas: {operation_time}s"
        
        # Limpa dados de teste
        for i in range(1000):
            r.delete(f"test:bulk:{i}")
    
    def test_memory_usage(self, redis_config):
        """Testa uso de memória"""
        r = redis.Redis(**redis_config)
        
        # Obtém informações de memória
        info = r.info('memory')
        
        # Verifica se o Redis está utilizando memória de forma razoável
        used_memory_mb = info['used_memory'] / (1024 * 1024)
        assert used_memory_mb < 100, f"Uso de memória muito alto: {used_memory_mb}MB"
