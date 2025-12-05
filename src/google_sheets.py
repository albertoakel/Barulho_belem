import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st


# =============================
# Conexão
# =============================
def conectar_sheets(sheet_name="BarulhoBelem"):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive", ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope)

    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet


# =============================
# Operações
# =============================
def salvar_registro(sheet, dados):
    sheet.append_row(dados)

def carregar_registros(sheet):
    registros = sheet.get_all_records()
    return pd.DataFrame(registros)

def limpar_registros(sheet):
    sheet.clear()
    sheet.append_row([
        "Data", "Endereço", "Latitude", "Longitude", "Origem",
        "Frequência", "Intensidade", "Horário", "Duração_horas",
        "dB", "Observações"
    ])