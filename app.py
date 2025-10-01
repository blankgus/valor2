import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

st.set_page_config(page_title="SchoolValuation Pro+ v8", layout="wide")
st.title("🏫 SchoolValuation Pro+ v8")

# ==============================
# LINKS IMPORTANTES
# ==============================
st.markdown("🔗 **[Cadastrar Nova Escola](https://colegiopauliceia.com/school/cadastro.html)**")
st.markdown("🔗 **[Ver Escolas Cadastradas](https://colegiopauliceia.com/school/cadastro.html)**")

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
            # Garantir que as colunas existam
            cols_to_show = ['name', 'estado', 'valor_liquido']
            cols_available = [col for col in cols_to_show if col in df.columns]
            if cols_available:
                st.dataframe(df[cols_available].rename(columns={
                    'name': 'Nome', 'estado': 'Estado', 'valor_liquido': 'Valor Líquido'
                }).style.format({'Valor Líquido': 'R$ {:,.0f}'}))
            else:
                st.info("Nenhuma escola com dados completos.")
        else:
            st.info("Nenhuma escola cadastrada ainda.")
    else:
        st.warning(f"Erro ao carregar escolas: {response.status_code}")
except Exception as e:
    st.info("⚠️ Lista de escolas indisponível no momento.")

# ==============================
# VALUATION (sem salvamento automático)
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
    mensalidade_ei = st.number_input("Mensalidade (EI)", min_value=0.0, value=600.0)
    mensalidade_ef1 = st.number_input("Mensalidade (EF1)", min_value=0.0, value=750.0)
    mensalidade_ef2 = st.number_input("Mensalidade (EF2)", min_value=0.0, value=900.0)
    mensalidade_em = st.number_input("Mensalidade (EM)", min_value=0.0, value=1100.0)

st.header("2. Custos e Estrutura")
col3, col4 = st.columns(2)
with col3:
    custos_diretos_percent = st.slider("Custos diretos (%)", 0, 100, 40) / 100
    despesas_admin_percent = st.slider("Despesas admin (%)", 0, 100, 15) / 100
    impostos_percent = st.slider("Impostos (%)", 0, 30, 8) / 100

with col4:
    tem_imovel = st.radio("Imóvel próprio?", ("Não", "Sim"), horizontal=True)
    if tem_imovel == "Sim":
        valor_imovel = st.number_input("Valor do imóvel (R$)", min_value=0.0, value=3000000.0)
        valor_instalacoes = 0.0
    else:
        valor_imovel = 0.0
        aluguel_mensal = st.number_input("Aluguel (R$)", min_value=0.0, value=25000.0)
        valor_instalacoes = st.number_input("Valor instalações (R$)", min_value=0.0, value=500000.0)
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

# Gráfico de custos (opcional)
st.subheader("📈 Distribuição de Custos")
custos_data = {
    "Custos Diretos": custos_diretos,
    "Despesas Admin": despesas_admin,
    "Aluguel": aluguel_anual,
    "EBITDA": ebitda_ajustado
}
st.bar_chart(custos_data)

# ==============================
# GERAR RELATÓRIO EM PDF
# ==============================
if st.button("📄 Gerar Relatório em PDF"):
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Valuation", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(0, 10, f"Valor Líquido: R$ {valor_liquido:,.2f}", ln=True)
    pdf.cell(0, 10, f"EBITDA Ajustado: R$ {ebitda_ajustado:,.2f}", ln=True)
    pdf.cell(0, 10, f"Taxa de Ocupação: {taxa_ocupacao:.1%}", ln=True)
    pdf.cell(0, 10, f"Total de Alunos: {total_alunos}", ln=True)
    pdf.cell(0, 10, f"Receita Anual: R$ {receita_total:,.2f}", ln=True)
    
    pdf_output = pdf.output(dest="S").encode("latin-1")
    st.download_button(
        "📥 Baixar PDF",
        pdf_output,
        "relatorio_valuation.pdf",
        "application/pdf"
    )

# ==============================
# INSTRUÇÕES PARA SALVAR
# ==============================
st.info("""
💡 **Para salvar este valuation:**
1. Anote o **Valor Líquido** calculado
2. Acesse [Cadastro de Escolas](https://colegiopauliceia.com/school/cadastro.html)
3. Preencha o formulário com os dados
""")
