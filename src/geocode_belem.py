from opencage.geocoder import OpenCageGeocode
from functools import lru_cache
import streamlit as st
# =============================
# Inicialização do Geocoder
# =============================
geocoder = OpenCageGeocode(st.secrets["OPENCAGE_API"]["OPENCAGE_API_KEY"])


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


# =============================
# Funções com cache
# =============================
@lru_cache(maxsize=2000)
def geocode_cached(query):
    return geocoder.geocode(
        query,
        country_code="br",
        bounds=(-1.479, -48.50, -1.057, -48.33))


@lru_cache(maxsize=5000)
def reverse_cached(lat, lng):
    return geocoder.reverse_geocode(lat, lng, language="pt")



def buscar_endereco_belem(endereco_raw: str):
    """
    Geocodifica dentro de Belém usando cache + validação.
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
    Reverse geocode dentro de Belém.
    """
    #result = geocoder.reverse_geocode(lat, lng, language="pt")
    result=reverse_cached(lat, lng)

    if not result:
        return None

    if not validar_localizacao_belem(result):
        return False

    return result[0]["formatted"]