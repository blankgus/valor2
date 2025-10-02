import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

st.set_page_config(page_title="SchoolValuation Pro+ v9", layout="wide")
st.title("🏫 SchoolValuation Pro+ v9")

# ==============================
# LINKS IMPORTANTES
# ==============================
st.markdown("🔗 **[Cadastrar Nova Escola](https://colegiopauliceia.com/school/cadastro.html)**")
st.markdown("🔗 **[Ver Escolas Cadastradas](https://colegiopauliceia.com/school/cadastro.html)**")

# ==============================
# LISTAR ESCOLAS COM DETALHES
# ==============================
st.header("🏫 Escolas Cadastradas")
try:
    response = requests.get("https://colegiopauliceia.com/school/api.php?secret=10XP20to30", timeout=5)
    if response.status_code == 200:
        schools = response.json()
        if schools:
            df = pd.DataFrame(schools)
            # Mostrar colunas disponíveis
            cols = ['name', 'estado', 'valor_liquido', 'total_alunos', 'receita_total', 'ebitda_ajustado']
            cols = [c for c in cols if c in df.columns]
            if cols:
                st.dataframe(df[cols].rename(columns={
                    'name': 'Nome',
                    'estado': 'Estado',
                    'valor_liquido': 'Valor Líquido',
                    'total_alunos': 'Alunos',
                    'receita_total': 'Receita Anual',
                    'ebitda_ajustado': 'EBITDA'
                }).style.format({
                    'Valor Líquido': 'R$ {:,.0f}',
                    'Receita Anual': 'R$ {:,.0f}',
                    'EBITDA': 'R$ {:,.0f}'
                }))
            else:
                st.info("Escolas cadastradas, mas sem dados detalhados.")
        else:
            st.info("Nenhuma escola cadastrada ainda.")
    else:
        st.warning(f"Erro ao carregar escolas: {response.status_code}")
except Exception as e:
    st.info("Lista de escolas temporariamente indisponível.")

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
# BOTÃO PARA SALVAR COMPLETO
# ==============================
if st.button("💾 Salvar Valuation Completo"):
    school_data = {
        "name": f"Escola_{datetime.now().strftime('%Y%m%d_%H%M')}",
        "estado": "SP",
        "valor_liquido": valor_liquido,
        "total_alunos": total_alunos,
        "receita_total": receita_total,
        "ebitda_ajustado": ebitda_ajustado,
        "taxa_ocupacao": taxa_ocupacao,
        "custos_diretos": custos_diretos,
        "despesas_admin": despesas_admin,
        "aluguel_anual": aluguel_anual,
        "valor_imovel": valor_imovel,
        "valor_instalacoes": valor_instalacoes,
        "total_passivos": total_passivos
    }
    try:
        response = requests.post(
            "https://colegiopauliceia.com/school/api.php?secret=10XP20to30",
            json=school_data,
            timeout=10
        )
        if response.status_code == 200:
            st.success("✅ Valuation salvo com sucesso!")
            st.experimental_rerun()
        else:
            st.error("❌ Erro ao salvar escola")
    except Exception as e:
        st.error(f"❌ Falha na conexão: {str(e)}")

# ==============================
# RESULTADO FINAL COM GRÁFICOS
# ==============================
st.header("✅ Valor Final")
st.metric("Valor Líquido", f"R$ {valor_liquido:,.0f}")

st.subheader("📊 Gráfico de Ocupação")
st.progress(int(taxa_ocupacao * 100))
st.caption(f"Ocupação: {taxa_ocupacao:.1%} ({total_alunos}/{capacidade_total} alunos)")

st.subheader("📈 Distribuição de Receita")
receita_data = {
    "EI": receita_ei,
    "EF1": receita_ef1,
    "EF2": receita_ef2,
    "EM": receita_em
}
st.bar_chart(receita_data)

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
# EXPORTAR EM EXCEL COMPLETO
# ==============================
if st.button("📥 Exportar Relatório Completo em Excel"):
    # Dados principais
    dados_principais = {
        "Item": [
            "Valor Líquido",
            "EBITDA Ajustado",
            "Receita Total",
            "Total de Alunos",
            "Taxa de Ocupação",
            "Custos Diretos",
            "Despesas Administrativas",
            "Aluguel Anual",
            "Valor do Imóvel",
            "Valor das Instalações",
            "Dívidas Totais"
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
    
    df_principal = pd.DataFrame(dados_principais)
    
    # Due diligence
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
    df_checklist = pd.DataFrame(checklist, columns=["Categoria", "Item", "Status", "Observações"])
    
    # Exportar
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_principal.to_excel(writer, sheet_name="Resumo Financeiro", index=False)
        df_checklist.to_excel(writer, sheet_name="Due Diligence", index=False)
    
    st.download_button(
        "📥 Baixar Relatório Completo",
        output.getvalue(),
        "relatorio_valuation_completo.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
