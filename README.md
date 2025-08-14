# Chatbot de Informações da Signa

Este projeto é um chatbot inteligente capaz de responder a dúvidas sobre a empresa Signa, seus produtos e serviços. Ele foi desenvolvido como parte de um desafio técnico para demonstrar a aplicação de soluções de Inteligência Artificial a um problema de negócio real.

A aplicação utiliza a técnica de **Retrieval-Augmented Augmented Generation (RAG)** para fornecer respostas precisas, baseando-se exclusivamente no conteúdo extraído do site oficial da empresa.

## Arquitetura do Projeto

A solução é dividida em três componentes principais:

1.  **Backend (FastAPI):** Uma API REST que gerencia a comunicação com o chatbot. Ela expõe endpoints para iniciar o scraping do site, verificar o status do processo e receber as perguntas do usuário.
2.  **RAG Pipeline:** A lógica de IA, implementada com a biblioteca LangChain, que processa a base de conhecimento. A pipeline faz a raspagem de dados, cria *embeddings* dos textos e usa um LLM (Large Language Model) para gerar respostas.
3.  **Frontend (HTML, CSS e JavaScript):** Uma interface web minimalista para interação com o usuário, que simula um chat.

A arquitetura completa da aplicação está encapsulada em um contêiner Docker para garantir a portabilidade e facilitar a execução.

## Tecnologias Utilizadas

* **Backend:** Python 3.11, FastAPI
* **Scraping e Geração de RAG:** LangChain, `requests`, `beautifulsoup4`, `langchain-openai`, `chromadb`
* **Interface:** HTML, CSS, JavaScript
* **Containerização:** Docker, Docker Compose

## Pré-requisitos

Para executar a aplicação, você só precisa ter o **Docker** e o **Docker Compose** instalados na sua máquina.

## Como Executar a Aplicação

Siga estes passos para ter a aplicação rodando em poucos minutos:

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/nicholastadeusantoss/signa_sage
    cd signa_sage
    ```

2.  **Configure a Chave da API da OpenAI:**
    * Crie um arquivo chamado `.env` na pasta raiz do projeto.
    * Adicione sua chave de API ao arquivo no seguinte formato:
        ```env
        OPENAI_API_KEY="sua_chave_da_api_aqui"
        ```

3.  **Construa e Execute o Contêiner Docker:**
    * No terminal, na pasta raiz do projeto, execute o comando:
        ```bash
        docker-compose up --build
        ```
    * Este comando irá construir a imagem Docker, instalar todas as dependências (Python e de sistema) e iniciar o servidor.

4.  **Acesse a Aplicação:**
    * Abra seu navegador e acesse a URL:
        `http://localhost:8000/static/index.html`

## Fluxo de Uso do Chatbot

1.  **Tela Inicial:** Ao acessar a página, o chat estará inativo e você verá uma mensagem informando que a base de conhecimento precisa ser atualizada.
2.  **Atualizar a Base de Conhecimento:**
    * Clique no botão **"Atualizar Base"** para iniciar o processo de scraping de forma autônoma.
    * Um indicador de progresso será exibido. O processo pode levar alguns minutos.
3.  **Chat Ativo:** Quando o scraping for concluído e o chatbot for inicializado, a interface do chat será liberada.
4.  **Interagir:** Você pode fazer perguntas sobre a Signa e seus produtos.
5. **Adicionando mais páginas na base de conhecimento:** Caso queira, você pode adicionar mais páginas na base de conhecimento, só é necessário colar o link no espaço onde diz "Insira um link para adicionar à base..." e esperar o Scraping.

## Testes da Aplicação

O projeto inclui testes unitários para a API e a lógica de scraping.

* Para executar os testes, abra um novo terminal na pasta raiz do projeto (enquanto o Docker estiver rodando) e use o seguinte comando:
    ```bash
    docker-compose exec chatbot_signa pytest
    ```