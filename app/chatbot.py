# app/chatbot.py
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter # Mudamos para essa classe
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from pathlib import Path

# Adiciona um prompt de segurança e anti-alucinação
PROMPT_TEMPLATE = """
Você é um chatbot da empresa Signa. Sua principal tarefa é responder a perguntas sobre a empresa, seus produtos e serviços, com base nas informações fornecidas no contexto abaixo.

Diretrizes de Segurança e Privacidade:
- Responda apenas com base no CONTEXTO fornecido. Não use conhecimento externo.
- Se a resposta para a pergunta não estiver no CONTEXTO, diga "Não tenho informações sobre isso no momento.".
- Não responda a perguntas sobre informações pessoais, dados de clientes ou qualquer conteúdo sensível (LGPD).
- Recuse responder a perguntas sobre tópicos que possam ser perigosos, ilegais, antiéticos ou que promovam ódio.

CONTEXTO: {context}

PERGUNTA DO USUÁRIO: {question}

Sua resposta:
"""
PROMPT = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])

class SignaChatbot:
    def __init__(self, api_key: str):
        base_dir = Path(__file__).parent.parent
        text_dir = base_dir / "data" / "txt"
        
        docs = []

        if not text_dir.exists() or not any(text_dir.iterdir()):
            raise FileNotFoundError(f"Nenhum arquivo de texto encontrado no diretório: {text_dir}. Execute o scraping primeiro.")
        
        for file_path in text_dir.iterdir():
            if file_path.suffix == ".txt":
                try:
                    loader = TextLoader(str(file_path), encoding='utf-8')
                    docs.extend(loader.load())
                except Exception as e:
                    print(f"Erro ao carregar o TXT {file_path.name}: {e}")
                    continue

        if not docs:
            raise ValueError("A lista de documentos está vazia. Nenhuma informação foi extraída dos arquivos de texto.")

        # AVISO: AVISO: AVISO: Esta parte foi ajustada!
        # Usando um separador mais inteligente para evitar chunks muito grandes
        text_splitter = RecursiveCharacterTextSplitter(
            separators=[".", "?", "!", "\n\n"],
            chunk_size=750,
            chunk_overlap=75,
            length_function=len
        )
        split_docs = text_splitter.split_documents(docs)

        if not split_docs:
            raise ValueError("A lista de documentos dividida está vazia. Nenhum chunk de texto foi criado.")

        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.docsearch = Chroma.from_documents(split_docs, embeddings)

        self.llm = OpenAI(openai_api_key=api_key, temperature=0)
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.docsearch.as_retriever(search_kwargs={"k": 1}),
            verbose=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

    def ask(self, question: str):
        response = self.qa_chain.invoke({'query': question})
        return response['result']