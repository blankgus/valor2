import streamlit as st
import pandas as pd
import requests

st.title("🏫 SchoolValuation Pro+ v8")
st.markdown("✅ App carregado com sucesso!")

# Link para cadastro
st.markdown("🔗 [Cadastrar Nova Escola](https://colegiopauliceia.com/school/cadastro.html)")

# Listar escolas
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
        st.error(f"Erro HTTP {response.status_code}")
except Exception as e:
    st.error(f"Erro de conexão: {str(e)}")
