# app/main.py
from fastapi import FastAPI, HTTPException, Query, Request, Response
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from .chatbot import SignaChatbot
from .scraping import scrape_to_text, scrape_single_page_to_text


signa_chatbot = None
chatbot_ready = False
scraping_in_progress = False
scraping_progress = {"pages_scraped": 0, "total_pages": 50}
executor = ThreadPoolExecutor(max_workers=1)

def initialize_chatbot():
    global signa_chatbot, chatbot_ready
    print("Tentando inicializar o chatbot...")
    try:
        signa_chatbot = SignaChatbot(api_key=OPENAI_API_KEY)
        chatbot_ready = True
        print("Chatbot inicializado com sucesso!")
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        print("A base de conhecimento não foi encontrada. O chatbot permanecerá offline.")
        signa_chatbot = None
        chatbot_ready = False
    except Exception as e:
        print(f"Erro inesperado ao inicializar o chatbot: {e}")
        signa_chatbot = None
        chatbot_ready = False

# Carrega as variáveis do .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Verifique seu arquivo .env.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_chatbot()
    yield
    if executor:
        executor.shutdown(wait=True)

app = FastAPI(
    title="Signa Chatbot",
    description="API para o chatbot da empresa Signa.",
    version="1.0.0",
    lifespan=lifespan 
)

# Adiciona o middleware de CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent.parent

frontend_path = str(BASE_DIR / "frontend")

app.mount("/static", StaticFiles(directory=frontend_path), name="static")

class Question(BaseModel):
    question: str

class UrlPayload(BaseModel):
    url: str

def run_scraping_full_in_thread(max_pages_to_scrape):
    global scraping_in_progress
    try:
        scrape_to_text(max_pages=max_pages_to_scrape, progress_tracker=scraping_progress)
        initialize_chatbot()
    except Exception as e:
        print(f"Erro ao executar a tarefa de scraping: {e}")
    finally:
        scraping_in_progress = False

def run_single_scraping_in_thread(url):
    global scraping_in_progress
    try:
        scrape_single_page_to_text(url, progress_tracker=scraping_progress)
        initialize_chatbot()
    except Exception as e:
        print(f"Erro ao executar a tarefa de scraping de URL: {e}")
    finally:
        scraping_in_progress = False

@app.get("/scrape")
def start_full_scrape(max_pages: int = Query(15)):
    global scraping_in_progress, chatbot_ready, scraping_progress
    if scraping_in_progress:
        raise HTTPException(status_code=409, detail="Scraping já está em andamento.")
    
    scraping_progress = {"pages_scraped": 0, "total_pages": max_pages} 
    scraping_in_progress = True
    chatbot_ready = False
    
    executor.submit(run_scraping_full_in_thread, max_pages)
    
    return {"status": "success", "message": "Scraping iniciado. O chatbot estará disponível em breve."}

@app.post("/scrape_url")
def start_single_scrape(payload: UrlPayload):
    global scraping_in_progress, chatbot_ready, scraping_progress
    if scraping_in_progress:
        raise HTTPException(status_code=409, detail="Scraping já está em andamento.")

    url = payload.url
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"

    scraping_progress = {"pages_scraped": 0, "total_pages": 1}
    scraping_in_progress = True
    chatbot_ready = False
    
    executor.submit(run_single_scraping_in_thread, url)
    
    return {"status": "success", "message": f"Scraping da página {url} iniciado. O chatbot será atualizado."}

@app.get("/status")
def get_status():
    global scraping_in_progress, chatbot_ready, scraping_progress
    return {
        "scraping_in_progress": scraping_in_progress,
        "chatbot_ready": chatbot_ready,
        "progress": scraping_progress
    }

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Chatbot da Signa. Use a URL /static/index.html para acessar a interface."}

@app.post("/chat")
def chat_with_bot(question: Question):
    if not chatbot_ready:
        raise HTTPException(status_code=503, detail="O chatbot ainda não está disponível.")
    
    try:
        response = signa_chatbot.ask(question.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))