import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(layout="wide")

# =========================
# CARGA DE DATOS
# =========================
df = pd.read_csv("vendas.csv", sep=";", decimal=",")

# Limpiar columna Total (ERROR SOLUCIONADO)
df["Total"] = (
    df["Total"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.replace("R$", "", regex=False)
    .str.strip()
)
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

# =========================
# TRANSFORMACIONES
# =========================

# Fechas
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# Cambiar nombres de ciudades
df["City"] = df["City"].replace({
    "Yangon": "Brasilia",
    "Mandalay": "São Paulo",
    "Naypyitaw": "Curitiba"
})

# Traducir métodos de pago
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
ticket_promedio = total_faturamento / num_vendas if num_vendas > 0 else 0

city_top = (
    df_filtered.groupby("City")["Total"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
)

payment_top = df_filtered["Payment"].value_counts().idxmax()

# Layout KPIs
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}")
kpi2.metric("N° Vendas", num_vendas)
kpi3.metric("Ticket Promédio", f"R$ {ticket_promedio:,.2f}")
kpi4.metric("Cidade Top", city_top)
kpi5.metric("Pagamento Top", payment_top)

st.markdown("---")

# =========================
# GRÁFICOS
# =========================
col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)

# Faturamento por día
fig_date = px.bar(
    df_filtered,
    x="Date",
    y="Total",
    color="City",
    title="Faturamento por dia"
)
col1.plotly_chart(fig_date, use_container_width=True)

# Faturamento por producto
fig_prod = px.bar(
    df_filtered,
    x="Product line",
    y="Total",
    color="City",
    title="Faturamento por tipo de produto"
)
col2.plotly_chart(fig_prod, use_container_width=True)

# Faturamento por ciudad
city_total = df_filtered.groupby("City")[["Total"]].sum().reset_index()
fig_city = px.bar(
    city_total,
    x="City",
    y="Total",
    title="Faturamento por cidade"
)
col3.plotly_chart(fig_city, use_container_width=True)

# Tipo de pago
fig_kind = px.pie(
    df_filtered,
    values="Total",
    names="Payment",
    title="Faturamento por tipo de pagamento"
)
col4.plotly_chart(fig_kind, use_container_width=True)

# Rating promedio por ciudad
city_rating = df_filtered.groupby("City")[["Rating"]].mean().reset_index()
fig_rating = px.bar(
    city_rating,
    x="City",
    y="Rating",
    title="Avaliação Média"
)
col5.plotly_chart(fig_rating, use_container_width=True)