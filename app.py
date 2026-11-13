import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Dashboard de vendas",
    page_icon="📊",
    layout="wide",
)

# Dados de demonstração: um registro por mês e categoria.
meses = pd.date_range("2026-01-01", periods=12, freq="MS")
vendas_por_categoria = {
    "Eletrônicos": [1200, 1350, 1280, 1500, 1600, 1550, 1700, 1800, 1750, 1900, 2050, 2200],
    "Casa": [800, 820, 900, 870, 950, 980, 1020, 1100, 1080, 1150, 1200, 1300],
    "Esportes": [500, 550, 520, 600, 650, 700, 680, 750, 800, 780, 850, 900],
}

registros = []
for indice, mes in enumerate(meses):
    for categoria, valores in vendas_por_categoria.items():
        registros.append(
            {
                "Mês": mes,
                "Categoria": categoria,
                "Vendas": valores[indice],
            }
        )

df = pd.DataFrame(registros)

st.title("Dashboard de vendas")
st.caption("Explore os resultados por categoria usando os filtros e gráficos interativos.")

# Filtro de categoria.
categorias = sorted(df["Categoria"].unique().tolist())
categorias_selecionadas = st.sidebar.multiselect(
    "Categorias",
    options=categorias,
    default=categorias,
)

if categorias_selecionadas:
    dados = df[df["Categoria"].isin(categorias_selecionadas)].copy()
else:
    dados = df.iloc[0:0].copy()

if dados.empty:
    st.info("Selecione pelo menos uma categoria na barra lateral.")
    st.stop()

# Cards: indicadores resumidos do conjunto filtrado.
total_vendas = dados["Vendas"].sum()
media_mensal = dados.groupby("Mês")["Vendas"].sum().mean()
vendas_por_categoria_filtrada = dados.groupby("Categoria")["Vendas"].sum()
categoria_lider = vendas_por_categoria_filtrada.idxmax()

def moeda_br(valor):
    """Formata um número como moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


card1, card2, card3 = st.columns(3)
card1.metric("Vendas no período", moeda_br(total_vendas))
card2.metric("Média mensal", moeda_br(media_mensal))
card3.metric("Categoria líder", categoria_lider)

# Agregações para os gráficos.
vendas_mensais = (
    dados.groupby("Mês", as_index=False)["Vendas"]
    .sum()
    .sort_values("Mês")
)
vendas_categorias = (
    dados.groupby("Categoria", as_index=False)["Vendas"]
    .sum()
    .sort_values("Vendas", ascending=False)
)

coluna_linha, coluna_pizza = st.columns(2)

with coluna_linha:
    st.subheader("Evolução mensal")
    figura_linha = px.line(
        vendas_mensais,
        x="Mês",
        y="Vendas",
        markers=True,
        title="Vendas totais por mês",
        labels={"Mês": "Mês", "Vendas": "Vendas (R$)"},
    )
    figura_linha.update_layout(xaxis_title=None, yaxis_title="Vendas (R$)")
    st.plotly_chart(figura_linha, use_container_width=True)

with coluna_pizza:
    st.subheader("Participação por categoria")
    figura_pizza = px.pie(
        vendas_categorias,
        names="Categoria",
        values="Vendas",
        title="Participação no total de vendas",
        hole=0.35,
    )
    figura_pizza.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(figura_pizza, use_container_width=True)

st.subheader("Comparação entre categorias")
figura_barras = px.bar(
    vendas_categorias,
    x="Categoria",
    y="Vendas",
    color="Categoria",
    title="Vendas totais por categoria",
    labels={"Categoria": "Categoria", "Vendas": "Vendas (R$)"},
    text_auto=".2s",
)
figura_barras.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Vendas (R$)")
st.plotly_chart(figura_barras, use_container_width=True)

st.subheader("Dados filtrados")
st.dataframe(
    dados.sort_values(["Mês", "Categoria"]),
    use_container_width=True,
    hide_index=True,
)

df.to_csv('dados.csv', index=False)