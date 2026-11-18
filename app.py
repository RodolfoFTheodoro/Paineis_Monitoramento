import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Painel SINASC - Grande ABC",
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
    background: #dcecf7;
    border-left: 8px solid #0072B2;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 14px;
}
.panel-header h1 {
    color: #16324f;
    font-size: 2rem;
    margin: 0 0 4px 0;
}
.panel-header p {
    color: #52616b;
    font-size: 1rem;
    margin: 0;
}
.filter-box {
    background: #f6f8fa;
    border: 1px solid #dbe2ea;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 14px;
}
.read-caption {
    color: #52616b;
    font-size: 0.92rem;
    margin: 2px 0 18px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="panel-header">
  <h1>Painel de Monitoramento de Nascimentos</h1>
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

with st.container():
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    filtro_municipios, filtro_meses, filtro_sexos = st.columns([2, 1, 1])

    with filtro_municipios:
        st.markdown("**Município**")
        municipios_selecionados = []
        municipio_colunas = st.columns(4)
        for indice, municipio_nome in enumerate(municipios):
            if municipio_colunas[indice % 4].checkbox(
                municipio_nome,
                value=True,
                key=f"mun_{municipio_nome}",
            ):
                municipios_selecionados.append(municipio_nome)

    with filtro_meses:
        meses_selecionados = st.multiselect(
            "Mês",
            options=meses_disponiveis,
            format_func=lambda valor: nomes_meses.get(int(valor), str(valor)),
            default=meses_disponiveis,
        )

    with filtro_sexos:
        sexos_selecionados = st.multiselect(
            "Sexo",
            options=sexos,
            default=sexos,
        )

    st.markdown('</div>', unsafe_allow_html=True)

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
sexo_predominante = sexo_validos.value_counts().idxmax() if not sexo_validos.empty else "—"
qtd_sexo_predominante = int(sexo_validos.value_counts().max()) if not sexo_validos.empty else 0
peso_medio = dados_filtrados["Pesos válidos"].mean()
idade_media = dados_filtrados["Idade da mãe"].mean()

card1, card2, card3, card4 = st.columns(4)
card1.metric("Nascimentos", f"{total:,}".replace(".", "X").replace(",", ".").replace("X", ","))
card2.metric("Sexo predominante", sexo_predominante)
card3.metric("Peso médio", f"{peso_medio:,.0f} g".replace(",", ".") if pd.notna(peso_medio) else "—")
card4.metric("Idade média da mãe", f"{idade_media:.1f} anos".replace(".", ",") if pd.notna(idade_media) else "—")

st.divider()

cores = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]

# 1. Nascimentos por município
municipio = contar_categorias(dados_filtrados, "Município")
municipio = municipio.sort_values("Nascimentos", ascending=True)
fig = px.bar(
    municipio,
    y="Município",
    x="Nascimentos",
    orientation="h",
    title="Nascimentos por município de residência",
    text_auto=True,
    color="Município",
    color_discrete_sequence=cores,
)
fig.update_layout(
    title={"text": "Nascimentos por município de residência", "x": 0, "font": {"size": 20}},
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
    title="Tipo de parto por faixa etária materna",
    color_discrete_map={"Vaginal": "#0072B2", "Cesáreo": "#E69F00"},
)
fig_idade.update_layout(
    title={"text": "Tipo de parto por faixa etária materna", "x": 0, "font": {"size": 20}},
    xaxis_title="Idade da mãe",
)

linha1_col1, linha1_col2 = st.columns(2)
with linha1_col1:
    st.plotly_chart(fig, width="stretch")
    st.markdown(
        '<p class="read-caption"><strong>Como ler:</strong> a barra mais alta indica o município com mais nascimentos. As barras estão ordenadas do menor para o maior número de registros.</p>',
        unsafe_allow_html=True,
    )
with linha1_col2:
    st.plotly_chart(fig_idade, width="stretch")
    st.markdown(
        '<p class="read-caption"><strong>Como ler:</strong> compara o tipo de parto entre idades maternas. Azul representa parto vaginal e laranja, cesárea; a idade avança da faixa mais jovem para a mais velha.</p>',
        unsafe_allow_html=True,
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
    title="Peso ao nascer segundo o sexo",
    labels={"Pesos válidos": "Peso (gramas)"},
    category_orders={"Sexo": ["Feminino", "Masculino"]},
    color_discrete_map={"Feminino": "#CC79A7", "Masculino": "#0072B2"},
)
fig_peso.update_layout(
    title={"text": "Peso ao nascer segundo o sexo", "x": 0, "font": {"size": 20}},
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
    title="Distribuição por raça/cor",
    text_auto=True,
    category_orders={"Raça/cor": raca_ordem},
    color_discrete_sequence=cores,
)
fig_raca.update_layout(
    title={"text": "Distribuição por raça/cor", "x": 0, "font": {"size": 20}},
    showlegend=False,
    xaxis_title=None,
)

linha2_col1, linha2_col2 = st.columns(2)
with linha2_col1:
    st.plotly_chart(fig_peso, width="stretch")
    st.markdown(
        '<p class="read-caption"><strong>Como ler:</strong> compara pesos válidos entre nascimentos masculinos e femininos. A caixa concentra a faixa central dos dados e a linha representa a mediana em gramas.</p>',
        unsafe_allow_html=True,
    )
with linha2_col2:
    st.plotly_chart(fig_raca, width="stretch")
    st.markdown(
        '<p class="read-caption"><strong>Como ler:</strong> mostra quantos nascimentos foram registrados em cada raça/cor. As categorias aparecem da menor para a maior ocorrência.</p>',
        unsafe_allow_html=True,
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
    title="Tipo de parto segundo a escolaridade materna",
    category_orders={"Escolaridade": ordem_escolaridade},
    color_discrete_map={"Vaginal": "#0072B2", "Cesáreo": "#E69F00"},
)
fig_escolaridade.update_layout(
    title={"text": "Tipo de parto segundo a escolaridade materna", "x": 0, "font": {"size": 20}},
    xaxis_tickangle=-20,
)

st.plotly_chart(fig_escolaridade, width="stretch")
st.markdown(
    '<p class="read-caption"><strong>Como ler:</strong> relaciona o tipo de parto com os anos de estudo da mãe. As categorias avançam da menor para a maior escolaridade; azul representa vaginal e laranja, cesárea.</p>',
    unsafe_allow_html=True,
)

st.divider()
with st.expander("Visualizar dados filtrados"):
    colunas = [
        "Município", "Data de nascimento", "Idade da mãe", "Sexo",
        "Tipo de parto", "Duração da gestação", "Tipo de gravidez",
        "Consultas pré-natais", "Peso ao nascer", "Raça/cor",
        "Escolaridade",
    ]
    st.dataframe(
        dados_filtrados[colunas].sort_values("Data de nascimento"),
        width="stretch",
        hide_index=True,
    )
