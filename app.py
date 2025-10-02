import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
from datetime import datetime

st.set_page_config(page_title="SchoolValuation Pro", layout="wide")
st.title("🏫 SchoolValuation Pro")

# ==============================
# DADOS OPERACIONAIS
# ==============================
st.header("1. Dados da Escola")
col1, col2 = st.columns(2)
with col1:
    total_alunos = st.number_input("Total de Alunos", min_value=0, value=400)
    mensalidade_media = st.number_input("Mensalidade Média (R$)", min_value=0.0, value=1000.0)
with col2:
    custos_percent = st.slider("Custos (%)", 0, 100, 60) / 100
    valor_imovel = st.number_input("Valor do Imóvel (R$)", min_value=0.0, value=3000000.0)

# Cálculos
receita_anual = total_alunos * mensalidade_media * 12
ebitda = receita_anual * (1 - custos_percent)
valor_liquido = ebitda * 6 + valor_imovel  # múltiplo fixo para simplicidade

# ==============================
# RESULTADO
# ==============================
st.header("✅ Resultado do Valuation")
st.metric("Receita Anual", f"R$ {receita_anual:,.0f}")
st.metric("EBITDA", f"R$ {ebitda:,.0f}")
st.metric("Valor Líquido", f"R$ {valor_liquido:,.0f}")

# Gráfico
st.subheader("📊 Gráfico")
st.bar_chart({"Receita": [receita_anual], "Custos": [receita_anual * custos_percent]})

# ==============================
# RESUMO E DUE DILIGENCE
# ==============================
st.subheader("📋 Resumo dos Dados")
resumo = pd.DataFrame({
    "Item": ["Alunos", "Mensalidade", "Receita", "EBITDA", "Valor Líquido"],
    "Valor": [total_alunos, f"R$ {mensalidade_media:,.0f}", f"R$ {receita_anual:,.0f}", f"R$ {ebitda:,.0f}", f"R$ {valor_liquido:,.0f}"]
})
st.dataframe(resumo, use_container_width=True)

st.subheader("🔍 Due Diligence")
checklist = pd.DataFrame({
    "Documento": [
        "Balanço Auditado",
        "Licenças de Funcionamento",
        "Histórico de Evasão",
        "Laudo do Imóvel"
    ],
    "Status": ["✅", "✅", "✅", "✅"]
})
st.dataframe(checklist, use_container_width=True)

# ==============================
# PDF COMPLETO
# ==============================
if st.button("📄 Gerar Relatório em PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Valuation", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(0, 10, f"Alunos: {total_alunos}", ln=True)
    pdf.cell(0, 10, f"Mensalidade Média: R$ {mensalidade_media:,.2f}", ln=True)
    pdf.cell(0, 10, f"Receita Anual: R$ {receita_anual:,.2f}", ln=True)
    pdf.cell(0, 10, f"EBITDA: R$ {ebitda:,.2f}", ln=True)
    pdf.cell(0, 10, f"Valor Líquido: R$ {valor_liquido:,.2f}", ln=True)
    pdf_output = pdf.output(dest="S").encode("latin-1")
    
    st.download_button(
        "📥 Baixar PDF",
        pdf_output,
        "valuation_relatorio.pdf",
        "application/pdf"
    )

# ==============================
# LINK PARA VPS (opcional)
# ==============================
st.markdown("---")
st.markdown("🔗 **[Gerenciar Documentos no VPS](https://colegiopauliceia.com/school/)**")
