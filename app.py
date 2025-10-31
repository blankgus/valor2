import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SchoolValuation Pro+ v10", layout="wide")
st.title("🏫 SchoolValuation Pro+ v10")

# ==============================
# DADOS OPERACIONAIS
# ==============================
st.header("1. Dados Operacionais")
col1, col2 = st.columns(2)
with col1:
    alunos_ei = st.number_input("Alunos - Educação Infantil", min_value=0, value=22)
    capacidade_ei = st.number_input("Capacidade máxima (EI)", min_value=1, value=36)
    alunos_ef1 = st.number_input("Alunos - Ensino Fundamental I", min_value=0, value=87)
    capacidade_ef1 = st.number_input("Capacidade máxima (EF1)", min_value=1, value=176)
    alunos_ef2 = st.number_input("Alunos - Ensino Fundamental II", min_value=0, value=123)
    capacidade_ef2 = st.number_input("Capacidade máxima (EF2)", min_value=1, value=189)
    alunos_em = st.number_input("Alunos - Ensino Médio", min_value=0, value=66)
    capacidade_em = st.number_input("Capacidade máxima (EM)", min_value=1, value=140)

with col2:
    mensalidade_ei = st.number_input("Mensalidade média (EI)", min_value=0.0, value=1715.0)
    mensalidade_ef1 = st.number_input("Mensalidade média (EF1)", min_value=0.0, value=2055.0)
    mensalidade_ef2 = st.number_input("Mensalidade média (EF2)", min_value=0.0, value=2160.0)
    mensalidade_em = st.number_input("Mensalidade média (EM)", min_value=0.0, value=2450.0)

st.header("2. Custos, Estrutura e Passivos")
col3, col4 = st.columns(2)
with col3:
    custos_diretos_percent = st.slider("Custos diretos (%)", 0, 100, 25) / 100
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
            value=500000.0
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
# DADOS PARA DCF (Fluxo de Caixa Descontado)
# ==============================
st.header("4. Parâmetros para DCF")
col_dcf1, col_dcf2, col_dcf3 = st.columns(3)
taxa_crescimento = col_dcf1.slider("Taxa de crescimento anual (%)", 0.0, 15.0, 5.0) / 100
periodo_explicito = col_dcf2.slider("Período explícito (anos)", 3, 10, 5)
wacc = col_dcf3.slider("WACC (%)", 8.0, 20.0, 12.0) / 100

# Projeção de fluxo de caixa
fcf_atual = ebitda_ajustado * (1 - impostos_percent)  # FCF ≈ EBITDA * (1 - impostos)
fcf_projetado = []
valor_terminal = 0

for ano in range(1, periodo_explicito + 1):
    fcf_ano = fcf_atual * ((1 + taxa_crescimento) ** ano)
    fcf_projetado.append(fcf_ano)
    if ano == periodo_explicito:
        valor_terminal = fcf_ano * (1 + 0.025) / (wacc - 0.025)

# Cálculo do DCF
vp_fcf = sum(fcf_projetado[i] / ((1 + wacc) ** (i + 1)) for i in range(len(fcf_projetado)))
vp_terminal = valor_terminal / ((1 + wacc) ** periodo_explicito)
valor_dcf = vp_fcf + vp_terminal

# Valor final combinado (média simples)
valor_final_combinado = (valor_bruto + valor_dcf) / 2

# ==============================
# RESUMO DOS VALUATIONS
# ==============================
st.subheader("📋 Valuation por Método")
valuation_data = {
    "Método": [
        "EBITDA + Patrimônio",
        "DCF (Fluxo de Caixa)",
        "Valor Final Sugerido"
    ],
    "Valor (R$)": [
        f"R$ {valor_bruto:,.0f}",
        f"R$ {valor_dcf:,.0f}",
        f"R$ {valor_final_combinado:,.0f}"
    ]
}
df_valuation = pd.DataFrame(valuation_data)
st.dataframe(df_valuation, use_container_width=True)

# ==============================
# GRÁFICOS
# ==============================
st.subheader("📊 Gráfico de Ocupação")
st.progress(int(taxa_ocupacao * 100))
st.caption(f"Ocupação: {taxa_ocupacao:.1%} ({total_alunos}/{capacidade_total} alunos)")

st.subheader("📈 Distribuição de Receita por Segmento")
receita_data = {
    "Segmento": ["EI", "EF1", "EF2", "EM"],
    "Receita": [receita_ei, receita_ef1, receita_ef2, receita_em]
}
df_receita = pd.DataFrame(receita_data)
fig = px.pie(df_receita, values='Receita', names='Segmento', title='Distribuição da Receita')
st.plotly_chart(fig, use_container_width=True)

st.subheader("⚖️ Comparação de Métodos")
metodos = ["EBITDA + Patrimônio", "DCF"]
valores = [valor_bruto, valor_dcf]
df_comp = pd.DataFrame({"Método": metodos, "Valor": valores})
st.bar_chart(df_comp.set_index("Método"))

# ==============================
# TEASER PARA COMPRADORES
# ==============================
st.subheader("📄 Teaser para Compradores")
teaser_text = f"""
Escola com {total_alunos} alunos ({taxa_ocupacao:.1%} de ocupação),
faturamento de R$ {receita_total:,.0f} e EBITDA de R$ {ebitda_ajustado:,.0f}.
Imóvel próprio incluso (R$ {valor_imovel:,.0f}).
Passivos: R$ {total_passivos:,.0f}.
**Valor final sugerido: R$ {valor_final_combinado:,.0f}**.
"""
st.text_area("Copie e envie para potenciais compradores:", teaser_text, height=200)

# ==============================
# DUE DILIGENCE CHECKLIST
# ==============================
st.subheader("🔍 Due Diligence Checklist")
checklist = [
    ["Financeiro", "Balanço auditado (3 anos)", "✅", ""],
    ["Financeiro", "Demonstração de fluxo de caixa", "✅", ""],
    ["Financeiro", "Dívidas fiscais quitadas", "✅" if divida_fiscal == 0 else "❌", ""],
    ["Legal", "Contrato social atualizado", "✅", ""],
    ["Legal", "Licenças de funcionamento", "✅", ""],
    ["Legal", "Processos judiciais", "✅", ""],
    ["Operacional", "Histórico de evasão (3 anos)", "✅", ""],
    ["Operacional", "Contratos de aluguel", "✅" if tem_imovel == "Não" else "N/A", ""],
    ["Operacional", "Laudo de avaliação do imóvel", "✅" if tem_imovel == "Sim" else "N/A", ""],
    ["Pedagógico", "Certificações internacionais", "✅", ""],
    ["Pedagógico", "Currículo Lattes dos coordenadores", "✅", ""],
]
df_checklist = pd.DataFrame(checklist, columns=["Categoria", "Item", "Status", "Observações"])
st.dataframe(df_checklist, use_container_width=True)

# ==============================
# LINK PARA VPS
# ==============================
st.markdown("---")
st.markdown("🔗 **[Gerenciar Escolas no VPS](https://colegiopauliceia.com/school/)**")

