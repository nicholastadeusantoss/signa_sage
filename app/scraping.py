# app/scraping.py
import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
from collections import deque

BASE_URL = "https://www.signa.pt/"
OUTPUT_DIR = "data/txt"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
PRIORITY_URLS = [
    "https://www.signa.pt/brindes/empresa.asp",
    "https://www.signa.pt/brindes/noticias.asp",
    "https://www.signa.pt/brindes/testemunhos.asp",
    "https://www.signa.pt/brindes/pedirOrcamento.asp",
    "https://www.signa.pt/brindes/contactos.asp"
]

def is_internal_url(url, base_url):
    return urlparse(url).netloc == urlparse(base_url).netloc

def scrape_to_text(max_pages=15, progress_tracker=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    urls_to_visit = deque(PRIORITY_URLS)
    if BASE_URL not in urls_to_visit:
        urls_to_visit.append(BASE_URL)
    visited_urls = set()
    pages_scraped = 0

    while urls_to_visit and pages_scraped < max_pages:
        url = urls_to_visit.popleft()
        if url in visited_urls:
            continue
        visited_urls.add(url)
        pages_scraped += 1
        print(f"Navegando para: {url} ({pages_scraped}/{max_pages})")
        
        if progress_tracker:
            progress_tracker["pages_scraped"] = pages_scraped
            progress_tracker["total_pages"] = max_pages
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            for script_or_style in soup(['script', 'style', 'nav', 'footer', 'form', 'header']):
                script_or_style.decompose()

            text = soup.get_text(separator=' ', strip=True)
            
            sanitized_name = re.sub(r'[\s\?&:=/#!]', '_', url.replace(BASE_URL, "")).replace('__', '_').strip('_')
            if not sanitized_name:
                sanitized_name = "index"
            
            file_name = f"{sanitized_name}.txt"
            output_path = os.path.join(OUTPUT_DIR, file_name)

            with open(output_path, "w", encoding="utf-8") as text_file:
                text_file.write(text)
            
            print(f"Texto salvo em: {output_path}")

            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(BASE_URL, link.get('href'))
                if is_internal_url(absolute_url, BASE_URL) and absolute_url not in visited_urls:
                    urls_to_visit.append(absolute_url)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            
    print("Download de textos concluído.")

def scrape_single_page_to_text(url, progress_tracker=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if progress_tracker:
        progress_tracker["pages_scraped"] = 0
        progress_tracker["total_pages"] = 1
        
    print(f"Raspando URL única: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        for script_or_style in soup(['script', 'style', 'nav', 'footer', 'form', 'header']):
            script_or_style.decompose()

        text = soup.get_text(separator=' ', strip=True)
        
        sanitized_name = re.sub(r'[\s\?&:=/#!]', '_', url.replace(BASE_URL, "")).replace('__', '_').strip('_')
        # Adiciona um timestamp para evitar colisão de nomes
        if not sanitized_name:
            import time
            sanitized_name = f"single_page_{int(time.time())}"
        
        file_name = f"{sanitized_name}.txt"
        output_path = os.path.join(OUTPUT_DIR, file_name)

        with open(output_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)
        
        print(f"Texto salvo em: {output_path}")

        if progress_tracker:
            progress_tracker["pages_scraped"] = 1
            progress_tracker["total_pages"] = 1
            
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")