import os
import json
import time
import psycopg2
import psycopg2.extras
import redis
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Importa a configuração de instrumentação e métricas customizadas
from instrumentation import (
    setup_opentelemetry, tracer,
    transactions_created_counter, transactions_deleted_counter, 
    api_requests_counter, transaction_amount_histogram,
    database_query_duration, active_connections_gauge
)

load_dotenv()

# --- Configurações e Conexões ---
app = FastAPI(title="Fintelli API - Finanças Inteligentes com IA")

setup_opentelemetry(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
redis_client = redis.Redis(host='cache', port=6379, db=0, decode_responses=True)
def get_db_connection():
    with tracer.start_as_current_span("database.connect") as span:
        active_connections_gauge.add(1)
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.name", os.getenv("POSTGRES_DB"))
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host="db"
            )
            span.set_attribute("db.connection.status", "success")
            return conn
        except Exception as e:
            span.set_attribute("db.connection.status", "error")
            span.record_exception(e)
            active_connections_gauge.add(-1)
            raise
@app.on_event("startup")
def on_startup():
    # Cria as tabelas no DB se não existirem
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, description VARCHAR(255) NOT NULL, amount NUMERIC(10, 2) NOT NULL, transaction_date DATE NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS fixed_expenses (id SERIAL PRIMARY KEY, description VARCHAR(255) NOT NULL, amount NUMERIC(10, 2) NOT NULL);")
    conn.commit()
    cur.close()
    conn.close()
    print("Banco de dados verificado.")

# --- Modelos Pydantic ---
class Transaction(BaseModel):
    id: Optional[int] = None
    description: str
    amount: float
    transaction_date: str
class FixedExpense(BaseModel):
    id: Optional[int] = None
    description: str
    amount: float

# --- Funções de Cache ---
def invalidate_summary_cache():
    with tracer.start_as_current_span("cache.invalidate") as span:
        span.set_attribute("cache.key", "financial_summary")
        redis_client.delete("financial_summary")
        span.set_attribute("cache.operation", "delete")

# --- Rotas da API ---

@app.get("/api/summary")
def get_summary():
    with tracer.start_as_current_span("api.get_summary") as span:
        api_requests_counter.add(1, {"endpoint": "/api/summary", "method": "GET"})
        
        # Tenta buscar no cache
        with tracer.start_as_current_span("cache.get") as cache_span:
            cache_span.set_attribute("cache.key", "financial_summary")
            cached_summary = redis_client.get("financial_summary")
            if cached_summary:
                cache_span.set_attribute("cache.hit", True)
                span.set_attribute("summary.source", "cache")
                return json.loads(cached_summary)
            cache_span.set_attribute("cache.hit", False)
        
        # Busca no banco de dados
        span.set_attribute("summary.source", "database")
        start_time = time.time()
        
        with tracer.start_as_current_span("database.query.summary") as db_span:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "transactions")
            
            cur.execute("SELECT amount FROM transactions")
            transactions = cur.fetchall()
            cur.close()
            conn.close()
            active_connections_gauge.add(-1)
            
            query_duration = time.time() - start_time
            database_query_duration.record(query_duration, {"operation": "get_summary"})
            db_span.set_attribute("db.rows_returned", len(transactions))
        
        # Calcula resumo
        with tracer.start_as_current_span("business.calculate_summary") as calc_span:
            income = sum(float(row['amount']) for row in transactions if row['amount'] > 0)
            expense = sum(float(row['amount']) for row in transactions if row['amount'] < 0)
            summary = {"income": income, "expense": expense, "balance": income + expense}
            
            calc_span.set_attribute("summary.income", income)
            calc_span.set_attribute("summary.expense", expense)
            calc_span.set_attribute("summary.balance", income + expense)
            calc_span.set_attribute("summary.transactions_count", len(transactions))
        
        # Salva no cache
        with tracer.start_as_current_span("cache.set") as cache_span:
            cache_span.set_attribute("cache.key", "financial_summary")
            cache_span.set_attribute("cache.ttl", 3600)
            redis_client.set("financial_summary", json.dumps(summary), ex=3600)
        
        return summary

@app.get("/api/transactions", response_model=List[Transaction])
def get_transactions():
    with tracer.start_as_current_span("api.get_transactions") as span:
        api_requests_counter.add(1, {"endpoint": "/api/transactions", "method": "GET"})
        
        start_time = time.time()
        
        with tracer.start_as_current_span("database.query.transactions") as db_span:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "transactions")
            
            cur.execute("SELECT id, description, amount, to_char(transaction_date, 'YYYY-MM-DD') as transaction_date FROM transactions ORDER BY transaction_date DESC, id DESC")
            transactions = cur.fetchall()
            cur.close()
            conn.close()
            active_connections_gauge.add(-1)
            
            query_duration = time.time() - start_time
            database_query_duration.record(query_duration, {"operation": "get_transactions"})
            db_span.set_attribute("db.rows_returned", len(transactions))
            span.set_attribute("transactions.count", len(transactions))
        
        return [dict(row) for row in transactions]

