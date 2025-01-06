from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import pandas as pd
import os
import re
import time


def diretorio_projeto(nome_projeto="ProjetoInvestimento"):
    """
    Busca recursivamente o diretório base do projeto, partindo do arquivo atual.

    :param nome_projeto: Nome da pasta do projeto (padrão: 'ProjetoInvestimento').
    :return: Caminho absoluto para a pasta do projeto.
    """
    caminho_atual = os.path.abspath(__file__)  # Caminho do script atual
    while True:
        if os.path.basename(caminho_atual) == nome_projeto:
            return caminho_atual
        caminho_superior = os.path.dirname(caminho_atual)
        if caminho_superior == caminho_atual:  # Chegou ao root e não encontrou
            raise FileNotFoundError(f"Pasta '{nome_projeto}' não encontrada.")
        caminho_atual = caminho_superior


def log_message(log_path, message):
    print(message)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')} - {message}\n")


def click_with_retry(driver, element):
    for _ in range(3):  # Tentar clicar até 3 vezes
        try:
            element.click()
            return
        except Exception:
            print("Clique direto falhou, tentando via JavaScript.")
            try:
                driver.execute_script("arguments[0].click();", element)
                return
            except Exception as e:
                print(f"Erro ao clicar no elemento: {e}")
                time.sleep(1)  # Esperar antes de tentar novamente


def initialize_driver():
    chrome_options = Options()
    diretorio_download = os.path.join(diretorio_projeto(), 'DataCom Proventos')
    prefs = {
        "download.default_directory": diretorio_download,  # Define o diretorio padrao
        "download.promp_for_download": False,  # Desativa o prompt de download
        "download.directory_upgrade": True,  # Atualiza o diretorio automaticamente
        "safebrosing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-webgl")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def close_overlays(driver):
    try:
        popup_close_button = driver.find_element(
            By.CLASS_NAME, "popupCloseIcon")
        if popup_close_button.is_displayed():
            popup_close_button.click()
            print("Overlay fechado com sucesso!")
    except Exception:
        print("Nenhum overlay encontrado.")


def select_countries(driver, wait):
    try:
        filter_button = wait.until(
            EC.element_to_be_clickable((By.ID, "filterStateAnchor")))
        filter_button.click()
        print("Botão de filtros clicado para abrir os filtros!")

        wait.until(EC.presence_of_element_located(
            (By.ID, "calendarFilterBox_country")))
        print("Lista de países carregada com sucesso!")

        country_checkboxes = driver.find_elements(
            By.XPATH, '//input[@name="country[]"]')
        for checkbox in country_checkboxes:
            country_id = checkbox.get_attribute("id")
            if checkbox.is_selected() and country_id != "country32":
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView(true);", checkbox)
                    time.sleep(0.5)
                    checkbox.click()
                    print(f"Desmarcado: {country_id}")
                except Exception:
                    print(f"Falha ao clicar no checkbox {
                          country_id}, tentando com JavaScript.")
                    driver.execute_script("arguments[0].click();", checkbox)

        brazil_checkbox = driver.find_element(By.ID, "country32")
        if not brazil_checkbox.is_selected():
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", brazil_checkbox)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", brazil_checkbox)
        print("Brasil selecionado com sucesso!")

        apply_button = driver.find_element(By.ID, "ecSubmitButton")
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", apply_button)
        time.sleep(0.5)
        click_with_retry(driver, apply_button)
        print("Filtros aplicados com sucesso!")
    except Exception as e:
        print(f"Erro ao selecionar apenas o Brasil: {e}")


def select_dates(driver, wait, start_date, end_date):
    try:
        date_picker_button = wait.until(
            EC.element_to_be_clickable((By.ID, "datePickerToggleBtn")))
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", date_picker_button)
        time.sleep(0.5)
        click_with_retry(driver, date_picker_button)
        print("Botão do seletor de datas clicado!")

        wait.until(EC.presence_of_element_located(
            (By.ID, "ui-datepicker-div")))
        print("Seletor de datas carregado com sucesso!")

        start_date_input = driver.find_element(By.ID, "startDate")
        start_date_input.clear()
        start_date_input.send_keys(start_date)
        print(f"Data de início {start_date} selecionada com sucesso!")

        end_date_input = driver.find_element(By.ID, "endDate")
        end_date_input.clear()
        end_date_input.send_keys(end_date)
        print(f"Data de término {end_date} selecionada com sucesso!")

        apply_button = driver.find_element(By.ID, "applyBtn")
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", apply_button)
        time.sleep(0.5)
        close_overlays(driver)
        click_with_retry(driver, apply_button)
        print("Botão 'Aplicar' clicado com sucesso!")
        time.sleep(20)
    except Exception as e:
        print(f"Erro ao selecionar as datas: {e}")


