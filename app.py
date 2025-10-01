import streamlit as st

st.title("App Funcionando")
st.write("Se você vê esta mensagem, o app está OK!")
if st.button("Salvar Valuation"):
    # Dados a serem salvos
    valuation_data = {
        "name": f"Escola_{int(valor_liquido)}",
        "estado": "SP",  # Pode ser um input
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
        API_URL = "https://colegiopauliceia.com/school/api.php"
        response = requests.post(
            f"{API_URL}?secret=10XP20to30",
            json=valuation_data,
            timeout=10
        )
        if response.status_code == 200:
    st.success("Valuation salvo com sucesso!")
            st.experimental_rerun()
        else:
            st.error(f"❌ Erro ao salvar: {response.text}")
    except Exception as e:
        st.error(f"❌ Erro de conexão: {str(e)}")

