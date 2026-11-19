import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure
import streamlit as st


st.set_page_config(
    page_title="Panorama Materno-Infantil do Grande ABC",
    page_icon="👶",
    layout="wide",
)

MUNICIPIOS = {
    "354780": "Santo André",
    "354870": "São Bernardo do Campo",
    "354880": "São Caetano do Sul",
    "351380": "Diadema",
    "352940": "Mauá",
    "354330": "Ribeirão Pires",
    "354410": "Rio Grande da Serra",
}

MAP_PARTO = {"1": "Vaginal", "2": "Cesáreo", "9": "Ignorado"}
MAP_GESTACAO = {
    "1": "Menos de 22 semanas",
    "2": "22 a 27 semanas",
    "3": "28 a 31 semanas",
    "4": "32 a 36 semanas",
    "5": "37 a 41 semanas",
    "6": "42 semanas ou mais",
    "9": "Ignorado",
}
MAP_GRAVIDEZ = {
    "1": "Única",
    "2": "Dupla",
    "3": "Tripla ou mais",
    "9": "Ignorado",
}
MAP_SEXO = {"1": "Masculino", "2": "Feminino", "0": "Ignorado"}
MAP_RACA = {
    "1": "Branca",
    "2": "Preta",
    "3": "Amarela",
    "4": "Parda",
    "5": "Indígena",
}
MAP_CONSULTAS = {
    "1": "Nenhuma",
    "2": "1 a 3",
    "3": "4 a 6",
    "4": "7 ou mais",
    "9": "Ignorado",
}
MAP_ESCOLARIDADE = {
    "1": "Nenhuma",
    "2": "1 a 3 anos",
    "3": "4 a 7 anos",
    "4": "8 a 11 anos",
    "5": "12 anos ou mais",
    "9": "Ignorado",
}


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    dados = pd.read_csv(
        "SINASC_2026.csv",
        sep=";",
        dtype=str,
        encoding="utf-8-sig",
        low_memory=False,
    )
    dados = dados[dados["CODMUNRES"].isin(MUNICIPIOS)].copy()

    dados["Município"] = dados["CODMUNRES"].map(MUNICIPIOS)
    dados["Data de nascimento"] = pd.to_datetime(
        dados["DTNASC"], format="%d%m%Y", errors="coerce"
    )
    dados["Mês"] = dados["Data de nascimento"].dt.month
    dados["Nome do mês"] = dados["Data de nascimento"].dt.strftime("%b").str.capitalize()
    dados["PESO"] = pd.to_numeric(dados["PESO"], errors="coerce")
    dados["IDADEMAE"] = pd.to_numeric(dados["IDADEMAE"], errors="coerce")
    dados["Peso ao nascer"] = dados["PESO"]
    dados["Idade da mãe"] = dados["IDADEMAE"]

    dados["Tipo de parto"] = dados["PARTO"].map(MAP_PARTO).fillna("Ignorado")
    dados["Duração da gestação"] = (
        dados["GESTACAO"].map(MAP_GESTACAO).fillna("Ignorado")
    )
    dados["Tipo de gravidez"] = (
        dados["GRAVIDEZ"].map(MAP_GRAVIDEZ).fillna("Ignorado")
    )
    dados["Sexo"] = dados["SEXO"].map(MAP_SEXO).fillna("Ignorado")
    dados["Raça/cor"] = dados["RACACOR"].map(MAP_RACA).fillna("Ignorado")
    dados["Consultas pré-natais"] = (
        dados["CONSULTAS"].map(MAP_CONSULTAS).fillna("Ignorado")
    )
    dados["Escolaridade"] = (
        dados["ESCMAE"].map(MAP_ESCOLARIDADE).fillna("Ignorado")
    )

    dados["Faixa etária materna"] = pd.cut(
        dados["IDADEMAE"],
        bins=[0, 19, 24, 29, 34, 39, 100],
        labels=["≤19", "20–24", "25–29", "30–34", "35–39", "40+"],
        right=True,
    ).astype("string")

    dados["Pesos válidos"] = dados["Peso ao nascer"].where(
        dados["Peso ao nascer"].between(500, 6500)
    )
    return dados


