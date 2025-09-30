import streamlit as st
import pandas as pd
import os
import sqlite3
from dotenv import load_dotenv

# Carregar configurações
load_dotenv()

# Configurações do projeto
PROJECT_ROOT = os.getenv("PROJECT_ROOT", os.getcwd())
DB_PATH = os.getenv("DB_PATH", os.path.join(PROJECT_ROOT, "school_valuation.db"))
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(PROJECT_ROOT, "uploads"))

# Criar pastas necessárias
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Verificar permissões
if not os.access(PROJECT_ROOT, os.W_OK):
    st.error(f"❌ Sem permissão de escrita em: {PROJECT_ROOT}")
    st.stop()

# ==============================
# BANCO DE DADOS (com tratamento de erros)
# ==============================
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                estado TEXT,
                valor_liquido REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Erro ao criar banco de dados em {DB_PATH}: {str(e)}")
        st.stop()

# Inicializar BD imediatamente
init_db()

# ==============================
# LOGIN SIMPLES
# ==============================
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        user = st.text_input("Usuário", value=os.getenv("USERNAME", "admin"))
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user == os.getenv("USERNAME") and pwd == os.getenv("PASSWORD"):
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos")
        st.stop()

# ==============================
# APP PRINCIPAL
# ==============================
if __name__ == "__main__":
    check_password()
    
    st.title("🏫 SchoolValuation Pro+ v4")
    st.success(f"✅ Banco de dados ativo em: {DB_PATH}")
    st.info(f"📁 Uploads salvos em: {UPLOAD_FOLDER}")

    # --- FORMULÁRIO ---
    school_name = st.text_input("Nome da Escola")
    estado = st.selectbox("Estado", ["SP", "RJ", "MG"])
    valor = st.number_input("Valor Líquido (R$)", min_value=0.0)

    if st.button("💾 Salvar"):
        if not school_name:
            st.error("Nome é obrigatório!")
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO schools (name, estado, valor_liquido) VALUES (?, ?, ?)",
                    (school_name, estado, valor)
                )
                conn.commit()
                conn.close()
                st.success("✅ Escola salva com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {str(e)}")

    # --- LISTAR ESCOLAS ---
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM schools", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df)
    except Exception as e:
        st.error(f"Erro ao carregar escolas: {str(e)}")import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Carregar configurações
load_dotenv()
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "senha")
DB_PATH = os.getenv("DB_PATH", "school_valuation.db")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

