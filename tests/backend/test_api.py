import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import psycopg2
import redis
import json
from unittest.mock import patch, MagicMock

# Importa a aplicação principal
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/backend/app'))

from main import app

client = TestClient(app)

class TestTransactionsAPI:
    """Testes para endpoints de transações"""
    
    def test_get_summary_empty_database(self):
        """Testa o resumo com banco vazio"""
        with patch('main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            response = client.get("/api/summary")
            assert response.status_code == 200
            data = response.json()
            assert data == {"income": 0, "expense": 0, "balance": 0}

    def test_get_summary_with_transactions(self):
        """Testa o resumo com transações"""
        with patch('main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            # Simula transações: receita de 1000 e despesa de -500
            mock_cursor.fetchall.return_value = [
                {'amount': 1000.00},
                {'amount': -500.00}
            ]
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            response = client.get("/api/summary")
            assert response.status_code == 200
            data = response.json()
            assert data["income"] == 1000.0
            assert data["expense"] == -500.0
            assert data["balance"] == 500.0

    def test_get_transactions_empty(self):
        """Testa listagem de transações vazia"""
        with patch('main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            response = client.get("/api/transactions")
            assert response.status_code == 200
            assert response.json() == []

    def test_add_transaction_success(self):
        """Testa adição de transação com sucesso"""
        with patch('main.get_db_connection') as mock_db, \
             patch('main.invalidate_summary_cache') as mock_cache:
            
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = {'id': 1}
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            transaction_data = {
                "description": "Salário",
                "amount": 5000.00,
                "transaction_date": "2024-06-14"
            }
            
            response = client.post("/api/transactions", json=transaction_data)
            assert response.status_code == 201
            data = response.json()
            assert data["id"] == 1
            assert data["description"] == "Salário"
            assert data["amount"] == 5000.00

    def test_add_transaction_invalid_data(self):
        """Testa adição de transação com dados inválidos"""
        invalid_data = {
            "description": "",  # Descrição vazia
            "amount": "invalid",  # Valor inválido
            "transaction_date": "invalid-date"  # Data inválida
        }
        
        response = client.post("/api/transactions", json=invalid_data)
        assert response.status_code == 422  # Validation Error

    def test_delete_transaction_success(self):
        """Testa remoção de transação com sucesso"""
        with patch('main.get_db_connection') as mock_db, \
             patch('main.invalidate_summary_cache') as mock_cache:
            
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            response = client.delete("/api/transactions/1")
            assert response.status_code == 204

class TestFixedExpensesAPI:
    """Testes para endpoints de gastos fixos"""
    
    def test_get_fixed_expenses_empty(self):
        """Testa listagem de gastos fixos vazia"""
        with patch('main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            response = client.get("/api/fixed-expenses")
            assert response.status_code == 200
            assert response.json() == []

    def test_add_fixed_expense_success(self):
        """Testa adição de gasto fixo com sucesso"""
        with patch('main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = {'id': 1}
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            expense_data = {
                "description": "Internet",
                "amount": 100.00
            }
            
            response = client.post("/api/fixed-expenses", json=expense_data)
            assert response.status_code == 201
            data = response.json()
            assert data["id"] == 1
            assert data["description"] == "Internet"
            assert data["amount"] == 100.00

class TestCacheIntegration:
    """Testes para integração com Redis"""
    
    def test_cache_summary_hit(self):
        """Testa cache hit no resumo"""
        with patch('main.redis_client') as mock_redis:
            # Simula cache hit
            cached_data = '{"income": 1000, "expense": -500, "balance": 500}'
            mock_redis.get.return_value = cached_data
            
            response = client.get("/api/summary")
            assert response.status_code == 200
            data = response.json()
            assert data["balance"] == 500

    def test_cache_summary_miss(self):
        """Testa cache miss no resumo"""
        with patch('main.redis_client') as mock_redis, \
             patch('main.get_db_connection') as mock_db:
            
            # Simula cache miss
            mock_redis.get.return_value = None
            
            # Simula resposta do banco
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [{'amount': 1000.00}]
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            response = client.get("/api/summary")
            assert response.status_code == 200
            # Verifica se o cache foi populado
            mock_redis.set.assert_called_once()

class TestDatabaseIntegration:
    """Testes para integração com PostgreSQL"""
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Setup do banco de teste"""
        # Aqui você configuraria um banco de teste real
        # Por simplicidade, usaremos mocks
        pass

    def test_database_connection(self):
        """Testa conexão com o banco"""
        with patch('main.psycopg2.connect') as mock_connect:
            mock_connect.return_value = MagicMock()
            
            from main import get_db_connection
            conn = get_db_connection()
            assert conn is not None
            mock_connect.assert_called_once()

class TestOpenTelemetryInstrumentation:
    """Testes para instrumentação OpenTelemetry"""
    
    def test_traces_are_created(self):
        """Testa se traces são criados nas requisições"""
        with patch('main.transactions_created_counter') as mock_counter:
            transaction_data = {
                "description": "Test Trace",
                "amount": 100.00,
                "transaction_date": "2024-06-14"
            }
            
            with patch('main.get_db_connection') as mock_db:
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_cursor.fetchone.return_value = {'id': 1}
                mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
                mock_db.return_value = mock_conn
                
                response = client.post("/api/transactions", json=transaction_data)
                assert response.status_code == 201
                
                # Verifica se a métrica customizada foi incrementada
                mock_counter.add.assert_called_once_with(1)

class TestAPIDocumentation:
    """Testes para documentação da API"""
    
    def test_openapi_docs_available(self):
        """Testa se a documentação OpenAPI está disponível"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json_available(self):
        """Testa se o JSON da OpenAPI está disponível"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert openapi_spec["info"]["title"] == "Fintelli API - Finanças Inteligentes com IA"

if __name__ == "__main__":
    pytest.main([__file__])
