import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
from datetime import datetime

st.set_page_config(page_title="SchoolValuation Pro+ v10", layout="wide")
st.title("🏫 SchoolValuation Pro+ v10")

# ==============================
# VALUATION COMPLETO
# ==============================
st.header("1. Dados Operacionais")
col1, col2 = st.columns(2)
with col1:
    alunos_ei = st.number_input("Alunos - Educação Infantil", min_value=0, value=100)
    capacidade_ei = st.number_input("Capacidade máxima (EI)", min_value=1, value=120)
    alunos_ef1 = st.number_input("Alunos - Ensino Fundamental I", min_value=0, value=120)
    capacidade_ef1 = st.number_input("Capacidade máxima (EF1)", min_value=1, value=140)
    alunos_ef2 = st.number_input("Alunos - Ensino Fundamental II", min_value=0, value=100)
    capacidade_ef2 = st.number_input("Capacidade máxima (EF2)", min_value=1, value=120)
    alunos_em = st.number_input("Alunos - Ensino Médio", min_value=0, value=80)
    capacidade_em = st.number_input("Capacidade máxima (EM)", min_value=1, value=100)

with col2:
    mensalidade_ei = st.number_input("Mensalidade média (EI)", min_value=0.0, value=600.0)
    mensalidade_ef1 = st.number_input("Mensalidade média (EF1)", min_value=0.0, value=750.0)
    mensalidade_ef2 = st.number_input("Mensalidade média (EF2)", min_value=0.0, value=900.0)
    mensalidade_em = st.number_input("Mensalidade média (EM)", min_value=0.0, value=1100.0)

st.header("2. Custos, Estrutura e Passivos")
col3, col4 = st.columns(2)
with col3:
    custos_diretos_percent = st.slider("Custos diretos (%)", 0, 100, 40) / 100
    despesas_admin_percent = st.slider("Despesas administrativas (%)", 0, 100, 15) / 100
    impostos_percent = st.slider("Impostos (%)", 0, 30, 8) / 100

with col4:
    tem_imovel = st.radio("Imóvel próprio?", ("Não", "Sim"), horizontal=True)
    if tem_imovel == "Sim":
        valor_imovel = st.number_input("Valor de mercado do imóvel (R$)", min_value=0.0, value=3000000.0)
        valor_instalacoes = 0.0
    else:
        valor_imovel = 0.0
        aluguel_mensal = st.number_input("Aluguel mensal (R$)", min_value=0.0, value=25000.0)
        valor_instalacoes = st.number_input(
            "Valor estimado das instalações (R$)", 
            min_value=0.0, 
            value=500000.0,
            help="Ex: laboratórios, quadras, mobiliário, tecnologia."
        )
    divida_fiscal = st.number_input("Dívidas fiscais (R$)", min_value=0.0, value=0.0)
    divida_financeira = st.number_input("Dívidas financeiras (R$)", min_value=0.0, value=0.0)

multiplo_ebitda = st.slider("Múltiplo de EBITDA", 2.0, 10.0, 6.0, step=0.5)

# Cálculos
receita_ei = alunos_ei * mensalidade_ei * 12
receita_ef1 = alunos_ef1 * mensalidade_ef1 * 12
receita_ef2 = alunos_ef2 * mensalidade_ef2 * 12
receita_em = alunos_em * mensalidade_em * 12
receita_total = receita_ei + receita_ef1 + receita_ef2 + receita_em

aluguel_anual = aluguel_mensal * 12 if tem_imovel == "Não" else 0
custos_diretos = receita_total * custos_diretos_percent
despesas_admin = receita_total * despesas_admin_percent
ebitda_contabil = receita_total - custos_diretos - despesas_admin - aluguel_anual

total_alunos = alunos_ei + alunos_ef1 + alunos_ef2 + alunos_em
capacidade_total = capacidade_ei + capacidade_ef1 + capacidade_ef2 + capacidade_em
taxa_ocupacao = total_alunos / capacidade_total if capacidade_total > 0 else 0
total_passivos = divida_fiscal + divida_financeira

st.header("3. Ajuste de EBITDA")
col_adj1, col_adj2, col_adj3, col_adj4 = st.columns(4)
desp_nao_rec = col_adj1.number_input("Despesas não recorrentes", value=0.0)
pro_labore_exc = col_adj2.number_input("Pró-labore excedente", value=0.0)
multas = col_adj3.number_input("Multas e juros", value=0.0)
receitas_nao_rec = col_adj4.number_input("Receitas não recorrentes", value=0.0)

ebitda_ajustado = ebitda_contabil + desp_nao_rec + pro_labore_exc + multas - receitas_nao_rec

valor_ebitda = ebitda_ajustado * multiplo_ebitda
valor_bruto = valor_ebitda + valor_imovel
if tem_imovel == "Não":
    valor_bruto += valor_instalacoes
valor_liquido = valor_bruto - total_passivos

# ==============================
# RESULTADO FINAL COM GRÁFICOS
# ==============================
st.header("✅ Valor Final")
st.metric("Valor Líquido", f"R$ {valor_liquido:,.0f}")

st.subheader("📊 Gráfico de Ocupação")
st.progress(int(taxa_ocupacao * 100))
st.caption(f"Ocupação: {taxa_ocupacao:.1%} ({total_alunos}/{capacidade_total} alunos)")

# ==============================
# GERAR RELATÓRIO EM PDF COMPLETO
# ==============================
if st.button("📄 Gerar Relatório Completo em PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Valuation - Escola", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(0, 10, f"Valor Líquido: R$ {valor_liquido:,.2f}", ln=True)
    pdf.cell(0, 10, f"EBITDA Ajustado: R$ {ebitda_ajustado:,.2f}", ln=True)
    pdf.cell(0, 10, f"Receita Anual Total: R$ {receita_total:,.2f}", ln=True)
    pdf.cell(0, 10, f"Total de Alunos: {total_alunos}", ln=True)
    pdf.cell(0, 10, f"Taxa de Ocupação: {taxa_ocupacao:.1%}", ln=True)
    pdf.cell(0, 10, f"Custos Diretos: R$ {custos_diretos:,.2f}", ln=True)
    pdf.cell(0, 10, f"Despesas Administrativas: R$ {despesas_admin:,.2f}", ln=True)
    pdf.cell(0, 10, f"Aluguel Anual: R$ {aluguel_anual:,.2f}", ln=True)
    pdf.cell(0, 10, f"Valor do Imóvel: R$ {valor_imovel:,.2f}", ln=True)
    pdf.cell(0, 10, f"Valor das Instalações: R$ {valor_instalacoes:,.2f}", ln=True)
    pdf.cell(0, 10, f"Dívidas Totais: R$ {total_passivos:,.2f}", ln=True)
    
    # Output
    pdf_output = pdf.output(dest="S").encode("latin-1")
    st.download_button(
        "📥 Baixar PDF Completo",
        pdf_output,
        "relatorio_valuation_completo.pdf",
        "application/pdf"
    )

# ==============================
# LINKS PARA O VPS (opcional)
# ==============================
st.markdown("---")
st.markdown("🔗 **[Cadastrar Escola no Sistema](https://colegiopauliceia.com/school/cadastro.html)**")
st.markdown("🔗 **[Ver Escolas Cadastradas](https://colegiopauliceia.com/school/cadastro.html)**")