# Criar pastas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# BANCO DE DADOS
# ==============================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabela de escolas
    c.execute('''
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            estado TEXT,
            alunos_total INTEGER,
            capacidade_total INTEGER,
            receita_anual REAL,
            ebitda_ajustado REAL,
            valor_liquido REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Tabela de dados detalhados
    c.execute('''
        CREATE TABLE IF NOT EXISTS valuation_data (
            school_id INTEGER PRIMARY KEY,
            dados_json TEXT,
            FOREIGN KEY(school_id) REFERENCES schools(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_school(name, estado, alunos, capacidade, receita, ebitda, valor):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR REPLACE INTO schools 
            (name, estado, alunos_total, capacidade_total, receita_anual, ebitda_ajustado, valor_liquido)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, estado, alunos, capacidade, receita, ebitda, valor))
        school_id = c.lastrowid
        conn.commit()
        return school_id
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return None
    finally:
        conn.close()

def save_valuation_data(school_id, dados_dict):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR REPLACE INTO valuation_data (school_id, dados_json)
            VALUES (?, ?)
        ''', (school_id, json.dumps(dados_dict)))
        conn.commit()
    finally:
        conn.close()

def get_schools():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM schools ORDER BY name", conn)
    conn.close()
    return df

def get_valuation_data(school_id):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT dados_json FROM valuation_data WHERE school_id = ?", (school_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

# Inicializar BD
init_db()

# ==============================
# FUNÇÕES AUXILIARES (mantidas)
# ==============================
def calcular_ebitda_ajustado(ebitda_contabil, despesas_nao_recorrentes=0, pro_labore_excedente=0, receitas_nao_recorrentes=0, multas_e_juros=0):
    ajustes = despesas_nao_recorrentes + pro_labore_excedente + multas_e_juros - receitas_nao_recorrentes
    return ebitda_contabil + ajustes, ajustes

def gerar_due_diligence_excel():
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
    df = pd.DataFrame(checklist, columns=["Categoria", "Item", "Status", "Observações"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Due Diligence", index=False)
    return output.getvalue()

# ==============================
# LOGIN
# ==============================
def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Usuário", value=USERNAME, disabled=True)
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Usuário", value=USERNAME, disabled=True)
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        st.error("Senha incorreta")
        return False
    else:
        return True

# ==============================
# APP PRINCIPAL
# ==============================
if __name__ == "__main__":
    if check_password():
        st.set_page_config(page_title="SchoolValuation Pro+ v4", layout="wide")
        st.title("🏫 SchoolValuation Pro+ v4")
        st.markdown("Sistema profissional com banco de dados e gerenciamento de escolas.")

        # --- SELEÇÃO/REGISTRO DE ESCOLA ---
        st.header("🏫 Gerenciar Escolas")
        schools_df = get_schools()
        school_names = ["Nova Escola"] + schools_df["name"].tolist() if not schools_df.empty else ["Nova Escola"]
        selected_school = st.selectbox("Selecione uma escola", school_names)

        # Carregar dados se não for nova
        loaded_data = {}
        if selected_school != "Nova Escola":
            school_row = schools_df[schools_df["name"] == selected_school].iloc[0]
            loaded_data = get_valuation_data(school_row["id"])
            st.success(f"✅ Carregando dados de: {selected_school}")

        # --- FORMULÁRIO DE DADOS ---
        st.header("1. Dados da Escola")
        col1, col2 = st.columns(2)
        with col1:
            school_name = st.text_input("Nome da Escola", value=loaded_data.get("school_name", "") if loaded_data else "")
            estado = st.selectbox("Estado", ["SP", "RJ", "MG", "RS", "PR"], 
                                index=["SP", "RJ", "MG", "RS", "PR"].index(loaded_data.get("estado", "SP")) if loaded_data else 0)

        # Restante dos inputs (exemplo com EI)
        with col2:
            alunos_ei = st.number_input("Alunos - EI", min_value=0, value=loaded_data.get("alunos_ei", 100))
            capacidade_ei = st.number_input("Capacidade (EI)", min_value=1, value=loaded_data.get("capacidade_ei", 120))
            # ... (repita para EF1, EF2, EM, mensalidades, etc.)

        # --- SALVAR ESCOLA ---
        if st.button("💾 Salvar Escola e Calcular Valuation"):
            if not school_name:
                st.error("Nome da escola é obrigatório!")
            else:
                # Aqui você faria todos os cálculos (receita, ebitda, etc.)
                # Exemplo simplificado:
                receita_total = 3_840_000  # Substitua pelos cálculos reais
                ebitda_ajustado = 1_428_000
                valor_liquido = 11_600_000

                # Salvar na tabela principal
                school_id = save_school(school_name, estado, 400, 480, receita_total, ebitda_ajustado, valor_liquido)
                
                # Salvar dados detalhados
                all_data = {
                    "school_name": school_name,
                    "estado": estado,
                    "alunos_ei": alunos_ei,
                    "capacidade_ei": capacidade_ei,
                    # ... todos os outros campos
                }
                if school_id:
                    save_valuation_data(school_id, all_data)
                    st.success("✅ Escola salva com sucesso!")
                    st.experimental_rerun()

        # --- LISTA DE ESCOLAS ---
        if not schools_df.empty:
            st.header("📋 Escolas Cadastradas")
            st.dataframe(schools_df[["name", "estado", "alunos_total", "valor_liquido"]].style.format({"valor_liquido": "R$ {:,.0f}"}))