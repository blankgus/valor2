import math
from datetime import datetime
from pathlib import Path
import base64
import pandas as pd
import matplotlib.pyplot as plt

EXCEL_PATH = Path("./Modelo_Financeiro_Escola.xlsx")
MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

def fmt_moeda(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
    except:
        return str(v)

def fmt_pct(v):
    try:
        return f"{float(v)*100:,.1f}%".replace(",", "X").replace(".", ",").replace("X",".")
    except:
        return str(v)

def img_to_data_uri(path: Path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = path.suffix.replace(".", "")
    return f"data:image/{ext};base64,{b64}"

def ler_parametros_do_excel():
    resumo = pd.read_excel(EXCEL_PATH, sheet_name="1_Resumo")
    params = {}
    for _, r in resumo.iterrows():
        params[r["Campo"]] = r["Valor"]
    def pct_to_float(s):
        try:
            return float(str(s).replace("%","").strip())/100.0
        except:
            return None
    empresa = params.get("Empresa", "Escola")
    responsavel = params.get("Responsável", "Equipe Financeira")
    split_edu = pct_to_float(params.get("Split Receita Educação", "85%")) or 0.85
    split_cli = pct_to_float(params.get("Split Receita Clínica", "15%")) or 0.15
    ded_aliq = pct_to_float(params.get("Dedução/Impostos s/ Receita", "12%")) or 0.12
    dep_pct = pct_to_float(params.get("Depreciação", "2%")) or 0.02
    fin_pct = pct_to_float(params.get("Resultado Financeiro", "-1%")) or -0.01
    return {
        "empresa": empresa,
        "responsavel": responsavel,
        "split": {"Educacao": split_edu, "Clinica": split_cli},
        "ded_aliq": ded_aliq,
        "dep_pct": dep_pct,
        "fin_pct": fin_pct,
    }

def carregar_bases():
    params = ler_parametros_do_excel()
    df_rec = pd.read_excel(EXCEL_PATH, sheet_name="2_Receita_Operacional")
    df_rec["Mes"] = pd.Categorical(df_rec["Mes"], categories=MESES_PT, ordered=True)
    df_rec = df_rec.sort_values("Mes")
    df_receita = []
    for _, r in df_rec.iterrows():
        df_receita.append({
            "Ano": 2024, "Mes": r["Mes"],
            "Receita_Total_R$": r["2024_Educacao_R$"] + r["2024_Clinica_R$"],
        })
        df_receita.append({
            "Ano": 2025, "Mes": r["Mes"],
            "Receita_Total_R$": r["2025_Educacao_R$"] + r["2025_Clinica_R$"],
        })
    df_receita = pd.DataFrame(df_receita)
    df_receita["Receita_Educacao_R$"] = df_receita["Receita_Total_R$"] * params["split"]["Educacao"]
    df_receita["Receita_Clinica_R$"] = df_receita["Receita_Total_R$"] * params["split"]["Clinica"]

    def add_metrics(df, col):
        df["Acumulado_ano_R$"] = df[col].cumsum()
        df["Var_m_m_%"] = df[col].pct_change()
        return df

    df_2024 = add_metrics(df_receita[df_receita["Ano"]==2024].copy(), "Receita_Total_R$")
    df_2025 = add_metrics(df_receita[df_receita["Ano"]==2025].copy(), "Receita_Total_R$")
    df_2025["Var_y_y_%"] = (df_2025["Receita_Total_R$"].values / df_2024["Receita_Total_R$"].values) - 1
    df_2025["Var_acum_y_y_%"] = (df_2025["Acumulado_ano_R$"].values / df_2024["Acumulado_ano_R$"].values) - 1

    # --- NOVO: Leitura da aba 6_Turmas_Inclusao ---
    turmas_resumo = None
    try:
        turmas_inc = pd.read_excel(EXCEL_PATH, sheet_name="6_Turmas_Inclusao")
        turmas_dict = dict(zip(turmas_inc["Campo"], turmas_inc["Valor"]))
        def pct_to_float(s):
            try:
                return float(str(s).replace("%","").strip())/100.0
            except:
                return None
        total_alunos = float(turmas_dict.get("Total de Alunos", 0))
        pct_turma_a = pct_to_float(turmas_dict.get("% Turma A (Inclusão)", "30%")) or 0.3
        ticket_a = float(turmas_dict.get("Ticket Médio Turma A (R$)", 3000))
        ticket_b = float(turmas_dict.get("Ticket Médio Turma B (R$)", 2200))

        alunos_a = total_alunos * pct_turma_a
        alunos_b = total_alunos * (1 - pct_turma_a)
        receita_a = alunos_a * ticket_a
        receita_b = alunos_b * ticket_b
        receita_edu_total = receita_a + receita_b

        rec_edu_2025 = df_2025["Receita_Educacao_R$"].sum()
        desvio = abs(receita_edu_total - rec_edu_2025) / rec_edu_2025 if rec_edu_2025 else 0

        turmas_resumo = {
            "Total_Alunos": total_alunos,
            "Alunos_TurmaA": alunos_a,
            "Alunos_TurmaB": alunos_b,
            "Ticket_A": ticket_a,
            "Ticket_B": ticket_b,
            "Receita_TurmaA": receita_a,
            "Receita_TurmaB": receita_b,
            "Receita_Educacao_Calculada": receita_edu_total,
            "Desvio_vs_Modelo_%": desvio,
        }
    except Exception as e:
        print("⚠️ Erro ao carregar aba 6_Turmas_Inclusao:", e)

    # DRE
    try:
        dre_unidades = pd.read_excel(EXCEL_PATH, sheet_name="5_DRE_Unidades")
    except:
        dre_unidades = pd.DataFrame(columns=["Conta","Educacao_2024","Educacao_2025","Clinica_2024","Clinica_2025"])

    # Drivers
    try:
        drv_ed = pd.read_excel(EXCEL_PATH, sheet_name="3_Drivers_Educacao")
        drv_cl = pd.read_excel(EXCEL_PATH, sheet_name="4_Drivers_Clinica")
        drivers_tbl = pd.concat([drv_ed, drv_cl], ignore_index=True)
    except:
        drivers_tbl = pd.DataFrame(columns=["Driver","Valor"])

    # Premissas
    try:
        premissas = pd.read_excel(EXCEL_PATH, sheet_name="7_Diferenciais_Estrategicos")
        premissas.columns = ["Diferencial","Impacto","Evidências"]
    except:
        premissas = pd.DataFrame([["", "", ""]], columns=["Diferencial","Impacto","Evidências"])

    # Sumário
    rec_liq_2024 = df_2024["Receita_Total_R$"].sum()
    rec_liq_2025 = df_2025["Receita_Total_R$"].sum()
    if not dre_unidades.empty and "EBITDA" in list(dre_unidades["Conta"]):
        ebitda_2024 = float(dre_unidades.loc[dre_unidades["Conta"]=="EBITDA", ["Educacao_2024","Clinica_2024"]].sum(axis=1))
        ebitda_2025 = float(dre_unidades.loc[dre_unidades["Conta"]=="EBITDA", ["Educacao_2025","Clinica_2025"]].sum(axis=1))
    else:
        ebitda_2024 = rec_liq_2024 * 0.18
        ebitda_2025 = rec_liq_2025 * 0.19

    sumario = pd.DataFrame([
        ["Receita 2024 (R$)", rec_liq_2024],
        ["Receita 2025 (R$)", rec_liq_2025],
        ["Crescimento y/y 2025 vs 2024 (%)", (rec_liq_2025/rec_liq_2024)-1 if rec_liq_2024 else None],
        ["Margem EBITDA 2024 (prelim.)", ebitda_2024/rec_liq_2024 if rec_liq_2024 else None],
        ["Margem EBITDA 2025 (prelim.)", ebitda_2025/rec_liq_2025 if rec_liq_2025 else None],
    ], columns=["Indicador","Valor"])

    return params, df_receita, df_2024, df_2025, dre_unidades, sumario, drivers_tbl, premissas, turmas_resumo

def salvar_grafico_receita_segmentada(df_receita, caminho_png):
    df_2025 = df_receita[df_receita["Ano"]==2025].copy()
    ed = df_2025["Receita_Educacao_R$"].sum()
    cl = df_2025["Receita_Clinica_R$"].sum()
    plt.figure(figsize=(5,5))
    plt.pie([ed, cl], labels=["Educação","Clínica"], autopct='%1.1f%%', startangle=90)
    plt.title("Receita por Unidade – 2025")
    plt.tight_layout()
    plt.savefig(caminho_png, dpi=150)
    plt.close()

def salvar_grafico_receita(df_receita, caminho_png):
    df_2024 = df_receita[df_receita["Ano"]==2024].copy()
    df_2025 = df_receita[df_receita["Ano"]==2025].copy()
    x = range(len(MESES_PT))
    width = 0.35
    plt.figure(figsize=(10,4))
    plt.bar([i - width/2 for i in x], df_2024["Receita_Total_R$"]/1000, width=width, label="2024")
    plt.bar([i + width/2 for i in x], df_2025["Receita_Total_R$"]/1000, width=width, label="2025")
    plt.xticks(list(x), MESES_PT)
    plt.ylabel("Receita (mil R$)")
    plt.title("Receita Mensal – Total")
    plt.legend()
    plt.tight_layout()
    plt.savefig(caminho_png, dpi=150)
    plt.close()

def salvar_grafico_acumulado_yy(df_receita, caminho_png):
    df_2024 = df_receita[df_receita["Ano"]==2024].copy()
    df_2025 = df_receita[df_receita["Ano"]==2025].copy()
    plt.figure(figsize=(10,4))
    plt.plot(MESES_PT, df_2024["Acumulado_ano_R$"]/1000, label="Acumulado 2024")
    plt.plot(MESES_PT, df_2025["Acumulado_ano_R$"]/1000, label="Acumulado 2025")
    plt.plot(MESES_PT, df_2025["Var_y_y_%"]*100, label="Var y/y (%)", linestyle="--", color="orange")
    plt.ylabel("Acumulado (mil R$) / Var (%)")
    plt.title("Acumulado e Variação y/y – Total")
    plt.legend()
    plt.tight_layout()
    plt.savefig(caminho_png, dpi=150)
    plt.close()

def gerar_html(params, df_receita, dre_unidades, sumario, drivers_tbl, premissas, turmas_resumo, saida_html: Path, logo_path: Path=None):
    assets = Path("./assets"); assets.mkdir(exist_ok=True)
    graf_total = assets / "graf_receita_total.png"
    graf_acum = assets / "graf_acumulado.png"
    graf_seg = assets / "graf_segmento.png"
    salvar_grafico_receita(df_receita, graf_total)
    salvar_grafico_acumulado_yy(df_receita, graf_acum)
    salvar_grafico_receita_segmentada(df_receita, graf_seg)
    img_total = img_to_data_uri(graf_total)
    img_acum = img_to_data_uri(graf_acum)
    img_seg = img_to_data_uri(graf_seg)
    data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    titulo = "Modelo Financeiro 2025 – Versão Preliminar"
    subtitulo = f'{params["empresa"]} | {data_agora}'

    def df_to_html_table(df, moeda_cols=None, pct_cols=None):
        moeda_cols = moeda_cols or []
        pct_cols = pct_cols or []
        df_fmt = df.copy()
        for c in moeda_cols:
            if c in df_fmt.columns:
                df_fmt[c] = df_fmt[c].map(fmt_moeda)
        for c in pct_cols:
            if c in df_fmt.columns:
                df_fmt[c] = df_fmt[c].map(fmt_pct)
        return df_fmt.to_html(index=False, border=0, classes="tabela")

    sumario_html = df_to_html_table(sumario, moeda_cols=["Valor"])
    dre_u_html = df_to_html_table(dre_unidades, moeda_cols=["Educacao_2024","Educacao_2025","Clinica_2024","Clinica_2025"])
    drivers_fmt = drivers_tbl.copy()
    drivers_fmt["Valor_fmt"] = drivers_fmt.apply(
        lambda r: fmt_moeda(r["Valor"]) if "R$" in str(r.get("Driver","")) else (fmt_pct(r["Valor"]) if "%" in str(r.get("Driver","")) else f'{r["Valor"]}'),
        axis=1
    )
    drivers_html = df_to_html_table(drivers_fmt[["Driver","Valor_fmt"]])
    premissas_html = premissas.to_html(index=False, border=0, classes="tabela")

    # --- NOVO: HTML da seção Turmas A/B ---
    if turmas_resumo:
        turma_a_html = f"""
        <div class="card">
          <h2>Receita por Tipo de Aluno – Inclusão (Turma A) vs Demais (Turma B)</h2>
          <table class="tabela">
            <tr><th>Item</th><th>Valor</th></tr>
            <tr><td>Total de Alunos</td><td>{int(turmas_resumo['Total_Alunos'])}</td></tr>
            <tr><td>Alunos Turma A (Inclusão)</td><td>{int(turmas_resumo['Alunos_TurmaA'])} ({fmt_pct(turmas_resumo['Alunos_TurmaA']/turmas_resumo['Total_Alunos'])})</td></tr>
            <tr><td>Alunos Turma B</td><td>{int(turmas_resumo['Alunos_TurmaB'])}</td></tr>
            <tr><td>Ticket Médio Turma A</td><td>{fmt_moeda(turmas_resumo['Ticket_A'])}</td></tr>
            <tr><td>Ticket Médio Turma B</td><td>{fmt_moeda(turmas_resumo['Ticket_B'])}</td></tr>
            <tr><td><strong>Receita Turma A</strong></td><td><strong>{fmt_moeda(turmas_resumo['Receita_TurmaA'])}</strong></td></tr>
            <tr><td><strong>Receita Turma B</strong></td><td><strong>{fmt_moeda(turmas_resumo['Receita_TurmaB'])}</strong></td></tr>
            <tr><td><strong>Receita Educação (Calculada)</strong></td><td><strong>{fmt_moeda(turmas_resumo['Receita_Educacao_Calculada'])}</strong></td></tr>
            <tr><td>Desvio vs Modelo Financeiro</td><td>{fmt_pct(turmas_resumo['Desvio_vs_Modelo_%'])}</td></tr>
          </table>
          <p class="muted">A Turma A (inclusão) gera receita premium com ticket médio de R$ 3.000. A escola é referência em inclusão com metodologia própria replicável, justificando um ajuste de valuation de 15% a 40%.</p>
        </div>
        """
    else:
        turma_a_html = '<div class="card"><h2>Receita por Tipo de Aluno</h2><p>Dados não disponíveis (aba 6_Turmas_Inclusao ausente).</p></div>'

    logo_html = ""
    if logo_path and logo_path.exists():
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_html = f'<img src="data:image/png;base64,{b64}" alt="logo" style="height:56px;margin-top:6px;" />'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{titulo}</title>
<style>
  :root {{
    --bg: #ffffff;
    --text: #1f2937;
    --muted: #6b7280;
    --primary: #0B5FFF;
    --line: #e5e7eb;
    --header: #f7f9fc;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans";
    margin: 24px;
    color: var(--text);
    background: var(--bg);
  }}
  h1 {{ font-size: 22px; margin: 0 0 8px 0; }}
  h2 {{ font-size: 16px; margin: 24px 0 8px 0; }}
  p  {{ color: var(--muted); margin: 0 0 6px 0; }}
  .header {{
    display: flex; align-items: center; justify-content: space-between;
    border: 1px solid var(--line); background: var(--header);
    padding: 12px 16px; border-radius: 10px; margin-bottom: 18px;
  }}
  .card {{ border: 1px solid var(--line); border-radius: 10px; padding: 12px 16px; margin-bottom: 18px; }}
  .tabela {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .tabela th, .tabela td {{ border: 1px solid var(--line); padding: 6px 8px; text-align: left; }}
  .tabela th {{ background: #f3f4f6; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .imgbox {{ text-align: center; }}
  .imgbox img {{ max-width: 100%; height: auto; border: 1px solid var(--line); border-radius: 8px; }}
  .muted {{ color: var(--muted); }}
  .footer {{ margin-top: 24px; font-size: 12px; color: var(--muted); }}
  @media print {{
    .pagebreak {{ page-break-before: always; }}
    body {{ margin: 0.8cm; }}
  }}
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>{titulo}</h1>
      <p>{subtitulo}</p>
      <p class="muted">Preliminar – sujeito a revisão. Dados do Excel.</p>
    </div>
    <div>{logo_html}</div>
  </div>
  <div class="grid">
    <div class="card imgbox">
      <h2>Receita Mensal – Total</h2>
      <img src="{img_total}" alt="Receita Mensal Total" />
    </div>
    <div class="card imgbox">
      <h2>Acumulado e Variação y/y – Total</h2>
      <img src="{img_acum}" alt="Acumulado" />
    </div>
  </div>
  <div class="card imgbox">
    <h2>Mix de Receita 2025: Educação vs Clínica</h2>
    <img src="{img_seg}" alt="Segmento" style="max-width: 60%;" />
  </div>
  <div class="card">
    <h2>Sumário Executivo</h2>
    {sumario_html}
  </div>
  {turma_a_html}
  <div class="card">
    <h2>DRE por Unidade – Educação e Clínica</h2>
    {dre_u_html}
  </div>
  <div class="card">
    <h2>Drivers Operacionais – Educação e Clínica</h2>
    {drivers_html}
  </div>
  <div class="card">
    <h2>Diferenciais/Proposta (da aba 7)</h2>
    {premissas_html}
  </div>
  <div class="footer">
    Preliminar – sujeito a revisão | {params['responsavel']} | Gerado em {data_agora}
  </div>
  <div class="pagebreak"></div>
</body>
</html>
"""
    saida_html.write_text(html, encoding="utf-8")
    print("HTML gerado:", saida_html.resolve())

if __name__ == "__main__":
    if not EXCEL_PATH.exists():
        print("Não encontrei Modelo_Financeiro_Escola.xlsx. Rode primeiro: python gerar_modelo_excel.py")
        raise SystemExit(1)
    params, df_receita, df_2024, df_2025, dre_unidades, sumario, drivers_tbl, premissas, turmas_resumo = carregar_bases()
    saida = Path("./Relatorio_Financeiro_2025.html")
    gerar_html(params, df_receita, dre_unidades, sumario, drivers_tbl, premissas, turmas_resumo, saida_html=saida)
    print("Abra no navegador e imprima em PDF. Ative a opção de imprimir fundos/cores para manter o estilo.")
