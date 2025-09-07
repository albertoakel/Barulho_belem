import streamlit as st
import pandas as pd
import datetime
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials


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
SHEET_NAME = "BarulhoBelem_DB"
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
# Geolocalização inicial
# =========================
geolocator = Nominatim(user_agent="barulho_belem")
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
        placeholder="Ex: Rua XYZ, 123, Bairro ABC, CEP"
    )

    if endereco_input and endereco_input != st.session_state["endereco_input"]:
        location = geolocator.geocode(endereco_input)
        if location:
            latitude, longitude = location.latitude, location.longitude
            endereco = location.address
            st.session_state["endereco_input"] = endereco
            st.success(f"Endereço localizado: {endereco}")
        else:
            st.warning("Endereço não encontrado. Clique no mapa para selecionar.")

    # Mapa responsivo
    m = folium.Map(location=[latitude, longitude], zoom_start=13)
    folium.Marker([latitude, longitude], tooltip="Local selecionado").add_to(m)
    map_data = st_folium(m, height=400, width="100%")

    if map_data and map_data["last_clicked"]:
        latitude = map_data["last_clicked"]["lat"]
        longitude = map_data["last_clicked"]["lng"]
        try:
            location = geolocator.reverse((latitude, longitude), language="pt")
            if location:
                endereco = location.address
                st.session_state["endereco_input"] = endereco
                st.info(f"Endereço aproximado (mapa): {endereco}")
            else:
                endereco = "Não encontrado"
        except:
            endereco = "Erro na geocodificação"

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
with st.expander("Opções avançadas"):
    if st.button("🗑️ Limpar registros"):
        limpar_registros()
        st.warning("Todos os registros foram apagados.")
