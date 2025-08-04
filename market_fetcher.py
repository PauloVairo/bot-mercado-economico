import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ATENÇÃO: Para a Laatus, cookies podem ser necessários se houver proteção
PANORAMA_LAATUS_COOKIES = {}

def extract_table_data_panoramas(soup, title_text):
    data = []
    title_div = soup.find("div", string=lambda text: text and title_text in text)
    if title_div:
        container_div = title_div.find_parent("div")
        if container_div:
            table = container_div.find("table")
            if table:
                for row in table.find_all("tr")[1:]:
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
    }

    s = requests.Session()
    if session_cookies:
        s.cookies.update(session_cookies)

    try:
        response = s.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar Panoramas Laatus: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    extracted_data = {
        "Asia/Pacifico": extract_table_data_panoramas(soup, "Ásia/Pacífico"),
        "Europa": extract_table_data_panoramas(soup, "Europa"),
        "America": extract_table_data_panoramas(soup, "América"),
        "DXY": extract_table_data_panoramas(soup, "DXY"),
        "Metais": extract_table_data_panoramas(soup, "Metais"),
        "Energia": extract_table_data_panoramas(soup, "Energia"),
        "Futuros (CFDs)": extract_table_data_panoramas(soup, "Futuros (CFDs)"),
        "NASDAQ": extract_table_data_panoramas(soup, "NASDAQ")
    }

    return extracted_data

def get_investing_futures_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    url = "https://br.investing.com/indices/indices-futures"
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.genTbl.closedTbl.elpTbl"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        data = []
        table = soup.find("table", class_="genTbl closedTbl elpTbl")

        if table:
            for row in table.find("tbody").find_all("tr"):
                cols = row.find_all("td")
                if cols:
                    ativo = cols[1].get_text(strip=True)
                    data.append({
                        "Ativo": ativo,
                        "Mês": cols[2].get_text(strip=True),
                        "Último": cols[3].get_text(strip=True),
                        "Máxima": cols[4].get_text(strip=True),
                        "Mínima": cols[5].get_text(strip=True),
                        "Variação": cols[6].get_text(strip=True),
                        "Var.%": cols[7].get_text(strip=True),
                        "Hora": cols[8].get_text(strip=True)
                    })
        return data

    except Exception as e:
        print(f"Erro ao extrair dados do Investing.com: {e}")
        return None
    finally:
        driver.quit()

def format_panoramas_data_for_telegram(data):
    message = "📊 *Atualização do Mercado Panoramas Laatus* 📊\n\n"
    sections_order = [
        ("Asia/Pacifico", ["Shanghai", "Hang Seng", "Nikkei 225"]),
        ("Europa", ["Euro Stoxx 50", "FTSE 100", "DAX"]),
        ("DXY", ["DXY"]),
        ("Metais", ["Min. Ferro"]),
        ("Energia", ["WTI", "Brent"]),
        ("Futuros (CFDs)", ["S&P500_F", "NASDAQ_F"])
    ]

    for section_title, ativos_desejados in sections_order:
        if section_title in data and data[section_title]:
            message += f"*-- {section_title} --*\n"
            for item in data[section_title]:
                if item["Ativo"] in ativos_desejados:
                    message += f"{item['Ativo']}: {item['Último']} ({item['Var.%']})\n"
            message += "\n"

    return message

def format_investing_data_for_telegram(data):
    message = "📈 *Futuros de Índices (Investing)* 📈\n\n"
    ativos_desejados = [
        "US 500", "US Tech 100",
        "DAX", "CAC 40", "FTSE 100", "Euro Stoxx 50",
        "Nikkei 225", "Hang Seng", "Shanghai"
    ]

    for item in data:
        if item["Ativo"] in ativos_desejados:
            message += f"*{item['Ativo']}* ({item['Mês']})\n"
            message += f"Último: {item['Último']} | Var.%: {item['Var.%']}\nHora: {item['Hora']}\n\n"

    if not any(item["Ativo"] in ativos_desejados for item in data):
        message += "⚠️ Nenhum ativo relevante encontrado.\n"

    return message

def coletar_todos_os_dados():
    dados = {
        "panoramas_laatus": get_panoramalaatus_data(session_cookies=PANORAMA_LAATUS_COOKIES),
        "investing_futures": get_investing_futures_data()
    }
    return dados

def gerar_mensagem_mercado(dados):
    mensagem = ""
    if dados["panoramas_laatus"]:
        mensagem += format_panoramas_data_for_telegram(dados["panoramas_laatus"])
    else:
        mensagem += "⚠️ Erro ao obter dados do Panoramas Laatus.\n\n"

    if dados["investing_futures"]:
        mensagem += format_investing_data_for_telegram(dados["investing_futures"])
    else:
        mensagem += "⚠️ Erro ao obter dados do Investing.com.\n\n"

    return mensagem

# Para testes locais:
if __name__ == "__main__":
    print("🔍 Testando coleta e geração de mensagem do mercado...")
    dados = coletar_todos_os_dados()
    mensagem = gerar_mensagem_mercado(dados)
    print(mensagem)
