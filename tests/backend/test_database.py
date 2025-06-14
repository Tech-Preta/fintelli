"""
Testes específicos para validação do PostgreSQL
"""
import pytest
import psycopg2
import psycopg2.extras
from unittest.mock import patch
import os

class TestPostgreSQLValidation:
    """Testes para validação do PostgreSQL"""
    
    @pytest.fixture
    def db_config(self):
        """Configuração de conexão com o banco"""
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'finance_db'),
            'user': os.getenv('POSTGRES_USER', 'finance_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password')
        }
    
    def test_database_connection(self, db_config):
        """Testa se é possível conectar ao banco de dados"""
        try:
            conn = psycopg2.connect(**db_config)
            assert conn is not None
            conn.close()
        except psycopg2.Error as e:
            pytest.fail(f"Falha na conexão com o banco: {e}")
    
    def test_tables_exist(self, db_config):
        """Verifica se as tabelas necessárias existem"""
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Verifica se a tabela transactions existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'transactions'
            );
        """)
        
        result = cursor.fetchone()
        assert result['exists'] == True, "Tabela 'transactions' não encontrada"
        
        cursor.close()
        conn.close()
    
    def test_insert_and_retrieve_transaction(self, db_config):
        """Testa inserção e recuperação de dados"""
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Cria tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                type VARCHAR(20) NOT NULL,
                description TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insere dados de teste
        test_data = {
            'type': 'income',
            'description': 'Teste de receita',
            'amount': 1000.00,
            'date': '2024-01-15'
        }
        
        cursor.execute("""
            INSERT INTO transactions (type, description, amount, date)
            VALUES (%(type)s, %(description)s, %(amount)s, %(date)s)
            RETURNING id;
        """, test_data)
        
        transaction_id = cursor.fetchone()['id']
        assert transaction_id is not None
        
        # Recupera o dado inserido
        cursor.execute("""
            SELECT * FROM transactions WHERE id = %s;
        """, (transaction_id,))
        
        result = cursor.fetchone()
        assert result['type'] == test_data['type']
        assert result['description'] == test_data['description']
        assert float(result['amount']) == test_data['amount']
        
        # Limpa dados de teste
        cursor.execute("DELETE FROM transactions WHERE id = %s;", (transaction_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def test_database_constraints(self, db_config):
        """Testa constraints e validações do banco"""
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Tenta inserir dados inválidos (amount com valor muito grande)
        with pytest.raises(psycopg2.Error):
            cursor.execute("""
                INSERT INTO transactions (type, description, amount, date)
                VALUES ('income', 'Teste inválido', 99999999999999.99, '2024-01-15');
            """)
        
        conn.rollback()
        cursor.close()
        conn.close()

class TestDatabasePerformance:
    """Testes de performance do banco de dados"""
    
    def test_query_performance(self, db_config):
        """Testa performance de consultas"""
        import time
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM transactions;")
        cursor.fetchone()
        end_time = time.time()
        
        query_time = end_time - start_time
        assert query_time < 1.0, f"Consulta muito lenta: {query_time}s"
        
        cursor.close()
        conn.close()
