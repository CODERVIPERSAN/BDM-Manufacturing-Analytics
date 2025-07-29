# 🏭 BDM Manufacturing Data Analytics Project

A comprehensive business intelligence solution for manufacturing data analysis with interactive dashboards and strategic insights.

## 📋 Project Overview

This project provides advanced analytics for manufacturing data, featuring interactive visualizations, quadrant analysis, and strategic business insights. The solution helps identify sales patterns, production trends, and optimization opportunities.

## 🚀 Features

### 📊 Interactive Dashboard
- **Real-time Filtering**: Dynamic filters for customers and date ranges
- **Multiple Visualization Types**: Bar charts, line plots, scatter plots, heatmaps, and pie charts
- **Responsive Design**: Professional UI with custom CSS styling
- **Tabbed Interface**: Organized content across different analytical views

### 📈 Analytics Capabilities
1. **Sales Distribution Analysis**
   - Customer-wise sales breakdown
   - Revenue concentration analysis
   - Market share visualization

2. **Production Trend Analysis**
   - Daily production volume tracking
   - Production heatmaps by customer and date
   - Trend identification and forecasting

3. **Quadrant Analysis**
   - Strategic product positioning
   - Volume vs. Sales analysis
   - Product categorization (HV-HS, HV-LS, LV-HS, LV-LS)

4. **Product Performance Metrics**
   - Top-performing products analysis
   - Profitability assessment
   - Performance benchmarking

5. **Business Intelligence**
   - Customer profitability matrix
   - Monthly trend analysis
   - Strategic recommendations

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Visualization**: Plotly, Plotly Express
- **Data Processing**: Pandas, NumPy
- **Styling**: Custom CSS
- **Language**: Python 3.8+

## 📁 Project Structure

```
BDM_project/
├── Main4 - Main3.csv           # Raw manufacturing data
├── advanced_dashboard.py       # Enhanced dashboard application
├── BDM_dashboard.py           # Basic dashboard (legacy)
├── BDM_Analysis_Report.md     # Comprehensive analysis report
└── README.md                  # Project documentation
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone or download the project files**
2. **Install required packages**:
   ```bash
   pip install streamlit pandas plotly numpy scipy matplotlib seaborn
   ```

3. **Navigate to project directory**:
   ```bash
   cd BDM_project
   ```

4. **Run the dashboard**:
   ```bash
   streamlit run advanced_dashboard.py
   ```

5. **Access the dashboard**:
   - Local URL: http://localhost:8501
   - Network URL: http://192.168.0.130:8501

## 📊 Dashboard Features

### 🎯 Key Metrics
- **Total Sales**: Overall revenue across all customers
- **Total Quantity**: Combined production volume
- **Unique Products**: Number of distinct products
- **Average Rate**: Mean pricing across products

### 📈 Visualization Tabs

#### 1. Sales Analysis
- Horizontal bar chart showing sales distribution by customer
- Pie chart displaying market share percentages
- Color-coded visualizations for easy interpretation

#### 2. Production Trends
- Time series line chart for daily production volumes
- Heatmap showing production patterns by customer and date
- Interactive markers for detailed data exploration

#### 3. Quadrant Analysis
- Scatter plot with quadrant divisions
- Product categorization based on volume and sales
- Interactive hover data with product details
- Summary statistics for each quadrant

#### 4. Product Performance
- Top 20 products by sales value
- Performance metrics table
- Color-coded bar charts for easy comparison

#### 5. Detailed Insights
- Strategic recommendations
- Key findings summary
- Customer profitability matrix
- Monthly trend analysis

## 📋 Key Findings

### 🎯 Business Insights

1. **Customer Concentration Risk**
   - Top 4 customers account for ~70% of sales
   - Heavy reliance on key customers poses business risk
   - Diversification strategy recommended

2. **Production Variability**
   - Significant daily production fluctuations
   - Reactive rather than proactive planning
   - Demand forecasting improvements needed

3. **Product Portfolio Analysis**
   - High-value, low-volume products show strong profitability
   - Some high-volume products have low sales efficiency
   - Strategic product mix optimization opportunities

### 💡 Strategic Recommendations

1. **Risk Mitigation**
   - Diversify customer base
   - Secure long-term contracts
   - Explore new markets

2. **Operational Excellence**
   - Implement demand forecasting
   - Optimize production scheduling
   - Improve inventory management

3. **Product Strategy**
   - Focus on high-margin products
   - Improve underperforming lines
   - Consider discontinuing poor performers

## 🔍 Usage Guide

### Dashboard Navigation
1. **Sidebar Filters**: Use to filter data by customer and date range
2. **Metrics Row**: View key performance indicators at the top
3. **Tabs**: Navigate between different analytical views
4. **Interactive Charts**: Hover, zoom, and pan for detailed exploration
5. **Data Statistics**: Enable in sidebar for additional insights

### Best Practices
- Start with the Sales Analysis tab for overview
- Use filters to focus on specific time periods or customers
- Leverage the Quadrant Analysis for strategic planning
- Review Detailed Insights for actionable recommendations

## 📈 Future Enhancements

### Planned Features
- [ ] Machine learning predictive models
- [ ] Real-time data integration
- [ ] Export capabilities (PDF, Excel)
- [ ] Advanced forecasting algorithms
- [ ] Mobile-responsive design
- [ ] User authentication and role-based access
- [ ] Automated report generation
- [ ] Integration with ERP systems

### Advanced Analytics
- [ ] Seasonal decomposition analysis
- [ ] Customer lifetime value analysis
- [ ] Inventory optimization models
- [ ] Price elasticity analysis
- [ ] Market basket analysis

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📧 Support

For questions, issues, or feature requests, please create an issue in the project repository or contact the development team.

---

**📊 BDM Manufacturing Analytics** - Empowering data-driven decisions through advanced business intelligence.

*Last updated: July 2025*