@app.post("/api/transactions", response_model=Transaction, status_code=201)
def add_transaction(transaction: Transaction):
    with tracer.start_as_current_span("api.add_transaction") as span:
        api_requests_counter.add(1, {"endpoint": "/api/transactions", "method": "POST"})
        span.set_attribute("transaction.description", transaction.description)
        span.set_attribute("transaction.amount", transaction.amount)
        span.set_attribute("transaction.date", transaction.transaction_date)
        
        # Registra métricas do valor da transação
        transaction_amount_histogram.record(
            abs(transaction.amount), 
            {"type": "income" if transaction.amount > 0 else "expense"}
        )
        
        start_time = time.time()
        
        with tracer.start_as_current_span("database.insert.transaction") as db_span:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            db_span.set_attribute("db.operation", "INSERT")
            db_span.set_attribute("db.table", "transactions")
            
            cur.execute(
                "INSERT INTO transactions (description, amount, transaction_date) VALUES (%s, %s, %s) RETURNING id", 
                (transaction.description, transaction.amount, transaction.transaction_date)
            )
            new_id = cur.fetchone()['id']
            conn.commit()
            cur.close()
            conn.close()
            active_connections_gauge.add(-1)
            
            query_duration = time.time() - start_time
            database_query_duration.record(query_duration, {"operation": "insert_transaction"})
            db_span.set_attribute("db.new_id", new_id)
        
        # Invalida cache
        invalidate_summary_cache()
        transaction.id = new_id
        
        # Incrementa a métrica customizada
        transactions_created_counter.add(1, {
            "type": "income" if transaction.amount > 0 else "expense"
        })
        
        span.set_attribute("transaction.id", new_id)
        span.set_attribute("operation.success", True)
        
        return transaction

@app.delete("/api/transactions/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int):
    with tracer.start_as_current_span("api.delete_transaction") as span:
        api_requests_counter.add(1, {"endpoint": "/api/transactions", "method": "DELETE"})
        span.set_attribute("transaction.id", transaction_id)
        
        start_time = time.time()
        
        with tracer.start_as_current_span("database.delete.transaction") as db_span:
            conn = get_db_connection()
            cur = conn.cursor()
            db_span.set_attribute("db.operation", "DELETE")
            db_span.set_attribute("db.table", "transactions")
            db_span.set_attribute("transaction.id", transaction_id)
            
            cur.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
            rows_affected = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            active_connections_gauge.add(-1)
            
            query_duration = time.time() - start_time
            database_query_duration.record(query_duration, {"operation": "delete_transaction"})
            db_span.set_attribute("db.rows_affected", rows_affected)
            span.set_attribute("operation.rows_affected", rows_affected)
        
        # Invalida cache e registra métrica
        invalidate_summary_cache()
        transactions_deleted_counter.add(1)
        
        span.set_attribute("operation.success", True)
        return {}

@app.get("/api/fixed-expenses", response_model=List[FixedExpense])
def get_fixed_expenses():
    with tracer.start_as_current_span("api.get_fixed_expenses") as span:
        api_requests_counter.add(1, {"endpoint": "/api/fixed-expenses", "method": "GET"})
        
        start_time = time.time()
        
        with tracer.start_as_current_span("database.query.fixed_expenses") as db_span:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "fixed_expenses")
            
            cur.execute("SELECT * FROM fixed_expenses ORDER BY description")
            fixed_expenses = cur.fetchall()
            cur.close()
            conn.close()
            active_connections_gauge.add(-1)
            
            query_duration = time.time() - start_time
            database_query_duration.record(query_duration, {"operation": "get_fixed_expenses"})
            db_span.set_attribute("db.rows_returned", len(fixed_expenses))
            span.set_attribute("fixed_expenses.count", len(fixed_expenses))
        
        return [dict(row) for row in fixed_expenses]

@app.post("/api/fixed-expenses", response_model=FixedExpense, status_code=201)
def add_fixed_expense(expense: FixedExpense):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("INSERT INTO fixed_expenses (description, amount) VALUES (%s, %s) RETURNING id", (expense.description, expense.amount))
    new_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    expense.id = new_id
    return expense

@app.delete("/api/fixed-expenses/{expense_id}", status_code=204)
def delete_fixed_expense(expense_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM fixed_expenses WHERE id = %s", (expense_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {}

@app.post("/api/analyze-invoice")
async def analyze_invoice(file: UploadFile = File(...)):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Chave da API do Gemini não configurada.")
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        pdf_content = await file.read()
        prompt = "Analise o texto da fatura... (prompt completo omitido por brevidade)"
        response = model.generate_content([prompt, {"mime_type": "application/pdf", "data": pdf_content}])
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar o PDF: {e}")
