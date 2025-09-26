import pandas as pd
import glob 
import os
import matplotlib.pyplot as plt
import numpy as np

def treatDate(dfFlights, column):

    dfFlights[column] = pd.to_datetime(dfFlights[column], format="%d/%m/%Y %H:%M")
    return dfFlights[column]

def formatFlights(df:pd.DataFrame):

    df["Partida Prevista"] = treatDate(df, "Partida Prevista")
    df["Partida Real"] = treatDate(df, "Partida Real")
    df["Atraso Partida"] = (df["Partida Real"] - df["Partida Prevista"]).dt.total_seconds() / 60

    df["Chegada Prevista"] = treatDate(df, "Chegada Prevista")
    df["Chegada Real"] = treatDate(df, "Chegada Real")
    df["Atraso Chegada"] = (df["Chegada Real"] - df["Chegada Prevista"]).dt.total_seconds() / 60

    return df

def formatAirportCodes(df: pd.DataFrame):

    df = df[(df["iso_country"] == "BR") & (df["type"] != "heliport")]

    return df

def joinDataFrames(path):

    dfFlightsList = []

    for file in os.listdir(path):
        if file.endswith(".csv"):

            filePath = os.path.join(path, file)

            dfFlights = pd.read_csv(filePath, header=1, sep=";", encoding="utf-8")

            dfFlightsList.append(dfFlights)

    finaldfFlights = pd.concat(dfFlightsList)

    return finaldfFlights

def period_of_day(hour):
    if 0 <= hour < 6:
        return "Madrugada"
    elif 6 <= hour < 12:
        return "Manhã"
    elif 12 <= hour < 18:
        return "Tarde"
    else:
        return "Noite"
    
