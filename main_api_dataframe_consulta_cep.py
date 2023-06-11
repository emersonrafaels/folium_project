import pandas as pd

from api_consulta_cep import BuscaEndereco

def obtem_dados_cep(dataframe, coluna_cep, coluna_lat, coluna_long, token=None):

    # PERCORRENDO OS DADOS DO DATAFRAME
    for idx, row in df.iterrows():

        # OBTENDO O CEP DE CONSULTA
        cep_consulta = row[coluna_cep]

        # OBTENDO OS DADOS VIA AI
        result_consulta_cep = BuscaEndereco(cep=cep_consulta).consulta_cep(token=token)

        # VERIFICANDO SE EXISTEM AS COLUNAS QUE OS DADOS SERÃO SALVOS
        for column in [coluna_lat, coluna_long]:
            if column not in dataframe.columns:
                dataframe[column] = 0

        # SALVANDO OS DADOS
        dataframe.at[idx, coluna_lat] = result_consulta_cep.get(cep_consulta).get("LATITUDE")
        dataframe.at[idx, coluna_long] = result_consulta_cep.get(cep_consulta).get("LONGITUDE")

    return dataframe

data_dir = "DATA/footprint_agencias.xlsx"

df = pd.read_excel(data_dir, engine="openpyxl")

token = "10c9397802c79fb5a5415edabe9af2be"

df_cep = obtem_dados_cep(dataframe=df,
                         coluna_cep="CEP",
                         coluna_lat="LATITUDE",
                         coluna_long="LONGITUDE",
                         token=token)

df_cep.to_excel("DATA/BASE_COM_CEP.xlsx", index=None)

print("PROCESSO CONCLUIDO COM SUCESSO - BASE ENRIQUECIDA COM INFORMAÇÕES DE CEP")