def contar_categorias(dados: pd.DataFrame, coluna: str) -> pd.DataFrame:
    return (
        dados[coluna]
        .value_counts(dropna=False)
        .rename_axis(coluna)
        .reset_index(name="Nascimentos")
    )


dados = carregar_dados()

st.markdown("""
<style>
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #dbe2ea;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 5px 14px rgba(31, 55, 77, 0.12);
}
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
    color: #1f2d3d;
}
.panel-header {
    background: #eef1f3;
    border-left: 6px solid #697780;
    border-radius: 10px;
    padding: 18px 24px;
    margin-bottom: 14px;
}
.panel-header h1 {
    color: #29343c;
    font-size: 2rem;
    margin: 0 0 4px 0;
}
.panel-header p {
    color: #52616b;
    font-size: 1rem;
    margin: 0;
}
.read-caption {
    color: #59656e;
    font-size: 0.92rem;
    margin: -4px 0 10px 0;
}
[data-testid="stMultiSelectTagsContainer"] span:has(> button[aria-label^="Remove"]) {
    background-color: #e9edef !important;
    border: 1px solid #d0d6da !important;
    color: #36414a !important;
}
[data-testid="stMultiSelectTagsContainer"] button[aria-label^="Remove"] svg {
    fill: #59656e !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    border-color: #cbd2d7 !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
    border-color: #7b8790 !important;
    box-shadow: 0 0 0 2px #49545d !important;
}
button:focus-visible,
input:focus-visible,
[role="combobox"]:focus-visible {
    outline: 3px solid #49545d !important;
    outline-offset: 2px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="panel-header">
    <h1>Panorama Materno-Infantil do Grande ABC</h1>
  <p>Responsáveis: Beatriz Jora • Laryssa Theodoro • Rodolfo Theodoro</p>
</div>
""", unsafe_allow_html=True)

municipios = sorted(dados["Município"].unique())
meses_disponiveis = sorted(dados["Mês"].dropna().unique())
nomes_meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}
sexos = ["Masculino", "Feminino", "Ignorado"]

if "filtro_municipios" not in st.session_state:
    st.session_state["filtro_municipios"] = municipios
if "filtro_meses" not in st.session_state:
    st.session_state["filtro_meses"] = meses_disponiveis
if "filtro_sexos" not in st.session_state:
    st.session_state["filtro_sexos"] = sexos


def selecionar_todos_filtros() -> None:
    st.session_state["filtro_municipios"] = municipios
    st.session_state["filtro_meses"] = meses_disponiveis
    st.session_state["filtro_sexos"] = sexos


with st.container():
    filtro_municipios, filtro_meses, filtro_sexos = st.columns([2, 1, 1])

    with filtro_municipios:
        municipios_selecionados = st.multiselect(
            "Município",
            options=municipios,
            key="filtro_municipios",
        )
        st.caption(f"{len(municipios_selecionados)} de {len(municipios)} selecionados")

    with filtro_meses:
        meses_selecionados = st.multiselect(
            "Mês",
            options=meses_disponiveis,
            format_func=lambda valor: nomes_meses.get(int(valor), str(valor)),
            key="filtro_meses",
        )
        st.caption(f"{len(meses_selecionados)} de {len(meses_disponiveis)} selecionados")

    with filtro_sexos:
        sexos_selecionados = st.multiselect(
            "Sexo",
            options=sexos,
            key="filtro_sexos",
        )
        st.caption(f"{len(sexos_selecionados)} de {len(sexos)} selecionados")

    st.button(
        "Selecionar todos",
        help="Restaura todos os municípios, meses e sexos.",
        on_click=selecionar_todos_filtros,
        key="selecionar_todos_filtros",
    )

dados_filtrados = dados[
    dados["Município"].isin(municipios_selecionados)
    & dados["Mês"].isin(meses_selecionados)
    & dados["Sexo"].isin(sexos_selecionados)
].copy()

if dados_filtrados.empty:
    st.warning("Nenhum registro corresponde aos filtros selecionados.")
    st.stop()

total = len(dados_filtrados)
sexo_validos = dados_filtrados["Sexo"].where(
    dados_filtrados["Sexo"].isin(["Masculino", "Feminino"])
).dropna()
sexo_predominante = str(sexo_validos.value_counts().idxmax()) if not sexo_validos.empty else "—"
qtd_sexo_predominante = int(sexo_validos.value_counts().max()) if not sexo_validos.empty else 0
peso_medio = dados_filtrados["Pesos válidos"].mean()
idade_media = dados_filtrados["Idade da mãe"].mean()

