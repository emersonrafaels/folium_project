from os import path
from json import loads

import pandas as pd
import streamlit as st
import folium
import validators
from streamlit_folium import st_folium
from streamlit_custom_notification_box import custom_notification_box
from streamlit_extras.app_logo import add_logo
from streamlit_extras.dataframe_explorer import dataframe_explorer

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

@st.cache_data
def load_data():

  # REALIZANDO A LEITURA DOS DADOS
  df = pd.read_excel("/content/gdrive/MyDrive/FOOTPRINT/footprint_agencias.xlsx")

  return df

@st.cache_data
def download_data(df):

  return df.to_csv(index=None).encode('latin1')

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

def load_map():

  def add_layers_control(mapobj, validator_add_layer=True):

    if validator_add_layer:

      # ADICIONANDO OS LAYERS
      folium.TileLayer(attr="openstreetmap").add_to(mapobj)
      #folium.TileLayer(attr="mapquestopen").add_to(mapobj)
      #folium.TileLayer(attr="cartodbpositron").add_to(mapobj)

      # ADICIONANDO LAYER CONTROL
      folium.LayerControl().add_to(mapobj)

    return mapobj

  def add_markers(mapobj, data=None, circle_radius=0):

    folium.Marker(
      location=[-23.536791847273886, -46.7784728049161],
      popup="ITAU OSASCO",
      icon=folium.Icon(color='red', icon="glyphicon glyphicon-briefcase"),
  ).add_to(mapobj)

    folium.Marker(
        location=[-23.56863373566806, -46.648261720258745],
        popup="AV PAULISTA I",
        icon=folium.Icon(color="green", icon="glyphicon glyphicon-briefcase"),
    ).add_to(mapobj)

    folium.Marker(
        location=[-23.5644555638821, -46.653611733750736],
        popup="AV PAULISTA II",
        icon=folium.Icon(color="orange", icon="glyphicon glyphicon-briefcase"),
    ).add_to(mapobj)

    if circle_radius > 0:

      # MULTIPLICA O RAIO POR 1000, PARA REALIZAR A CONVERSÃO DE M PARA KM
      folium.Circle(radius=circle_radius*1000, 
                    location=[[-23.536791847273886, -46.7784728049161]]).add_to(mapobj)

    return mapobj

  footprint_map = folium.Map(location=[-23.561118452973457, -46.656451389570975], 
                            zoom_start=12, 
                            tiles="Stamen Terrain")

  # ADICIONANDO LAYERS
  footprint_map = add_layers_control(mapobj=footprint_map, 
                                    validator_add_layer=True)

  # ADICIONANDO MAKERS
  footprint = add_markers(mapobj=footprint_map, data=None)

  return footprint_map

def main():

  # CONFIGURANDO O APP
  st.set_page_config(page_title="FOOTPRINT - GESTÃO DO PARQUE DE AGÊNCIAS", 
                     page_icon=":world-map:", 
                     layout="wide", 
                     menu_items={
                                'Get Help': None,
                                'Report a bug': None,
                                'About': "# APP Desenvolvido pela SQUAD Gestão do Parque de Agências"
                            }
                     )

  # ADICIONANDO TITULO DA PÁGINA
  st.title("APP - FOOTPRINT - GESTÃO DO PARQUE DE AGÊNCIAS")

  # ADICIONANDO LOGO
  add_logo(logo_url="http://placekitten.com/120/120")

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
    st.markdown("### Dados do footprint")
    filtered_df = dataframe_explorer(df_footprint, case=False)
    st.dataframe(filtered_df, use_container_width=True)

    # CRIANDO MAPA
    mapobj = load_map()

    # INCLUINDO NO APP
    st.markdown("### Parque de agências")
    st_col1, st_col2 = st.columns(2)
    with st_col1: 
      result_view_sombreamento = st.checkbox("Visualizar sombreamento", 
                                              value=False, 
                                              key=None, 
                                              help=None, 
                                              on_change=None, 
                                              disabled=False, 
                                              label_visibility="visible")
    if result_view_sombreamento:
      with st_col2: 
        raio_sombreamento = st.slider('Raio desejado (em km):', 0, 1000, 5)

    st_data = st_folium(mapobj, width=1000, height=500)

    st_col1, st_col2 = st.columns(2)

    with st_col1:

      st.download_button(
      label="Download dados (csv)",
      data=download_data(df_footprint),
      file_name='FOOTPRINT_DADOS.csv',
      mime='text/csv',
      )

    with st_col2:

      st.button(
          label="Download mapa",
          on_click=download_map(mapobj)
      )

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
