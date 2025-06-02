import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(page_title="E-Commerce Analytics", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce_data.csv")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df = df[(df['Quantity'] > 0) & (df['TotalPrice'] > 0)]
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")
year = st.sidebar.selectbox("Select Year", sorted(df['InvoiceDate'].dt.year.unique()))
country = st.sidebar.selectbox("Select Country", sorted(df['Country'].unique()))

df_filtered = df[(df['InvoiceDate'].dt.year == year) & (df['Country'] == country)]

# Title
st.title("📊 E-Commerce Dashboard")
st.markdown(f"### Year: {year} | Country: {country}")

# KPI cards
col1, col2, col3 = st.columns(3)
col1.metric("💰 Revenue", f"${df_filtered['TotalPrice'].sum():,.2f}")
col2.metric("🧾 Orders", df_filtered['InvoiceNo'].nunique())
col3.metric("👥 Customers", df_filtered['CustomerID'].nunique())

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Sales Trends", "🏆 Top Products", "🧠 RFM Segmentation"])

# Tab 1: Sales Trends
with tab1:
    st.subheader("Monthly Revenue")
    df_filtered['Month'] = df_filtered['InvoiceDate'].dt.to_period("M").astype(str)
    revenue_monthly = df_filtered.groupby('Month')['TotalPrice'].sum().reset_index()

    fig1 = px.line(revenue_monthly, x="Month", y="TotalPrice", markers=True,
                   labels={"TotalPrice": "Revenue"}, template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

# Tab 2: Top Products
with tab2:
    st.subheader("Top 10 Products")
    top_products = df_filtered.groupby('Description')['Quantity'].sum().nlargest(10).reset_index()

    fig2 = px.bar(top_products, x='Quantity', y='Description', orientation='h',
                  title="Best-Selling Products", color='Quantity',
                  template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# Tab 3: RFM Segmentation
with tab3:
    st.subheader("Customer Segmentation (RFM)")

    snapshot_date = df_filtered['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df_filtered.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    }).rename(columns={'InvoiceDate': 'Recency', 'InvoiceNo': 'Frequency', 'TotalPrice': 'Monetary'})

    rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'], 4, labels=[1, 2, 3, 4])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

    top_customers = rfm[rfm['RFM_Score'] == '444'].sort_values('Monetary', ascending=False).head(10)
    st.markdown("##### 🔝 Top Customers (RFM Score = 444)")
    st.dataframe(top_customers.style.format({'Monetary': '${:,.2f}'}), use_container_width=True)

    st.markdown("##### 🔥 RFM Segment Overview")
    heatmap_data = rfm.groupby(['R_Score', 'F_Score']).size().reset_index(name='Count')
    fig3 = px.density_heatmap(
        heatmap_data, x='F_Score', y='R_Score', z='Count',
        color_continuous_scale='Blues', template="plotly_dark"
    )
    st.plotly_chart(fig3, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by **Sourish Das** | [GitHub](https://github.com) | [LinkedIn](https://linkedin.com)")
