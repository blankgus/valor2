import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="SchoolValuation Pro+ v10", layout="wide")
st.title("SchoolValuation Pro+ v10")

# ==============================
# DADOS OPERACIONAIS
# ==============================
st.header("1. Dados Operacionais")
col1, col2 = st.columns(2)
with col1:
    alunos_ei = st.number_input("Alunos - Educacao Infantil", min_value=0, value=22)
    capacidade_ei = st.number_input("Capacidade maxima (EI)", min_value=1, value=36)
    alunos_ef1 = st.number_input("Alunos - Ensino Fundamental I", min_value=0, value=87)
    capacidade_ef1 = st.number_input("Capacidade maxima (EF1)", min_value=1, value=156)
    alunos_ef2 = st.number_input("Alunos - Ensino Fundamental II", min_value=0, value=123)
    capacidade_ef2 = st.number_input("Capacidade maxima (EF2)", min_value=1, value=169)
    alunos_em = st.number_input("Alunos - Ensino Medio", min_value=0, value=66)
    capacidade_em = st.number_input("Capacidade maxima (EM)", min_value=1, value=120)

with col2:
    mensalidade_ei = st.number_input("Mensalidade media (EI)", min_value=0.0, value=1715.0)
    mensalidade_ef1 = st.number_input("Mensalidade media (EF1)", min_value=0.0, value=2055.0)
    mensalidade_ef2 = st.number_input("Mensalidade media (EF2)", min_value=0.0, value=2160.0)
    mensalidade_em = st.number_input("Mensalidade media (EM)", min_value=0.0, value=2450.0)

st.header("2. Custos, Estrutura e Passivos")
col3, col4 = st.columns(2)
with col3:
    custos_diretos_percent = st.slider("Custos diretos (%)", 0, 100, 25) / 100
    despesas_admin_percent = st.slider("Despesas administrativas (%)", 0, 100, 15) / 100
    impostos_percent = st.slider("Impostos (%)", 0, 30, 8) / 100

with col4:
    tem_imovel = st.radio("Imovel proprio?", ("Nao", "Sim"), horizontal=True)
    if tem_imovel == "Sim":
        valor_imovel = st.number_input("Valor de mercado do imovel (R$)", min_value=0.0, value=3000000.0)
        valor_instalacoes = 0.0
    else:
        valor_imovel = 0.0
        aluguel_mensal = st.number_input("Aluguel mensal (R$)", min_value=0.0, value=25000.0)
        valor_instalacoes = st.number_input(
            "Valor estimado das instalacoes (R$)", 
            min_value=0.0, 
            value=500000.0
        )
    divida_fiscal = st.number_input("Dividas fiscais (R$)", min_value=0.0, value=0.0)
    divida_financeira = st.number_input("Dividas financeiras (R$)", min_value=0.0, value=0.0)

multiplo_ebitda = st.slider("Multiplo de EBITDA", 2.0, 10.0, 6.0, step=0.5)

# Cálculos
receita_ei = alunos_ei * mensalidade_ei * 12
receita_ef1 = alunos_ef1 * mensalidade_ef1 * 12
receita_ef2 = alunos_ef2 * mensalidade_ef2 * 12
receita_em = alunos_em * mensalidade_em * 12
receita_total = receita_ei + receita_ef1 + receita_ef2 + receita_em

aluguel_anual = aluguel_mensal * 12 if tem_imovel == "Nao" else 0
custos_diretos = receita_total * custos_diretos_percent
despesas_admin = receita_total * despesas_admin_percent
ebitda_contabil = receita_total - custos_diretos - despesas_admin - aluguel_anual

total_alunos = alunos_ei + alunos_ef1 + alunos_ef2 + alunos_em
capacidade_total = capacidade_ei + capacidade_ef1 + capacidade_ef2 + capacidade_em
taxa_ocupacao = total_alunos / capacidade_total if capacidade_total > 0 else 0
total_passivos = divida_fiscal + divida_financeira

st.header("3. Ajuste de EBITDA")
col_adj1, col_adj2, col_adj3, col_adj4 = st.columns(4)
desp_nao_rec = col_adj1.number_input("Despesas nao recorrentes", value=0.0)
pro_labore_exc = col_adj2.number_input("Pro-labore excedente", value=0.0)
multas = col_adj3.number_input("Multas e juros", value=0.0)
receitas_nao_rec = col_adj4.number_input("Receitas nao recorrentes", value=0.0)

ebitda_ajustado = ebitda_contabil + desp_nao_rec + pro_labore_exc + multas - receitas_nao_rec

