import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(layout="wide")

# =========================
# CARGA DE DADOS
# =========================
df = pd.read_csv("vendas.csv", sep=";", decimal=",", encoding="latin1")

# Limpar coluna Total
df["Total"] = (
    df["Total"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.replace("R$", "", regex=False)
    .str.strip()
)
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

# =========================
# TRANSFORMAÇÕES
# =========================

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# Cidades
df["City"] = df["City"].replace({
    "Yangon": "Brasília",
    "Mandalay": "São Paulo",
    "Naypyitaw": "Curitiba"
})

# Pagamentos
df["Payment"] = df["Payment"].replace({
    "Ewallet": "Carteira digital",
    "Cash": "Dinheiro",
    "Credit card": "Cartão de crédito"
})

# =========================
# FILTRO
# =========================
month = st.sidebar.selectbox("Mês", df["Month"].unique())
df_filtered = df[df["Month"] == month]

# =========================
# TÍTULO
# =========================
st.title("Basic Analysis")

# =========================
# KPIs
# =========================
total_faturamento = df_filtered["Total"].sum()
num_vendas = len(df_filtered)
ticket_medio = total_faturamento / num_vendas if num_vendas > 0 else 0

city_top = (
    df_filtered.groupby("City")["Total"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
)

payment_top = df_filtered["Payment"].value_counts().idxmax()

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}")
kpi2.metric("N° Vendas", num_vendas)
kpi3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
kpi4.metric("Cidade Top", city_top)
kpi5.metric("Pagamento Top", payment_top)

st.markdown("---")

# =========================
# GRÁFICOS
# =========================
col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)

fig_date = px.bar(df_filtered, x="Date", y="Total", color="City",
                  title="Faturamento por dia")
col1.plotly_chart(fig_date, use_container_width=True)

fig_prod = px.bar(df_filtered, x="Product line", y="Total", color="City",
                  title="Faturamento por tipo de produto")
col2.plotly_chart(fig_prod, use_container_width=True)

city_total = df_filtered.groupby("City")[["Total"]].sum().reset_index()
fig_city = px.bar(city_total, x="City", y="Total",
                  title="Faturamento por cidade")
col3.plotly_chart(fig_city, use_container_width=True)

fig_kind = px.pie(df_filtered, values="Total", names="Payment",
                  title="Faturamento por tipo de pagamento")
col4.plotly_chart(fig_kind, use_container_width=True)

city_rating = df_filtered.groupby("City")[["Rating"]].mean().reset_index()
fig_rating = px.bar(city_rating, x="City", y="Rating",
                    title="Avaliação Média")
col5.plotly_chart(fig_rating, use_container_width=True)

# =========================
# DATATABLE CLIENTES
# =========================
st.markdown("---")
st.subheader("Tabela de Clientes")

# Campo de busca
search = st.text_input("Buscar cliente")

df_table = df_filtered[[
    "name",
    "age",
    "Gender",
    "City",
    "Product line",
    "Quantity",
    "Payment"
]].copy()

# Renombrar columnas (Português Brasil)
df_table.columns = [
    "Nome",
    "Idade",
    "Gênero",
    "Cidade",
    "Linha de Produto",
    "Quantidade",
    "Pagamento"
]

# Filtro de búsqueda
if search:
    df_table = df_table[
        df_table.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
    ]

# Mostrar tabla
st.dataframe(df_table, use_container_width=True)

