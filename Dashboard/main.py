import streamlit as st
import pandas as pd
import datetime
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Mapa do Barulho - Belém", layout="wide")
st.title("📍 Registro de Barulho em Belém")

# Inicializa DataFrame
if "registros" not in st.session_state:
    st.session_state["registros"] = pd.DataFrame(columns=[
        "Data", "Endereço", "Latitude", "Longitude", "Origem", "Frequência",
        "Intensidade", "Horário", "Duração_horas", "dB", "Observações"
    ])

geolocator = Nominatim(user_agent="barulho_belem")

# Coordenadas iniciais de Belém
latitude, longitude = -1.455833, -48.503889
endereco = ""

# =========================
# Entrada manual de endereço
# =========================
st.subheader("📌 Informe o local do barulho")

if "endereco_input" not in st.session_state:
    st.session_state["endereco_input"] = ""

endereco_input = st.text_input(
    "Digite o endereço (Rua, nº, bairro, CEP) - opcional:",
    value=st.session_state["endereco_input"]
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

# =========================
# Mapa interativo
# =========================
st.subheader("🗺️ Ou clique no mapa para marcar a localização")

m = folium.Map(location=[latitude, longitude], zoom_start=13)
folium.Marker([latitude, longitude], tooltip="Local selecionado").add_to(m)
map_data = st_folium(m, height=600, width=1200)

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
# Formulário de registro
# =========================
with st.form("registro_barulho"):
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
    intensidade = st.radio("Nível de incômodo", ["Baixo", "Médio", "Alto"])
    horario = st.multiselect("Período em que mais ocorre", ["Manhã", "Tarde", "Noite", "Madrugada"])
    duracao = st.slider("Duração média (horas)", 0.0, 12.0, 1.0, step=0.5)
    decibeis = st.number_input("Medição aproximada (dB) - opcional", min_value=0, max_value=150, step=1)
    observacoes = st.text_area("Observações adicionais")

    enviado = st.form_submit_button("Salvar registro")

# =========================
# Salvar registro
# =========================
if enviado:
    if st.session_state["endereco_input"]:
        novo_registro = {
            "Data": datetime.datetime.now(),
            "Endereço": st.session_state["endereco_input"],
            "Latitude": latitude,
            "Longitude": longitude,
            "Origem": origem,
            "Frequência": frequencia,
            "Intensidade": intensidade,
            "Horário": ", ".join(horario),
            "Duração_horas": duracao,
            "dB": decibeis if decibeis > 0 else None,
            "Observações": observacoes
        }
        st.session_state["registros"] = pd.concat(
            [st.session_state["registros"], pd.DataFrame([novo_registro])],
            ignore_index=True
        )

        # ======== Salvar CSV com timestamp ========
        path = '/home/akel/PycharmProjects/Barulho_belem/data/raw/'
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y_%H_%M_%S")
        filename = f"reg_{timestamp}.csv"
        st.session_state["registros"].to_csv(path+filename, index=False)
        st.success(f"✅ Registro salvo com sucesso! ")
        #st.success(f"✅ Registro salvo com sucesso! Arquivo: `{filename}`")

    else:
        st.error("⚠️ Nenhum endereço selecionado. Informe ou clique no mapa.")

# =========================
# Mostrar registros
# =========================
st.subheader("📊 Registros realizados")
st.dataframe(st.session_state["registros"])
