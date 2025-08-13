# app/chatbot.py
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader # Nova importação

class SignaChatbot:
    def __init__(self, api_key: str):
        docs = []
        # Percorre todos os arquivos TXT na pasta
        text_dir = "data/txt"
        if not os.path.exists(text_dir) or not os.listdir(text_dir):
            raise FileNotFoundError(f"Nenhum arquivo de texto encontrado no diretório: {text_dir}. Execute o scraping primeiro.")
        
        for filename in os.listdir(text_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(text_dir, filename)
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs.extend(loader.load())
                except Exception as e:
                    print(f"Erro ao carregar o TXT {filename}: {e}")
                    continue

        if not docs:
            raise ValueError("A lista de documentos está vazia. Nenhuma informação foi extraída dos arquivos de texto.")

        # Divide o texto em pedaços (chunks)
        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(docs)

        if not split_docs:
            raise ValueError("A lista de documentos dividida está vazia. Nenhum chunk de texto foi criado.")

        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.docsearch = Chroma.from_documents(split_docs, embeddings)

        self.llm = OpenAI(openai_api_key=api_key, temperature=0)
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.docsearch.as_retriever(),
            verbose=True
        )

    def ask(self, question: str):
        response = self.qa_chain.run(question)
        return response