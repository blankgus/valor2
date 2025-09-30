import streamlit as st
import pandas as pd
import requests
import os

# Configuração da API
API_URL = "https://colegiopauliceia.com/schoolvalor-api/api.php"
API_SECRET = os.getenv("API_SECRET", "10XP20to30")  # Defina no Streamlit Cloud

def save_school_to_api(name, estado, valor_liquido):
    """Salva escola na API do VPS"""
    try:
        response = requests.post(
            f"{API_URL}?secret={API_SECRET}",
            json={"name": name, "estado": estado, "valor_liquido": valor_liquido},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_schools_from_api():
    """Busca escolas da API"""
    try:
        response = requests.get(f"{API_URL}?secret={API_SECRET}", timeout=10)
        return response.json()
    except Exception as e:
        return []

# ==============================
# APP PRINCIPAL
# ==============================
st.set_page_config(page_title="SchoolValuation Pro+ v6", layout="wide")
st.title("🏫 SchoolValuation Pro+ v6")
st.markdown("Sistema com banco de dados remoto e gerenciamento de documentos.")

# --- LISTAR ESCOLAS EXISTENTES ---
st.header("🏫 Escolas Cadastradas")
schools = get_schools_from_api()
if isinstance(schools, list) and schools:
    df = pd.DataFrame(schools)
    st.dataframe(df[["name", "estado", "valor_liquido"]].rename(columns={
        "name": "Nome", "estado": "Estado", "valor_liquido": "Valor Líquido"
    }).style.format({"Valor Líquido": "R$ {:,.0f}"}))
else:
    st.info("Nenhuma escola cadastrada ainda.")

# --- FORMULÁRIO DE VALUATION ---
st.header("1. Dados da Escola")
school_name = st.text_input("Nome da Escola (obrigatório para salvar)")
estado = st.selectbox("Estado", ["SP", "RJ", "MG", "RS", "PR"])

# ... (seus inputs de valuation aqui - mantidos iguais)
# Exemplo simplificado:
valor_liquido = st.number_input("Valor Líquido (R$)", min_value=0.0, value=1000000.0)

# --- SALVAR NA API ---
if st.button("💾 Salvar Escola no Banco de Dados"):
    if not school_name:
        st.error("Nome da escola é obrigatório!")
    else:
        result = save_school_to_api(school_name, estado, valor_liquido)
        if "error" in result:
            st.error(f"❌ Erro: {result['error']}")
        else:
            st.success("✅ Escola salva com sucesso!")
            st.markdown(f"[📎 Gerenciar Documentos]({result['upload_url']})")

# --- LINK DIRETO PARA DOCUMENTOS ---
st.header("📎 Acesso Rápido a Documentos")
st.markdown(
    "Acesse o sistema de documentos: "
    "[🔗 Gerenciar Documentos](https://colegiopauliceia.com/schoolvalor-docs/)"
)

