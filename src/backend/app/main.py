import os
import json
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
from instrumentation import setup_opentelemetry, transactions_created_counter

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
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host="db"
    )
    return conn
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
    redis_client.delete("financial_summary")

# --- Rotas da API ---

@app.get("/api/summary")
def get_summary():
    cached_summary = redis_client.get("financial_summary")
    if cached_summary: return json.loads(cached_summary)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT amount FROM transactions")
    transactions = cur.fetchall()
    cur.close()
    conn.close()
    income = sum(float(row['amount']) for row in transactions if row['amount'] > 0)
    expense = sum(float(row['amount']) for row in transactions if row['amount'] < 0)
    summary = {"income": income, "expense": expense, "balance": income + expense}
    redis_client.set("financial_summary", json.dumps(summary), ex=3600)
    return summary

@app.get("/api/transactions", response_model=List[Transaction])
def get_transactions():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, description, amount, to_char(transaction_date, 'YYYY-MM-DD') as transaction_date FROM transactions ORDER BY transaction_date DESC, id DESC")
    transactions = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in transactions]

@app.post("/api/transactions", response_model=Transaction, status_code=201)
def add_transaction(transaction: Transaction):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("INSERT INTO transactions (description, amount, transaction_date) VALUES (%s, %s, %s) RETURNING id", (transaction.description, transaction.amount, transaction.transaction_date))
    new_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    invalidate_summary_cache()
    transaction.id = new_id
    
    # Incrementa a métrica customizada
    transactions_created_counter.add(1)
    
    return transaction

@app.delete("/api/transactions/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
    conn.commit()
    cur.close()
    conn.close()
    invalidate_summary_cache()
    return {}

@app.get("/api/fixed-expenses", response_model=List[FixedExpense])
def get_fixed_expenses():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM fixed_expenses ORDER BY description")
    fixed_expenses = cur.fetchall()
    cur.close()
    conn.close()
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
