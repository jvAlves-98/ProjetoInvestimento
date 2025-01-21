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


def lista_datas():
    """
    Extrai as datas salvas no diretorio de historico cotações para as acoes IBOV
    Para evitar perdas é gerado a partir do penultimo registro ou seja mes anterior para evitar meses incompletos
    """
    datas_extraidas = []

    # Lista de todos os arquivos salvos de AcoesIBOV
    if not os.path.exists(output_path):
        raise FileNotFoundError(f'Diretorio não encontrado: {output_path}')

    arquivos_csv = os.listdir(output_path)

    # Loop para a extração das datas de cada arquivo
    for arquivo in arquivos_csv:
        # Extrair datas usando expressão regular
        match = re.search(r"(\d{2}_\d{4})", arquivo)
        if match:
            # Transformação em data completa "dd/mm/YYYY"
            trecho = match.group(1).replace("_", "/")
            data_formatada = f"01/{trecho}"

            # Adiciona a as datas capturadas
            datas_extraidas.append(data_formatada)

    # Convertendo as datas extraidas e mantendo a penultima data "Gerando mes anterior e atual novamente"
    if not datas_extraidas:
        return "2024-01-01"

    datas_extraidas = pd.to_datetime(datas_extraidas, format='%d/%m/%Y')
    if len(datas_extraidas) < 2:
        return datas_extraidas[0].strftime('%Y-%m-%d')

    datas_extraidas = sorted(datas_extraidas)[-2]
    return datas_extraidas.strftime('%Y-%m-%d')


def salvar_datacom(data_inicial, output_path):
    """
    Gera o historio mes a mes a partir da data inicial
    """

    data_final = datetime.now()
    data_atual = datetime.strptime(
        data_inicial, "%Y-%m-%d")  # Data do contexto

    while data_atual < data_final:
        proximo_mes = data_atual + timedelta(days=31)
        fim_mes = (proximo_mes.replace(day=1) - timedelta(days=1))

        data_inicio = data_atual.strftime("%d/%m/%Y")
        data_fim = fim_mes.strftime("%d/%m/%Y")
        
        # Inicializar o driver
        driver = initialize_driver()
        wait = WebDriverWait(driver, 15)

        # Navegar até a página e configurar os filtros
        url = "https://br.investing.com/dividends-calendar/"
        driver.get(url)
        close_overlays(driver)
        select_countries(driver, wait)
        select_dates(driver, wait, start_date=data_inicio,
                     end_date=data_fim)

        # Extrair os dados
        df = extract_table_data(driver, wait)
        if not df.empty:
            filename = f"DATACOM_{data_fim[2:].replace('/', '_')}.csv"
            filepath = os.path.join(output_path, filename)
            df.to_csv(filepath, sep=';', index=False, encoding="utf-8")

        driver.quit()

        data_atual = proximo_mes.replace(day=1)




# Configurações Gerais
output_path = os.path.join(diretorio_projeto(), 'DataCom Proventos')
data_inicial = lista_datas()


salvar_datacom(data_inicial, output_path)
