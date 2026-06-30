
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Afficionado Coffee Dashboard",
    page_icon="☕",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("☕ Afficionado Coffee Roasters")
st.markdown("### Product Optimization & Revenue Contribution Analysis")

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("coffee_cleaned.csv")
    df["Revenue"] = df["transaction_qty"] * df["unit_price"]
    df["transaction_time"] = pd.to_datetime(
    df["transaction_time"],
    errors="coerce"
)
    df["Hour"] = df["transaction_time"].dt.hour
    return df

df = load_data()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("🔍 Filters")

store = st.sidebar.selectbox(
    "Store Location",
    ["All"] + sorted(df["store_location"].unique().tolist())
)

category = st.sidebar.selectbox(
    "Product Category",
    ["All"] + sorted(df["product_category"].unique().tolist())
)

product_type = st.sidebar.selectbox(
    "Product Type",
    ["All"] + sorted(df["product_type"].unique().tolist())
)

top_n = st.sidebar.slider(
    "Top N Products",
    5,
    20,
    10
)

# -----------------------------
# Apply Filters
# -----------------------------
filtered_df = df.copy()

if store != "All":
    filtered_df = filtered_df[
        filtered_df["store_location"] == store
    ]

if category != "All":
    filtered_df = filtered_df[
        filtered_df["product_category"] == category
    ]

if product_type != "All":
    filtered_df = filtered_df[
        filtered_df["product_type"] == product_type
    ]

# -----------------------------
# KPI Calculations
# -----------------------------
total_revenue = filtered_df["Revenue"].sum()

total_transactions = filtered_df["transaction_id"].nunique()

total_units = filtered_df["transaction_qty"].sum()

avg_order = (
    filtered_df
    .groupby("transaction_id")["Revenue"]
    .sum()
    .mean()
)

# -----------------------------
# KPI Cards
# -----------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Revenue",
    f"${total_revenue:,.0f}"
)

col2.metric(
    "🛒 Transactions",
    f"{total_transactions:,}"
)

col3.metric(
    "☕ Units Sold",
    f"{total_units:,}"
)

col4.metric(
    "📈 Avg Order Value",
    f"${avg_order:.2f}"
)

st.divider()


# ==========================================================
# Revenue by Category
# ==========================================================

st.subheader("📊 Revenue by Product Category")

category_revenue = (
    filtered_df.groupby("product_category")["Revenue"]
    .sum()
    .reset_index()
)

fig = px.pie(
    category_revenue,
    names="product_category",
    values="Revenue",
    hole=0.45,
    title="Revenue Distribution"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Top Products
# ==========================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🏆 Top Products by Revenue")

    top_revenue = (
        filtered_df.groupby("product_detail")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    fig = px.bar(
        top_revenue,
        x="Revenue",
        y="product_detail",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    st.subheader("☕ Top Products by Units Sold")

    top_qty = (
        filtered_df.groupby("product_detail")["transaction_qty"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    fig = px.bar(
        top_qty,
        x="transaction_qty",
        y="product_detail",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)



# ==========================================================
# Store-wise Revenue
# ==========================================================

st.subheader("🏪 Revenue by Store Location")

store_revenue = (
    filtered_df.groupby("store_location")["Revenue"]
    .sum()
    .reset_index()
)

fig = px.bar(
    store_revenue,
    x="store_location",
    y="Revenue",
    color="store_location",
    title="Revenue by Store"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Revenue by Hour
# ==========================================================

st.subheader("⏰ Revenue by Hour")

hourly_revenue = (
    filtered_df.groupby("Hour")["Revenue"]
    .sum()
    .reset_index()
)

fig = px.line(
    hourly_revenue,
    x="Hour",
    y="Revenue",
    markers=True,
    title="Hourly Revenue"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Product Type Revenue
# ==========================================================

st.subheader("☕ Product Type Revenue")

ptype = (
    filtered_df.groupby("product_type")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    ptype,
    x="Revenue",
    y="product_type",
    orientation="h",
    title="Top Product Types"
)

st.plotly_chart(fig, use_container_width=True)



# ==========================================================
# Revenue vs Popularity
# ==========================================================

st.subheader("📈 Revenue vs Popularity")

scatter = (
    filtered_df.groupby("product_detail")
    .agg({
        "transaction_qty":"sum",
        "Revenue":"sum"
    })
    .reset_index()
)

fig = px.scatter(
    scatter,
    x="transaction_qty",
    y="Revenue",
    hover_name="product_detail",
    size="Revenue",
    color="Revenue",
    title="Revenue vs Popularity"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Pareto Analysis
# ==========================================================

st.subheader("📊 Pareto Analysis (80/20 Rule)")

pareto = (
    filtered_df.groupby("product_detail")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

pareto["Revenue %"] = (
    pareto["Revenue"] /
    pareto["Revenue"].sum()
) * 100

pareto["Cumulative %"] = pareto["Revenue %"].cumsum()

fig = px.line(
    pareto,
    x="product_detail",
    y="Cumulative %",
    markers=True,
    title="Pareto Analysis"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Product Efficiency
# ==========================================================

st.subheader("🏆 Product Efficiency")

efficiency = (
    filtered_df.groupby("product_detail")
    .agg({
        "Revenue":"sum",
        "transaction_id":"count"
    })
)

efficiency.columns = ["Revenue","Transactions"]

efficiency["Efficiency Score"] = (
    efficiency["Revenue"] /
    efficiency["Transactions"]
)

efficiency = efficiency.sort_values(
    "Efficiency Score",
    ascending=False
)

st.dataframe(efficiency.head(15))

# ==========================================================
# Download Button
# ==========================================================

st.subheader("📥 Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_coffee_data.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown(
    "### ✅ Dashboard Created by Md Shayan"
)

