import streamlit as st
import pandas as pd

st.set_page_config(page_title="SchoolValuation Pro+ v6", layout="wide")
st.title("🏫 SchoolValuation Pro+ v6")
st.markdown("Valuation profissional para escolas particulares.")

# --- LINK PARA CADASTRO ---
st.header("🔗 Cadastro de Escolas")
st.markdown(
    "Para cadastrar sua escola e gerenciar documentos, acesse nosso sistema seguro: "
    "[👉 Cadastrar Escola](https://colegiopauliceia.com/cadastro.html)"
)

# --- VALUATION (sem API) ---
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

# --- CÁLCULOS ---
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

# --- VALUATION ---
valor_ebitda = ebitda_ajustado * multiplo_ebitda
valor_bruto = valor_ebitda + valor_imovel
if tem_imovel == "Não":
    valor_bruto += valor_instalacoes
valor_liquido = valor_bruto - total_passivos

st.header("✅ Valor Final")
st.metric("Valor Líquido", f"R$ {valor_liquido:,.0f}")

if st.button("Gerar Due Diligence Excel"):
    import io
    from openpyxl import Workbook
    
    checklist = [
        ["Financeiro", "Balanço auditado (3 anos)", "", ""],
        ["Financeiro", "Demonstração de fluxo de caixa", "", ""],
        ["Financeiro", "Dívidas fiscais quitadas", "", ""],
        ["Legal", "Contrato social atualizado", "", ""],
        ["Legal", "Licenças de funcionamento", "", ""],
        ["Legal", "Processos judiciais", "", ""],
        ["Operacional", "Histórico de evasão (3 anos)", "", ""],
        ["Operacional", "Contratos de aluguel", "", ""],
        ["Operacional", "Laudo de avaliação do imóvel", "", ""],
        ["Pedagógico", "Certificações internacionais", "", ""],
        ["Pedagógico", "Currículo Lattes dos coordenadores", "", ""],
    ]
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(checklist, columns=["Categoria", "Item", "Status", "Observações"]).to_excel(writer, sheet_name="Due Diligence", index=False)
    
    st.download_button("📥 Baixar Checklist", output.getvalue(), "due_diligence.xlsx")

