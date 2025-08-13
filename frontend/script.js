document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const scrapeBtn = document.getElementById('scrape-btn');
    const addUrlBtn = document.getElementById('add-url-btn');
    const newUrlInput = document.getElementById('new-url-input');
    const statusMessage = document.getElementById('status-message');
    const chatApiUrl = 'http://127.0.0.1:8000/chat';
    const scrapeApiUrl = 'http://127.0.0.1:8000/scrape';
    const scrapeUrlApiUrl = 'http://127.0.0.1:8000/scrape_url';
    const statusApiUrl = 'http://127.0.0.1:8000/status';

    let chatbotReady = false;
    let statusInterval = null;

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = text;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function setUIState(isReady, isScraping) {
        // Estado de scraping
        if (isScraping) {
            scrapeBtn.disabled = true;
            addUrlBtn.disabled = true;
            userInput.disabled = true;
            sendBtn.disabled = true;
            scrapeBtn.classList.add('disabled-btn');
            addUrlBtn.classList.add('disabled-btn');
        } 
        // Estado pronto
        else if (isReady) {
            scrapeBtn.disabled = false;
            addUrlBtn.disabled = false;
            userInput.disabled = false;
            sendBtn.disabled = false;
            scrapeBtn.classList.remove('disabled-btn');
            addUrlBtn.classList.remove('disabled-btn');
            scrapeBtn.textContent = "Re-atualizar Base";
            addMessage('bot', 'Olá! Sou o assistente virtual da Signa. Como posso ajudar?');
        } 
        // Estado offline
        else {
            scrapeBtn.disabled = false;
            addUrlBtn.disabled = false;
            userInput.disabled = true;
            sendBtn.disabled = true;
            scrapeBtn.classList.remove('disabled-btn');
            addUrlBtn.classList.remove('disabled-btn');
            scrapeBtn.textContent = "Atualizar Base";
        }
    }

    async function checkStatus() {
        try {
            const response = await fetch(statusApiUrl);
            const data = await response.json();
            chatbotReady = data.chatbot_ready;
            
            setUIState(data.chatbot_ready, data.scraping_in_progress);

            if (data.scraping_in_progress) {
                const progress = data.progress;
                statusMessage.textContent = `Scraping em andamento: ${progress.pages_scraped} de ${progress.total_pages} páginas.`;
            } else if (data.chatbot_ready) {
                statusMessage.textContent = 'Base de conhecimento pronta. O chatbot está online.';
                if (statusInterval) {
                    clearInterval(statusInterval);
                    statusInterval = null;
                }
            } else {
                statusMessage.textContent = 'Base de conhecimento não encontrada. Clique em "Atualizar Base".';
            }
        } catch (error) {
            console.error('Erro ao checar status:', error);
            statusMessage.textContent = 'Erro ao conectar com o servidor.';
            setUIState(false, false);
        }
    }
    
    async function startScraping(url = null) {
        statusMessage.textContent = "Iniciando o scraping...";
        setUIState(false, true);

        try {
            const endpoint = url ? scrapeUrlApiUrl : scrapeApiUrl;
            const options = url ? { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ url: url }) } : { method: 'GET' };
            
            const response = await fetch(endpoint, options);
            const data = await response.json();
            
            statusMessage.textContent = data.message;
            if (!statusInterval) {
                statusInterval = setInterval(checkStatus, 2000);
            }
        } catch (error) {
            console.error('Erro ao iniciar scraping:', error);
            statusMessage.textContent = "Erro ao iniciar scraping. Verifique o console.";
            setUIState(false, false);
        }
    }

    scrapeBtn.addEventListener('click', () => startScraping());

    addUrlBtn.addEventListener('click', () => {
        const url = newUrlInput.value.trim();
        if (url) {
            startScraping(url);
            newUrlInput.value = '';
        } else {
            alert("Por favor, insira um link válido.");
        }
    });

    sendBtn.addEventListener('click', async () => {
        const question = userInput.value.trim();
        if (question === '') return;

        addMessage('user', question);
        userInput.value = '';

        if (!chatbotReady) {
            addMessage('bot', 'Desculpe, o chatbot ainda não está disponível.');
            return;
        }

        try {
            const response = await fetch(chatApiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });
            const data = await response.json();
            addMessage('bot', data.answer);
        } catch (error) {
            console.error('Erro ao se comunicar com o chatbot:', error);
            addMessage('bot', `Desculpe, ocorreu um erro: ${error.message}`);
        }
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    checkStatus();
});