card1, card2, card3, card4 = st.columns(4)
card1.metric("Nascimentos", f"{total:,}".replace(",", "."))
card2.metric("Sexo predominante", sexo_predominante)
card3.metric("Peso médio", f"{peso_medio:,.0f} g".replace(",", ".") if pd.notna(peso_medio) else "—")
card4.metric("Idade média da mãe", f"{idade_media:.1f} anos".replace(".", ",") if pd.notna(idade_media) else "—")

st.divider()

cores = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]


def aplicar_texto_com_contraste(figura: Figure) -> None:
    for trace in figura.data:
        marcador = getattr(trace, "marker", None)
        cor_fundo = getattr(marcador, "color", None)
        if not isinstance(cor_fundo, str) or not cor_fundo.startswith("#") or len(cor_fundo) != 7:
            continue

        canais = [int(cor_fundo[indice:indice + 2], 16) / 255 for indice in (1, 3, 5)]
        canais_lineares = [
            canal / 12.92 if canal <= 0.04045 else ((canal + 0.055) / 1.055) ** 2.4
            for canal in canais
        ]
        luminancia = sum(
            peso * canal
            for peso, canal in zip((0.2126, 0.7152, 0.0722), canais_lineares)
        )
        trace.update(textfont_color="#1f2d3d" if luminancia > 0.179 else "#ffffff")


