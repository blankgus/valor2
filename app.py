import streamlit as st
import pandas as pd

st.title("🏫 SchoolValuation Pro+ v7")
st.success("✅ App carregado com sucesso!")

# Simular lista de escolas
st.header("🏫 Escolas Cadastradas")
schools = [
    {"Nome": "Escola A", "Estado": "SP", "Valor": 1500000},
    {"Nome": "Escola B", "Estado": "RJ", "Valor": 950000}
]
df = pd.DataFrame(schools)
st.dataframe(df.style.format({"Valor": "R$ {:,.0f}"}))

# Valuation
st.header("✅ Valor Final")
valor = st.number_input("Valor Líquido (R$)", value=1000000)
st.metric("Valor Líquido", f"R$ {valor:,.0f}")

# Gráfico
st.subheader("📊 Gráfico de Ocupação")
st.progress(85)
st.caption("Ocupação: 85%")
