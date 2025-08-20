"""
Data processing module for AWS billing data
Handles data transformation and analysis following SOLID principles
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BillingDataProcessor:
    """
    Processes AWS billing data for dashboard visualization
    Follows Single Responsibility Principle
    """
    
    def __init__(self):
        """Initialize the data processor"""
        pass
    
    def process_cost_and_usage_response(self, response: Dict) -> pd.DataFrame:
        """
        Convert AWS Cost Explorer response to pandas DataFrame
        
        Args:
            response: AWS Cost Explorer API response
            
        Returns:
            pd.DataFrame: Processed billing data
        """
        if not response or 'ResultsByTime' not in response:
            return pd.DataFrame()
        
        data_rows = []
        
        for result in response['ResultsByTime']:
            time_period = result['TimePeriod']
            start_date = time_period['Start']
            end_date = time_period['End']
            
            if 'Groups' in result:
                # Data grouped by dimension (e.g., service)
                for group in result['Groups']:
                    keys = group['Keys']
                    metrics = group['Metrics']
                    
                    for metric_name, metric_data in metrics.items():
                        data_rows.append({
                            'StartDate': start_date,
                            'EndDate': end_date,
                            'Service': keys[0] if keys else 'Total',
                            'MetricName': metric_name,
                            'Amount': float(metric_data['Amount']),
                            'Unit': metric_data['Unit']
                        })
            else:
                # Total data without grouping
                metrics = result['Total']
                for metric_name, metric_data in metrics.items():
                    data_rows.append({
                        'StartDate': start_date,
                        'EndDate': end_date,
                        'Service': 'Total',
                        'MetricName': metric_name,
                        'Amount': float(metric_data['Amount']),
                        'Unit': metric_data['Unit']
                    })
        
        df = pd.DataFrame(data_rows)
        if not df.empty:
            df['StartDate'] = pd.to_datetime(df['StartDate'])
            df['EndDate'] = pd.to_datetime(df['EndDate'])
        
        return df
    
    def calculate_cost_trends(self, df: pd.DataFrame, granularity: str = "DAILY") -> Dict:
        """
        Calculate cost trends and insights
        
        Args:
            df: Processed billing DataFrame
            
        Returns:
            Dict: Cost trend analysis
        """
        if df.empty:
            return {}
        
        # Filter for BlendedCost metric
        cost_df = df[df['MetricName'] == 'BlendedCost'].copy()
        
        if cost_df.empty:
            return {}
        
        # Calculate total cost by time period
        total_by_period = cost_df.groupby('StartDate')['Amount'].sum().reset_index()
        total_by_period = total_by_period.sort_values('StartDate')
        
        # Calculate average based on granularity
        if granularity == "HOURLY":
            average_label = "average_hourly_cost"
        elif granularity == "WEEKLY":
            average_label = "average_weekly_cost"
        elif granularity == "MONTHLY":
            average_label = "average_monthly_cost"
        else:  # DAILY
            average_label = "average_daily_cost"
        
        trends = {
            'total_cost': total_by_period['Amount'].sum(),
            average_label: total_by_period['Amount'].mean(),
            'periods': len(total_by_period),
            'cost_by_period': total_by_period.to_dict('records'),
            'granularity': granularity
        }
        
        # Calculate period-over-period change if we have multiple periods
        if len(total_by_period) >= 2:
            current_cost = total_by_period.iloc[-1]['Amount']
            previous_cost = total_by_period.iloc[-2]['Amount']
            
            if previous_cost > 0:
                period_change = ((current_cost - previous_cost) / previous_cost) * 100
                
                # Label the change based on granularity
                if granularity == "HOURLY":
                    change_label = "hour_over_hour"
                elif granularity == "WEEKLY":
                    change_label = "week_over_week"
                elif granularity == "MONTHLY":
                    change_label = "month_over_month"
                else:  # DAILY
                    change_label = "day_over_day"
                
                trends[f'{change_label}_change_percent'] = period_change
                trends[f'{change_label}_change_amount'] = current_cost - previous_cost
                
                # Keep the old key for backward compatibility
                trends['mom_change_percent'] = period_change
                trends['mom_change_amount'] = current_cost - previous_cost
        
        return trends
    
    def get_top_services_by_cost(
        self,
        df: pd.DataFrame,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Get top N services by total cost
        
        Args:
            df: Processed billing DataFrame
            top_n: Number of top services to return
            
        Returns:
            pd.DataFrame: Top services by cost
        """
        if df.empty:
            return pd.DataFrame()
        
        # Filter for BlendedCost and exclude 'Total'
        cost_df = df[
            (df['MetricName'] == 'BlendedCost') & 
            (df['Service'] != 'Total')
        ].copy()
        
        if cost_df.empty:
            return pd.DataFrame()
        
        # Group by service and sum costs
        service_costs = cost_df.groupby('Service')['Amount'].sum().reset_index()
        service_costs = service_costs.sort_values('Amount', ascending=False)
        
        return service_costs.head(top_n)
    
    def calculate_service_cost_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate cost trends for each service over time
        
        Args:
            df: Processed billing DataFrame
            
        Returns:
            pd.DataFrame: Service cost trends over time
        """
        if df.empty:
            return pd.DataFrame()
        
        # Filter for BlendedCost and exclude 'Total'
        cost_df = df[
            (df['MetricName'] == 'BlendedCost') & 
            (df['Service'] != 'Total')
        ].copy()
        
        if cost_df.empty:
            return pd.DataFrame()
        
        # Pivot to get services as columns and dates as rows
        pivot_df = cost_df.pivot_table(
            index='StartDate',
            columns='Service',
            values='Amount',
            fill_value=0
        ).reset_index()
        
        return pivot_df
    
    def generate_cost_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive cost summary
        
        Args:
            df: Processed billing DataFrame
            
        Returns:
            Dict: Cost summary statistics
        """
        if df.empty:
            return {
                'total_cost': 0,
                'service_count': 0,
                'time_periods': 0,
                'top_service': 'N/A',
                'top_service_cost': 0
            }
        
        cost_df = df[df['MetricName'] == 'BlendedCost'].copy()
        
        summary = {
            'total_cost': cost_df['Amount'].sum(),
            'service_count': len(cost_df[cost_df['Service'] != 'Total']['Service'].unique()),
            'time_periods': len(cost_df['StartDate'].unique()),
        }
        
        # Find top service
        service_costs = cost_df[cost_df['Service'] != 'Total'].groupby('Service')['Amount'].sum()
        if not service_costs.empty:
            top_service = service_costs.idxmax()
            summary['top_service'] = top_service
            summary['top_service_cost'] = service_costs.max()
        else:
            summary['top_service'] = 'N/A'
            summary['top_service_cost'] = 0
        
        return summary
    
    def aggregate_to_weekly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate daily data to weekly periods
        
        Args:
            df: DataFrame with daily billing data
            
        Returns:
            pd.DataFrame: Weekly aggregated data
        """
        if df.empty:
            return df
        
        # Create a copy to avoid modifying original data
        weekly_df = df.copy()
        
        # Add week start date (Monday of each week)
        weekly_df['WeekStart'] = weekly_df['StartDate'].dt.to_period('W-MON').dt.start_time
        
        # Group by week and service, sum the amounts
        aggregated = weekly_df.groupby(['WeekStart', 'Service', 'MetricName', 'Unit']).agg({
            'Amount': 'sum'
        }).reset_index()
        
        # Rename WeekStart back to StartDate for consistency
        aggregated['StartDate'] = aggregated['WeekStart']
        aggregated['EndDate'] = aggregated['WeekStart'] + timedelta(days=6)
        
        # Drop the temporary WeekStart column
        aggregated = aggregated.drop('WeekStart', axis=1)
        
        # Reorder columns to match original structure
        column_order = ['StartDate', 'EndDate', 'Service', 'MetricName', 'Amount', 'Unit']
        aggregated = aggregated[column_order]
        
        return aggregated