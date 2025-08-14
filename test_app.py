import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.scraping import scrape_to_text

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_data_folder():
    if os.path.exists("data/txt"):
        for file in os.listdir("data/txt"):
            os.remove(os.path.join("data/txt", file))
    yield
    if os.path.exists("data/txt"):
        for file in os.listdir("data/txt"):
            os.remove(os.path.join("data/txt", file))

def test_status_endpoint_not_ready():
    """Testa se o endpoint de status retorna que o chatbot não está pronto."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["chatbot_ready"] is False
    assert "progress" in data
    assert data["scraping_in_progress"] is False

def test_scrape_to_text_creates_files():
    """
    Testa se a função de scraping cria arquivos corretamente.
    """
 
    max_pages_to_test = 2
    

    scrape_to_text(max_pages=max_pages_to_test)
    

    assert os.path.exists("data/txt")
    assert len(os.listdir("data/txt")) == max_pages_to_test

def test_scrape_to_text_with_zero_pages():
    """
    Testa se a função de scraping não cria arquivos quando o max_pages é 0.
    """
    max_pages_to_test = 0
    
    scrape_to_text(max_pages=max_pages_to_test)
    
    if os.path.exists("data/txt"):
        assert len(os.listdir("data/txt")) == 0