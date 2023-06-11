import base64
from os import path
from json import loads
from pathlib import Path

import branca
import pandas as pd
import streamlit as st
import folium
import validators
from streamlit_folium import st_folium
from streamlit_custom_notification_box import custom_notification_box
from streamlit_extras.app_logo import add_logo
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

def add_logo(logo_url: str, height: int = 120):

    """

      FUNÇÃO CUJO OBJETIVO É ADICIONAR UM LOGO NO SIDEBAR
      DO APP STREAMLIT.

      RECEBE UMA IMAGEM EM:
        URL DA WEB
        PATH DA MÁQUINA

      # Arguments
        logo_url             - Required: Local onde está a imagem (String)
        height               - Optional: Altura da imagem (Integer)

    """

    if validators.url(logo_url) is True:
        logo = f"url({logo_url})"
    else:
        logo = f"url(data:image/png;base64,{base64.b64encode(Path(logo_url).read_bytes()).decode()})"

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: {logo};
                background-repeat: no-repeat;
                padding-top: {height - 40}px;
                background-position: 20px 20px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_data():

  # REALIZANDO A LEITURA DOS DADOS
  df = pd.read_excel("/content/gdrive/MyDrive/FOOTPRINT/BASE_COM_CEP.xlsx")

  return df


def download_data(df):

  # INICIALIZANDO O VALIDATOR
  validator = False

  try:
    df.to_excel("FOOTPRINT.xlsx", index=None)

    validator = True

    if validator:

      pass

      # st.success('Dados salvos com sucesso', icon="✅")
  except Exception as ex:
    print(ex)

def download_map(mapobj):

  # INICIALIZANDO O VALIDATOR
  validator = False

  try:
    mapobj.save("MAPA_FOOTPRINT.html")

    validator = True

    if validator:

      pass

      # st.success('HTML salvo com sucesso', icon="✅")
  except Exception as ex:
    print(ex)

def convert_df_html(row_df, 
                    col_header=None,
                    left_col_color="#140083", 
                    right_col_color="#140083", 
                    left_text_color="#FFFFFF", 
                    right_text_color="#FFFFFF"):

  # INICIANDO A VARIÁVEL DE RETORNO
  html = ""

  # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ AS TABLES
  html_table = ""

  html_header = """<!DOCTYPE html>
      <html>
      <head>
        <h4 style="margin-bottom:10"; width="200px">{}</h4>""".format(row_df.get(col_header)) + """
        <style>
      table {
        border:1px solid #b3adad;
        border-collapse:collapse;
        padding:5px;
        font-family: inherit;
      }
      table th {
        border:1px solid #b3adad;
        padding:5px;
        background: #f0f0f0;
        color: #313030;
      }
      table td {
        border:1px solid #b3adad;
        text-align:center;
        padding:5px;
        background: #ffffff;
        color: #313030;
      }
    </style>
      </head>
          <table style="height: 126px; width: 350px;">
      <tbody>
    """

  # VERIFICANDO SE O ARGUMENTO É UM DICT
  if isinstance(row_df, (dict, pd.Series)):

    # PERCORRENDO O DICT
    for key, value in row_df.items():

      html_table += """
        <tr>
        <td style="background-color: """+ left_col_color + ";font-weight: bold"""";"><span style="color: text_left_color_to_replace;">key_to_replace</span></td>
        <td style="width: 150px;background-color: """+ right_col_color +""";"><span style="color: right_left_color_to_replace;">value_to_replace</span></td>
        </tr>
      """
      html_table = html_table.replace("key_to_replace", str(key)).replace("value_to_replace", str(value))
      html_table = html_table.replace("text_left_color_to_replace", str(left_text_color)).replace("right_left_color_to_replace", str(right_text_color))

    # UNINDO OS HTML
    html = "{}{}".format(html_header, html_table)

  return html

