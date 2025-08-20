"""
AWS Billing Dashboard - Main Streamlit Application
A lightweight dashboard for analyzing AWS billing data
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
from src.aws_client import AWSBillingClient
from src.data_processor import BillingDataProcessor
from src.visualizations import BillingVisualizations
from config.settings import DEFAULT_DAYS_BACK, MAX_DAYS_BACK, TOP_SERVICES_COUNT, GRANULARITY_LIMITS

# Page configuration
st.set_page_config(
    page_title="AWS Billing Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


class BillingDashboard:
    """
    Main dashboard application class
    Orchestrates all components following SOLID principles
    """
    
    def __init__(self):
        """Initialize dashboard components"""
        self.aws_client = AWSBillingClient()
        self.data_processor = BillingDataProcessor()
        self.visualizations = BillingVisualizations()
        
    def run(self):
        """Main application entry point"""
        self._render_header()
        self._render_sidebar()
        
        # Check AWS credentials
        if not self._validate_aws_connection():
            return
        
        # Get user inputs
        date_range, aws_granularity, display_granularity = self._get_user_inputs()
        
        # Load and process data
        with st.spinner("Loading billing data..."):
            raw_data = self._load_billing_data(date_range, aws_granularity)
            
        if not raw_data:
            st.error("No billing data found for the selected period.")
            return
        
        # Process data
        df = self.data_processor.process_cost_and_usage_response(raw_data)
        
        if df.empty:
            st.warning("No cost data available for the selected period.")
            return
        
        # Apply weekly aggregation if needed
        if display_granularity == "WEEKLY":
            df = self.data_processor.aggregate_to_weekly(df)
        
        # Render dashboard
        self._render_dashboard(df, display_granularity)
    
    def _render_header(self):
        """Render application header"""
        st.title("💰 AWS Billing Dashboard")
        st.markdown(
            "Analyze your AWS costs with interactive charts and insights. "
            "Perfect for developers and business leaders to track cloud spending."
        )
        st.divider()
    
    def _render_sidebar(self):
        """Render sidebar with controls"""
        st.sidebar.title("Dashboard Controls")
        st.sidebar.markdown("Configure your billing analysis below:")
    
    def _validate_aws_connection(self) -> bool:
        """Validate AWS connection and credentials"""
        with st.spinner("Validating AWS credentials..."):
            if not self.aws_client.validate_credentials():
                st.error(
                    "❌ **AWS Connection Failed**\n\n"
                    "Please ensure your AWS credentials are properly configured:\n"
                    "- Use `aws configure` command\n"
                    "- Or set environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)\n"
                    "- Ensure you have Cost Explorer permissions"
                )
                return False
        
        st.success("✅ AWS connection successful!")
        return True
    
    def _get_user_inputs(self) -> tuple:
        """Get user inputs from sidebar"""
        st.sidebar.subheader("📅 Time Period Filters")
        
        # Quick time period selection (like AWS Console)
        time_period_option = st.sidebar.selectbox(
            "Quick Select",
            options=[
                "Last 7 days",
                "Last 30 days", 
                "Last 3 months",
                "Last 6 months",
                "Last 12 months",
                "Custom Range"
            ],
            index=1,  # Default to "Last 30 days"
            help="Choose a predefined time period or select custom range"
        )
        
        # Calculate date range based on selection
        end_date = datetime.now()
        
        if time_period_option == "Last 7 days":
            start_date = end_date - timedelta(days=7)
        elif time_period_option == "Last 30 days":
            start_date = end_date - timedelta(days=30)
        elif time_period_option == "Last 3 months":
            start_date = end_date - timedelta(days=90)
        elif time_period_option == "Last 6 months":
            start_date = end_date - timedelta(days=180)
        elif time_period_option == "Last 12 months":
            start_date = end_date - timedelta(days=365)
        else:  # Custom Range
            st.sidebar.markdown("**Custom Date Range**")
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=DEFAULT_DAYS_BACK),
                    max_value=datetime.now() - timedelta(days=1)
                )
            
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now(),
                    max_value=datetime.now()
                )
            
            # Convert to datetime for consistency
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.min.time())
        
        # Validate date range
        if start_date >= end_date:
            st.sidebar.error("Start date must be before end date")
            st.stop()
        
        if (end_date - start_date).days > MAX_DAYS_BACK:
            st.sidebar.error(f"Date range cannot exceed {MAX_DAYS_BACK} days")
            st.stop()
        
        # Granularity selection with smart defaults
        st.sidebar.subheader("📊 Analysis Settings")
        
        # Smart granularity suggestions based on time range
        days_diff = (end_date - start_date).days
        
        if days_diff <= 2:
            granularity_options = ["HOURLY", "DAILY"]
            default_granularity = "HOURLY"
            help_text = "Hourly view recommended for short periods"
        elif days_diff <= 31:
            granularity_options = ["HOURLY", "DAILY", "MONTHLY"]
            default_granularity = "DAILY"
            help_text = "Daily view recommended for this period"
        elif days_diff <= 93:
            granularity_options = ["DAILY", "WEEKLY", "MONTHLY"]
            default_granularity = "WEEKLY"
            help_text = "Weekly view recommended for this period"
        else:
            granularity_options = ["WEEKLY", "MONTHLY"]
            default_granularity = "MONTHLY"
            help_text = "Monthly view recommended for longer periods"
        
        # Add weekly option by processing daily data
        display_options = []
        actual_granularity_map = {}
        
        for option in granularity_options:
            if option == "WEEKLY":
                display_options.append("WEEKLY")
                actual_granularity_map["WEEKLY"] = "DAILY"  # We'll aggregate daily data to weekly
            else:
                display_options.append(option)
                actual_granularity_map[option] = option
        
        selected_granularity = st.sidebar.selectbox(
            "Data Granularity",
            options=display_options,
            index=display_options.index(default_granularity) if default_granularity in display_options else 0,
            help=help_text
        )
        
        # Get actual AWS API granularity
        aws_granularity = actual_granularity_map[selected_granularity]
        
        # Validate granularity limits
        max_days_for_granularity = GRANULARITY_LIMITS.get(selected_granularity, 365)
        if days_diff > max_days_for_granularity:
            st.sidebar.error(
                f"⚠️ {selected_granularity} granularity supports maximum {max_days_for_granularity} days. "
                f"Please select a shorter time period or different granularity."
            )
            st.stop()
        
        # Display selected period info
        st.sidebar.info(
            f"📊 **Selected Period:**\n"
            f"From: {start_date.strftime('%Y-%m-%d')}\n"
            f"To: {end_date.strftime('%Y-%m-%d')}\n"
            f"Duration: {days_diff} days\n"
            f"Granularity: {selected_granularity}"
        )
        
        return (start_date, end_date), aws_granularity, selected_granularity
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def _load_billing_data(_self, date_range: tuple, aws_granularity: str) -> dict:
        """Load billing data from AWS (cached)"""
        start_date, end_date = date_range
        
        return _self.aws_client.get_cost_by_service(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            granularity=aws_granularity
        )
    
    def _render_dashboard(self, df: pd.DataFrame, display_granularity: str = "DAILY"):
        """Render main dashboard content"""
        # Generate summary
        summary = self.data_processor.generate_cost_summary(df)
        trends = self.data_processor.calculate_cost_trends(df, display_granularity)
        
        # Display key metrics
        st.subheader("📈 Key Metrics")
        self.visualizations.display_metrics_cards(summary)
        
        # Add period-over-period change if available
        if 'mom_change_percent' in trends:
            # Dynamic label based on granularity
            change_labels = {
                "HOURLY": "Hour-over-Hour Change",
                "DAILY": "Day-over-Day Change",
                "WEEKLY": "Week-over-Week Change", 
                "MONTHLY": "Month-over-Month Change"
            }
            change_label = change_labels.get(display_granularity, "Period-over-Period Change")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label=change_label,
                    value=f"{trends['mom_change_percent']:+.1f}%",
                    delta=f"${trends['mom_change_amount']:+,.2f}"
                )
        
        st.divider()
        
        # Cost trends chart
        granularity_label = {
            "HOURLY": "Hourly",
            "DAILY": "Daily", 
            "WEEKLY": "Weekly",
            "MONTHLY": "Monthly"
        }.get(display_granularity, "Daily")
        
        st.subheader(f"📊 {granularity_label} Cost Trends")
        if 'cost_by_period' in trends and trends['cost_by_period']:
            trend_df = pd.DataFrame(trends['cost_by_period'])
            trend_chart = self.visualizations.create_cost_trend_chart(
                trend_df, 
                title=f"{granularity_label} Cost Trends Over Time",
                granularity=display_granularity
            )
            st.plotly_chart(trend_chart, use_container_width=True)
        
        # Service analysis
        st.subheader("🔍 Service Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top services by cost
            top_services = self.data_processor.get_top_services_by_cost(
                df, top_n=TOP_SERVICES_COUNT
            )
            
            if not top_services.empty:
                pie_chart = self.visualizations.create_service_cost_pie_chart(top_services)
                st.plotly_chart(pie_chart, use_container_width=True)
        
        with col2:
            # Service cost bar chart
            if not top_services.empty:
                bar_chart = self.visualizations.create_service_cost_bar_chart(top_services)
                st.plotly_chart(bar_chart, use_container_width=True)
        
        # Service trends over time
        st.subheader("📈 Service Trends Over Time")
        service_trends = self.data_processor.calculate_service_cost_trends(df)
        
        if not service_trends.empty:
            # Get top 5 services for trend analysis
            top_5_services = top_services.head(5)['Service'].tolist()
            trend_chart = self.visualizations.create_service_trend_chart(
                service_trends, 
                services=top_5_services
            )
            st.plotly_chart(trend_chart, use_container_width=True)
        
        # Data table
        st.subheader("📋 Detailed Data")
        with st.expander("View Raw Data"):
            st.dataframe(df, use_container_width=True)
        
        # Export functionality
        self._render_export_section(df, summary)
    
    def _render_export_section(self, df: pd.DataFrame, summary: dict):
        """Render data export section"""
        st.subheader("💾 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"aws_billing_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Summary export
            summary_text = f"""
AWS Billing Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Cost: ${summary.get('total_cost', 0):,.2f}
Services Used: {summary.get('service_count', 0)}
Time Periods: {summary.get('time_periods', 0)}
Top Service: {summary.get('top_service', 'N/A')}
Top Service Cost: ${summary.get('top_service_cost', 0):,.2f}
            """
            
            st.download_button(
                label="📊 Download Summary",
                data=summary_text,
                file_name=f"aws_billing_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )


def main():
    """Application entry point"""
    try:
        dashboard = BillingDashboard()
        dashboard.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An error occurred: {e}")
        st.info("Please check your AWS credentials and try again.")


if __name__ == "__main__":
    main()