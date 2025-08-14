# Use uma imagem base Python leve e estável
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala as dependências de sistema essenciais (sem o GTK3)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    shared-mime-info

# Copia o arquivo de requisitos e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da sua aplicação para o contêiner
COPY . .

# Expõe a porta que o Uvicorn irá rodar
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]