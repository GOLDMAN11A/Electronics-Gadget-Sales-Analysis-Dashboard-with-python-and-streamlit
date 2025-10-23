# import the needed libraries
import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Electronics Gadget Sales Dashboard", layout="wide")

# Load data
data_files = [
    'Sales_April_2019.csv', 'Sales_August_2019.csv', 'Sales_December_2019.csv',
    'Sales_February_2019.csv', 'Sales_January_2019.csv', 'Sales_July_2019.csv',
    'Sales_June_2019.csv', 'Sales_March_2019.csv', 'Sales_May_2019.csv',
    'Sales_November_2019.csv', 'Sales_October_2019.csv', 'Sales_September_2019.csv'
]
dt = [pd.read_csv(f) for f in data_files]
df = pd.concat(dt)

# Data cleaning
df.dropna(how='all', inplace=True)
df.drop_duplicates(inplace=True)
df = df[df['Quantity Ordered'].str.isdigit()]
df['Quantity Ordered'] = df['Quantity Ordered'].astype(int)
df = df[df['Price Each'].str.isdigit()]
df['Price Each'] = df['Price Each'].astype(float)
df = df[df['Order ID'].str.isdigit()]
df['Order ID'] = df['Order ID'].astype(int)
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

# Feature engineering
df['Month'] = df['Order Date'].dt.month_name()
df['Day'] = df['Order Date'].dt.day_name()
df['Order Time'] = df['Order Date'].dt.time
df['Amount'] = (df['Quantity Ordered'] * df['Price Each']).round(2)
df['City'] = df['Purchase Address'].apply(lambda city: city.split(',')[-2])

st.markdown("<h1 style='color:green;'>📊 Electronics Gadget Sales Analysis</h1>", unsafe_allow_html=True)
st.markdown("#### By OLUWADAMILARE JACOB")

# FILTERS
with st.sidebar:
    st.header("Filter Data")
    # Product filter
    products = df['Product'].unique()
    selected_products = st.multiselect("Select Product(s):", options=products, default=list(products))
    # City filter
    cities = df['City'].unique()
    selected_cities = st.multiselect("Select City/Cities:", options=cities, default=list(cities))
    # Month filter
    months = df['Month'].dropna().unique()
    selected_months = st.multiselect("Select Month(s):", options=months, default=list(months))

# Apply filters
filtered_df = df[
    df['Product'].isin(selected_products) &
    df['City'].isin(selected_cities) &
    df['Month'].isin(selected_months)
]

# KPIs
Total_Products = filtered_df['Product'].nunique()
No_of_City = filtered_df['City'].nunique()
Quantity_Ordered = filtered_df['Quantity Ordered'].sum()
Revenue = filtered_df['Amount'].sum()

st.header("Key Performance Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products", Total_Products)
col2.metric("No. of Cities", No_of_City)
col3.metric("Quantity Ordered", Quantity_Ordered)
col4.metric("Revenue ($)", f"{Revenue:,.2f}")

# Weekly Sales Trend
st.subheader("Weekly Sales Trend")
weekly = filtered_df.groupby('Day')['Amount'].sum()
weekly = weekly.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
fig1 = px.line(
    weekly,
    x=weekly.index,
    y=weekly.values,
    markers=True,
    labels={'x': 'Day', 'y': 'Total Amount'},
    title='Weekly Sales Trend for 2019'
)
fig1.update_traces(line_color='red')
fig1.update_layout(xaxis_tickangle=30)
st.plotly_chart(fig1, use_container_width=True)

# Product Sales Performance
st.subheader("Product Sales Performance by Total Orders and Amount")
per = filtered_df.groupby('Product')[['Amount', 'Quantity Ordered']].sum().sort_values(by='Quantity Ordered', ascending=False)
fig2 = px.bar(
    per,
    x=per.index,
    y=['Amount', 'Quantity Ordered'],
    barmode='stack',
    labels={'value': 'Total', 'variable': 'Metric', 'Product': 'Product'},
    title='Product Sales Performance',
    color_discrete_map={'Amount': 'gold', 'Quantity Ordered': 'lightgreen'}
)
fig2.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig2, use_container_width=True)

# City Revenue
st.subheader("City With The Highest Revenue")
city_sales = filtered_df.groupby('City')['Amount'].sum().sort_values(ascending=False)
fig3 = px.bar(
    city_sales,
    x=city_sales.index,
    y=city_sales.values,
    labels={'x': 'City', 'y': 'Total Revenue'},
    title='Revenue by City',
    color_discrete_sequence=['skyblue']
)
fig3.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig3, use_container_width=True)

# Product Sales by City
st.subheader("Product Sales by City")
gd = filtered_df.groupby(['City', 'Product'])['Amount'].sum().unstack()
fig4 = px.bar(
    gd,
    barmode='group',
    labels={'value': 'Average Amount', 'City': 'City', 'variable': 'Product'},
    title='Average Product Sales by City'
)
fig4.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("Data Source: Blord Group Electronics Gadget Sales 2019")

# show raw data
with st.expander('Show Raw Data'):
    st.dataframe(filtered_df.reset_index(drop=True))