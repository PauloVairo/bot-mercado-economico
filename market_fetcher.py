import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ATENÇÃO: Para que a extração do Panoramas Laatus funcione, você precisará
# obter os cookies da sua sessão logada no navegador e inseri-los aqui.
# Isso não é trivial e pode ser contra os termos de serviço do site.
# Exemplo: {"sessionid": "SEU_SESSION_ID_AQUI", "csrftoken": "SEU_CSRF_TOKEN_AQUI"}
PANORAMA_LAATUS_COOKIES = {}

def extract_table_data_panoramas(soup, title_text):
    data = []
    title_div = soup.find("div", string=lambda text: text and title_text in text)
    if title_div:
        container_div = title_div.find_parent("div")
        if container_div:
            table = container_div.find("table")
            if table:
                for row in table.find_all("tr")[1:]: # Skip header row
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
        print(f"Erro ao acessar a página do Panoramas Laatus: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    
    extracted_data = {}
    extracted_data["Asia/Pacifico"] = extract_table_data_panoramas(soup, "Ásia/Pacífico")
    extracted_data["Europa"] = extract_table_data_panoramas(soup, "Europa")
    extracted_data["America"] = extract_table_data_panoramas(soup, "América")
    extracted_data["DXY"] = extract_table_data_panoramas(soup, "DXY")
    extracted_data["Metais"] = extract_table_data_panoramas(soup, "Metais")
    extracted_data["Energia"] = extract_table_data_panoramas(soup, "Energia")
    extracted_data["Futuros (CFDs)"] = extract_table_data_panoramas(soup, "Futuros (CFDs)")
    extracted_data["NASDAQ"] = extract_table_data_panoramas(soup, "NASDAQ")

    return extracted_data

def get_investing_futures_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # No Replit, o chromedriver geralmente está disponível no PATH
    # Se não estiver, você pode precisar especificar o caminho completo:
    # service = Service(executable_path="/usr/bin/chromedriver") 
    
    driver = webdriver.Chrome(options=chrome_options) # service=service se o caminho for especificado
    
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
                    row_data = {}
                    asset_name_element = cols[1].find("a") 
                    if asset_name_element:
                        row_data["Ativo"] = asset_name_element.get_text(strip=True)
                    else:
                        row_data["Ativo"] = cols[1].get_text(strip=True)

                    row_data["Mês"] = cols[2].get_text(strip=True) if len(cols) > 2 else "N/A"
                    row_data["Último"] = cols[3].get_text(strip=True) if len(cols) > 3 else "N/A"
                    row_data["Máxima"] = cols[4].get_text(strip=True) if len(cols) > 4 else "N/A"
                    row_data["Mínima"] = cols[5].get_text(strip=True) if len(cols) > 5 else "N/A"
                    row_data["Variação"] = cols[6].get_text(strip=True) if len(cols) > 6 else "N/A"
                    row_data["Var.%"] = cols[7].get_text(strip=True) if len(cols) > 7 else "N/A"
                    row_data["Hora"] = cols[8].get_text(strip=True) if len(cols) > 8 else "N/A"
                    
                    data.append(row_data)
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
        ("Europa", ["Euro Stoxx 50", "FTSE 100", "DAX", "CAC 40", "IBEX 35", "FTSE MIB"]),
        ("DXY", ["DXY"]),
        ("Metais", ["Min. Ferro"]),
        ("Energia", ["WTI", "Brent"]),
        ("Futuros (CFDs)", ["S&P500_F", "NASDAQ_F"])
    ]

    for section_title, desired_assets in sections_order:
        if section_title in data and data[section_title]:
            message += f"*-- {section_title} --*\n"
            for item in data[section_title]:
                if item["Ativo"] in desired_assets or not desired_assets: 
                    message += f"  {item['Ativo']}: {item['Último']} ({item['Var.%']})\n"
            message += "\n"
            
    return message

def format_investing_data_for_telegram(data):
    message = "📈 *Atualização de Futuros de Índices (Investing.com)* 📈\n\n"
    
    desired_assets = [
        "US 500", "US Tech 100", 
        "DAX", "CAC 40", "FTSE 100", "Euro Stoxx 50", "IBEX 35", 
        "Nikkei 225", "Hang Seng", "Shanghai", 
    ]

    for item in data:
        if item["Ativo"] in desired_assets:
            message += f"*{item['Ativo']}* ({item['Mês']})\n"
            message += f"  Último: {item['Último']} | Var.%: {item['Var.%']}\n"
            message += f"  Hora: {item['Hora']}\n\n"
            
    if not any(item["Ativo"] in desired_assets for item in data):
        message += "Nenhum dado relevante encontrado para os ativos solicitados nesta atualização.\n"

    return message

def coletar_todos_os_dados():
    dados = {
        "panoramas_laatus": None,
        "investing_futures": None
    }
    
    print("Buscando dados do Panoramas Laatus...")
    dados["panoramas_laatus"] = get_panoramalaatus_data(session_cookies=PANORAMA_LAATUS_COOKIES)
    
    print("Buscando dados de futuros de índices do Investing.com...")
    dados["investing_futures"] = get_investing_futures_data()
    
    return dados

def gerar_mensagem_mercado(dados):
    mensagem_final = ""
    if dados["panoramas_laatus"]:
        mensagem_final += format_panoramas_data_for_telegram(dados["panoramas_laatus"])
    else:
        mensagem_final += "⚠️ Erro ao buscar dados do Panoramas Laatus. Verifique os cookies da sessão.\n\n"
        
    if dados["investing_futures"]:
        mensagem_final += format_investing_data_for_telegram(dados["investing_futures"])
    else:
        mensagem_final += "⚠️ Erro ao buscar dados de futuros de índices do Investing.com.\n\n"
        
    return mensagem_final

if __name__ == "__main__":
    print("Testando coletar_todos_os_dados e gerar_mensagem_mercado...")
    dados_teste = coletar_todos_os_dados()
    mensagem_teste = gerar_mensagem_mercado(dados_teste)
    print(mensagem_teste)

