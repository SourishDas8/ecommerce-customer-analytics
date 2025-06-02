import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="E-Commerce Analytics", layout="wide")

# Load & preprocess
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce_data.csv")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df = df[df['Quantity'] > 0]
    df = df[df['TotalPrice'] > 0]
    return df

df = load_data()

st.title("📊 E-Commerce Analytics Dashboard")

# ======================
#  METRIC CARDS SECTION
# ======================
col1, col2, col3, col4 = st.columns(4)
total_revenue = round(df['TotalPrice'].sum(), 2)
total_orders = df['InvoiceNo'].nunique()
total_customers = df['CustomerID'].nunique()
top_country = df.groupby('Country')['TotalPrice'].sum().idxmax()

col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
col2.metric("🧾 Total Orders", total_orders)
col3.metric("🧍 Unique Customers", total_customers)
col4.metric("🌍 Top Country", top_country)

# =========================
#  TABS FOR NAVIGATION
# =========================
tab1, tab2, tab3 = st.tabs(["📈 Sales Analysis", "🛒 Top Products", "👥 RFM Segmentation"])

# ======================
#  TAB 1: SALES ANALYSIS
# ======================
with tab1:
    st.subheader("Monthly Revenue")
    df['Month'] = df['InvoiceDate'].dt.to_period('M')
    monthly_revenue = df.groupby('Month')['TotalPrice'].sum()
    st.line_chart(monthly_revenue.astype(float))

    st.subheader("Revenue by Country")
    country_revenue = df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=country_revenue.values, y=country_revenue.index, palette="viridis", ax=ax)
    ax.set_xlabel("Revenue")
    ax.set_ylabel("Country")
    st.pyplot(fig)

# ======================
#  TAB 2: TOP PRODUCTS
# ======================
with tab2:
    st.subheader("Top 10 Products by Quantity Sold")
    top_products = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_products.values, y=top_products.index, palette="mako", ax=ax)
    ax.set_xlabel("Quantity Sold")
    st.pyplot(fig)

# ======================
#  TAB 3: RFM SEGMENTATION
# ======================
with tab3:
    st.subheader("RFM Segmentation of Customers")

    ref_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (ref_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    }).rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalPrice': 'Monetary'
    })

    rfm['R_Quartile'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
    rfm['F_Quartile'] = pd.qcut(rfm['Frequency'], 4, labels=[1, 2, 3, 4])
    rfm['M_Quartile'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])
    rfm['RFM_Score'] = rfm['R_Quartile'].astype(str) + rfm['F_Quartile'].astype(str) + rfm['M_Quartile'].astype(str)

    st.write("🔝 Top Customers (RFM Score = 444)")
    st.dataframe(rfm[rfm['RFM_Score'] == '444'].sort_values(by='Monetary', ascending=False).head(10))

    st.write("📊 RFM Segment Heatmap")
    rfm_counts = rfm.groupby(['R_Quartile', 'F_Quartile']).size().unstack()

    fig2, ax2 = plt.subplots()
    sns.heatmap(rfm_counts, annot=True, fmt="d", cmap="YlGnBu", ax=ax2)
    st.pyplot(fig2)
