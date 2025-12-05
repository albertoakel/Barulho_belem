import streamlit as st
import pandas as pd
import datetime
#from geopy.geocoders import Nominatim
from opencage.geocoder import OpenCageGeocode
from functools import lru_cache


import folium
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials


import streamlit as st
#vs_cel
# =========================
# Configurações da página
# =========================
st.set_page_config(page_title="Mapa do Barulho - Belém", layout="wide")
st.title("📍 Registro de Barulho em Belém 0.9")

# =========================
# Google Sheets
# =========================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
SHEET_NAME = "BarulhoBelem"
sheet = client.open(SHEET_NAME).sheet1

def salvar_registro(dados):
    sheet.append_row(dados)

def carregar_registros():
    registros = sheet.get_all_records()
    return pd.DataFrame(registros)

def limpar_registros():
    sheet.clear()
    sheet.append_row(["Data", "Endereço", "Latitude", "Longitude", "Origem",
                      "Frequência", "Intensidade", "Horário", "Duração_horas",
                      "dB", "Observações"])

# =========================
# Funções de Geolocalização - Belém
# =========================
def padronizar_endereco_belem(endereco_raw: str) -> str:
    """
    Garante que a busca seja feita em Belém, PA.
    """
    if not endereco_raw:
        return ""

    endereco_raw = endereco_raw.strip()

    # Se o usuário já digitou cidade ou estado, não modifica
    termos_belem = ["belém", "belem", "pará", "pa", "brasil"]
    if any(t in endereco_raw.lower() for t in termos_belem):
        return endereco_raw

    # Caso contrário, força busca dentro de Belém
    return f"{endereco_raw}, Belém, Pará, Brasil"


def validar_localizacao_belem(result):
    """
    Checa se o resultado do OpenCage está realmente dentro de Belém.
    """
    if not result:
        return False

    comp = result[0].get("components", {})
    cidade = comp.get("city") or comp.get("town") or comp.get("municipality") or ""

    return cidade.lower() in ["belém", "belem"]


def buscar_endereco_belem(endereco_raw: str):
    """
    Faz a busca pelo endereço no OpenCage, forçando Belém e validando retorno.
    """
    endereco_padrao = padronizar_endereco_belem(endereco_raw)
    #result = geocoder.geocode(endereco_padrao)
    result = geocode_cached(endereco_padrao)


    if not result:
        return None  # nada encontrado

    if not validar_localizacao_belem(result):
        return False  # encontrado fora de Belém

    lat = result[0]["geometry"]["lat"]
    lng = result[0]["geometry"]["lng"]
    end_formatado = result[0]["formatted"]

    return lat, lng, end_formatado


def reverse_buscando_belem(lat, lng):
    """
    Inverso: a partir da coordenada, tenta obter endereço dentro de Belém.
    """
    #result = geocoder.reverse_geocode(lat, lng, language="pt")
    result=reverse_cached(lat, lng, language="pt")

    if not result:
        return None

    if not validar_localizacao_belem(result):
        return False

    return result[0]["formatted"]


# =========================
# Geolocalização inicial
# =========================
#geolocator = Nominatim(user_agent="barulho_belem")
geocoder = OpenCageGeocode(st.secrets["OPENCAGE_API"]["OPENCAGE_API_KEY"])

@lru_cache(maxsize=2000)
def geocode_cached(query):
    return geocoder.geocode(
        query,
        country_code="br",
        bounds=(-1.479, -48.50, -1.057, -48.33)   # Belém e região
    )

@lru_cache(maxsize=5000)
def reverse_cached(lat, lng):
    return geocoder.reverse_geocode(lat, lng, language="pt")
latitude, longitude = -1.455833, -48.503889
endereco = ""

if "endereco_input" not in st.session_state:
    st.session_state["endereco_input"] = ""

# =========================
# Tabs para melhor UX
# =========================
tab_mapa, tab_form = st.tabs(["🗺️ Mapa", "📋 Formulário"])

# =========================
# Tab Mapa
# =========================
with tab_mapa:
    st.subheader("Selecione a localização do barulho")

    endereco_input = st.text_input(
        "Digite o endereço (opcional):",
        value=st.session_state["endereco_input"],
        placeholder="Ex: Rua Padre Eutíquio, 100"
    )

    # --- BUSCA PELO ENDEREÇO DIGITADO ---
    if endereco_input and endereco_input != st.session_state["endereco_input"]:

        busca = buscar_endereco_belem(endereco_input)

        if busca is None:
            st.warning("Endereço não encontrado. Tente ser mais específico.")
        elif busca is False:
            st.error("Endereço encontrado, mas fora de Belém. Corrija novamente.")
        else:
            latitude, longitude, endereco = busca
            st.session_state["endereco_input"] = endereco
            st.success(f"Endereço localizado: {endereco}")

    # --- MAPA ---
    m = folium.Map(location=[latitude, longitude], zoom_start=13)
    folium.Marker([latitude, longitude], tooltip="Local selecionado").add_to(m)
    map_data = st_folium(m, height=400, width="100%")

    # --- CLIQUE NO MAPA ---
    if map_data and map_data.get("last_clicked"):
        lat_click = map_data["last_clicked"]["lat"]
        lng_click = map_data["last_clicked"]["lng"]

        endereco_click = reverse_buscando_belem(lat_click, lng_click)

        if endereco_click is None:
            st.warning("Não foi possível identificar endereço neste ponto.")
        elif endereco_click is False:
            st.error("O ponto clicado não está em Belém. Escolha outro.")
        else:
            latitude, longitude = lat_click, lng_click
            endereco = endereco_click
            st.session_state["endereco_input"] = endereco
            st.info(f"Endereço aproximado (mapa): {endereco}")

