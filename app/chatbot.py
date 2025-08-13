# app/chatbot.py
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from pathlib import Path

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
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=1000,
            chunk_overlap=100,
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
            retriever=self.docsearch.as_retriever(search_kwargs={"k": 2}),
            verbose=True
        )

    def ask(self, question: str):
        response = self.qa_chain.invoke({'query': question})
        return response['result']