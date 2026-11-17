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

st.title("Painel de Monitoramento de Nascimentos")
st.caption(
    "SINASC 2026 • Região Metropolitana do Grande ABC • "
    "Dados de residência da mãe"
)

with st.sidebar:
    st.header("Filtros")
    municipios = sorted(dados["Município"].unique())
    municipios_selecionados = st.multiselect(
        "Município",
        options=municipios,
        default=municipios,
    )

    meses_disponiveis = sorted(dados["Mês"].dropna().unique())
    nomes_meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }
    meses_selecionados = st.multiselect(
        "Mês",
        options=meses_disponiveis,
        format_func=lambda valor: nomes_meses.get(int(valor), str(valor)),
        default=meses_disponiveis,
    )

    sexos = ["Masculino", "Feminino", "Ignorado"]
    sexos_selecionados = st.multiselect(
        "Sexo",
        options=sexos,
        default=sexos,
    )

    st.divider()
    st.write(f"**Registros encontrados:** {len(dados):,}".replace(",", "."))

dados_filtrados = dados[
    dados["Município"].isin(municipios_selecionados)
    & dados["Mês"].isin(meses_selecionados)
    & dados["Sexo"].isin(sexos_selecionados)
].copy()

if dados_filtrados.empty:
    st.warning("Nenhum registro corresponde aos filtros selecionados.")
    st.stop()

total = len(dados_filtrados)
cesareos = (dados_filtrados["Tipo de parto"] == "Cesáreo").sum()
percentual_cesareo = 100 * cesareos / total
peso_medio = dados_filtrados["Pesos válidos"].mean()
idade_media = dados_filtrados["Idade da mãe"].mean()

card1, card2, card3, card4 = st.columns(4)
card1.metric("Nascimentos", f"{total:,}".replace(",", "."))
card2.metric("Partos cesáreos", f"{percentual_cesareo:.1f}%")
card3.metric("Peso médio", f"{peso_medio:,.0f} g".replace(",", ".") if pd.notna(peso_medio) else "—")
card4.metric("Idade média da mãe", f"{idade_media:.1f} anos" if pd.notna(idade_media) else "—")

st.divider()

aba1, aba2, aba3 = st.tabs(["Visão geral", "Gestação e nascimento", "Mãe e município"])