def exibir_grafico(titulo: str, como_ler: str, figura: Figure) -> None:
    with st.container(border=True):
        st.subheader(titulo)
        st.markdown(
            f'<p class="read-caption"><strong>Como ler:</strong> {como_ler}</p>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(figura, width="stretch")

# 1. Nascimentos por município
municipio = contar_categorias(dados_filtrados, "Município")
municipio = municipio.sort_values("Nascimentos", ascending=True)
fig = px.bar(
    municipio,
    y="Município",
    x="Nascimentos",
    orientation="h",
    text_auto=True,
    color="Município",
    color_discrete_sequence=cores,
)
fig.update_traces(textposition="outside", textfont_color="#1f2d3d", cliponaxis=False)
fig.update_layout(
    yaxis_title=None,
    showlegend=False,
)

# 2. Tipo de parto por faixa etária
cesareo_idade = (
    dados_filtrados[
        dados_filtrados["Tipo de parto"].isin(["Vaginal", "Cesáreo"])
        & dados_filtrados["Faixa etária materna"].notna()
    ]
    .groupby(["Faixa etária materna", "Tipo de parto"], observed=True)
    .size()
    .reset_index(name="Nascimentos")
)
ordem_idade = ["≤19", "20–24", "25–29", "30–34", "35–39", "40+"]

cesareo_idade["Faixa etária materna"] = pd.Categorical(
    cesareo_idade["Faixa etária materna"], categories=ordem_idade, ordered=True
)
cesareo_idade = cesareo_idade.sort_values(["Faixa etária materna", "Tipo de parto"])
fig_idade = px.bar(
    cesareo_idade,
    x="Faixa etária materna",
    y="Nascimentos",
    color="Tipo de parto",
    barmode="stack",
    text_auto=True,
    color_discrete_map={"Vaginal": "#0072B2", "Cesáreo": "#E69F00"},
)
fig_idade.update_traces(textposition="inside")
aplicar_texto_com_contraste(fig_idade)
fig_idade.update_layout(
    xaxis_title="Idade da mãe",
)

linha1_col1, linha1_col2 = st.columns(2)
with linha1_col1:
    exibir_grafico(
        "Nascimentos por município de residência",
        "A barra mais alta indica o município com mais nascimentos. As barras estão ordenadas do menor para o maior número de registros.",
        fig,
    )
with linha1_col2:
    exibir_grafico(
        "Tipo de parto por faixa etária materna",
        "Compara o tipo de parto entre idades maternas. Azul representa parto vaginal e laranja, cesárea; a idade avança da faixa mais jovem para a mais velha.",
        fig_idade,
    )

# 3. Peso ao nascer segundo o sexo
peso_sexo = dados_filtrados[
    dados_filtrados["Pesos válidos"].notna()
    & dados_filtrados["Sexo"].isin(["Masculino", "Feminino"])
].sort_values("Sexo")
fig_peso = px.box(
    peso_sexo,
    x="Sexo",
    y="Pesos válidos",
    color="Sexo",
    labels={"Pesos válidos": "Peso (gramas)"},
    category_orders={"Sexo": ["Feminino", "Masculino"]},
    color_discrete_map={"Feminino": "#CC79A7", "Masculino": "#0072B2"},
)
fig_peso.update_layout(
    showlegend=False,
)

# 4. Distribuição por raça/cor — menor para maior ocorrência
raca = contar_categorias(dados_filtrados, "Raça/cor")
raca = raca.sort_values("Nascimentos", ascending=True)
raca_ordem = raca["Raça/cor"].tolist()
fig_raca = px.bar(
    raca,
    x="Raça/cor",
    y="Nascimentos",
    color="Raça/cor",
    text_auto=True,
    category_orders={"Raça/cor": raca_ordem},
    color_discrete_sequence=cores,
)
fig_raca.update_traces(textposition="outside", textfont_color="#1f2d3d", cliponaxis=False)
fig_raca.update_layout(
    showlegend=False,
    xaxis_title=None,
)

linha2_col1, linha2_col2 = st.columns(2)
with linha2_col1:
    exibir_grafico(
        "Peso ao nascer segundo o sexo",
        "Compara pesos válidos entre nascimentos masculinos e femininos. A caixa concentra a faixa central dos dados e a linha representa a mediana em gramas.",
        fig_peso,
    )
with linha2_col2:
    exibir_grafico(
        "Distribuição por raça/cor",
        "Mostra quantos nascimentos foram registrados em cada raça/cor. As categorias aparecem da menor para a maior ocorrência.",
        fig_raca,
    )

# 5. Tipo de parto segundo a escolaridade materna
parto_escolaridade = (
    dados_filtrados[
        dados_filtrados["Tipo de parto"].isin(["Vaginal", "Cesáreo"])
        & dados_filtrados["Escolaridade"].ne("Ignorado")
    ]
    .groupby(["Escolaridade", "Tipo de parto"], observed=True)
    .size()
    .reset_index(name="Nascimentos")
)
ordem_escolaridade = ["Nenhuma", "1 a 3 anos", "4 a 7 anos", "8 a 11 anos", "12 anos ou mais"]
parto_escolaridade["Escolaridade"] = pd.Categorical(
    parto_escolaridade["Escolaridade"], categories=ordem_escolaridade, ordered=True
)
parto_escolaridade = parto_escolaridade.sort_values(["Escolaridade", "Tipo de parto"])
fig_escolaridade = px.bar(
    parto_escolaridade,
    x="Escolaridade",
    y="Nascimentos",
    color="Tipo de parto",
    barmode="stack",
    text_auto=True,
    category_orders={"Escolaridade": ordem_escolaridade},
    color_discrete_map={"Vaginal": "#0072B2", "Cesáreo": "#E69F00"},
)
fig_escolaridade.update_traces(textposition="inside")
aplicar_texto_com_contraste(fig_escolaridade)
fig_escolaridade.update_layout(
    xaxis_tickangle=-20,
)

exibir_grafico(
    "Tipo de parto segundo a escolaridade materna",
    "Relaciona o tipo de parto com os anos de estudo da mãe. As categorias avançam da menor para a maior escolaridade; azul representa vaginal e laranja, cesárea.",
    fig_escolaridade,
)

st.divider()
with st.expander("Visualizar dados filtrados"):
    colunas = [
        "Município", "Data de nascimento", "Idade da mãe", "Sexo",
        "Tipo de parto", "Duração da gestação", "Tipo de gravidez",
        "Consultas pré-natais", "Peso ao nascer", "Raça/cor",
        "Escolaridade",
    ]
    dados_exportacao = dados_filtrados[colunas].sort_values("Data de nascimento")
    st.download_button(
        "Baixar dados filtrados (CSV)",
        data=dados_exportacao.to_csv(index=False).encode("utf-8-sig"),
        file_name="nascimentos_filtrados.csv",
        mime="text/csv",
    )
    st.dataframe(
        dados_exportacao,
        width="stretch",
        hide_index=True,
    )
