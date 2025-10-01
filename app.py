import streamlit as st
import requests

st.title("SchoolValuation Pro+ v8")

# Teste direto
try:
    response = requests.get("https://colegiopauliceia.com/school/api.php?secret=10XP20to30")
    st.write(f"Status: {response.status_code}")
    st.write(f"Resposta: {response.text[:100]}")
except Exception as e:
    st.error(f"Erro: {str(e)}")
