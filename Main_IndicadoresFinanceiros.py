from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os


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


def indicadores_AcoesIBOV():

    url = 'https://statusinvest.com.br/acoes/busca-avancada'
    indicadores_antigo = os.path.join(
        projeto, 'Indicadores Financeiros', 'statusinvest-busca-avancada.csv')
    indicadores_novo = os.path.join(
        projeto, 'Indicadores Financeiros', 'Indicadores_AcoesIBOV.csv')
    servico = Service(ChromeDriverManager().install())

    # Configurando diretorio para download e do Chrome
    diretorio_download = os.path.join(
        diretorio_projeto(), 'Indicadores Financeiros')
    options = Options()
    prefs = {
        "download.default_directory": diretorio_download,  # Define o diretorio padrao
        "download.promp_for_download": False,  # Desativa o prompt de download
        "download.directory_uprade": True,  # Atualiza o diretorio automaticamente
        "safebrosing.enabled": True  # Evita alertas de seguranças
    }
    options.add_experimental_option("prefs", prefs)
    # options.add_argument('--headless') Ativa o modo headless por algum movito o codigo não faz o download
    options.add_argument('window-size=1920,1080')

    # Aciona o webdriver
    driver = webdriver.Chrome(service=servico, options=options)
    driver.get(url)
    time.sleep(2)

    # Aciona o botao de filtrar e aguarda o popup
    try:
        button_buscar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="main-2"]/div[3]/div/div/div/button[2]'))
        )
        button_buscar.click()
    except Exception as e:
        print(f'Erro ao clicar no botao de busca: {e}')

    # Fechar popup de anuncios
    try:
        button_close = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn-close'))
        )
        button_close.click()
    except Exception as e:
        print(f'Erro ao clicar no botao de busca: {e}')

    # Fazendo o download e apagando arquivo anterior
    if os.path.exists(indicadores_novo):
        os.remove(indicadores_novo)
        try:
            button_download = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div/a[contains(@class, "btn-download")]'))
            )
            button_download.click()
        except Exception as e:
            print(f'Erro ao clicar no botao de busca: {e}')

    else:
        try:
            button_download = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div/a[contains(@class, "btn-download")]'))
            )
            button_download.click()
        except Exception as e:
            print(f'Erro ao clicar no botao de busca: {e}')

    # Loop para esperar o arquivo
    tempo_maximo = 60
    tempo_inicio = time.time()
    while not os.path.exists(indicadores_antigo):
        time.sleep(1)
        if time.time() - tempo_inicio > tempo_maximo:
            break
    else:
        os.rename(indicadores_antigo, indicadores_novo)

    # Finaliza a sessão
    driver.quit()


def indicadores_FiiIBOV():

    url = 'https://statusinvest.com.br/fundos-imobiliarios/busca-avancada'
    indicadores_antigo = os.path.join(diretorio_projeto(
    ), 'Indicadores Financeiros', 'statusinvest-busca-avancada.csv')
    indicadores_novo = os.path.join(
        diretorio_projeto(), 'Indicadores Financeiros', 'Indicadores_FiiIBOV.csv')
    servico = Service(ChromeDriverManager().install())

    # Configurando diretorio para download e do Chrome
    diretorio_download = os.path.join(
        diretorio_projeto(), 'Indicadores Financeiros')
    options = Options()
    prefs = {
        "download.default_directory": diretorio_download,  # Define o diretorio padrao
        "download.promp_for_download": False,  # Desativa o prompt de download
        "download.directory_uprade": True,  # Atualiza o diretorio automaticamente
        "safebrosing.enabled": True  # Evita alertas de seguranças
    }
    options.add_experimental_option("prefs", prefs)
    # options.add_argument('--headless') Ativa o modo headless por algum movito o codigo não faz o download
    options.add_argument('window-size=1920,1080')

    # Aciona o webdriver
    driver = webdriver.Chrome(service=servico, options=options)
    driver.get(url)
    time.sleep(2)

    # Aciona o botao de filtrar e aguarda o popup
    try:
        button_buscar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="main-2"]/div[3]/div/div/div/button[2]'))
        )
        button_buscar.click()
    except Exception as e:
        print(f'Erro ao clicar no botao de busca: {e}')

    # Fechar popup de anuncios
    try:
        button_close = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn-close'))
        )
        button_close.click()
    except Exception as e:
        print(f'Erro ao clicar no botao de busca: {e}')

    # Fazendo o download e apagando arquivo anterior
    if os.path.exists(indicadores_novo):
        os.remove(indicadores_novo)
        try:
            button_download = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div/a[contains(@class, "btn-download")]'))
            )
            button_download.click()
        except Exception as e:
            print(f'Erro ao clicar no botao de busca: {e}')

    else:
        try:
            button_download = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div/a[contains(@class, "btn-download")]'))
            )
            button_download.click()
        except Exception as e:
            print(f'Erro ao clicar no botao de busca: {e}')

    # Loop para esperar o arquivo
    tempo_maximo = 60
    tempo_inicio = time.time()
    while not os.path.exists(indicadores_antigo):
        time.sleep(1)
        if time.time() - tempo_inicio > tempo_maximo:
            break
    else:
        os.rename(indicadores_antigo, indicadores_novo)

    # Finaliza a sessão
    driver.quit()


# Diretorio projeto
projeto = diretorio_projeto()


indicadores_AcoesIBOV()
indicadores_FiiIBOV()
