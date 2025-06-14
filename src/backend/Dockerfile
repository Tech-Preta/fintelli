# Usa uma imagem oficial do Python.
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner.
WORKDIR /app

# Copia o arquivo de dependências e instala.
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o diretório de trabalho.
COPY ./app /app

# Expõe a porta que a aplicação irá rodar.
EXPOSE 8000

# O comando para rodar a aplicação (será sobrescrito pelo docker-compose para desenvolvimento).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
