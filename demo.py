#!/usr/bin/env python3
"""
Demo script for AWS Billing Dashboard
Shows sample data and functionality without requiring AWS credentials
"""
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# Import our modules
from src.data_processor import BillingDataProcessor
from src.visualizations import BillingVisualizations

def create_sample_data():
    """Create sample AWS billing data for demonstration"""
    
    # Sample AWS Cost Explorer response
    sample_response = {
        'ResultsByTime': [
            {
                'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-31'},
                'Groups': [
                    {
                        'Keys': ['Amazon EC2-Instance'],
                        'Metrics': {'BlendedCost': {'Amount': '245.50', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon S3'],
                        'Metrics': {'BlendedCost': {'Amount': '89.25', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon RDS'],
                        'Metrics': {'BlendedCost': {'Amount': '156.75', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['AWS Lambda'],
                        'Metrics': {'BlendedCost': {'Amount': '12.30', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon CloudFront'],
                        'Metrics': {'BlendedCost': {'Amount': '34.80', 'Unit': 'USD'}}
                    }
                ]
            },
            {
                'TimePeriod': {'Start': '2024-02-01', 'End': '2024-02-29'},
                'Groups': [
                    {
                        'Keys': ['Amazon EC2-Instance'],
                        'Metrics': {'BlendedCost': {'Amount': '289.75', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon S3'],
                        'Metrics': {'BlendedCost': {'Amount': '95.40', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon RDS'],
                        'Metrics': {'BlendedCost': {'Amount': '167.20', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['AWS Lambda'],
                        'Metrics': {'BlendedCost': {'Amount': '18.45', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon CloudFront'],
                        'Metrics': {'BlendedCost': {'Amount': '41.25', 'Unit': 'USD'}}
                    }
                ]
            },
            {
                'TimePeriod': {'Start': '2024-03-01', 'End': '2024-03-31'},
                'Groups': [
                    {
                        'Keys': ['Amazon EC2-Instance'],
                        'Metrics': {'BlendedCost': {'Amount': '312.90', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon S3'],
                        'Metrics': {'BlendedCost': {'Amount': '102.15', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon RDS'],
                        'Metrics': {'BlendedCost': {'Amount': '178.60', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['AWS Lambda'],
                        'Metrics': {'BlendedCost': {'Amount': '25.80', 'Unit': 'USD'}}
                    },
                    {
                        'Keys': ['Amazon CloudFront'],
                        'Metrics': {'BlendedCost': {'Amount': '48.70', 'Unit': 'USD'}}
                    }
                ]
            }
        ]
    }
    
    return sample_response

def run_demo():
    """Run the demo dashboard"""
    
    st.set_page_config(
        page_title="AWS Billing Dashboard - Demo",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 AWS Billing Dashboard - Demo Mode")
    st.markdown(
        "This demo shows the dashboard functionality with sample data. "
        "No AWS credentials required!"
    )
    
    st.info(
        "🔍 **Demo Features:**\n"
        "- Interactive cost trend charts\n"
        "- Service cost breakdown\n"
        "- Month-over-month analysis\n"
        "- Top services identification"
    )
    
    st.divider()
    
    # Initialize components
    processor = BillingDataProcessor()
    visualizations = BillingVisualizations()
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Process data
    df = processor.process_cost_and_usage_response(sample_data)
    
    # Generate insights
    summary = processor.generate_cost_summary(df)
    trends = processor.calculate_cost_trends(df)
    
    # Display metrics
    st.subheader("📈 Key Metrics")
    visualizations.display_metrics_cards(summary)
    
    # Month-over-month change
    if 'mom_change_percent' in trends:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Month-over-Month Change",
                value=f"{trends['mom_change_percent']:+.1f}%",
                delta=f"${trends['mom_change_amount']:+,.2f}"
            )
    
    st.divider()
    
    # Cost trends
    st.subheader("📊 Cost Trends")
    if 'cost_by_period' in trends:
        trend_df = pd.DataFrame(trends['cost_by_period'])
        trend_chart = visualizations.create_cost_trend_chart(trend_df)
        st.plotly_chart(trend_chart, use_container_width=True)
    
    # Service analysis
    st.subheader("🔍 Service Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        top_services = processor.get_top_services_by_cost(df, top_n=10)
        pie_chart = visualizations.create_service_cost_pie_chart(top_services)
        st.plotly_chart(pie_chart, use_container_width=True)
    
    with col2:
        # Bar chart
        bar_chart = visualizations.create_service_cost_bar_chart(top_services)
        st.plotly_chart(bar_chart, use_container_width=True)
    
    # Service trends
    st.subheader("📈 Service Trends Over Time")
    service_trends = processor.calculate_service_cost_trends(df)
    top_5_services = top_services.head(5)['Service'].tolist()
    trend_chart = visualizations.create_service_trend_chart(
        service_trends, 
        services=top_5_services
    )
    st.plotly_chart(trend_chart, use_container_width=True)
    
    # Sample data table
    st.subheader("📋 Sample Data")
    with st.expander("View Processed Data"):
        st.dataframe(df, use_container_width=True)
    
    # Instructions for real usage
    st.divider()
    st.subheader("🚀 Ready to Use with Real Data?")
    
    st.markdown("""
    **To use with your AWS account:**
    
    1. **Configure AWS credentials:**
       ```bash
       aws configure
       ```
    
    2. **Run the main application:**
       ```bash
       streamlit run app.py
       ```
    
    3. **Required AWS permissions:**
       - `ce:GetCostAndUsage`
       - `ce:GetUsageReport`
       - `ce:GetDimensionValues`
    """)
    
    st.success("Demo completed! The dashboard is ready for production use.")

if __name__ == "__main__":
    run_demo()