valor_ebitda = ebitda_ajustado * multiplo_ebitda
valor_bruto = valor_ebitda + valor_imovel
if tem_imovel == "Nao":
    valor_bruto += valor_instalacoes
valor_liquido = valor_bruto - total_passivos

# ==============================
# RESUMO DOS DADOS
# ==============================
st.subheader("Resumo dos Dados Calculados")
resumo_data = {
    "Item": [
        "Valor Liquido",
        "EBITDA Ajustado",
        "Receita Anual",
        "Total de Alunos",
        "Taxa de Ocupacao",
        "Custos Diretos",
        "Despesas Administrativas",
        "Aluguel Anual",
        "Valor do Imovel",
        "Valor das Instalacoes",
        "Dividas Totais"
    ],
    "Valor": [
        f"R$ {valor_liquido:,.2f}",
        f"R$ {ebitda_ajustado:,.2f}",
        f"R$ {receita_total:,.2f}",
        total_alunos,
        f"{taxa_ocupacao:.1%}",
        f"R$ {custos_diretos:,.2f}",
        f"R$ {despesas_admin:,.2f}",
        f"R$ {aluguel_anual:,.2f}",
        f"R$ {valor_imovel:,.2f}",
        f"R$ {valor_instalacoes:,.2f}",
        f"R$ {total_passivos:,.2f}"
    ]
}
df_resumo = pd.DataFrame(resumo_data)
st.dataframe(df_resumo, use_container_width=True)

# ==============================
# GRAFICOS
# ==============================
st.subheader("Grafico de Ocupacao")
st.progress(int(taxa_ocupacao * 100))
st.caption(f"Ocupacao: {taxa_ocupacao:.1%} ({total_alunos}/{capacidade_total} alunos)")

st.subheader("Distribuicao de Receita por Segmento")
receita_data = {
    "EI": receita_ei,
    "EF1": receita_ef1,
    "EF2": receita_ef2,
    "EM": receita_em
}
st.bar_chart(receita_data)

# ==============================
# DUE DILIGENCE CHECKLIST
# ==============================
st.subheader("Due Diligence Checklist")
checklist = [
    ["Financeiro", "Balanço auditado (3 anos)", "Sim", ""],
    ["Financeiro", "Demonstracao de fluxo de caixa", "Sim", ""],
    ["Financeiro", "Dividas fiscais quitadas", "Sim" if divida_fiscal == 0 else "Nao", ""],
    ["Legal", "Contrato social atualizado", "Sim", ""],
    ["Legal", "Licencas de funcionamento", "Sim", ""],
    ["Legal", "Processos judiciais", "Sim", ""],
    ["Operacional", "Historico de evasao (3 anos)", "Sim", ""],
    ["Operacional", "Contratos de aluguel", "Sim" if tem_imovel == "Nao" else "N/A", ""],
    ["Operacional", "Laudo de avaliacao do imovel", "Sim" if tem_imovel == "Sim" else "N/A", ""],
    ["Pedagogico", "Certificacoes internacionais", "Sim", ""],
    ["Pedagogico", "Curriculo Lattes dos coordenadores", "Sim", ""],
]
df_checklist = pd.DataFrame(checklist, columns=["Categoria", "Item", "Status", "Observacoes"])
st.dataframe(df_checklist, use_container_width=True)

# ==============================
# GERAR PDF COMPLETO (COM FONTE UNICODE)
# ==============================
if st.button("Gerar Relatório Completo em PDF"):
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Adiciona a fonte Unicode
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    
    # Título
    pdf.cell(0, 10, "Relatório de Valuation - Escola", ln=True, align="C")
    pdf.ln(10)
    
    # Resumo
    pdf.cell(0, 10, "Resumo dos Dados Calculados", ln=True)
    for i in range(len(resumo_data["Item"])):
        linha = f"{resumo_data['Item'][i]}: {resumo_data['Valor'][i]}"
        pdf.multi_cell(0, 8, linha)
    
    pdf.ln(5)
    pdf.cell(0, 10, "Due Diligence Checklist", ln=True)
    for item in checklist:
        linha = f"{item[0]} - {item[1]}: {item[2]}"
        pdf.multi_cell(0, 8, linha)
    
    pdf_output = pdf.output(dest="S")
    st.download_button(
        "Baixar Relatório Completo",
        pdf_output,
        "relatorio_valuation_completo.pdf",
        "application/pdf"
    )
# ==============================
# LINK PARA VPS
# ==============================
st.markdown("---")
st.markdown("🔗 **[Gerenciar Escolas no VPS](https://colegiopauliceia.com/school/)**")