if __name__ == "__main__":
    
    # path = r"D:\Eng Software\8 FASE\Atividade N1\dataset"
    # airportCodesPath = r"D:\Eng Software\8 FASE\Atividade N1\airport-codes.csv"
    
    path = r"C:\Users\vinir\Trabalhos Faculdade\8° Fase\Ciência de dados\Atividade N1\dataset"
    airportCodesPath = r"C:\Users\vinir\Trabalhos Faculdade\8° Fase\Ciência de dados\Atividade N1\airport-codes.csv"
    
    # path = r"C:\Users\viniciusrr\Projetos\Python\Atividade N1\dataset"
    # airportCodesPath = r"C:\Users\viniciusrr\Projetos\Python\Atividade N1\airport-codes.csv"
    
    dir = os.listdir(path)
    excelFile = os.path.join(path, dir[0])
    dfFlights = pd.read_csv(excelFile, sep=";", header=1, encoding="utf-8")

    dfFlights = joinDataFrames(path)

    dfFlights = formatFlights(dfFlights)

    dfCodes = pd.read_csv(airportCodesPath, sep=",", encoding="utf-8")
    dfCodes = formatAirportCodes(dfCodes)

    icaoCode = set(dfCodes["icao_code"])
    dfBrFlights = dfFlights[(dfFlights["ICAO Aeródromo Origem"].isin(icaoCode)) & (dfFlights["ICAO Aeródromo Destino"].isin(icaoCode))]
    
    
    dfBrFlights = dfBrFlights[dfBrFlights["Situação Voo"] == "REALIZADO"]
    
    print("-----------------------------")
    print("Total de voos realizados")
    print(dfBrFlights)
    
    dfBrFlights = dfBrFlights[(dfBrFlights['Atraso Partida'] > 0) | (dfBrFlights['Atraso Chegada'] > 0)]
    
    print("-----------------------------")
    print("Total de voos que atrasaram")
    print(dfBrFlights)
    
    dfBrFlights['Ano'] = dfBrFlights['Partida Prevista'].dt.year
    dfBrFlights['Dia Semana'] = dfBrFlights['Partida Prevista'].dt.day_name()
    dfBrFlights['Hora Prevista'] = dfBrFlights['Partida Prevista'].dt.hour
    
    delayPerYears = dfBrFlights.groupby('Ano').size()
    
    #Aeroportos com mais atrasos

    delaysOrigin = dfBrFlights['ICAO Aeródromo Origem'].value_counts()
    delayDestination = dfBrFlights['ICAO Aeródromo Destino'].value_counts()
    airportDelays = delaysOrigin.add(delayDestination, fill_value=0).sort_values(ascending=False)
    topDelays = airportDelays.head(10)
    
    #Variação de atrasos nos aeroportos
    
    airportYearly = dfBrFlights.groupby(["Ano", "ICAO Aeródromo Origem"]).size().unstack(fill_value=0)
    variation = airportYearly.diff().sum().sort_values()

    print("Aeroporto que mais aumentou atrasos:", variation.idxmax(), "(", variation.max(), ")")
    print("Aeroporto que mais diminuiu atrasos:", variation.idxmin(), "(", variation.min(), ")")
    topAirports = airportYearly.sum().sort_values(ascending=False).head(5).index
    
    #Periodo do dia com mais atraso por ano
    
    dfBrFlights["Período"] = dfBrFlights["Hora Prevista"].apply(period_of_day)
    periodos_ano = dfBrFlights.groupby(["Ano", "Período"]).size().unstack(fill_value=0)
    
    #Companhias aéreas com mais atrasos por ano
    
    airlineDelays = dfBrFlights["ICAO Empresa Aérea"].value_counts().sort_values(ascending=False)
    # airlineDelays = dfBrFlights.groupby(["Ano", "ICAO Empresa Aérea"]).size().unstack(fill_value=0)
    topAirlinesDelays = airlineDelays.head(10)
    
    #------------- Plotando os gráficos ------------------
    
    # fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(20, 12))

    # Flatten a matriz de eixos para fácil acesso
    axes = axes.flatten()

    # 2. Plotar cada gráfico em seu respectivo eixo

    # Gráfico 1: Atrasos por Aeroporto
    topDelays.plot(kind="bar", ax=axes[0])
    axes[0].set_title("Aeroportos com mais atrasos", fontsize=14)
    axes[0].set_xlabel("Aeroporto (ICAO)", fontsize=12)
    axes[0].set_ylabel("Quantidade de atrasos", fontsize=12)
    axes[0].tick_params(axis='x', rotation=0)
    axes[0].grid(axis="y", linestyle="-", alpha=0.7)
    # Exibir os valores acima das barras
    for i, v in enumerate(topDelays.values):
        axes[0].text(i, v + 1, str(int(v)), ha="center", fontsize=10)

    # Gráfico 2: Evolução de Atrasos por Aeroporto
    airportYearly[topAirports].plot(kind="line", marker="o", ax=axes[1])
    axes[1].set_title("Evolução de atrasos por aeroporto")
    axes[1].set_ylabel("Quantidade de atrasos")
    axes[1].set_xlabel("Ano")
    axes[1].grid(True, alpha=0.5)

    # Gráfico 3: Atrasos por Dia da Semana
    daysOfWeek = dfBrFlights.groupby(["Ano", "Dia Semana"]).size().unstack(fill_value=0)
    daysOfWeek.plot(kind="bar", ax=axes[2])
    axes[2].set_title("Atrasos por dia da semana (a cada ano)")
    axes[2].set_ylabel("Quantidade de atrasos")
    axes[2].set_xlabel("Ano")
    axes[2].legend(title="Dia da Semana")
    axes[2].tick_params(axis='x', rotation=0)
    axes[2].grid(axis="y", alpha=0.6)

    # Gráfico 4: Atrasos por Período do Dia
    periodos_ano.plot(kind="bar", ax=axes[3])
    axes[3].set_title("Atrasos por período do dia (a cada ano)")
    axes[3].set_ylabel("Quantidade de atrasos")
    axes[3].set_xlabel("Ano")
    axes[3].legend(title="Período")
    axes[3].tick_params(axis='x', rotation=0)
    axes[3].grid(axis="y", alpha=0.6)

    # Gráfico 5: Companhias Aéreas com Mais Atrasos
    topAirlinesDelays.plot(kind="bar", ax=axes[4])
    axes[4].set_title("Companhia aérea com mais atrasos")
    axes[4].set_ylabel("Quantidade de atrasos")
    axes[4].set_xlabel("Ano")
    axes[4].legend(title="Companhias")
    axes[4].tick_params(axis='x', rotation=0)
    axes[4].grid(axis="y", alpha=0.6)

    # 3. Remover o último eixo vazio para melhor visualização
    fig.delaxes(axes[5])

    # 4. Ajustar layout para evitar sobreposição e exibir a figura
    plt.tight_layout()
    plt.show()


    print(dfBrFlights.columns)

    print("Gerando arquivo...")
    # dfBrFlights.to_excel("result.xlsx", index=False, engine="openpyxl")
    # dfCodes.to_excel('airportCodes.xlsx', index=False, engine="openpyxl")    