# with tab_mapa:
#     st.subheader("Selecione a localização do barulho")
#     endereco_input = st.text_input(
#         "Digite o endereço (opcional):",
#         value=st.session_state["endereco_input"],
#         placeholder="Ex: Rua XYZ, 123, Bairro ABC, CEP"
#     )
#
#     if endereco_input and endereco_input != st.session_state["endereco_input"]:
#         #location = geolocator.geocode(endereco_input)
#         result = geocoder.geocode(endereco_input)
#         if result:
#             latitude = result[0]['geometry']['lat']
#             longitude = result[0]['geometry']['lng']
#             endereco = result[0]['formatted']
#             #latitude, longitude = location.latitude, location.longitude
#             #endereco = location.address
#             st.session_state["endereco_input"] = endereco
#             st.success(f"Endereço localizado: {endereco}")
#         else:
#             st.warning("Endereço não encontrado. Clique no mapa para selecionar.")
#
#     # Mapa responsivo
#     m = folium.Map(location=[latitude, longitude], zoom_start=13)
#     folium.Marker([latitude, longitude], tooltip="Local selecionado").add_to(m)
#     map_data = st_folium(m, height=400, width="100%")
#
#     if map_data and map_data["last_clicked"]:
#         latitude = map_data["last_clicked"]["lat"]
#         longitude = map_data["last_clicked"]["lng"]
#         try:
#             #location = geolocator.reverse((latitude, longitude), language="pt")
#             result = geocoder.reverse_geocode(latitude, longitude, language='pt')
#             if result:
#                 endereco = result[0]['formatted']
#                 #endereco = location.address
#                 st.session_state["endereco_input"] = endereco
#                 st.info(f"Endereço aproximado (mapa): {endereco}")
#             else:
#                 endereco = "Não encontrado"
#         except:
#             endereco = "Erro na geocodificação"

# =========================
# Tab Formulário
# =========================
with tab_form:
    st.subheader("Informe os detalhes do barulho")
    with st.form("registro_barulho"):
        # Colunas para melhor visualização em celular
        col1, col2 = st.columns(2)
        with col1:
            origem = st.selectbox("Origem do barulho", [
                "Som de carro (propaganda)",
                "Autofalantes em residências",
                "Festa em bares",
                "Paredão, Trio e Aparelhagens",
                "Trânsito intenso (ônibus, motos, buzinas)",
                "Obras/Construção",
                "Eventos públicos (igreja, procissão, shows)",
                "Outros"
            ])
            frequencia = st.selectbox("Frequência", [
                "Todos os dias", "Todos os finais de semana", "Ocasionalmente"
            ])
            intensidade = st.radio("Nível de incômodo", ["Baixo", "Médio", "Alto"], horizontal=True)
        with col2:
            horario = st.multiselect("Período em que mais ocorre", ["Manhã", "Tarde", "Noite", "Madrugada"])
            duracao = st.slider("Duração média (horas)", 0.0, 12.0, 1.0, step=0.5)
            decibeis = st.number_input("Medição aproximada (dB) - opcional", min_value=0, max_value=150, step=1)

        observacoes = st.text_area("Observações adicionais", placeholder="Ex: Som contínuo, barulho alto em finais de semana")

        enviado = st.form_submit_button("✅ Salvar registro")

    if enviado:
        if st.session_state["endereco_input"]:
            novo_registro = [
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                st.session_state["endereco_input"],
                latitude,
                longitude,
                origem,
                frequencia,
                intensidade,
                ", ".join(horario),
                duracao,
                decibeis if decibeis > 0 else "",
                observacoes
            ]
            salvar_registro(novo_registro)
            st.success("✅ Registro salvo com sucesso!")
        else:
            st.error("⚠️ Nenhum endereço selecionado. Informe ou clique no mapa.")

# =========================
# Opções avançadas
# =========================
# with st.expander("Opções avançadas"):
#     if st.button("🗑️ Limpar registros"):
#         limpar_registros()
#         st.warning("Todos os registros foram apagados.")


