import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

st.set_page_config(page_title="SchoolValuation Pro+ v7", layout="wide")
st.title("🏫 SchoolValuation Pro+ v7")
st.markdown("Valuation profissional com salvamento e PDF.")

# ==============================
# LISTAR ESCOLAS SALVAS
# ==============================
st.header("🏫 Escolas Cadastradas")
try:
    response = requests.get("https://colegiopauliceia.com/school/api.php?secret=10XP20to30", timeout=5)
    if response.status_code == 200:
        schools = response.json()
        if schools:
            df = pd.DataFrame(schools)
            st.dataframe(df[['name', 'estado', 'valor_liquido']].rename(columns={
                'name': 'Nome', 'estado': 'Estado', 'valor_liquido': 'Valor Líquido'
            }).style.format({'Valor Líquido': 'R$ {:,.0f}'}))
        else:
            st.info("Nenhuma escola cadastrada.")
    else:
        st.warning("Não foi possível carregar escolas.")
except:
    st.info("Lista temporariamente indisponível.")

# ==============================
# VALUATION
# ==============================
st.header("1. Dados Operacionais")
col1, col2 = st.columns(2)
with col1:
    alunos_ei = st.number_input("Alunos - EI", min_value=0, value=100)
    capacidade_ei = st.number_input("Capacidade (EI)", min_value=1, value=120)
    alunos_ef1 = st.number_input("Alunos - EF1", min_value=0, value=120)
    capacidade_ef1 = st.number_input("Capacidade (EF1)", min_value=1, value=140)
    alunos_ef2 = st.number_input("Alunos - EF2", min_value=0, value=100)
    capacidade_ef2 = st.number_input("Capacidade (EF2)", min_value=1, value=120)
    alunos_em = st.number_input("Alunos - EM", min_value=0, value=80)
    capacidade_em = st.number_input("Capacidade (EM)", min_value=1, value=100)

with col2:
    mensalidade_ei = st.number_input("Mensalidade (EI)", min_value=0.0, value=600.0