def load_map(data=None, 
             circle_radius=0, 
             validator_add_layer=False):

  def add_layers_control(mapobj, validator_add_layer=False):

    if validator_add_layer:

      st.text("ENTROU")

      # ADICIONANDO OS LAYERS
      folium.TileLayer("Stamen Terrain").add_to(mapobj)
      folium.TileLayer("Stamen Toner").add_to(mapobj)
      folium.TileLayer("Cartodb dark_matter").add_to(mapobj)

      # ADICIONANDO LAYER CONTROL
      folium.LayerControl().add_to(mapobj)

    return mapobj

  def add_markers(mapobj, data=None, circle_radius=0):

    # VERIFICANDO SE HÁ UM DATAFRAME ENVIADO COMO ARGUMENTO
    if data is not None:
      # PERCORRENDO O DATAFRAME
      for idx, row in data.iterrows():

        # OBTENDO O STATUS
        status = row.get("STATUS")

        # OBTENDO LATITUDE E LONGITUDE
        lat = row.get("LATITUDE")
        long = row.get("LONGITUDE")

        # OBTENDO O HTML DO ICON
        html = convert_df_html(row_df=row, col_header="ENDEREÇO", 
                              left_col_color="#140083", 
                              right_col_color="#140083", 
                              left_text_color="#FF7200", 
                              right_text_color="#FFFFFF")
        iframe = branca.element.IFrame(html=html, width=510, height=280)
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)

        if str(status).upper() == "VERMELHA":
          current_icon = folium.features.CustomIcon(icon_image="/content/gdrive/MyDrive/FOOTPRINT/itau_vermelho.png", 
                                                    icon_size=(16, 16))
        elif str(status).upper() == "AMARELA":
          current_icon = folium.features.CustomIcon(icon_image="/content/gdrive/MyDrive/FOOTPRINT/itau_amarelo.png", 
                                                    icon_size=(16, 16))
        else:
          current_icon = folium.features.CustomIcon(icon_image="/content/gdrive/MyDrive/FOOTPRINT/itau_verde.png", 
                                                    icon_size=(16, 16))

        folium.Marker(
          location=[lat, long],
          popup=popup, 
          icon=current_icon, 
          lazy=True
      ).add_to(mapobj)

    return mapobj

  footprint_map = folium.Map(location=[-15.768857589354258, -47.905384728712384], 
                             zoom_start=4, 
                             tiles="openstreetmap")

  # ADICIONANDO LAYERS
  footprint_map = add_layers_control(mapobj=footprint_map, 
                                     validator_add_layer=validator_add_layer)

  # ADICIONANDO MAKERS
  footprint_map = add_markers(mapobj=footprint_map, 
                              data=data, 
                              circle_radius=circle_radius)

  return footprint_map

def convert_dataframe_to_aggrid(data, 
                                validator_all_rows_selected=True):

  gb = GridOptionsBuilder.from_dataframe(data)
  gb.configure_pagination(paginationAutoPageSize=True, 
                          paginationPageSize=5) #Add pagination
  gb.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel="") #Add a sidebar
  gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
  
  # VALIDANDO SE É DESEJADO QUE TODAS AS LINHAS INICIEM SELECIONADAS
  if validator_all_rows_selected:
    gb.configure_selection('multiple', pre_selected_rows=list(range(len(data))))

  gridOptions = gb.build()

  grid_response = AgGrid(
      data,
      gridOptions=gridOptions,
      data_return_mode='AS_INPUT', 
      update_mode='MODEL_CHANGED', 
      fit_columns_on_grid_load=False,
      theme='streamlit',
      enable_enterprise_modules=True,
      height=350, 
      width='100%',
      reload_data=False
  )

  return grid_response

