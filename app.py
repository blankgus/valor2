import streamlit as st
import pandas as pd
import requests
import os

API_URL = "https://www.colegiopauliceia.com/schoolvalor-api/api.php"
API_SECRET = os.getenv("API_SECRET", "10XP20to30")

def get_schools():
    try:
        response = requests.get(f"{API_URL}?secret={API_SECRET}", timeout=10)
        return response.json() if response.status_code == 200 else []
    except:
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
st.title("🏫 Cadastro de Escolas (Teste)")

# Listar
st.subheader("Escolas Cadastradas")
schools = get_schools()
if schools:
    df = pd.DataFrame(schools)
    st.dataframe(df[['name', 'estado', 'valor_liquido']])

# Formulário
st.subheader("Cadastrar Nova Escola")
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
