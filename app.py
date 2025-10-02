import streamlit as st
import pandas as pd

st.set_page_config(page_title="SchoolValuation Pro+ v9", layout="wide")
st.title("🏫 SchoolValuation Pro+ v9")

# Links para cadastro
st.markdown("🔗 **[Cadastrar Nova Escola](https://colegiopauliceia.com/school/cadastro.html)**")
st.markdown("🔗 **[Ver Escolas Cadastradas](https://colegiopauliceia.com/school/cadastro.html)**")

# Valuation básico
st.header("1. Dados Operacionais")
alunos = st.number_input("Total de Alunos", min_value=0, value=400)
mensalidade = st.number_input("Mensalidade Média (R$)", min_value=0.0, value=1000.0)
receita_anual = alunos * mensalidade * 12

st.header("2. Custos e Estrutura")
custos_percent = st.slider("Custos (%)", 0, 100, 60) / 100
ebitda = receita_anual * (1 - custos_percent)

st.header("✅ Resultado")
st.metric("Receita Anual", f"R$ {receita_anual:,.0f}")
st.metric("EBITDA", f"R$ {ebitda:,.0f}")

# Gráfico simples
st.subheader("📊 Gráfico de Receita vs. Custos")
st.bar_chart({"Receita": [receita_anual], "Custos": [receita_anual * custos_percent]})
