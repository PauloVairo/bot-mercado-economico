import requests
from bs4 import BeautifulSoup

# ATENÇÃO: Se necessário, adicione cookies válidos da sua sessão no site Panoramas Laatus
PANORAMA_LAATUS_COOKIES = {}

def extract_table_data_panoramas(soup, title_text):
    data = []
    title_div = soup.find("div", string=lambda text: text and title_text in text)
    if title_div:
        container_div = title_div.find_parent("div")
        if container_div:
            table = container_div.find("table")
            if table:
                for row in table.find_all("tr")[1:]:  # Pular o cabeçalho
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        ativo = cols[0].get_text(strip=True)
                        ultimo = cols[1].get_text(strip=True)
                        variacao = cols[2].get_text(strip=True)
                        data.append({"Ativo": ativo, "Último": ultimo, "Var.%": variacao})
    return data

def get_panoramalaatus_data(session_cookies=None):
    url = "https://panoramalaatus.com.br/"
    headers = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"



