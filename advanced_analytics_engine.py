import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AdvancedBDMAnalytics:
    def __init__(self):
        self.data = None
        self.models = {}
        self.insights = {}
        
    def load_and_prepare_data(self, csv_file='Main4 - Main3.csv'):
        """Load and prepare data for advanced analysis"""
        try:
            # Read the CSV file
            data = pd.read_csv(csv_file)
            
            # Clean numeric columns
            def clean_currency(x):
                try:
                    if str(x).strip() in ['-', '', 'nan', 'NaN']:
                        return 0.0
                    return float(str(x).replace(',', ''))
                except (ValueError, AttributeError):
                    return 0.0
            
            # Apply cleaning to numeric columns
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
            
            # Calculate comprehensive business metrics
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
            
            # Time-based features
            data['Month'] = data['Date'].dt.month
            data['Day_of_Week'] = data['Date'].dt.dayofweek
            data['Quarter'] = data['Date'].dt.quarter
            
            # Efficiency metrics
            data['Manpower_Efficiency'] = (data['Target  Manpower'] / data['Actual Manpower'].replace(0, 1)) * 100
            data['Material_Efficiency'] = (data['Target RawMaterial(Cost)'] / data['Actual RawMaterial'].replace(0, 1)) * 100
            data['Machine_Efficiency'] = (data['Target Machinepower(Cost)'] / data['Actual Machine power'].replace(0, 1)) * 100
            data['Overall_Efficiency'] = (data['Manpower_Efficiency'] + data['Material_Efficiency'] + data['Machine_Efficiency']) / 3
            
            # Revenue per unit metrics
            data['Revenue_Per_Unit'] = data['Value'] / data['Qty'].replace(0, 1)
            data['Cost_Per_Unit'] = data['Total_Actual_Cost'] / data['Qty'].replace(0, 1)
            
            self.data = data
            print(f"Data loaded successfully: {len(data)} records with {data.shape[1]} features")
            return data
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def perform_statistical_analysis(self):
        """Perform comprehensive statistical analysis"""
        if self.data is None or self.data.empty:
            return
            
        print("\\n" + "="*50)
        print("STATISTICAL ANALYSIS REPORT")
        print("="*50)
        
        # Descriptive Statistics
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns
        desc_stats = self.data[numerical_cols].describe()
        
        # Correlation Analysis
        correlation_matrix = self.data[numerical_cols].corr()
        
        # Key correlations with Value (revenue)
        value_correlations = correlation_matrix['Value'].sort_values(ascending=False)
        
        print("\\nTOP FACTORS INFLUENCING REVENUE:")
        print("-" * 35)
        for factor, corr in value_correlations.head(10).items():
            if factor != 'Value':
                print(f"{factor:<30}: {corr:.3f}")
        
        # Variance Analysis by Category
        print("\\nCOST VARIANCE ANALYSIS:")
        print("-" * 25)
        variance_categories = ['variation Manpower', 'variation RawMaterial', 
                             'variation Machine power', 'variation overhead ']
        for cat in variance_categories:
            if cat in self.data.columns:
                mean_var = self.data[cat].mean()
                std_var = self.data[cat].std()
                print(f"{cat:<25}: Mean={mean_var:6.2f}%, Std={std_var:6.2f}%")
        
        # Customer Performance Statistics
        customer_stats = self.data.groupby('Customer').agg({
            'Value': ['count', 'sum', 'mean'],
            'Profit_Margin': 'mean',
            'Overall_Efficiency': 'mean'
        }).round(2)
        
        print("\\nCUSTOMER PERFORMANCE SUMMARY:")
        print("-" * 32)
        for customer in customer_stats.index:
            orders = customer_stats.loc[customer, ('Value', 'count')]
            revenue = customer_stats.loc[customer, ('Value', 'sum')]
            avg_margin = customer_stats.loc[customer, ('Profit_Margin', 'mean')]
            print(f"{customer:<15}: Orders={orders:3.0f}, Revenue=₹{revenue:10,.0f}, Margin={avg_margin:5.1f}%")
        
        # Statistical Tests
        print("\\nSTATISTICAL SIGNIFICANCE TESTS:")
        print("-" * 35)
        
        # Test for significant differences in profit margins between customers
        customers = self.data['Customer'].unique()
        if len(customers) > 1:
            customer_margins = [self.data[self.data['Customer'] == cust]['Profit_Margin'].values 
                              for cust in customers]
            f_stat, p_value = stats.f_oneway(*customer_margins)
            print(f"Profit Margin variation between customers: F={f_stat:.3f}, p={p_value:.3f}")
            if p_value < 0.05:
                print("✓ Significant differences in profit margins between customers")
            else:
                print("✗ No significant differences in profit margins between customers")
        
        # Store insights
        self.insights['statistical'] = {
            'top_revenue_factors': value_correlations.head(5).to_dict(),
            'variance_analysis': {cat: {'mean': self.data[cat].mean(), 'std': self.data[cat].std()} 
                                for cat in variance_categories if cat in self.data.columns},
            'customer_performance': customer_stats.to_dict()
        }
    
    def build_predictive_models(self):
        """Build machine learning models for prediction and forecasting"""
        if self.data is None or self.data.empty:
            return
            
        print("\\n" + "="*50)
        print("PREDICTIVE MODELING ANALYSIS")
        print("="*50)
        
        # Prepare features for modeling
        feature_columns = ['Qty', 'Rate', 'Total_Target_Cost', 'Month', 'Quarter', 'Day_of_Week']
        
        # Encode categorical variables
        le = LabelEncoder()
        data_model = self.data.copy()
        data_model['Customer_Encoded'] = le.fit_transform(data_model['Customer'])
        data_model['Product_Encoded'] = le.fit_transform(data_model['Part description'])
        
        feature_columns.extend(['Customer_Encoded', 'Product_Encoded'])
        
        # Remove rows with missing values in key columns
        model_data = data_model.dropna(subset=feature_columns + ['Value', 'Profit_Margin'])
        
        if len(model_data) < 50:
            print("Insufficient data for reliable modeling")
            return
        
        # 1. Revenue Prediction Model
        print("\\n1. REVENUE PREDICTION MODEL")
        print("-" * 30)
        
        X = model_data[feature_columns]
        y_revenue = model_data['Value']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_revenue, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Random Forest Model
        rf_revenue = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_revenue.fit(X_train_scaled, y_train)
        
        y_pred = rf_revenue.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"Revenue Prediction Accuracy (R²): {r2:.3f}")
        print(f"Mean Absolute Error: ₹{mae:,.0f}")
        print(f"Root Mean Square Error: ₹{np.sqrt(mse):,.0f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'Feature': feature_columns,
            'Importance': rf_revenue.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print("\\nTop Revenue Prediction Features:")
        for _, row in feature_importance.head(5).iterrows():
            print(f"{row['Feature']:<20}: {row['Importance']:.3f}")
        
        self.models['revenue'] = {'model': rf_revenue, 'scaler': scaler, 'accuracy': r2}
        
        # 2. Profit Margin Prediction Model
        print("\\n2. PROFIT MARGIN PREDICTION MODEL")
        print("-" * 35)
        
        y_margin = model_data['Profit_Margin']
        X_train, X_test, y_train_margin, y_test_margin = train_test_split(X, y_margin, test_size=0.2, random_state=42)
        
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        gb_margin = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gb_margin.fit(X_train_scaled, y_train_margin)
        
        y_pred_margin = gb_margin.predict(X_test_scaled)
        r2_margin = r2_score(y_test_margin, y_pred_margin)
        mae_margin = mean_absolute_error(y_test_margin, y_pred_margin)
        
        print(f"Profit Margin Prediction Accuracy (R²): {r2_margin:.3f}")
        print(f"Mean Absolute Error: {mae_margin:.2f}%")
        
        self.models['profit_margin'] = {'model': gb_margin, 'scaler': scaler, 'accuracy': r2_margin}
        
        # 3. Cost Efficiency Clustering
        print("\\n3. OPERATIONAL EFFICIENCY CLUSTERING")
        print("-" * 40)
        
        efficiency_features = ['Manpower_Efficiency', 'Material_Efficiency', 'Machine_Efficiency', 'Overall_Efficiency']
        efficiency_data = model_data[efficiency_features].dropna()
        
        if len(efficiency_data) > 10:
            kmeans = KMeans(n_clusters=3, random_state=42)
            clusters = kmeans.fit_predict(efficiency_data)
            
            model_data.loc[efficiency_data.index, 'Efficiency_Cluster'] = clusters
            
            # Analyze clusters
            cluster_analysis = model_data.groupby('Efficiency_Cluster')[efficiency_features + ['Value', 'Profit_Margin']].mean()
            
            print("Efficiency Cluster Analysis:")
            for cluster in cluster_analysis.index:
                overall_eff = cluster_analysis.loc[cluster, 'Overall_Efficiency']
                avg_margin = cluster_analysis.loc[cluster, 'Profit_Margin']
                print(f"Cluster {cluster}: Efficiency={overall_eff:.1f}%, Profit Margin={avg_margin:.1f}%")
            
            self.models['efficiency_clustering'] = kmeans
    
    def generate_business_insights(self):
        """Generate comprehensive business insights and recommendations"""
        if self.data is None or self.data.empty:
            return
            
        print("\\n" + "="*50)
        print("BUSINESS INTELLIGENCE INSIGHTS")
        print("="*50)
        
        # 1. Revenue Analysis
        total_revenue = self.data['Value'].sum()
        avg_profit_margin = self.data['Profit_Margin'].mean()
        total_orders = len(self.data)
        
        print("\\n1. KEY BUSINESS METRICS")
        print("-" * 25)
        print(f"Total Revenue: ₹{total_revenue:,.0f}")
        print(f"Average Profit Margin: {avg_profit_margin:.1f}%")
        print(f"Total Orders: {total_orders:,}")
        print(f"Average Order Value: ₹{total_revenue/total_orders:,.0f}")
        
        # 2. Customer Analysis
        print("\\n2. CUSTOMER INSIGHTS")
        print("-" * 20)
        
        customer_revenue = self.data.groupby('Customer')['Value'].sum().sort_values(ascending=False)
        top_customers = customer_revenue.head(3)
        
        print("Top 3 Customers by Revenue:")
        for i, (customer, revenue) in enumerate(top_customers.items(), 1):
            percentage = (revenue / total_revenue) * 100
            print(f"{i}. {customer}: ₹{revenue:,.0f} ({percentage:.1f}%)")
        
        # Customer concentration risk
        top_80_percent = customer_revenue.cumsum() / customer_revenue.sum() <= 0.8
        customers_80_percent = top_80_percent.sum()
        print(f"\\nCustomer Concentration: {customers_80_percent} customers generate 80% of revenue")
        if customers_80_percent <= 3:
            print("⚠️  HIGH RISK: Heavy dependence on few customers")
        elif customers_80_percent <= 5:
            print("⚠️  MEDIUM RISK: Moderate customer concentration")
        else:
            print("✓ LOW RISK: Well-diversified customer base")
        
        # 3. Product Performance
        print("\\n3. PRODUCT PERFORMANCE")
        print("-" * 22)
        
        product_performance = self.data.groupby('Part description').agg({
            'Value': 'sum',
            'Qty': 'sum',
            'Profit_Margin': 'mean'
        }).sort_values('Value', ascending=False)
        
        print("Top 5 Products by Revenue:")
        for i, (product, row) in enumerate(product_performance.head(5).iterrows(), 1):
            print(f"{i}. {product[:40]}: ₹{row['Value']:,.0f} (Margin: {row['Profit_Margin']:.1f}%)")
        
        # 4. Operational Efficiency
        print("\\n4. OPERATIONAL EFFICIENCY")
        print("-" * 26)
        
        avg_manpower_eff = self.data['Manpower_Efficiency'].mean()
        avg_material_eff = self.data['Material_Efficiency'].mean()
        avg_machine_eff = self.data['Machine_Efficiency'].mean()
        avg_overall_eff = self.data['Overall_Efficiency'].mean()
        
        print(f"Average Manpower Efficiency: {avg_manpower_eff:.1f}%")
        print(f"Average Material Efficiency: {avg_material_eff:.1f}%")
        print(f"Average Machine Efficiency: {avg_machine_eff:.1f}%")
        print(f"Overall Operational Efficiency: {avg_overall_eff:.1f}%")
        
        # Efficiency recommendations
        if avg_overall_eff < 95:
            print("\\n⚠️  EFFICIENCY IMPROVEMENT NEEDED:")
            if avg_manpower_eff < avg_overall_eff:
                print("   - Focus on manpower optimization")
            if avg_material_eff < avg_overall_eff:
                print("   - Improve material utilization")
            if avg_machine_eff < avg_overall_eff:
                print("   - Enhance machine productivity")
        
        # 5. Cost Variance Analysis
        print("\\n5. COST VARIANCE ANALYSIS")
        print("-" * 26)
        
        avg_cost_variance = self.data['Cost_Variance_Pct'].mean()
        print(f"Average Cost Variance: {avg_cost_variance:.1f}%")
        
        if avg_cost_variance > 5:
            print("⚠️  HIGH COST VARIANCE: Review cost estimation process")
        elif avg_cost_variance > 2:
            print("⚠️  MODERATE COST VARIANCE: Monitor cost control")
        else:
            print("✓ GOOD COST CONTROL: Variance within acceptable limits")
        
        # 6. Strategic Recommendations
        print("\\n6. STRATEGIC RECOMMENDATIONS")
        print("-" * 30)
        
        recommendations = []
        
        # Customer diversification
        if customers_80_percent <= 3:
            recommendations.append("🎯 Diversify customer base to reduce concentration risk")
        
        # Profit margin improvement
        low_margin_products = product_performance[product_performance['Profit_Margin'] < avg_profit_margin]
        if len(low_margin_products) > 0:
            recommendations.append(f"📈 Review pricing for {len(low_margin_products)} low-margin products")
        
        # Operational efficiency
        if avg_overall_eff < 95:
            recommendations.append("⚙️  Implement operational efficiency improvement program")
        
        # Cost control
        if avg_cost_variance > 3:
            recommendations.append("💰 Strengthen cost estimation and control processes")
        
        # Growth opportunities
        high_margin_products = product_performance[product_performance['Profit_Margin'] > avg_profit_margin + 5]
        if len(high_margin_products) > 0:
            recommendations.append(f"🚀 Scale up production for {len(high_margin_products)} high-margin products")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # Store comprehensive insights
        self.insights['business'] = {
            'total_revenue': total_revenue,
            'avg_profit_margin': avg_profit_margin,
            'customer_concentration_risk': customers_80_percent,
            'operational_efficiency': avg_overall_eff,
            'cost_variance': avg_cost_variance,
            'recommendations': recommendations
        }
    
    def create_visualizations(self):
        """Create comprehensive data visualizations"""
        if self.data is None or self.data.empty:
            return
            
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('BDM Manufacturing Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Revenue by Customer
        customer_revenue = self.data.groupby('Customer')['Value'].sum().sort_values(ascending=True)
        customer_revenue.tail(10).plot(kind='barh', ax=axes[0,0], color='steelblue')
        axes[0,0].set_title('Top 10 Customers by Revenue')
        axes[0,0].set_xlabel('Revenue (₹)')
        
        # 2. Profit Margin Distribution
        axes[0,1].hist(self.data['Profit_Margin'], bins=30, alpha=0.7, color='green')
        axes[0,1].set_title('Profit Margin Distribution')
        axes[0,1].set_xlabel('Profit Margin (%)')
        axes[0,1].set_ylabel('Frequency')
        
        # 3. Cost Variance by Category
        variance_data = {
            'Manpower': self.data['variation Manpower'].mean(),
            'Material': self.data['variation RawMaterial'].mean(),
            'Machine': self.data['variation Machine power'].mean(),
            'Overhead': self.data['variation overhead '].mean()
        }
        categories = list(variance_data.keys())
        values = list(variance_data.values())
        colors = ['red' if v > 0 else 'green' for v in values]
        axes[0,2].bar(categories, values, color=colors, alpha=0.7)
        axes[0,2].set_title('Average Cost Variance by Category')
        axes[0,2].set_ylabel('Variance (%)')
        axes[0,2].tick_params(axis='x', rotation=45)
        
        # 4. Monthly Revenue Trend
        monthly_revenue = self.data.groupby(self.data['Date'].dt.to_period('M'))['Value'].sum()
        monthly_revenue.plot(ax=axes[1,0], marker='o', linewidth=2, color='blue')
        axes[1,0].set_title('Monthly Revenue Trend')
        axes[1,0].set_ylabel('Revenue (₹)')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # 5. Efficiency Scatter Plot
        axes[1,1].scatter(self.data['Overall_Efficiency'], self.data['Profit_Margin'], 
                         alpha=0.6, c='orange', s=60)
        axes[1,1].set_title('Efficiency vs Profit Margin')
        axes[1,1].set_xlabel('Overall Efficiency (%)')
        axes[1,1].set_ylabel('Profit Margin (%)')
        
        # 6. Top Products by Volume
        product_qty = self.data.groupby('Part description')['Qty'].sum().sort_values(ascending=True)
        product_qty.tail(8).plot(kind='barh', ax=axes[1,2], color='purple', alpha=0.7)
        axes[1,2].set_title('Top 8 Products by Volume')
        axes[1,2].set_xlabel('Quantity')
        
        plt.tight_layout()
        plt.savefig('BDM_Analytics_Visualizations.png', dpi=300, bbox_inches='tight')
        print("\\n📊 Visualizations saved as 'BDM_Analytics_Visualizations.png'")
        
        # Create correlation heatmap
        plt.figure(figsize=(12, 8))
        numerical_cols = ['Value', 'Qty', 'Rate', 'Profit_Margin', 'Overall_Efficiency', 
                         'Cost_Variance_Pct', 'ROI']
        correlation_matrix = self.data[numerical_cols].corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='RdYlBu_r', center=0, 
                   fmt='.2f', square=True)
        plt.title('Business Metrics Correlation Matrix')
        plt.tight_layout()
        plt.savefig('BDM_Correlation_Heatmap.png', dpi=300, bbox_inches='tight')
        print("📊 Correlation heatmap saved as 'BDM_Correlation_Heatmap.png'")
        
    def generate_comprehensive_report(self):
        """Generate a comprehensive analytics report"""
        if self.data is None or self.data.empty:
            print("No data available for analysis")
            return
        
        print("\\n" + "="*60)
        print("COMPREHENSIVE BDM ANALYTICS REPORT")
        print("="*60)
        print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data Period: {self.data['Date'].min().strftime('%Y-%m-%d')} to {self.data['Date'].max().strftime('%Y-%m-%d')}")
        print(f"Total Records Analyzed: {len(self.data):,}")
        
        # Run all analysis components
        self.perform_statistical_analysis()
        self.build_predictive_models()
        self.generate_business_insights()
        self.create_visualizations()
        
        print("\\n" + "="*60)
        print("EXECUTIVE SUMMARY")
        print("="*60)
        
        if 'business' in self.insights:
            business = self.insights['business']
            print(f"• Total Revenue: ₹{business['total_revenue']:,.0f}")
            print(f"• Average Profit Margin: {business['avg_profit_margin']:.1f}%")
            print(f"• Operational Efficiency: {business['operational_efficiency']:.1f}%")
            print(f"• Customer Concentration: {business['customer_concentration_risk']} customers for 80% revenue")
            print(f"• Cost Variance: {business['cost_variance']:.1f}%")
            
            print("\\nKEY RECOMMENDATIONS:")
            for i, rec in enumerate(business['recommendations'], 1):
                print(f"{i}. {rec}")
        
        print("\\n" + "="*60)
        print("REPORT COMPLETE")
        print("="*60)
        print("📁 Files Generated:")
        print("   - Professional_BDM_Analytics_Dashboard_[timestamp].xlsx")
        print("   - BDM_Analytics_Visualizations.png")
        print("   - BDM_Correlation_Heatmap.png")
        print("\\n✅ Advanced BDM Analytics Complete!")

if __name__ == "__main__":
    # Create and run the advanced analytics engine
    analytics = AdvancedBDMAnalytics()
    analytics.load_and_prepare_data()
    analytics.generate_comprehensive_report()