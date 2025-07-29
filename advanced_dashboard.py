import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="BDM Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
        color: #333333;
    }
    .insight-box h4 {
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .insight-box h5 {
        color: #34495e;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .insight-box strong {
        color: #2c3e50;
    }
    .insight-box ul li {
        color: #495057;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Load and prepare data
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('Main4 - Main3.csv')
        
        # Clean data
        def clean_currency(x):
            return float(str(x).replace(',', ''))
        
        data['Qty'] = data['Qty'].apply(clean_currency)
        data['Value'] = data['Value'].apply(clean_currency)
        data['Rate'] = data['Rate'].apply(clean_currency)
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce', dayfirst=True)
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

data = load_data()

# Header
st.markdown('<h1 class="main-header">🏭 Manufacturing Data Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("🔍 Filters")
customers = st.sidebar.multiselect("Select Customers", data['Customer'].unique(), default=data['Customer'].unique())
date_range = st.sidebar.date_input("Select Date Range", 
                                   value=(data['Date'].min(), data['Date'].max()),
                                   min_value=data['Date'].min(),
                                   max_value=data['Date'].max())

# Filter data
filtered_data = data[
    (data['Customer'].isin(customers)) &
    (data['Date'] >= pd.to_datetime(date_range[0])) &
    (data['Date'] <= pd.to_datetime(date_range[1]))
]

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_data['Value'].sum()
    st.metric("💰 Total Sales", f"₹{total_sales:,.0f}")

with col2:
    total_qty = filtered_data['Qty'].sum()
    st.metric("📦 Total Quantity", f"{total_qty:,.0f}")

with col3:
    unique_products = filtered_data['Part description'].nunique()
    st.metric("🛠️ Unique Products", f"{unique_products}")

with col4:
    avg_rate = filtered_data['Rate'].mean()
    st.metric("💱 Avg Rate", f"₹{avg_rate:,.0f}")

# Main content with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Sales Analysis", "📈 Production Trends", "🎯 Quadrant Analysis", "📋 Product Performance", "🔍 Detailed Insights"])

with tab1:
    st.subheader("Sales Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales by Customer
        sales_by_customer = filtered_data.groupby('Customer')['Value'].sum().reset_index()
        sales_by_customer = sales_by_customer.sort_values('Value', ascending=True)
        
        fig_bar = px.bar(
            sales_by_customer, 
            x='Value', 
            y='Customer', 
            orientation='h',
            title="Sales Distribution by Customer",
            color='Value',
            color_continuous_scale='viridis'
        )
        fig_bar.update_layout(height=500)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Pie chart for sales percentage
        fig_pie = px.pie(
            sales_by_customer, 
            values='Value', 
            names='Customer',
            title="Sales Share by Customer"
        )
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Production Volume Trends")
    
    # Daily production volume
    daily_production = filtered_data.groupby('Date')['Qty'].sum().reset_index()
    
    fig_line = px.line(
        daily_production, 
        x='Date', 
        y='Qty',
        title="Daily Production Volume",
        markers=True
    )
    fig_line.update_traces(line_color='#ff6b6b', marker_color='#ff6b6b')
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Production heatmap by customer and date
    pivot_data = filtered_data.pivot_table(values='Qty', index='Customer', columns=filtered_data['Date'].dt.date, aggfunc='sum', fill_value=0)
    
    fig_heatmap = px.imshow(
        pivot_data.values,
        x=[str(col) for col in pivot_data.columns],
        y=pivot_data.index,
        title="Production Heatmap (Customer vs Date)",
        color_continuous_scale='RdYlBu_r',
        aspect='auto'
    )
    fig_heatmap.update_layout(
        height=400,
        xaxis={'side': 'bottom'},
        coloraxis_colorbar=dict(
            title="Production Quantity",
            tickmode="linear",
            tick0=0,
            dtick=pivot_data.values.max()/5
        )
    )
    fig_heatmap.update_xaxes(tickangle=45)
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.subheader("Quadrant Analysis")
    
    # Calculate medians for quadrant analysis
    qty_median = filtered_data['Qty'].median()
    value_median = filtered_data['Value'].median()
    
    # Create quadrant labels
    def get_quadrant(row):
        if row['Qty'] > qty_median and row['Value'] > value_median:
            return "High Volume, High Sales"
        elif row['Qty'] > qty_median and row['Value'] <= value_median:
            return "High Volume, Low Sales"
        elif row['Qty'] <= qty_median and row['Value'] > value_median:
            return "Low Volume, High Sales"
        else:
            return "Low Volume, Low Sales"
    
    filtered_data['Quadrant'] = filtered_data.apply(get_quadrant, axis=1)
    
    # Scatter plot for quadrant analysis
    fig_scatter = px.scatter(
        filtered_data, 
        x='Qty', 
        y='Value',
        color='Quadrant',
        hover_data=['Part description', 'Customer'],
        title="Product Quadrant Analysis",
        size='Rate',
        size_max=20
    )
    
    # Add median lines
    fig_scatter.add_vline(x=qty_median, line_dash="dash", line_color="red", annotation_text="Qty Median")
    fig_scatter.add_hline(y=value_median, line_dash="dash", line_color="red", annotation_text="Value Median")
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Quadrant summary
    quadrant_summary = filtered_data.groupby('Quadrant').agg({
        'Part description': 'count',
        'Value': 'sum',
        'Qty': 'sum'
    }).reset_index()
    
    st.subheader("Quadrant Summary")
    st.dataframe(quadrant_summary, use_container_width=True)

with tab4:
    st.subheader("Product Performance Analysis")
    
    # Top products by sales
    top_products = filtered_data.groupby('Part description').agg({
        'Value': 'sum',
        'Qty': 'sum',
        'Rate': 'mean'
    }).reset_index().sort_values('Value', ascending=False).head(20)
    
    fig_top_products = px.bar(
        top_products, 
        x='Value', 
        y='Part description',
        orientation='h',
        title="Top 20 Products by Sales Value",
        color='Value',
        color_continuous_scale='plasma'
    )
    fig_top_products.update_layout(height=600)
    st.plotly_chart(fig_top_products, use_container_width=True)
    
    # Product performance metrics
    st.subheader("Product Performance Metrics")
    st.dataframe(top_products, use_container_width=True)

with tab5:
    st.subheader("Detailed Business Insights")
    
    # Results and Findings Section
    st.markdown("""
    <div class="insight-box">
    <h4>📊 Results and Findings</h4>
    
    <h5>Graphs and Pictorial Representation:</h5>
    <strong>Sales Distribution by Party:</strong><br>
    • Observation: 70% of sales come from the top 4 parties.<br>
    • Trend: Heavy reliance on a few key customers.<br><br>
    
    <strong>Production Volume Fluctuations:</strong><br>
    • Observation: Significant fluctuations in daily production volumes.<br>
    • Pattern: Indicates variability in demand and production processes.<br><br>
    
    <strong>Quadrant Analysis:</strong><br>
    • High Volume, High Sales: BOTTOM SUCTION DUCT, ROLLER UNDER DUCT<br>
    • High Volume, Low Sales: SUCTION VALVE, CLOSING COVER COMPL<br>
    • Low Volume, High Sales: BOTTOM CAN PLATE COM, SUCTION DOOR 2 COMPL<br>
    • Low Volume, Low Sales: SIDE SHEET RH COMPLE, FRONT COVER SHEET CO<br><br>
    
    <h5>Explanation of Trends and Patterns:</h5>
    <strong>Sales Distribution:</strong> The company is heavily reliant on a few key customers, which poses a risk if any of these customers reduce their orders. Diversifying party engagement is crucial to mitigate this risk.<br><br>
    
    <strong>Production Fluctuations:</strong> The variability in daily production volumes highlights the need for better demand forecasting and inventory management to align production with market demand.<br><br>
    
    <strong>Quadrant Analysis:</strong> The categorization of products into quadrants reveals that some high-potential products are underutilized due to inadequate production capacity, while low-performing products consume resources inefficiently. Tailored strategies for each quadrant will help optimize sales and production efficiency.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Strategic Recommendations Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
        <h4>🎯 Key Strategic Actions</h4>
        <ul>
        <li><strong>Customer Risk Mitigation:</strong> Diversify customer base to reduce dependency on top 4 customers</li>
        <li><strong>Production Planning:</strong> Implement advanced forecasting to stabilize production volumes</li>
        <li><strong>Resource Optimization:</strong> Focus on high-volume, high-sales products while improving efficiency</li>
        <li><strong>Market Expansion:</strong> Explore new markets for underutilized high-potential products</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
        <h4>💡 Operational Improvements</h4>
        <ul>
        <li><strong>Demand Forecasting:</strong> Better prediction models for production alignment</li>
        <li><strong>Inventory Management:</strong> Optimize stock levels based on demand patterns</li>
        <li><strong>Product Portfolio:</strong> Rationalize low-performing products in LL quadrant</li>
        <li><strong>Capacity Planning:</strong> Increase production capacity for high-potential products</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Advanced analytics
    st.subheader("Advanced Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer profitability analysis
        customer_metrics = filtered_data.groupby('Customer').agg({
            'Value': ['sum', 'mean'],
            'Qty': ['sum', 'mean'],
            'Rate': 'mean'
        }).round(2)
        customer_metrics.columns = ['Total Sales', 'Avg Sales', 'Total Qty', 'Avg Qty', 'Avg Rate']
        
        st.subheader("Customer Profitability Matrix")
        st.dataframe(customer_metrics, use_container_width=True)
    
    with col2:
        # Monthly trends
        if len(filtered_data) > 0:
            monthly_data = filtered_data.groupby(filtered_data['Date'].dt.to_period('M')).agg({
                'Value': 'sum',
                'Qty': 'sum'
            }).reset_index()
            monthly_data['Date'] = monthly_data['Date'].astype(str)
            
            fig_monthly = px.line(
                monthly_data, 
                x='Date', 
                y=['Value', 'Qty'],
                title="Monthly Sales & Quantity Trends"
            )
            st.plotly_chart(fig_monthly, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("📈 **BDM Analytics Dashboard** - Powered by Streamlit & Plotly")

# Sidebar additional info
if st.sidebar.checkbox("Show Data Statistics"):
    st.sidebar.subheader("Data Statistics")
    st.sidebar.write(f"Total Records: {len(filtered_data)}")
    st.sidebar.write(f"Date Range: {filtered_data['Date'].min().strftime('%Y-%m-%d')} to {filtered_data['Date'].max().strftime('%Y-%m-%d')}")
    st.sidebar.write(f"Customers: {filtered_data['Customer'].nunique()}")
    st.sidebar.write(f"Products: {filtered_data['Part description'].nunique()}")
