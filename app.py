import streamlit as st
import pandas as pd
import requests
import os

# Configuração
API_URL = "https://colegiopauliceia.com/schoolvalor-api/api.php"
API_SECRET = os.getenv("API_SECRET", "fallback_temporario")

# ==============================
# FUNÇÕES DE INTEGRAÇÃO COM A API (FICAM AQUI!)
# ==============================
def get_schools_from_api():
    """Busca lista de escolas da API no seu VPS"""
    try:
        response = requests.get(f"{API_URL}?secret={API_SECRET}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão com API: {str(e)}")
        if 'response' in locals():
            st.code(f"Resposta bruta: {response.text[:300]}...")
        return []
    except ValueError:
        st.error("❌ Resposta inválida da API (não é JSON)")
        if 'response' in locals():
            st.code(f"Resposta recebida: {response.text[:500]}")
        return []

def save_school_to_api(name, estado, valor_liquido):
    """Salva escola na API do seu VPS"""
    try:
        response = requests.post(
            f"{API_URL}?secret={API_SECRET}",
            json={"name": name, "estado": estado, "valor_liquido": valor_liquido},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==============================
# APP PRINCIPAL (Streamlit)
# ==============================
st.title("SchoolValuation Pro+")

# Listar escolas
schools = get_schools_from_api()
if schools:
    st.dataframe(pd.DataFrame(schools))

# Formulário
name = st.text_input("Nome da Escola")
estado = st.selectbox("Estado", ["SP", "RJ"])
valor = st.number_input("Valor")

if st.button("Salvar"):
    result = save_school_to_api(name, estado, valor)
    if "error" in result:
        st.error(f"Erro: {result['error']}")
    else:
        st.success("Salvo!")



