import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load CSV data
def load_data():
    data = pd.read_csv('Main4 - Main3.csv')
    return data

# Load data
data = load_data()

# Sidebar: Display raw data
def show_data():
    st.sidebar.header("Raw Data")
    if st.sidebar.checkbox("Show raw data"):
        st.write(data)

# Utility function to clean currency strings
def clean_currency(x):
    return float(str(x).replace(',', ''))

data['Qty'] = data['Qty'].apply(clean_currency)
data['Value'] = data['Value'].apply(clean_currency)
data['Rate'] = data['Rate'].apply(clean_currency)

def plot_sales_distribution(data):
    sales_distribution = data.groupby('Customer')['Value'].sum().reset_index().sort_values(by='Value', ascending=False)

    fig = px.bar(sales_distribution, x='Value', y='Customer', orientation='h', title='Sales Distribution by Party', color='Value', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

def plot_production_fluctuations(data):
    production_volume = data.groupby('Date')['Qty'].sum().reset_index()
    production_volume['Date'] = pd.to_datetime(production_volume['Date'], errors='coerce', dayfirst=True)

    fig = px.line(production_volume, x='Date', y='Qty', title='Production Volume Fluctuations', markers=True)
    fig.update_traces(line_color='blue')
    st.plotly_chart(fig, use_container_width=True)

def quadrant_analysis(data):
    data['Volume-Sales Ratio'] = data['Qty'] / data['Value']
    quadrant = data[['Part description', 'Qty', 'Value', 'Volume-Sales Ratio']].copy()
    quadrants = {'HV-HS': [], 'HV-LS': [], 'LV-HS': [], 'LV-LS': []}
    threshold_qty = quadrant['Qty'].median()
    threshold_value = quadrant['Value'].median()
    for _, row in quadrant.iterrows():
        if row['Qty'] > threshold_qty and row['Value'] > threshold_value:
            quadrants['HV-HS'].append(row['Part description'])
        elif row['Qty'] > threshold_qty:
            quadrants['HV-LS'].append(row['Part description'])
        elif row['Value'] > threshold_value:
            quadrants['LV-HS'].append(row['Part description'])
        else:
            quadrants['LV-LS'].append(row['Part description'])
    st.write('**High Volume, High Sales:**', ', '.join(quadrants['HV-HS']))
    st.write('**High Volume, Low Sales:**', ', '.join(quadrants['HV-LS']))
    st.write('**Low Volume, High Sales:**', ', '.join(quadrants['LV-HS']))
    st.write('**Low Volume, Low Sales:**', ', '.join(quadrants['LV-LS']))

# Show sidebar data
show_data()
# Main Header
st.title('Manufacturing Data Analytics Dashboard')
# Show sales distribution
st.header('Sales Distribution by Party')
plot_sales_distribution(data)
# Show production volume fluctuations
st.header('Production Volume Fluctuations')
plot_production_fluctuations(data)
# Quadrant Analysis
st.header('Quadrant Analysis')
quadrant_analysis(data)
# Summary
st.header('Key Insights')
st.markdown('**Sales Distribution:** Heavy reliance on a few key customers may pose risks in case of reduced orders. Diversification is advised.')
st.markdown('**Production Fluctuations:** Highlights the need for better scheduling and forecasting.')
st.markdown('**Quadrant Analysis:** Shows production vs. revenue efficiency for different products.')
