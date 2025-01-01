import pandas as pd
import yfinance as yf


def obter_tickers() -> list:
    """
    Processa o arquivo CSV com a lista de tickerts
    CSV retirado do Status Invest link: https://statusinvest.com.br/acoes/busca-avancada
    Retirada todas as colunas não relevantes
    Adicionado '.SA' pois o Yahoo Finance reconhece somente dessa forma
    """

    caminho_csv = 'statusinvest-busca-avancada.csv'

    ListaAcoes = pd.read_csv(caminho_csv, sep=';')
    ListaAcoes = ListaAcoes[['TICKER']]
    ListaAcoes = ListaAcoes.drop_duplicates()
    ListaAcoes['TICKER'] = ListaAcoes['TICKER'].astype(str) + '.SA'

    # Retornar como lista
    return ListaAcoes['TICKER'].tolist()


def obter_historico(StartDate, EndDate):
    dfHistorico = []

    for Tickers in obter_tickers():
        try:
            # Download das cotações do yfinance
            dfTicker = yf.download(Tickers, start=StartDate, end=EndDate)

            if dfTicker.empty:
                print(f"Nenhum dado encontrado para o ticker: {Tickers}")
                continue
            # Resentando o index do data frame para retirar a coluna "Date" do index
            dfTicker = dfTicker.reset_index()
            dfTicker.columns = dfTicker.columns.droplevel(1)
            dfTicker.columns = ['Date', 'Close',
                                'High', 'Low', 'Open', 'Volume']

            """
            Corrijinfo e normalizando a tabela.
            Arredondando os numeros e convertendo para o padrão brasileiro: "," separador de casas decimais.
            
            """
            colunas_numericas = ['Close', 'High', 'Low', 'Open']
            dfTicker[colunas_numericas] = dfTicker[colunas_numericas].round(2)
            dfTicker[colunas_numericas] = dfTicker[colunas_numericas].applymap(
                lambda x: f"{x: .2f}".replace('.', ',')
            )

            # Adicionando a coluna dos Tickers e todos os tickers em um unico DataFrame
            dfTicker['Ticker'] = Tickers
            dfHistorico.append(dfTicker)
        except Exception as e:
            print(f"Erro ao processar o ticker {Tickers}: {e}")
            continue

    dfFinal = pd.concat(dfHistorico, ignore_index=True)
    return dfFinal


StartDate = '2024-01-02'
EndDate = '2024-12-30'

dfFinal = obter_historico(StartDate, EndDate)

# Salvar o DataFrame final em um arquivo CSV
dfFinal.to_csv('Historio\Historico Ações\dados_historico.csv',
               sep=';', index=False)

# Exibir parte do DataFrame final
print(dfFinal.head())
