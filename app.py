import streamlit as st
import pandas as pd
import requests
import os

# Nova URL da API (subdomínio sem proxy)
API_URL = "https://api.colegiopauliceia.com/schoolvalor-api/api.php"
API_SECRET = os.getenv("API_SECRET", "10XP20to30")

def get_schools():
    try:
        response = requests.get(f"{API_URL}?secret={API_SECRET}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro HTTP {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Erro de conexão: {str(e)}")
        return []

def save_school(name, estado, valor):
    try:
        response = requests.post(
            f"{API_URL}?secret={API_SECRET}",
            json={"name": name, "estado": estado, "valor_liquido": valor},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- APP ---
st.title("🏫 SchoolValuation Pro+")

# Listar escolas
schools = get_schools()
if schools:
    df = pd.DataFrame(schools)
    st.dataframe(df[['name', 'estado', 'valor_liquido']])

# Formulário
name = st.text_input("Nome da Escola")
estado = st.selectbox("Estado", ["SP", "RJ", "MG"])
valor = st.number_input("Valor Líquido", min_value=0.0)

if st.button("Salvar"):
    if not name:
        st.error("Nome é obrigatório!")
    else:
        result = save_school(name, estado, valor)
        if "error" in result:
            st.error(f"Erro: {result['error']}")
        else:
            st.success("✅ Salvo com sucesso!")
            st.experimental_rerun()