with aba1:
    col1, col2 = st.columns(2)

    with col1:
        nascimento_mensal = (
            dados_filtrados.dropna(subset=["Data de nascimento"])
            .groupby(["Mês", "Nome do mês"], as_index=False)
            .size()
            .rename(columns={"size": "Nascimentos"})
            .sort_values("Mês")
        )
        fig = px.line(
            nascimento_mensal,
            x="Nome do mês",
            y="Nascimentos",
            markers=True,
            title="Evolução mensal dos nascimentos",
        )
        fig.update_layout(xaxis_title=None)
        st.plotly_chart(fig, width="stretch")

    with col2:
        parto = contar_categorias(dados_filtrados, "Tipo de parto")
        fig = px.bar(
            parto,
            x="Tipo de parto",
            y="Nascimentos",
            color="Tipo de parto",
            title="Distribuição por tipo de parto",
            text_auto=True,
        )
        fig.update_layout(showlegend=False, xaxis_title=None)
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        municipio = contar_categorias(dados_filtrados, "Município")
        municipio = municipio.sort_values("Nascimentos", ascending=True)
        fig = px.bar(
            municipio,
            y="Município",
            x="Nascimentos",
            orientation="h",
            title="Nascimentos por município de residência",
            text_auto=True,
        )
        fig.update_layout(yaxis_title=None)
        st.plotly_chart(fig, width="stretch")

    with col4:
        gravidez = contar_categorias(dados_filtrados, "Tipo de gravidez")
        fig = px.bar(
            gravidez,
            x="Tipo de gravidez",
            y="Nascimentos",
            color="Tipo de gravidez",
            title="Distribuição por tipo de gravidez",
            text_auto=True,
        )
        fig.update_layout(showlegend=False, xaxis_title=None)
        st.plotly_chart(fig, width="stretch")

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        gestacao = contar_categorias(dados_filtrados, "Duração da gestação")
        gestacao_ordem = list(MAP_GESTACAO.values())
        gestacao["Ordem"] = gestacao["Duração da gestação"].map(
            {categoria: indice for indice, categoria in enumerate(gestacao_ordem)}
        )
        gestacao = gestacao.sort_values("Ordem")
        fig = px.bar(
            gestacao,
            x="Duração da gestação",
            y="Nascimentos",
            title="Duração da gestação",
            text_auto=True,
        )
        fig.update_layout(xaxis_tickangle=-25)
        st.plotly_chart(fig, width="stretch")

    with col2:
        peso = dados_filtrados["Pesos válidos"].dropna()
        fig = px.histogram(
            peso,
            nbins=40,
            title="Distribuição do peso ao nascer",
            labels={"value": "Peso (gramas)", "count": "Nascimentos"},
        )
        fig.update_layout(xaxis_title="Peso (gramas)", yaxis_title="Nascimentos", showlegend=False)
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        peso_sexo = dados_filtrados[
            dados_filtrados["Pesos válidos"].notna()
            & dados_filtrados["Sexo"].isin(["Masculino", "Feminino"])
        ]
        fig = px.box(
            peso_sexo,
            x="Sexo",
            y="Pesos válidos",
            color="Sexo",
            title="Peso ao nascer segundo o sexo",
            labels={"Pesos válidos": "Peso (gramas)"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    with col4:
        consultas = contar_categorias(dados_filtrados, "Consultas pré-natais")
        consultas_ordem = list(MAP_CONSULTAS.values())
        consultas["Ordem"] = consultas["Consultas pré-natais"].map(
            {categoria: indice for indice, categoria in enumerate(consultas_ordem)}
        )
        consultas = consultas.sort_values("Ordem")
        fig = px.bar(
            consultas,
            x="Consultas pré-natais",
            y="Nascimentos",
            title="Número de consultas pré-natais",
            text_auto=True,
        )
        fig.update_layout(xaxis_title="Quantidade de consultas")
        st.plotly_chart(fig, width="stretch")

with aba3:
    col1, col2 = st.columns(2)
    with col1:
        cesareo_idade = (
            dados_filtrados[
                dados_filtrados["Tipo de parto"].isin(["Vaginal", "Cesáreo"])
                & dados_filtrados["Faixa etária materna"].notna()
            ]
            .groupby(["Faixa etária materna", "Tipo de parto"], observed=True)
            .size()
            .reset_index(name="Nascimentos")
        )
        fig = px.bar(
            cesareo_idade,
            x="Faixa etária materna",
            y="Nascimentos",
            color="Tipo de parto",
            barmode="stack",
            title="Tipo de parto por faixa etária materna",
        )
        fig.update_layout(xaxis_title="Idade da mãe")
        st.plotly_chart(fig, width="stretch")

    with col2:
        raca = contar_categorias(dados_filtrados, "Raça/cor")
        fig = px.bar(
            raca,
            x="Raça/cor",
            y="Nascimentos",
            color="Raça/cor",
            title="Distribuição por raça/cor",
            text_auto=True,
        )
        fig.update_layout(showlegend=False, xaxis_title=None)
        st.plotly_chart(fig, width="stretch")

    parto_escolaridade = (
        dados_filtrados[
            dados_filtrados["Tipo de parto"].isin(["Vaginal", "Cesáreo"])
            & dados_filtrados["Escolaridade"].ne("Ignorado")
        ]
        .groupby(["Escolaridade", "Tipo de parto"], observed=True)
        .size()
        .reset_index(name="Nascimentos")
    )
    fig = px.bar(
        parto_escolaridade,
        x="Escolaridade",
        y="Nascimentos",
        color="Tipo de parto",
        barmode="stack",
        title="Tipo de parto segundo a escolaridade materna",
    )
    fig.update_layout(xaxis_tickangle=-20)
    st.plotly_chart(fig, width="stretch")

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
