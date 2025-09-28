import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import matplotlib.dates as mdates
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

class ProfessionalBIReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.data = None
        self.analysis_results = {}
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles for professional reports"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1f4e79'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#2f5f8f'),
            fontName='Helvetica-Bold'
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#1f4e79'),
            fontName='Helvetica-Bold'
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        )
        
        self.bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            bulletIndent=10,
            fontName='Helvetica'
        )
    
    def load_and_analyze_data(self, csv_file='Main4 - Main3.csv'):
        """Load data and perform comprehensive analysis"""
        try:
            # Load and clean data
            data = pd.read_csv(csv_file)
            
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
            
            self.data = data
            self.perform_comprehensive_analysis()
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def perform_comprehensive_analysis(self):
        """Perform detailed business analysis"""
        if self.data is None:
            return
        
        # Financial Analysis
        self.analysis_results['financial'] = {
            'total_revenue': self.data['Value'].sum(),
            'avg_profit_margin': self.data['Profit_Margin'].mean(),
            'total_orders': len(self.data),
            'avg_order_value': self.data['Value'].mean(),
            'revenue_growth': self.calculate_revenue_growth(),
            'profit_trend': self.calculate_profit_trend()
        }
        
        # Customer Analysis
        customer_analysis = self.data.groupby('Customer').agg({
            'Value': ['count', 'sum', 'mean'],
            'Profit_Margin': 'mean',
            'Overall_Efficiency': 'mean'
        }).round(2)
        
        customer_revenue = self.data.groupby('Customer')['Value'].sum().sort_values(ascending=False)
        top_80_percent = customer_revenue.cumsum() / customer_revenue.sum() <= 0.8
        customers_80_percent = top_80_percent.sum()
        
        self.analysis_results['customer'] = {
            'analysis': customer_analysis,
            'top_customers': customer_revenue.head(10),
            'customer_concentration': customers_80_percent,
            'total_customers': self.data['Customer'].nunique()
        }
        
        # Product Analysis
        product_analysis = self.data.groupby('Part description').agg({
            'Value': ['sum', 'count'],
            'Qty': 'sum',
            'Profit_Margin': 'mean'
        }).round(2)
        
        self.analysis_results['product'] = {
            'analysis': product_analysis,
            'top_products': product_analysis['Value']['sum'].sort_values(ascending=False).head(10),
            'total_products': self.data['Part description'].nunique()
        }
        
        # Operational Efficiency
        self.analysis_results['operational'] = {
            'avg_manpower_efficiency': self.data['Manpower_Efficiency'].mean(),
            'avg_material_efficiency': self.data['Material_Efficiency'].mean(),
            'avg_machine_efficiency': self.data['Machine_Efficiency'].mean(),
            'overall_efficiency': self.data['Overall_Efficiency'].mean(),
            'cost_variance': self.data['Cost_Variance_Pct'].mean()
        }
        
        # Risk Analysis
        self.analysis_results['risk'] = {
            'customer_concentration_risk': 'High' if customers_80_percent <= 3 else 'Medium' if customers_80_percent <= 5 else 'Low',
            'profit_margin_volatility': self.data['Profit_Margin'].std(),
            'efficiency_variance': self.data['Overall_Efficiency'].std()
        }
    
    def calculate_revenue_growth(self):
        """Calculate revenue growth rate"""
        try:
            monthly_revenue = self.data.groupby(self.data['Date'].dt.to_period('M'))['Value'].sum()
            if len(monthly_revenue) >= 2:
                latest = monthly_revenue.iloc[-1]
                previous = monthly_revenue.iloc[-2]
                return ((latest - previous) / previous) * 100
            return 0
        except:
            return 0
    
    def calculate_profit_trend(self):
        """Calculate profit margin trend"""
        try:
            monthly_profit = self.data.groupby(self.data['Date'].dt.to_period('M'))['Profit_Margin'].mean()
            if len(monthly_profit) >= 2:
                return 'Improving' if monthly_profit.iloc[-1] > monthly_profit.iloc[-2] else 'Declining'
            return 'Stable'
        except:
            return 'Stable'
    
    def create_executive_summary(self):
        """Generate executive summary content"""
        financial = self.analysis_results['financial']
        customer = self.analysis_results['customer']
        operational = self.analysis_results['operational']
        risk = self.analysis_results['risk']
        
        summary = []
        summary.append(Paragraph("EXECUTIVE SUMMARY", self.title_style))
        summary.append(Spacer(1, 20))
        
        # Key Performance Indicators
        summary.append(Paragraph("Key Performance Indicators", self.heading_style))
        
        kpi_data = [
            ['Metric', 'Value', 'Status'],
            [f'Total Revenue', f"₹{financial['total_revenue']:,.0f}", 'Strong' if financial['total_revenue'] > 50000000 else 'Moderate'],
            [f'Average Profit Margin', f"{financial['avg_profit_margin']:.1f}%", 'Good' if financial['avg_profit_margin'] > 5 else 'Needs Improvement'],
            [f'Total Orders', f"{financial['total_orders']:,}", 'Active'],
            [f'Operational Efficiency', f"{operational['overall_efficiency']:.1f}%", 'Excellent' if operational['overall_efficiency'] > 100 else 'Good'],
            [f'Customer Base', f"{customer['total_customers']}", 'Diverse' if customer['total_customers'] > 10 else 'Concentrated']
        ]
        
        kpi_table = Table(kpi_data)
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        summary.append(kpi_table)
        summary.append(Spacer(1, 20))
        
        # Critical Findings
        summary.append(Paragraph("Critical Business Findings", self.heading_style))
        
        findings = [
            f"• Revenue Performance: Total revenue of ₹{financial['total_revenue']:,.0f} {'demonstrates strong market position' if financial['total_revenue'] > 50000000 else 'shows growth opportunity'}",
            f"• Customer Concentration: {customer['customer_concentration']} customers generate 80% of revenue - {risk['customer_concentration_risk'].lower()} risk level",
            f"• Operational Excellence: Overall efficiency of {operational['overall_efficiency']:.1f}% {'exceeds industry standards' if operational['overall_efficiency'] > 100 else 'meets operational targets'}",
            f"• Profit Margins: Average margin of {financial['avg_profit_margin']:.1f}% with {financial['profit_trend'].lower()} trend",
            f"• Cost Management: Average cost variance of {operational['cost_variance']:.1f}% indicates {'excellent' if abs(operational['cost_variance']) < 2 else 'good'} cost control"
        ]
        
        for finding in findings:
            summary.append(Paragraph(finding, self.bullet_style))
        
        summary.append(Spacer(1, 20))
        
        # Strategic Recommendations
        summary.append(Paragraph("Strategic Recommendations", self.heading_style))
        
        recommendations = self.generate_strategic_recommendations()
        for i, rec in enumerate(recommendations, 1):
            summary.append(Paragraph(f"{i}. {rec}", self.bullet_style))
        
        return summary
    
    def generate_strategic_recommendations(self):
        """Generate strategic business recommendations"""
        recommendations = []
        
        financial = self.analysis_results['financial']
        customer = self.analysis_results['customer']
        operational = self.analysis_results['operational']
        risk = self.analysis_results['risk']
        
        # Customer diversification
        if risk['customer_concentration_risk'] == 'High':
            recommendations.append("Implement customer diversification strategy to reduce dependency on top customers and mitigate revenue risk")
        
        # Operational efficiency
        if operational['overall_efficiency'] < 95:
            recommendations.append("Launch operational excellence program focusing on manpower, material, and machine efficiency improvements")
        
        # Profit margin optimization
        if financial['avg_profit_margin'] < 10:
            recommendations.append("Conduct comprehensive pricing review and value engineering to improve profit margins")
        
        # Cost control
        if abs(operational['cost_variance']) > 3:
            recommendations.append("Strengthen cost estimation and variance control processes to improve predictability")
        
        # Growth opportunities
        if financial['revenue_growth'] > 0:
            recommendations.append("Leverage positive revenue momentum to expand market share and explore new product lines")
        
        # Digital transformation
        recommendations.append("Invest in digital analytics and automation to enhance decision-making and operational efficiency")
        
        return recommendations[:6]  # Top 6 recommendations
    
    def create_detailed_analysis(self):
        """Generate detailed analysis sections"""
        content = []
        
        # Financial Performance Analysis
        content.append(PageBreak())
        content.append(Paragraph("DETAILED FINANCIAL ANALYSIS", self.title_style))
        content.append(Spacer(1, 20))
        
        financial = self.analysis_results['financial']
        
        content.append(Paragraph("Revenue Performance", self.heading_style))
        content.append(Paragraph(
            f"The organization generated total revenue of ₹{financial['total_revenue']:,.0f} across {financial['total_orders']:,} orders, "
            f"resulting in an average order value of ₹{financial['avg_order_value']:,.0f}. The revenue growth rate of "
            f"{financial['revenue_growth']:+.1f}% indicates {'strong business momentum' if financial['revenue_growth'] > 0 else 'market challenges that require strategic attention'}.",
            self.body_style
        ))
        content.append(Spacer(1, 15))
        
        content.append(Paragraph("Profitability Analysis", self.subheading_style))
        content.append(Paragraph(
            f"Average profit margin stands at {financial['avg_profit_margin']:.2f}% with a {financial['profit_trend'].lower()} trend. "
            f"This margin level {'exceeds industry benchmarks' if financial['avg_profit_margin'] > 15 else 'aligns with industry standards' if financial['avg_profit_margin'] > 8 else 'requires improvement to meet competitive levels'}. "
            "Key focus areas include cost optimization, pricing strategy refinement, and operational efficiency enhancement.",
            self.body_style
        ))
        content.append(Spacer(1, 20))
        
        # Customer Intelligence Analysis
        content.append(Paragraph("CUSTOMER INTELLIGENCE ANALYSIS", self.title_style))
        content.append(Spacer(1, 20))
        
        customer = self.analysis_results['customer']
        
        content.append(Paragraph("Customer Portfolio Overview", self.heading_style))
        content.append(Paragraph(
            f"The customer base comprises {customer['total_customers']} active customers, with the top {customer['customer_concentration']} customers "
            f"accounting for 80% of total revenue. This concentration level presents "
            f"{'high risk requiring immediate diversification' if customer['customer_concentration'] <= 3 else 'moderate risk manageable through strategic planning' if customer['customer_concentration'] <= 5 else 'low risk with well-distributed revenue streams'}.",
            self.body_style
        ))
        content.append(Spacer(1, 15))
        
        # Top customers table
        content.append(Paragraph("Top Customer Revenue Contributors", self.subheading_style))
        customer_data = [['Rank', 'Customer', 'Revenue', 'Share %']]
        total_revenue = customer['top_customers'].sum()
        
        for i, (customer_name, revenue) in enumerate(customer['top_customers'].head(5).items(), 1):
            share = (revenue / total_revenue) * 100
            customer_data.append([str(i), customer_name, f"₹{revenue:,.0f}", f"{share:.1f}%"])
        
        customer_table = Table(customer_data)
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2f5f8f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(customer_table)
        content.append(Spacer(1, 20))
        
        # Operational Excellence Analysis
        content.append(Paragraph("OPERATIONAL EXCELLENCE ANALYSIS", self.title_style))
        content.append(Spacer(1, 20))
        
        operational = self.analysis_results['operational']
        
        content.append(Paragraph("Efficiency Metrics", self.heading_style))
        efficiency_text = (
            f"Operational efficiency analysis reveals overall performance at {operational['overall_efficiency']:.1f}%, "
            f"comprising manpower efficiency of {operational['avg_manpower_efficiency']:.1f}%, "
            f"material efficiency of {operational['avg_material_efficiency']:.1f}%, and "
            f"machine efficiency of {operational['avg_machine_efficiency']:.1f}%. "
        )
        
        if operational['overall_efficiency'] > 100:
            efficiency_text += "The above-target performance indicates excellent operational management and optimization."
        elif operational['overall_efficiency'] > 95:
            efficiency_text += "Performance levels are satisfactory with opportunities for incremental improvements."
        else:
            efficiency_text += "Efficiency levels require focused improvement initiatives across all operational areas."
        
        content.append(Paragraph(efficiency_text, self.body_style))
        content.append(Spacer(1, 15))
        
        content.append(Paragraph("Cost Variance Analysis", self.subheading_style))
        content.append(Paragraph(
            f"Average cost variance of {operational['cost_variance']:.2f}% indicates "
            f"{'excellent cost control and accurate estimation processes' if abs(operational['cost_variance']) < 2 else 'satisfactory cost management with room for improvement' if abs(operational['cost_variance']) < 5 else 'significant cost control challenges requiring systematic review'}. "
            "Variance analysis by category enables targeted improvement initiatives for maximum impact.",
            self.body_style
        ))
        
        return content
    
    def create_risk_assessment(self):
        """Generate risk assessment and mitigation strategies"""
        content = []
        content.append(PageBreak())
        content.append(Paragraph("RISK ASSESSMENT & MITIGATION STRATEGIES", self.title_style))
        content.append(Spacer(1, 20))
        
        risk = self.analysis_results['risk']
        customer = self.analysis_results['customer']
        financial = self.analysis_results['financial']
        operational = self.analysis_results['operational']
        
        # Risk Matrix
        content.append(Paragraph("Business Risk Assessment", self.heading_style))
        
        risk_data = [
            ['Risk Category', 'Level', 'Impact', 'Mitigation Priority'],
            ['Customer Concentration', risk['customer_concentration_risk'], 'High' if customer['customer_concentration'] <= 3 else 'Medium', 'High'],
            ['Profit Margin Volatility', 'Medium' if risk['profit_margin_volatility'] > 5 else 'Low', 'Medium', 'Medium'],
            ['Operational Efficiency', 'Low' if operational['overall_efficiency'] > 95 else 'Medium', 'Medium', 'Medium'],
            ['Cost Control', 'Low' if abs(operational['cost_variance']) < 3 else 'Medium', 'Medium', 'High']
        ]
        
        risk_table = Table(risk_data)
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(risk_table)
        content.append(Spacer(1, 20))
        
        # Mitigation Strategies
        content.append(Paragraph("Risk Mitigation Strategies", self.heading_style))
        
        mitigation_strategies = [
            ("Customer Concentration Risk", [
                "Develop new customer acquisition strategy targeting mid-market segments",
                "Implement customer relationship management program to strengthen loyalty",
                "Diversify product portfolio to attract different customer segments",
                "Establish strategic partnerships for market expansion"
            ]),
            ("Operational Efficiency Risk", [
                "Implement lean manufacturing principles and continuous improvement programs",
                "Invest in automation and technology upgrades to enhance productivity",
                "Establish performance monitoring and feedback systems",
                "Develop cross-functional teams for problem-solving and innovation"
            ]),
            ("Financial Performance Risk", [
                "Strengthen financial planning and forecasting capabilities",
                "Implement dynamic pricing strategies based on market conditions",
                "Enhance cost management through detailed variance analysis",
                "Develop multiple revenue streams to reduce dependency"
            ])
        ]
        
        for category, strategies in mitigation_strategies:
            content.append(Paragraph(category, self.subheading_style))
            for strategy in strategies:
                content.append(Paragraph(f"• {strategy}", self.bullet_style))
            content.append(Spacer(1, 10))
        
        return content
    
    def create_action_plan(self):
        """Generate detailed action plan with timelines"""
        content = []
        content.append(PageBreak())
        content.append(Paragraph("STRATEGIC ACTION PLAN", self.title_style))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Implementation Roadmap", self.heading_style))
        content.append(Paragraph(
            "The following action plan provides a structured approach to implementing the strategic recommendations "
            "with specific timelines, responsible parties, and success metrics.",
            self.body_style
        ))
        content.append(Spacer(1, 15))
        
        # Action plan table
        action_data = [
            ['Priority', 'Action Item', 'Timeline', 'Expected Impact', 'Success Metric'],
            ['High', 'Customer Diversification Program', '6 months', 'Reduce concentration risk', '20% new customer revenue'],
            ['High', 'Operational Excellence Initiative', '9 months', 'Improve efficiency by 5%', '105% overall efficiency'],
            ['Medium', 'Cost Management System', '4 months', 'Reduce variance by 50%', '<2% cost variance'],
            ['Medium', 'Pricing Strategy Review', '3 months', 'Improve margins by 3%', '>12% profit margin'],
            ['Low', 'Digital Analytics Platform', '12 months', 'Enhanced decision making', 'Real-time dashboards']
        ]
        
        action_table = Table(action_data, colWidths=[0.8*inch, 2.2*inch, 1*inch, 1.5*inch, 1.5*inch])
        action_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        content.append(action_table)
        content.append(Spacer(1, 20))
        
        # Implementation guidelines
        content.append(Paragraph("Implementation Guidelines", self.heading_style))
        
        guidelines = [
            "Establish cross-functional project teams for each major initiative",
            "Implement regular progress review meetings with key stakeholders",
            "Develop detailed project plans with milestones and deliverables",
            "Allocate sufficient resources and budget for successful execution",
            "Create change management communication plan for organization-wide buy-in",
            "Establish performance monitoring systems for continuous tracking"
        ]
        
        for guideline in guidelines:
            content.append(Paragraph(f"• {guideline}", self.bullet_style))
        
        content.append(Spacer(1, 15))
        
        # Success factors
        content.append(Paragraph("Critical Success Factors", self.subheading_style))
        success_factors = [
            "Leadership commitment and visible support for initiatives",
            "Clear communication of benefits and expected outcomes",
            "Employee engagement and participation in improvement programs",
            "Regular monitoring and course correction based on feedback",
            "Integration with existing business processes and systems"
        ]
        
        for factor in success_factors:
            content.append(Paragraph(f"• {factor}", self.bullet_style))
        
        return content
    
    def generate_comprehensive_report(self, output_filename=None):
        """Generate the complete business intelligence report"""
        if self.data is None:
            print("No data available. Please load data first.")
            return False
        
        if output_filename is None:
            output_filename = f"Professional_BDM_Business_Intelligence_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(output_filename, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build report content
        story = []
        
        # Cover page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("BUSINESS INTELLIGENCE REPORT", self.title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Manufacturing Analytics & Strategic Insights", 
                              ParagraphStyle('Subtitle', parent=self.styles['Normal'], 
                                           fontSize=18, alignment=TA_CENTER, 
                                           textColor=colors.HexColor('#2f5f8f'))))
        story.append(Spacer(1, 1*inch))
        
        # Report details
        report_info = [
            f"Analysis Period: {self.data['Date'].min().strftime('%B %Y')} - {self.data['Date'].max().strftime('%B %Y')}",
            f"Total Records: {len(self.data):,}",
            f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "Confidential Business Document"
        ]
        
        for info in report_info:
            story.append(Paragraph(info, ParagraphStyle('ReportInfo', parent=self.styles['Normal'], 
                                                       fontSize=12, alignment=TA_CENTER, 
                                                       spaceAfter=12)))
        
        # Add all sections
        story.extend(self.create_executive_summary())
        story.extend(self.create_detailed_analysis())
        story.extend(self.create_risk_assessment())
        story.extend(self.create_action_plan())
        
        # Appendix
        story.append(PageBreak())
        story.append(Paragraph("APPENDIX: DATA SUMMARY", self.title_style))
        story.append(Spacer(1, 20))
        
        # Data summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Analysis Period', f"{self.data['Date'].min().strftime('%Y-%m-%d')} to {self.data['Date'].max().strftime('%Y-%m-%d')}"],
            ['Total Records', f"{len(self.data):,}"],
            ['Unique Customers', f"{self.data['Customer'].nunique()}"],
            ['Unique Products', f"{self.data['Part description'].nunique()}"],
            ['Date Range (Days)', f"{(self.data['Date'].max() - self.data['Date'].min()).days}"],
            ['Total Revenue', f"₹{self.data['Value'].sum():,.0f}"],
            ['Average Order Value', f"₹{self.data['Value'].mean():,.0f}"],
            ['Report Generation Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Professional Business Intelligence Report generated: {output_filename}")
        return output_filename

if __name__ == "__main__":
    # Generate comprehensive business intelligence report
    report_generator = ProfessionalBIReportGenerator()
    
    if report_generator.load_and_analyze_data():
        report_filename = report_generator.generate_comprehensive_report()
        print(f"\\n📊 Comprehensive Business Intelligence Report Complete!")
        print(f"📁 Report saved as: {report_filename}")
    else:
        print("❌ Failed to load data. Please check the CSV file.")