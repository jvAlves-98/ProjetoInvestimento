import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Variaveis para execução de codigos e caminhos para arquivos
db_AcoesIBOV = r"C:\Users\João Vitor\OneDrive\Workspace - Python VS Code\Projetos - Produção\ProjetoInvestimento\Historico cotações\Ações IBOV"

# Data inicial para  busca dos dados
data_inicial = '2021-01-01'


def obter_tickers() -> list:
    """
    Processa o arquivo CSV com a lista de tickerts.
    CSV retirado do Status Invest link: https://statusinvest.com.br/acoes/busca-avancada
    Retirada todas as colunas não relevantes.
    Adicionado '.SA' pois o Yahoo Finance reconhece somente dessa forma.
    """

    caminho_csv = 'statusinvest-busca-avancada.csv'

    ListaAcoes = pd.read_csv(caminho_csv, sep=';')
    ListaAcoes = ListaAcoes[['TICKER']]
    ListaAcoes = ListaAcoes.drop_duplicates()
    ListaAcoes['TICKER'] = ListaAcoes['TICKER'].astype(str) + '.SA'

    # Retornar como lista
    return ListaAcoes['TICKER'].tolist()


def obter_historico(StartDate, EndDate, Tickers):
    """
    Obtem o historico de cada ticker na data especificada.
    É feita cada consulta separadamente reduzindo o tempo de cada consulta.
    """

    try:
        # Download das cotações do yfinance
        dfTicker = yf.download(Tickers, start=StartDate, end=EndDate,
                               actions=True, ignore_tz=True, rounding=True, multi_level_index=False, progress=False)

        if dfTicker.empty:
            # print(f"Nenhum dado encontrado para o ticker: {Tickers}")
            return None

        # Resentando o index do data frame para retirar a coluna "Date" do index
        dfTicker = dfTicker.reset_index()
        dfTicker = dfTicker.drop(columns=['Stock Splits'])
        dfTicker.columns = ['Date', 'Close',
                            'Dividends', 'High', 'Low', 'Open', 'Volume']

        # Normalizando colunas de valores
        colunas_numericas = ['Close', 'Dividends', 'High', 'Low', 'Open']
        dfTicker[colunas_numericas] = dfTicker[colunas_numericas].map(
            lambda x: f"{x: .2f}".replace('.', ',')
        )

        # Adicionando a coluna dos Tickers e todos os tickers em um unico DataFrame
        dfTicker['Ticker'] = Tickers

        return dfTicker

    except Exception as e:
        # print(f"Erro ao processar o ticker {Tickers}: {e}")
        return None


def salvar_historico(data_inicial, db_AcoesIBOV):
    """
    Gera o histórico mensalmente a partir de uma data inicial e salva todos os tickers em um arquivo mensal.
    Salva no diretorio especifico criando um "DataBase"
    """

    # Data atual é a final a ser usada (Pode ser usado o dia anterior depende do horario de execução)
    data_final = datetime.now()
    data_atual = datetime.strptime(data_inicial, "%Y-%m-%d")

    # Iterar mensalmente
    while data_atual < data_final:
        # Definir o início e o fim do mês atual
        proximo_mes = data_atual + timedelta(days=31)
        fim_mes = (proximo_mes.replace(day=1) - timedelta(days=1))

        dfMes = []  # DataFrame para consolidar os dados do mês

        # Processa cada ticker e obter o historico do mes
        for ticker in obter_tickers():
            # print(f'Processando {ticker} de {data_atual} a {fim_mes}')
            dfHistorico = obter_historico(data_atual, fim_mes, ticker)
            if dfHistorico is not None:
                dfMes.append(dfHistorico)

        # Concatena os dados de todos o ticker no mês
        if dfMes:
            dfMes = pd.concat(dfMes, ignore_index=True)

            # Criando o nome do arquivo para o mes e ano
            nome_arquivo = os.path.join(db_AcoesIBOV, f'Acoes_IBOV_{
                                        data_atual.strftime("%m")}_{data_atual.strftime("%Y")}.csv')

            # Salvar o arquivo
            dfMes.to_csv(nome_arquivo, sep=';', index=False)
            # print(f'Arquivo salvo em: {nome_arquivo}')

        # Iterar a data atual para o mes seguinte
        data_atual = proximo_mes.replace(day=1)


salvar_historico(data_inicial, db_AcoesIBOV)
