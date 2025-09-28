import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Configure page
st.set_page_config(
    page_title="Professional BDM Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(90deg, #1f4e79 0%, #2f5f8f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .insight-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 6px solid #007bff;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        color: #333333;
        box-shadow: 0 4px 16px rgba(0, 123, 255, 0.15);
    }
    
    .insight-card h4 {
        color: #1f4e79;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .recommendation-item {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 5px solid #155724;
    }
    
    .warning-item {
        background: linear-gradient(90deg, #dc3545 0%, #fd7e14 100%);
        color: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 5px solid #721c24;
    }
    
    .success-item {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 5px solid #155724;
    }
    
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #007bff;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1f4e79 0%, #2f5f8f 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding-left: 24px;
        padding-right: 24px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .plotly-graph-div {
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_clean_data():
    """Load and clean the manufacturing data"""
    try:
        data = pd.read_csv('Main4 - Main3.csv')
        
        def clean_currency(x):
            try:
                if str(x).strip() in ['-', '', 'nan', 'NaN']:
                    return 0.0
                return float(str(x).replace(',', ''))
            except (ValueError, AttributeError):
                return 0.0
        
        # Clean numeric columns
        numeric_columns = ['Qty', 'Rate', 'Value', 'Fwt',
                         'Target  Manpower', 'variation Manpower', 'Actual Manpower',
                         'Target RawMaterial(Cost)', 'variation RawMaterial', 'Actual RawMaterial',
                         'Target Machinepower(Cost)', 'variation Machine power', 'Actual Machine power',
                         'Target Overhead(Cost)or Profit', 'variation overhead ', 'Actual Overhead or profit']
        
        for col in numeric_columns:
            if col in data.columns:
                data[col] = data[col].apply(clean_currency)
        
        # Convert date
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce', dayfirst=True)
        
        # Calculate business metrics
        data['Total_Target_Cost'] = (data['Target  Manpower'] + 
                                   data['Target RawMaterial(Cost)'] + 
                                   data['Target Machinepower(Cost)'] + 
                                   data['Target Overhead(Cost)or Profit'])
        
        data['Total_Actual_Cost'] = (data['Actual Manpower'] + 
                                   data['Actual RawMaterial'] + 
                                   data['Actual Machine power'] + 
                                   data['Actual Overhead or profit'])
        
        data['Cost_Variance'] = data['Total_Actual_Cost'] - data['Total_Target_Cost']
        data['Cost_Variance_Pct'] = (data['Cost_Variance'] / data['Total_Target_Cost'].replace(0, 1)) * 100
        data['Profit_Margin'] = ((data['Value'] - data['Total_Actual_Cost']) / data['Value'].replace(0, 1)) * 100
        data['Unit_Profit'] = (data['Value'] - data['Total_Actual_Cost']) / data['Qty'].replace(0, 1)
        data['ROI'] = (data['Value'] - data['Total_Target_Cost']) / data['Total_Target_Cost'].replace(0, 1) * 100
        
        # Efficiency metrics
        data['Manpower_Efficiency'] = (data['Target  Manpower'] / data['Actual Manpower'].replace(0, 1)) * 100
        data['Material_Efficiency'] = (data['Target RawMaterial(Cost)'] / data['Actual RawMaterial'].replace(0, 1)) * 100
        data['Machine_Efficiency'] = (data['Target Machinepower(Cost)'] / data['Actual Machine power'].replace(0, 1)) * 100
        data['Overall_Efficiency'] = (data['Manpower_Efficiency'] + data['Material_Efficiency'] + data['Machine_Efficiency']) / 3
        
        return data
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def create_download_link(df, filename, file_label):
    """Create a download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{file_label}</a>'
    return href

def generate_executive_insights(data):
    """Generate executive-level insights"""
    total_revenue = data['Value'].sum()
    avg_profit_margin = data['Profit_Margin'].mean()
    customer_revenue = data.groupby('Customer')['Value'].sum().sort_values(ascending=False)
    
    # Customer concentration analysis
    top_80_percent = customer_revenue.cumsum() / customer_revenue.sum() <= 0.8
    customers_80_percent = top_80_percent.sum()
    
    insights = []
    
    # Revenue insights
    if total_revenue > 50000000:  # 5 Crores
        insights.append(("success", "💰 Strong Revenue Performance", f"Total revenue of ₹{total_revenue:,.0f} indicates robust business performance."))
    elif total_revenue > 20000000:  # 2 Crores
        insights.append(("warning", "💰 Moderate Revenue Performance", f"Revenue of ₹{total_revenue:,.0f} shows room for growth."))
    else:
        insights.append(("error", "💰 Revenue Improvement Needed", f"Current revenue of ₹{total_revenue:,.0f} requires strategic focus."))
    
    # Customer concentration
    if customers_80_percent <= 3:
        insights.append(("error", "⚠️ High Customer Concentration Risk", f"Only {customers_80_percent} customers generate 80% of revenue. Diversification critical."))
    elif customers_80_percent <= 5:
        insights.append(("warning", "⚠️ Moderate Customer Risk", f"{customers_80_percent} customers generate 80% of revenue. Consider diversification."))
    else:
        insights.append(("success", "✅ Well-Diversified Customer Base", f"{customers_80_percent} customers for 80% revenue shows good distribution."))
    
    # Profit margin analysis
    if avg_profit_margin > 10:
        insights.append(("success", "📈 Excellent Profit Margins", f"Average margin of {avg_profit_margin:.1f}% is highly competitive."))
    elif avg_profit_margin > 5:
        insights.append(("warning", "📈 Moderate Profit Margins", f"Average margin of {avg_profit_margin:.1f}% has improvement potential."))
    else:
        insights.append(("error", "📉 Low Profit Margins", f"Average margin of {avg_profit_margin:.1f}% requires immediate attention."))
    
    # Operational efficiency
    avg_efficiency = data['Overall_Efficiency'].mean()
    if avg_efficiency > 100:
        insights.append(("success", "⚙️ High Operational Efficiency", f"Overall efficiency of {avg_efficiency:.1f}% exceeds targets."))
    elif avg_efficiency > 95:
        insights.append(("warning", "⚙️ Good Efficiency", f"Overall efficiency of {avg_efficiency:.1f}% is acceptable."))
    else:
        insights.append(("error", "⚙️ Efficiency Improvement Needed", f"Overall efficiency of {avg_efficiency:.1f}% below optimal levels."))
    
    return insights

# Load data
data = load_and_clean_data()

if data.empty:
    st.error("Failed to load data. Please check the CSV file.")
    st.stop()

# Header
st.markdown('<h1 class="main-header">🏭 Professional Manufacturing Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🔍 Analytics Controls")
st.sidebar.markdown("---")

# Filters
customers = st.sidebar.multiselect(
    "Select Customers", 
    data['Customer'].unique(), 
    default=data['Customer'].unique(),
    help="Filter data by customer companies"
)

date_range = st.sidebar.date_input(
    "Select Date Range", 
    value=(data['Date'].min(), data['Date'].max()),
    min_value=data['Date'].min(),
    max_value=data['Date'].max(),
    help="Choose the analysis period"
)

# Advanced filters
st.sidebar.markdown("### Advanced Filters")
min_order_value = st.sidebar.slider(
    "Minimum Order Value (₹)", 
    min_value=0, 
    max_value=int(data['Value'].max()), 
    value=0,
    help="Filter orders by minimum value"
)

profit_margin_filter = st.sidebar.slider(
    "Profit Margin Range (%)", 
    min_value=float(data['Profit_Margin'].min()), 
    max_value=float(data['Profit_Margin'].max()), 
    value=(float(data['Profit_Margin'].min()), float(data['Profit_Margin'].max())),
    help="Filter by profit margin range"
)

# Filter data
filtered_data = data[
    (data['Customer'].isin(customers)) &
    (data['Date'] >= pd.to_datetime(date_range[0])) &
    (data['Date'] <= pd.to_datetime(date_range[1])) &
    (data['Value'] >= min_order_value) &
    (data['Profit_Margin'] >= profit_margin_filter[0]) &
    (data['Profit_Margin'] <= profit_margin_filter[1])
]

# Executive Dashboard
st.markdown("## 📊 Executive Dashboard")

# Key metrics row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_revenue = filtered_data['Value'].sum()
    st.markdown(f"""
    <div class="metric-container">
        <h3>💰 Total Revenue</h3>
        <h2>₹{total_revenue:,.0f}</h2>
        <p>YTD Performance</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_margin = filtered_data['Profit_Margin'].mean()
    st.markdown(f"""
    <div class="metric-container">
        <h3>📈 Avg Profit Margin</h3>
        <h2>{avg_margin:.1f}%</h2>
        <p>Current Period</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_orders = len(filtered_data)
    st.markdown(f"""
    <div class="metric-container">
        <h3>📦 Total Orders</h3>
        <h2>{total_orders:,}</h2>
        <p>Active Orders</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    efficiency = filtered_data['Overall_Efficiency'].mean()
    st.markdown(f"""
    <div class="metric-container">
        <h3>⚙️ Efficiency</h3>
        <h2>{efficiency:.1f}%</h2>
        <p>Operational</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    customers_count = filtered_data['Customer'].nunique()
    st.markdown(f"""
    <div class="metric-container">
        <h3>🏢 Active Customers</h3>
        <h2>{customers_count}</h2>
        <p>Current Period</p>
    </div>
    """, unsafe_allow_html=True)

# Executive Insights
st.markdown("## 🎯 Executive Insights")
insights = generate_executive_insights(filtered_data)

insight_cols = st.columns(2)
for i, (level, title, description) in enumerate(insights):
    with insight_cols[i % 2]:
        if level == "success":
            st.markdown(f"""
            <div class="success-item">
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
        elif level == "warning":
            st.markdown(f"""
            <div class="warning-item">
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="warning-item">
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)

# Main content with tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Revenue Analysis", 
    "👥 Customer Intelligence", 
    "📦 Product Performance", 
    "⚙️ Operational Excellence", 
    "🔮 Predictive Analytics",
    "📋 Data Export"
])

with tab1:
    st.subheader("Revenue Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly revenue trend
        monthly_revenue = filtered_data.groupby(filtered_data['Date'].dt.to_period('M'))['Value'].sum()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=[str(x) for x in monthly_revenue.index], 
            y=monthly_revenue.values,
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig_trend.update_layout(
            title="Monthly Revenue Trend",
            xaxis_title="Month",
            yaxis_title="Revenue (₹)",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Customer revenue distribution
        customer_revenue = filtered_data.groupby('Customer')['Value'].sum().sort_values(ascending=False).head(10)
        
        fig_customer = px.bar(
            x=customer_revenue.values, 
            y=customer_revenue.index,
            orientation='h',
            title="Top 10 Customers by Revenue",
            labels={'x': 'Revenue (₹)', 'y': 'Customer'},
            color=customer_revenue.values,
            color_continuous_scale='viridis'
        )
        fig_customer.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_customer, use_container_width=True)
    
    # Revenue breakdown analysis
    st.subheader("Revenue Composition Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quarterly performance
        quarterly_data = filtered_data.groupby(filtered_data['Date'].dt.quarter).agg({
            'Value': 'sum',
            'Profit_Margin': 'mean'
        }).reset_index()
        
        fig_quarterly = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_quarterly.add_trace(
            go.Bar(x=[f"Q{q}" for q in quarterly_data['Date']], y=quarterly_data['Value'], name="Revenue"),
            secondary_y=False,
        )
        
        fig_quarterly.add_trace(
            go.Scatter(x=[f"Q{q}" for q in quarterly_data['Date']], y=quarterly_data['Profit_Margin'], 
                      mode='lines+markers', name="Profit Margin %"),
            secondary_y=True,
        )
        
        fig_quarterly.update_xaxes(title_text="Quarter")
        fig_quarterly.update_yaxes(title_text="Revenue (₹)", secondary_y=False)
        fig_quarterly.update_yaxes(title_text="Profit Margin (%)", secondary_y=True)
        fig_quarterly.update_layout(title="Quarterly Performance", height=400)
        
        st.plotly_chart(fig_quarterly, use_container_width=True)
    
    with col2:
        # Revenue by product category (top products)
        product_revenue = filtered_data.groupby('Part description')['Value'].sum().sort_values(ascending=False).head(8)
        
        fig_products = px.pie(
            values=product_revenue.values, 
            names=[name[:25] + "..." if len(name) > 25 else name for name in product_revenue.index],
            title="Revenue Distribution by Top Products"
        )
        fig_products.update_layout(height=400)
        st.plotly_chart(fig_products, use_container_width=True)

with tab2:
    st.subheader("Customer Intelligence Dashboard")
    
    # Customer performance matrix
    customer_analysis = filtered_data.groupby('Customer').agg({
        'Value': ['count', 'sum', 'mean'],
        'Qty': 'sum',
        'Profit_Margin': 'mean',
        'Overall_Efficiency': 'mean'
    }).round(2)
    
    customer_analysis.columns = ['Order_Count', 'Total_Revenue', 'Avg_Order_Value', 'Total_Qty', 'Avg_Profit_Margin', 'Avg_Efficiency']
    customer_analysis = customer_analysis.reset_index()
    
    # Customer segmentation
    revenue_median = customer_analysis['Total_Revenue'].median()
    frequency_median = customer_analysis['Order_Count'].median()
    
    def segment_customer(row):
        if row['Total_Revenue'] > revenue_median and row['Order_Count'] > frequency_median:
            return "💎 Champions"
        elif row['Total_Revenue'] > revenue_median:
            return "🏆 High Value"
        elif row['Order_Count'] > frequency_median:
            return "🔄 Frequent"
        else:
            return "🔍 Potential"
    
    customer_analysis['Segment'] = customer_analysis.apply(segment_customer, axis=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer scatter plot
        fig_scatter = px.scatter(
            customer_analysis, 
            x='Order_Count', 
            y='Total_Revenue',
            color='Segment',
            size='Avg_Order_Value',
            hover_data=['Customer'],
            title="Customer Segmentation Matrix"
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Customer segment distribution
        segment_counts = customer_analysis['Segment'].value_counts()
        
        fig_segments = px.pie(
            values=segment_counts.values, 
            names=segment_counts.index,
            title="Customer Segment Distribution"
        )
        fig_segments.update_layout(height=400)
        st.plotly_chart(fig_segments, use_container_width=True)
    
    # Customer details table
    st.subheader("Customer Performance Details")
    
    # Add styling to dataframe
    styled_customer_df = customer_analysis.style.format({
        'Total_Revenue': '₹{:,.0f}',
        'Avg_Order_Value': '₹{:,.0f}',
        'Total_Qty': '{:,.0f}',
        'Avg_Profit_Margin': '{:.2f}%',
        'Avg_Efficiency': '{:.1f}%'
    }).background_gradient(subset=['Total_Revenue'], cmap='Blues')
    
    st.dataframe(styled_customer_df, use_container_width=True, height=400)

with tab3:
    st.subheader("Product Performance Analytics")
    
    # Product analysis
    product_analysis = filtered_data.groupby('Part description').agg({
        'Value': ['sum', 'count'],
        'Qty': 'sum',
        'Profit_Margin': 'mean',
        'Rate': 'mean'
    }).round(2)
    
    product_analysis.columns = ['Total_Revenue', 'Order_Count', 'Total_Qty', 'Avg_Profit_Margin', 'Avg_Rate']
    product_analysis = product_analysis.reset_index()
    product_analysis = product_analysis.sort_values('Total_Revenue', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top products by revenue
        top_products = product_analysis.head(10)
        
        fig_top_products = px.bar(
            top_products, 
            x='Total_Revenue', 
            y='Part description',
            orientation='h',
            title="Top 10 Products by Revenue",
            color='Avg_Profit_Margin',
            color_continuous_scale='RdYlBu_r'
        )
        fig_top_products.update_layout(height=500)
        st.plotly_chart(fig_top_products, use_container_width=True)
    
    with col2:
        # Product performance matrix
        fig_matrix = px.scatter(
            product_analysis.head(20), 
            x='Total_Qty', 
            y='Total_Revenue',
            color='Avg_Profit_Margin',
            size='Order_Count',
            hover_data=['Part description'],
            title="Product Performance Matrix",
            color_continuous_scale='viridis'
        )
        fig_matrix.update_layout(height=500)
        st.plotly_chart(fig_matrix, use_container_width=True)
    
    # Product performance table
    st.subheader("Product Performance Details")
    
    # Format product names for better display
    display_products = product_analysis.head(20).copy()
    display_products['Product'] = display_products['Part description'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
    
    styled_product_df = display_products[['Product', 'Total_Revenue', 'Order_Count', 'Total_Qty', 'Avg_Profit_Margin', 'Avg_Rate']].style.format({
        'Total_Revenue': '₹{:,.0f}',
        'Total_Qty': '{:,.0f}',
        'Avg_Profit_Margin': '{:.2f}%',
        'Avg_Rate': '₹{:,.0f}'
    }).background_gradient(subset=['Total_Revenue'], cmap='Greens')
    
    st.dataframe(styled_product_df, use_container_width=True, height=400)

with tab4:
    st.subheader("Operational Excellence Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Efficiency metrics
        efficiency_metrics = {
            'Manpower': filtered_data['Manpower_Efficiency'].mean(),
            'Material': filtered_data['Material_Efficiency'].mean(),
            'Machine': filtered_data['Machine_Efficiency'].mean(),
            'Overall': filtered_data['Overall_Efficiency'].mean()
        }
        
        fig_efficiency = go.Figure(data=[
            go.Bar(
                x=list(efficiency_metrics.keys()), 
                y=list(efficiency_metrics.values()),
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            )
        ])
        
        fig_efficiency.update_layout(
            title="Operational Efficiency Metrics",
            yaxis_title="Efficiency (%)",
            height=400
        )
        fig_efficiency.add_hline(y=100, line_dash="dash", line_color="red", 
                                annotation_text="Target (100%)")
        
        st.plotly_chart(fig_efficiency, use_container_width=True)
    
    with col2:
        # Cost variance analysis
        variance_data = {
            'Manpower': filtered_data['variation Manpower'].mean(),
            'Material': filtered_data['variation RawMaterial'].mean(),
            'Machine': filtered_data['variation Machine power'].mean(),
            'Overhead': filtered_data['variation overhead '].mean()
        }
        
        colors = ['green' if v <= 0 else 'red' for v in variance_data.values()]
        
        fig_variance = go.Figure(data=[
            go.Bar(
                x=list(variance_data.keys()), 
                y=list(variance_data.values()),
                marker_color=colors
            )
        ])
        
        fig_variance.update_layout(
            title="Cost Variance by Category",
            yaxis_title="Variance (%)",
            height=400
        )
        fig_variance.add_hline(y=0, line_dash="dash", line_color="black")
        
        st.plotly_chart(fig_variance, use_container_width=True)
    
    # Efficiency trends
    st.subheader("Efficiency Trend Analysis")
    
    monthly_efficiency = filtered_data.groupby(filtered_data['Date'].dt.to_period('M')).agg({
        'Overall_Efficiency': 'mean',
        'Cost_Variance_Pct': 'mean'
    }).reset_index()
    
    fig_trends = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_trends.add_trace(
        go.Scatter(x=[str(x) for x in monthly_efficiency['Date']], 
                  y=monthly_efficiency['Overall_Efficiency'], 
                  name="Efficiency %", mode='lines+markers'),
        secondary_y=False,
    )
    
    fig_trends.add_trace(
        go.Scatter(x=[str(x) for x in monthly_efficiency['Date']], 
                  y=monthly_efficiency['Cost_Variance_Pct'], 
                  name="Cost Variance %", mode='lines+markers'),
        secondary_y=True,
    )
    
    fig_trends.update_xaxes(title_text="Month")
    fig_trends.update_yaxes(title_text="Efficiency (%)", secondary_y=False)
    fig_trends.update_yaxes(title_text="Cost Variance (%)", secondary_y=True)
    fig_trends.update_layout(title="Monthly Efficiency and Cost Variance Trends", height=400)
    
    st.plotly_chart(fig_trends, use_container_width=True)

with tab5:
    st.subheader("Predictive Analytics & Forecasting")
    
    st.info("🔮 **Predictive Models**: Revenue forecasting and trend analysis based on historical patterns")
    
    # Simple trend analysis and forecasting
    monthly_data = filtered_data.groupby(filtered_data['Date'].dt.to_period('M')).agg({
        'Value': 'sum',
        'Profit_Margin': 'mean'
    }).reset_index()
    
    if len(monthly_data) > 3:
        # Simple linear trend for next 3 months
        from datetime import datetime, timedelta
        import numpy as np
        
        # Calculate trend
        revenue_trend = np.polyfit(range(len(monthly_data)), monthly_data['Value'], 1)
        
        # Forecast next 3 months
        last_date = pd.to_datetime(monthly_data['Date'].iloc[-1].to_timestamp())
        forecast_months = []
        forecast_revenue = []
        
        for i in range(1, 4):
            next_month = last_date + pd.DateOffset(months=i)
            forecast_months.append(next_month.strftime('%Y-%m'))
            forecast_value = revenue_trend[0] * (len(monthly_data) + i - 1) + revenue_trend[1]
            forecast_revenue.append(max(0, forecast_value))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue forecast
            fig_forecast = go.Figure()
            
            # Historical data
            fig_forecast.add_trace(go.Scatter(
                x=[str(x) for x in monthly_data['Date']], 
                y=monthly_data['Value'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='blue')
            ))
            
            # Forecast
            fig_forecast.add_trace(go.Scatter(
                x=forecast_months, 
                y=forecast_revenue,
                mode='lines+markers',
                name='Forecast',
                line=dict(color='red', dash='dash')
            ))
            
            fig_forecast.update_layout(
                title="Revenue Forecast (Next 3 Months)",
                xaxis_title="Month",
                yaxis_title="Revenue (₹)",
                height=400
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
        
        with col2:
            # Forecast summary
            st.markdown("### 📊 Forecast Summary")
            
            total_forecast = sum(forecast_revenue)
            avg_historical = monthly_data['Value'].mean()
            
            st.metric("Projected 3-Month Revenue", f"₹{total_forecast:,.0f}")
            st.metric("Average Monthly (Historical)", f"₹{avg_historical:,.0f}")
            
            growth_rate = ((forecast_revenue[0] / monthly_data['Value'].iloc[-1]) - 1) * 100
            st.metric("Projected Growth Rate", f"{growth_rate:+.1f}%")
            
            # Risk factors
            st.markdown("#### ⚠️ Risk Factors")
            st.write("• Customer concentration risk")
            st.write("• Market demand fluctuations")
            st.write("• Operational efficiency variations")
            st.write("• Cost variance impact")
    
    else:
        st.warning("Insufficient data for reliable forecasting. Need at least 4 months of data.")

with tab6:
    st.subheader("Data Export & Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Analytics Reports")
        
        # Summary statistics
        summary_stats = {
            'Metric': ['Total Revenue', 'Average Order Value', 'Total Orders', 
                      'Average Profit Margin', 'Operational Efficiency', 'Active Customers'],
            'Value': [
                f"₹{filtered_data['Value'].sum():,.0f}",
                f"₹{filtered_data['Value'].mean():,.0f}",
                f"{len(filtered_data):,}",
                f"{filtered_data['Profit_Margin'].mean():.2f}%",
                f"{filtered_data['Overall_Efficiency'].mean():.1f}%",
                f"{filtered_data['Customer'].nunique()}"
            ]
        }
        
        summary_df = pd.DataFrame(summary_stats)
        st.dataframe(summary_df, use_container_width=True)
        
        # Download links
        st.markdown("### 💾 Download Reports")
        
        if st.button("Generate Customer Analysis Report"):
            customer_report = filtered_data.groupby('Customer').agg({
                'Value': ['count', 'sum', 'mean'],
                'Qty': 'sum',
                'Profit_Margin': 'mean'
            }).round(2)
            
            st.download_button(
                label="📊 Download Customer Report",
                data=customer_report.to_csv(),
                file_name=f"customer_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        st.markdown("### 📈 Export Options")
        
        export_options = st.multiselect(
            "Select data to export:",
            ["Filtered Data", "Customer Analysis", "Product Analysis", "Monthly Summary"],
            default=["Filtered Data"]
        )
        
        if st.button("Generate Export Package"):
            if "Filtered Data" in export_options:
                st.download_button(
                    label="📊 Download Filtered Data",
                    data=filtered_data.to_csv(index=False),
                    file_name=f"bdm_filtered_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            if "Customer Analysis" in export_options:
                customer_export = customer_analysis
                st.download_button(
                    label="👥 Download Customer Analysis",
                    data=customer_export.to_csv(index=False),
                    file_name=f"customer_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        st.markdown("### 📋 Report Features")
        st.info("""
        **Available Reports:**
        - Executive Summary Dashboard
        - Customer Segmentation Analysis  
        - Product Performance Report
        - Operational Efficiency Metrics
        - Predictive Analytics & Forecasting
        - Cost Variance Analysis
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <h4>📊 Professional BDM Analytics Dashboard</h4>
    <p>Powered by Advanced Data Analytics & Machine Learning | Created with Streamlit & Plotly</p>
    <p>Last Updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
</div>
""", unsafe_allow_html=True)

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard Info")
st.sidebar.info(f"""
**Data Summary:**
- Records: {len(filtered_data):,}
- Date Range: {filtered_data['Date'].min().strftime('%Y-%m-%d')} to {filtered_data['Date'].max().strftime('%Y-%m-%d')}
- Customers: {filtered_data['Customer'].nunique()}
- Products: {filtered_data['Part description'].nunique()}
""")

if st.sidebar.button("🔄 Refresh Dashboard"):
    st.rerun()