def extract_table_data(driver, wait):
    try:
        wait.until(EC.presence_of_element_located(
            (By.ID, "dividendsCalendarData")))
        print("Tabela carregada com sucesso!")

        table = driver.find_element(By.ID, "dividendsCalendarData")
        rows = table.find_elements(By.TAG_NAME, "tr")

        data = []
        for row in rows:
            if "theDay" in row.get_attribute("class"):
                continue

            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 7:
                data.append({
                    "Empresa": cells[1].text.strip(),
                    "Data ex-dividendos": cells[2].text.strip(),
                    "Dividendo": cells[3].text.strip(),
                    "Tipo": cells[4].text.strip(),
                    "Pagamento": cells[5].text.strip(),
                    "Rendimento": cells[6].text.strip(),
                })

        df = pd.DataFrame(data)
        print("Dados extraídos com sucesso!")
        return df

    except Exception as e:
        print(f"Erro ao extrair os dados da tabela: {e}")
        return pd.DataFrame()


def obter_datas_mes(output_path, data_padrao="2024-01-01"):
    """
    Extrai as datas relevantes (mês anterior e atual) a partir de arquivos no diretório.
    Caso nenhum arquivo seja encontrado, retorna o mês anterior e o mês atual com base na data padrão.

    :param db_path: Caminho do diretório onde os arquivos estão localizados.
    :param data_padrao: Data padrão no formato 'YYYY-MM-DD' caso nenhuma data seja encontrada.
    :return: Lista de tuplas com (início, fim) para o mês anterior e o mês atual.
    """
    datas_extraidas = []

    # Verifica se o diretório existe
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Diretório não encontrado: {output_path}")

    # Lista os arquivos no diretório
    arquivos_csv = os.listdir(output_path)

    # Extrai datas dos nomes dos arquivos
    for arquivo in arquivos_csv:
        match = re.search(r"(\d{2}_\d{4})", arquivo)  # Busca padrão `MM_YYYY`
        if match:
            trecho = match.group(1).replace("_", "/")
            data_formatada = f"01/{trecho}"  # Sempre o primeiro dia do mês
            datas_extraidas.append(data_formatada)

    # Define datas padrão se nenhuma data foi encontrada
    if not datas_extraidas:
        print(f"Nenhuma data encontrada. Usando data padrão: {data_padrao}")
        datas_extraidas = [data_padrao]

    # Verifica os formatos antes da conversão
    datas_extraidas = [
        pd.to_datetime(data, format="%d/%m/%Y", errors="coerce") if "/" in data else pd.to_datetime(data, format="%Y-%m-%d", errors="coerce")
        for data in datas_extraidas
    ]

    # Remove valores inválidos (NaT)
    datas_extraidas = [data for data in datas_extraidas if not pd.isnull(data)]

    if not datas_extraidas:
        raise ValueError("Nenhuma data válida encontrada.")

    # Ordena as datas
    datas_extraidas = sorted(datas_extraidas)

    # Determina o mês anterior e o mês atual
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)

    # Retorna as datas relevantes como objetos datetime
    return [
        (first_day_previous_month, last_day_previous_month),  # Mês passado
        (first_day_current_month, today),  # Mês atual
    ]


# Configurações Gerais
output_path = os.path.join(diretorio_projeto(), 'DataCom Proventos')
# Caminho do arquivo de log
log_path = os.path.join(output_path, "LOG_DATACOM.txt")
os.makedirs(output_path, exist_ok=True)

# Limpando o log no início
with open(log_path, "w", encoding="utf-8") as log_file:
    log_file.write("Log iniciado\n")

# Loop pelos dois meses definidos
for start_date, end_date in obter_datas_mes(output_path):
    try:
        start_date_str = start_date.strftime("%d/%m/%Y")
        end_date_str = end_date.strftime("%d/%m/%Y")

        log_message(log_path, f"Extraindo dados para o período: {
                    start_date_str} a {end_date_str}")

        # Inicializar o driver
        driver = initialize_driver()
        wait = WebDriverWait(driver, 15)

        # Navegar até a página e configurar os filtros
        url = "https://br.investing.com/dividends-calendar/"
        driver.get(url)
        close_overlays(driver)
        select_countries(driver, wait)
        select_dates(driver, wait, start_date=start_date_str,
                     end_date=end_date_str)

        # Extrair os dados
        df = extract_table_data(driver, wait)
        if not df.empty:
            filename = f"DATACOM_{end_date_str.replace('/', '_')}.csv"
            filepath = os.path.join(output_path, filename)
            df.to_csv(filepath, sep=';', index=False, encoding="utf-8")
            log_message(log_path, f"Dados salvos em {filepath}.")

    except Exception as e:
        log_message(log_path, f"Erro durante a extração para o período {
                    start_date_str} a {end_date_str}: {e}")

    finally:
        driver.quit()
