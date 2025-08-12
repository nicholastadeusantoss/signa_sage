import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings  
from langchain_openai import OpenAI            
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader

class SignaChatbot:
    def __init__(self, api_key: str):
        docs = []
        # Percorre todos os arquivos PDF na pasta
        for filename in os.listdir("data/pdfs"):
            if filename.endswith(".pdf"):
                file_path = os.path.join("data/pdfs", filename)
                loader = PyMuPDFLoader(file_path)
                docs.extend(loader.load())

        # Divide o texto dos PDFs em pedaços (chunks)
        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(docs)

        # Cria os embeddings e o banco de dados vetorial
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.docsearch = Chroma.from_documents(split_docs, embeddings)

        # Inicializa o LLM e a cadeia RAG
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