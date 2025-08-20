"""
AWS Client for Cost Explorer API
Handles AWS authentication and data retrieval
"""
import boto3
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from botocore.exceptions import ClientError, NoCredentialsError
import logging

from config.settings import AWS_COST_EXPLORER_REGION

logger = logging.getLogger(__name__)


class AWSBillingClient:
    """
    AWS Cost Explorer client following Single Responsibility Principle
    """
    
    def __init__(self, region: str = AWS_COST_EXPLORER_REGION):
        """Initialize AWS Cost Explorer client"""
        self.region = region
        self._client = None
        
    @property
    def client(self):
        """Lazy initialization of boto3 client"""
        if self._client is None:
            try:
                self._client = boto3.client('ce', region_name=self.region)
            except NoCredentialsError:
                st.error("AWS credentials not found. Please configure your AWS credentials.")
                st.stop()
        return self._client
    
    def validate_credentials(self) -> bool:
        """
        Validate AWS credentials by making a simple API call
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Make a simple call to validate credentials
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            self.client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"AWS credential validation failed: {e}")
            return False
    
    def get_cost_and_usage(
        self,
        start_date: str,
        end_date: str,
        granularity: str = 'MONTHLY',
        metrics: List[str] = None,
        group_by: List[Dict] = None
    ) -> Dict:
        """
        Get cost and usage data from AWS Cost Explorer
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            granularity: DAILY, MONTHLY, or HOURLY
            metrics: List of metrics to retrieve
            group_by: List of grouping dimensions
            
        Returns:
            Dict: Cost and usage data from AWS
        """
        if metrics is None:
            metrics = ['BlendedCost']
            
        try:
            params = {
                'TimePeriod': {
                    'Start': start_date,
                    'End': end_date
                },
                'Granularity': granularity,
                'Metrics': metrics
            }
            
            if group_by:
                params['GroupBy'] = group_by
                
            response = self.client.get_cost_and_usage(**params)
            return response
            
        except ClientError as e:
            error_msg = f"Failed to retrieve cost data: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return {}
    
    def get_services_list(self, start_date: str, end_date: str) -> List[str]:
        """
        Get list of AWS services used in the specified time period
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List[str]: List of AWS service names
        """
        try:
            response = self.client.get_dimension_values(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Dimension='SERVICE'
            )
            
            services = [item['Value'] for item in response.get('DimensionValues', [])]
            return sorted(services)
            
        except ClientError as e:
            logger.error(f"Failed to retrieve services list: {e}")
            return []
    
    def get_cost_by_service(
        self,
        start_date: str,
        end_date: str,
        granularity: str = 'MONTHLY'
    ) -> Dict:
        """
        Get cost breakdown by AWS service
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            granularity: DAILY, MONTHLY, or HOURLY
            
        Returns:
            Dict: Cost data grouped by service
        """
        group_by = [{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            metrics=['BlendedCost'],
            group_by=group_by
        )