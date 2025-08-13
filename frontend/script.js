document.addEventListener('DOMContentLoaded', () => {
    const chatInterface = document.getElementById('chatbot-container');
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const scrapeBtn = document.getElementById('scrape-btn');
    const statusMessage = document.getElementById('status-message');
    const chatApiUrl = 'http://127.0.0.1:8000/chat';
    const scrapeApiUrl = 'http://127.0.0.1:8000/scrape';
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

    function setChatEnabled(enabled) {
        userInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        if (enabled) {
            userInput.value = '';
            scrapeBtn.textContent = "Re-atualizar Base";
        }
    }

    async function checkStatus() {
        try {
            const response = await fetch(statusApiUrl);
            const data = await response.json();
            
            if (data.scraping_in_progress) {
                const progress = data.progress;
                statusMessage.textContent = `Scraping em andamento: ${progress.pages_scraped} de ${progress.total_pages} páginas.`;
                scrapeBtn.disabled = true;
                setChatEnabled(false);
            } else if (data.chatbot_ready) {
                statusMessage.textContent = 'Base de conhecimento pronta. O chatbot está online.';
                setChatEnabled(true);
                scrapeBtn.disabled = false;
                if (statusInterval) {
                    clearInterval(statusInterval);
                    statusInterval = null;
                }
            } else {
                statusMessage.textContent = 'Base de conhecimento não encontrada. Clique no botão para iniciar.';
                setChatEnabled(false);
                scrapeBtn.disabled = false;
            }
        } catch (error) {
            console.error('Erro ao checar status:', error);
            statusMessage.textContent = 'Erro ao conectar com o servidor.';
            setChatEnabled(false);
            scrapeBtn.disabled = false;
        }
    }

    async function handleScrape() {
        statusMessage.textContent = "Iniciando o scraping...";
        scrapeBtn.disabled = true;

        try {
            const response = await fetch(scrapeApiUrl);
            const data = await response.json();
            statusMessage.textContent = data.message;
            
            // Inicia o polling para checar o status
            if (!statusInterval) {
                statusInterval = setInterval(checkStatus, 2000);
            }
        } catch (error) {
            console.error('Erro ao iniciar scraping:', error);
            statusMessage.textContent = "Erro ao iniciar scraping. Verifique o console.";
            scrapeBtn.disabled = false;
        }
    }

    async function sendMessage() {
        const question = userInput.value.trim();
        if (question === '') return;

        addMessage('user', question);
        userInput.value = '';

        try {
            const response = await fetch(chatApiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Erro de rede: ${response.status}`);
            }

            const data = await response.json();
            addMessage('bot', data.answer);
        } catch (error) {
            console.error('Erro ao se comunicar com o chatbot:', error);
            addMessage('bot', `Desculpe, ocorreu um erro: ${error.message}`);
        }
    }

    scrapeBtn.addEventListener('click', handleScrape);
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Checa o status inicial ao carregar a página
    checkStatus();
});