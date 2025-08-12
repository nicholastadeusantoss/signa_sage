# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from .chatbot import SignaChatbot

# Carrega as variáveis do .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Verifique seu arquivo .env.")

# Inicializa o chatbot. Isso pode levar um tempo, pois ele processa todo o conteúdo.
print("Inicializando o chatbot. Isso pode levar alguns minutos...")
try:
    signa_chatbot = SignaChatbot(api_key=OPENAI_API_KEY)
except FileNotFoundError:
    print("O arquivo 'signa_content.json' não foi encontrado. Por favor, execute o scraper.")
    # Adicione uma lógica aqui para executar o scraper se quiser
    signa_chatbot = None # Ou levante um erro para interromper a execução
except Exception as e:
    print(f"Erro ao inicializar o chatbot: {e}")
    signa_chatbot = None

app = FastAPI(
    title="Signa Chatbot",
    description="API para o chatbot da empresa Signa.",
    version="1.0.0"
)

class Question(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Chatbot da Signa. Use o endpoint /chat para interagir."}

@app.post("/chat")
def chat_with_bot(question: Question):
    """
    Endpoint para enviar uma pergunta ao chatbot.
    """
    if signa_chatbot is None:
        raise HTTPException(status_code=500, detail="O chatbot não foi inicializado corretamente.")
    
    try:
        response = signa_chatbot.ask(question.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))