def main():

  # CONFIGURANDO O APP
  st.set_page_config(page_title="FOOTPRINT - GESTÃO DO PARQUE DE AGÊNCIAS", 
                     page_icon=":world-map:", 
                     layout="wide", 
                     )

  # ADICIONANDO TITULO DA PÁGINA
  st.title("APP - FOOTPRINT - GESTÃO DO PARQUE DE AGÊNCIAS")

  # ADICIONANDO LOGO
  add_logo(logo_url="http://placekitten.com/120/120")

  # INICIANDO A VARIÁVEL QUE CONTROLA O RAIO DE SOMBREAMENTO
  raio_sombreamento = 0

  with st.sidebar:

    # ESTUDO DESEJADO
    st.title("Defina o estudo desejado")

    options_estudos = ["Autosserviço", 
                       "Encerramento", 
                       "Remanejamento", 
                       "Abertura", 
                       "Áreas ociosas", 
                       "Intervenções estratégicas"]

    selected_estudo_desejado = st.radio(label="Estudo desejado", 
                                        options=options_estudos, 
                                        index=0, 
                                        key=None, 
                                        help="Escolha o estudo desejado e na página central aparecerá novas opções", 
                                        on_change=None, 
                                        disabled=False, 
                                        horizontal=False, 
                                        label_visibility="visible")

  if selected_estudo_desejado == "Autosserviço":

    # CARREGANDO DATAFRAME
    df_footprint = load_data()

    # INCLUINDO O DATAFRAME EM TELA
    st.markdown("### Autosserviço - Dados do footprint")
    dataframe_aggrid = convert_dataframe_to_aggrid(data=df_footprint)

    # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
    selected_df = pd.DataFrame(dataframe_aggrid["selected_rows"])

    if not selected_df.empty:

      selected_df = selected_df[df_footprint.columns]
    
    # INCLUINDO NO APP
    st.markdown("### Parque de agências")
    st_col1, st_col2 = st.columns(2)
    with st_col1: 
      result_view_sombreamento = st.checkbox("Visualizar sombreamento", 
                                              value=False, 
                                              key=None, 
                                              help="Habilita o controle de sombreamento sobre o mapa", 
                                              on_change=None, 
                                              disabled=False, 
                                              label_visibility="visible")
    if result_view_sombreamento:
      with st_col2: 
        raio_sombreamento = st.slider('Raio desejado (em km):',
                                      min_value=0, 
                                      max_value=1000, 
                                      step=1, 
                                      help="O raio é aplicado sobre o mapa", )
    
    # CRIANDO MAPA
    mapobj = load_map(data=selected_df, 
                      circle_radius=raio_sombreamento, 
                      validator_add_layer=True)

    # INCLUINDO O MAPA NO APP
    st_data = st_folium(mapobj, width=1000, height=500)

    st_col1, st_col2 = st.columns(2)

    with st_col1:

      st.button(
      label="Download dados (excel)",
      on_click=download_data, 
      args=(df_footprint,),
      )

    with st_col2:

      st.button(
          label="Download mapa",
          on_click=download_map,
          args=(mapobj,)
      )

  elif selected_estudo_desejado == "Encerramento":

    # CARREGANDO DATAFRAME
    df_footprint = load_data()

    # INCLUINDO O DATAFRAME EM TELA
    st.markdown("### Análise de encerramento")
    st.markdown("#### Selecione as agências que você deseja analisar")
    dataframe_aggrid_encerramento = convert_dataframe_to_aggrid(data=df_footprint, 
                                                   validator_all_rows_selected=False)

    # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
    selected_df_encerramento = pd.DataFrame(dataframe_aggrid_encerramento["selected_rows"])

    if not selected_df_encerramento.empty:

      selected_df_encerramento = selected_df_encerramento[df_footprint.columns]

      st.markdown("### Agências selecionadas")
      st.dataframe(selected_df_encerramento)

      st.markdown("### Faça upload do arquivo de simulação de encerramento")
      uploaded_file = st.file_uploader("Escolha o arquivo", 
                                       type=["csv", "xlsx"], 
                                       help="O arquivo deve conter as agências selecionadas, caso contrário, não será possível realizar a comparação")
      if uploaded_file is not None:
        st.sucess("UPLOAD REALIZADO COM SUCESSO")

  else:
      st.markdown("### Feature em desenvolvimento")

      styles = {'material-icons':{'color': 'black'},
                'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
                'notification-text': {'':''},
                'close-button':{'':''},
                'link':{'':''}}

      custom_notification_box(icon='view_kanban', 
                              textDisplay='Essa página está em construção', 
                              externalLink='', 
                              url="#", 
                              styles=styles, 
                              key="notification_desenv")

if __name__ == "__main__":
    main()