# import streamlit as st
# import pandas as pd
# import datetime
# from geopy.geocoders import Nominatim
# import folium
# from streamlit_folium import st_folium
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
#
# ##vs. 0.9
#
# st.set_page_config(page_title="Mapa do Barulho - Belém", layout="wide")
# st.title("📍 Registro de Barulho em Belém 0.9")
#
# # =========================
# # Configuração Google Sheets
# # =========================
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
# client = gspread.authorize(creds)
#
# # Abrir planilha
# SHEET_NAME = "BarulhoBelem_DB"
# sheet = client.open(SHEET_NAME).sheet1
#
# def salvar_registro(dados):
#     sheet.append_row(dados)
#
# def carregar_registros():
#     registros = sheet.get_all_records()
#     return pd.DataFrame(registros)
#
# def limpar_registros():
#     sheet.clear()
#     sheet.append_row(["Data", "Endereço", "Latitude", "Longitude", "Origem",
#                       "Frequência", "Intensidade", "Horário", "Duração_horas",
#                       "dB", "Observações"])
#
# # =========================
# # Geolocalização inicial
# # =========================
# geolocator = Nominatim(user_agent="barulho_belem")
# latitude, longitude = -1.455833, -48.503889
# endereco = ""
#
# if "endereco_input" not in st.session_state:
#     st.session_state["endereco_input"] = ""
#
# # =========================
# # Entrada manual
# # =========================
# st.subheader("📌 Informe o local do barulho")
# endereco_input = st.text_input(
#     "Digite o endereço (Rua, nº, bairro, CEP) - opcional:",
#     value=st.session_state["endereco_input"]
# )
#
# if endereco_input and endereco_input != st.session_state["endereco_input"]:
#     location = geolocator.geocode(endereco_input)
#     if location:
#         latitude, longitude = location.latitude, location.longitude
#         endereco = location.address
#         st.session_state["endereco_input"] = endereco
#         st.success(f"Endereço localizado: {endereco}")
#     else:
#         st.warning("Endereço não encontrado. Clique no mapa para selecionar.")
#
# # =========================
# # Mapa interativo
# # =========================
# st.subheader("🗺️ Ou clique no mapa para marcar a localização")
#
# m = folium.Map(location=[latitude, longitude], zoom_start=13)
# folium.Marker([latitude, longitude], tooltip="Local selecionado").add_to(m)
# map_data = st_folium(m, height=400, width=700)
#
# if map_data and map_data["last_clicked"]:
#     latitude = map_data["last_clicked"]["lat"]
#     longitude = map_data["last_clicked"]["lng"]
#     try:
#         location = geolocator.reverse((latitude, longitude), language="pt")
#         if location:
#             endereco = location.address
#             st.session_state["endereco_input"] = endereco
#             st.info(f"Endereço aproximado (mapa): {endereco}")
#         else:
#             endereco = "Não encontrado"
#     except:
#         endereco = "Erro na geocodificação"
#
# # =========================
# # Formulário de registro
# # =========================
# with st.form("registro_barulho"):
#     origem = st.selectbox("Origem do barulho", [
#         "Som de carro (propaganda)",
#         "Autofalantes em residências",
#         "Festa em bares",
#         "Paredão, Trio e Aparelhagens",
#         "Trânsito intenso (ônibus, motos, buzinas)",
#         "Obras/Construção",
#         "Eventos públicos (igreja, procissão, shows)",
#         "Outros"
#     ])
#     frequencia = st.selectbox("Frequência", [
#         "Todos os dias", "Todos os finais de semana", "Ocasionalmente"
#     ])
#     intensidade = st.radio("Nível de incômodo", ["Baixo", "Médio", "Alto"])
#     horario = st.multiselect("Período em que mais ocorre", ["Manhã", "Tarde", "Noite", "Madrugada"])
#     duracao = st.slider("Duração média (horas)", 0.0, 12.0, 1.0, step=0.5)
#     decibeis = st.number_input("Medição aproximada (dB) - opcional", min_value=0, max_value=150, step=1)
#     observacoes = st.text_area("Observações adicionais")
#
#     enviado = st.form_submit_button("Salvar registro")
#
# if enviado:
#     if st.session_state["endereco_input"]:
#         novo_registro = [
#             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             st.session_state["endereco_input"],
#             latitude,
#             longitude,
#             origem,
#             frequencia,
#             intensidade,
#             ", ".join(horario),
#             duracao,
#             decibeis if decibeis > 0 else "",
#             observacoes
#         ]
#         salvar_registro(novo_registro)
#         st.success("✅ Obrigado pelo Registro!")
#     else:
#         st.error("⚠️ Nenhum endereço selecionado. Informe ou clique no mapa.")
#
# # =========================
# # Mostrar registros
# # =========================
# #st.subheader("📊 Registros realizados")
# #df = carregar_registros()
# #st.dataframe(df)
#
# # Botão para baixar registros em CSV
# #csv_bytes = df.to_csv(index=False).encode("utf-8")
# #st.download_button("⬇️ Baixar registros em CSV", csv_bytes, "registros.csv", "text/csv")
#
## # Botão para limpar planilha
## if st.button("🗑️ Limpar registros"):
##     limpar_registros()
##     st.warning("Todos os registros foram apagados.")
