import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="E-Commerce Analytics Dashboard", layout="wide")

st.title("🛒 E-Commerce Customer Purchase Behavior Analysis")

@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce_data.csv")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df = df[df['Quantity'] > 0]
    df = df[df['TotalPrice'] > 0]
    return df

df = load_data()

st.header("Dataset Overview")
st.write(f"Number of records: {df.shape[0]}")
st.write("Missing values:")
st.write(df.isnull().sum())

st.header("Revenue by Country")
country_revenue = df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)
st.bar_chart(country_revenue)

st.header("Monthly Revenue Trend")
df['Month'] = df['InvoiceDate'].dt.to_period('M')
monthly_revenue = df.groupby('Month')['TotalPrice'].sum()
st.line_chart(monthly_revenue.astype(float))

st.header("Top 10 Products Sold by Quantity")
top_products = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_products)

st.header("RFM Customer Segmentation")

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

rfm['R_Quartile'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1])
rfm['F_Quartile'] = pd.qcut(rfm['Frequency'], 4, labels=[1,2,3,4])
rfm['M_Quartile'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4])
rfm['RFM_Score'] = rfm['R_Quartile'].astype(str) + rfm['F_Quartile'].astype(str) + rfm['M_Quartile'].astype(str)

st.write("Top Customers (RFM Score = 444):")
st.dataframe(rfm[rfm['RFM_Score'] == '444'].head())

st.write("Heatmap of RFM Segments:")
import seaborn as sns
import matplotlib.pyplot as plt

rfm_counts = rfm.groupby(['R_Quartile', 'F_Quartile']).size().unstack()

fig, ax = plt.subplots(figsize=(8,5))
sns.heatmap(rfm_counts, annot=True, fmt="d", cmap="Blues", ax=ax)
st.pyplot(fig)
