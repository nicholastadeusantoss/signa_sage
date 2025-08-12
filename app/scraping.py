# app/scraping.py
import asyncio
import os
import re
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
from collections import deque

BASE_URL = "https://www.signa.pt/"
OUTPUT_DIR = "data/pdfs"

# Lista de URLs para acessar prioritariamente
PRIORITY_URLS = [
    "https://www.signa.pt/brindes/empresa.asp",
    "https://www.signa.pt/brindes/noticias.asp",
    "https://www.signa.pt/brindes/testemunhos.asp",
    "https://www.signa.pt/brindes/pedirOrcamento.asp",
    "https://www.signa.pt/brindes/contactos.asp"
]

async def is_internal_url(url, base_url):
    """Verifica se a URL pertence ao mesmo domínio."""
    return urlparse(url).netloc == urlparse(base_url).netloc

async def scrape_to_pdf(max_pages=50):
    """
    Agente de web scraping que navega pelo site e salva cada página como PDF.
    Começa com URLs de alta prioridade.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Inicializa a fila com as URLs prioritárias e a URL base
    urls_to_visit = deque(PRIORITY_URLS)
    if BASE_URL not in urls_to_visit:
        urls_to_visit.append(BASE_URL)
        
    visited_urls = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        while urls_to_visit and len(visited_urls) < max_pages:
            url = urls_to_visit.popleft()
            
            if url in visited_urls:
                continue
            
            visited_urls.add(url)
            print(f"Navegando para: {url}")

            try:
                await page.goto(url, wait_until="networkidle")
                
                # ... (lógica para limpar e nomear o arquivo PDF, que já está correta) ...
                file_name = url.replace(BASE_URL, "").replace("/", "_").replace(".html", "").replace(".asp", "")
                file_name = re.sub(r'[?&:=]', '_', file_name)
                file_name = file_name.replace('__', '_')
                
                if not file_name or file_name == '_':
                    file_name = "index"
                
                output_path = os.path.join(OUTPUT_DIR, f"{file_name}.pdf")
                
                await page.pdf(path=output_path)
                print(f"PDF salvo em: {output_path}")

                # Encontra novos links para navegar (mantido como antes)
                links = await page.eval_on_selector_all('a', '(links) => links.map(a => a.href)')
                for link in links:
                    absolute_url = urljoin(BASE_URL, link)
                    if await is_internal_url(absolute_url, BASE_URL) and absolute_url not in visited_urls:
                        urls_to_visit.append(absolute_url)

            except Exception as e:
                print(f"Erro ao processar {url}: {e}")
        
        await browser.close()
    
    print("Download de PDFs concluído.")

if __name__ == "__main__":
    asyncio.run(scrape_to_pdf())