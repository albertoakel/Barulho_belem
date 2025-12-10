import streamlit as st
import pandas as pd
import datetime

import folium
from streamlit_folium import st_folium

from setup import setup_path
setup_path()
from src.google_sheets import *
from src.geocode_belem import *

# =========================
# Configurações da página
# =========================
st.set_page_config(page_title="Registro descartes - Belém", layout="wide")
st.title("📍 Registro Descartes 0.3")

sheet = conectar_sheets("Registro_lixo")

# =========================
# Estado Inicial
# =========================
if "lat" not in st.session_state:
    st.session_state.lat = -1.455833

if "lon" not in st.session_state:
    st.session_state.lon = -48.503889

if "endereco" not in st.session_state:
    st.session_state.endereco = ""

if "endereco_input" not in st.session_state:
    st.session_state.endereco_input = ""

if "trigger_map_update" not in st.session_state:
    st.session_state.trigger_map_update = False


if "mensagem_formulario" not in st.session_state:
    st.session_state.mensagem_formulario = ""

# =========================
# Tabs
# =========================
tab_mapa, tab_form = st.tabs(["🗺️ Mapa", "📋 Formulário"])


# =========================================================
# 🗺️ TAB MAPA
# =========================================================
with tab_mapa:
    st.subheader("Selecione a localização do Descarte")

    endereco_input = st.text_input(
        "Digite o endereço (opcional):",
        value=st.session_state.endereco_input,
        placeholder="Ex: Rua Padre Eutíquio, 100"
    )

    # --- BUSCA PELO ENDEREÇO DIGITADO ---
    if endereco_input and endereco_input != st.session_state.endereco_input:

        busca = buscar_endereco_belem(endereco_input)

        if busca is None:
            st.warning("Endereço não encontrado. Tente ser mais específico.")
        elif busca is False:
            st.error("Endereço encontrado, mas fora de Belém. Corrija novamente.")
        else:
            lat, lon, endereco = busca

            # Atualiza estado global
            st.session_state.lat = lat
            st.session_state.lon = lon
            st.session_state.endereco = endereco
            st.session_state.endereco_input = endereco
            st.session_state.trigger_map_update = True

            st.success(f"Endereço localizado: {endereco}")
            st.session_state.mensagem_formulario = "➡️ Agora vá para a aba **Formulário** para finalizar o envio."
            #st.info("➡️ Agora vá para a aba **Formulário** para finalizar o envio.")
    if st.session_state.mensagem_formulario:
        st.info(st.session_state.mensagem_formulario)

    # --- RENDER DO MAPA ---
    m = folium.Map(
        location=[st.session_state.lat, st.session_state.lon],
        tiles="CartoDB Positron",
        zoom_start=14
    )

    folium.Marker(
        [st.session_state.lat, st.session_state.lon],
        tooltip="Local selecionado"
    ).add_to(m)

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
            st.session_state.lat = lat_click
            st.session_state.lon = lng_click
            st.session_state.endereco = endereco_click
            st.session_state.endereco_input = endereco_click

            st.info(f"Endereço aproximado (mapa): {endereco_click}")
            st.info("➡️ Agora vá para a aba **Formulário** para finalizar o envio.")

        st.session_state.trigger_map_update = True


# =========================================================
# TAB FORMULÁRIO
# =========================================================
with tab_form:
    st.subheader("Informe alguns detalhes ")

    # =========================
    # NOVO → mostrar endereço escolhido
    # =========================
    st.markdown("### 📌 Endereço selecionado:")
    if st.session_state.endereco:
        st.success(st.session_state.endereco)
    else:
        st.warning("Nenhum endereço selecionado ainda. Escolha na aba **Mapa**.")
        st.stop()

    with st.form("registro_Descartes"):
        # Colunas para melhor visualização em celular
        col1, col2 = st.columns(2)
        with col1:
            origem = st.selectbox("Origem do Descarte", [
                "Carroceiro",
                "Domestico",
                "Outros"
            ])
            frequencia = st.selectbox("Frequência", [
                "Todos os dias", "Todos os finais de semana", "Ocasionalmente"
            ])

        with col2:
            horario = st.multiselect("Período em que mais ocorre", ["Manhã", "Tarde", "Noite", "Madrugada"])

        observacoes = st.text_area("Observações adicionais", placeholder="Ex: tipo de lixo,dimensão, caracteristicas, denuncias")

        enviado = st.form_submit_button("✅ Salvar registro")

    if enviado:
        novo_registro = [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.endereco,
            st.session_state.lat,
            st.session_state.lon,
            origem,
            ", ".join(horario),
            observacoes
        ]
        salvar_registro(sheet, novo_registro)
        st.success("✅ Registro salvo com sucesso! Obrigado pela contribuição.")
