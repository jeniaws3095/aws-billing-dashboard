"""
Tests for Data Processor module
"""
import pytest
import pandas as pd
from datetime import datetime

from src.data_processor import BillingDataProcessor


class TestBillingDataProcessor:
    """Test cases for BillingDataProcessor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processor = BillingDataProcessor()
        
        # Sample AWS response data
        self.sample_response = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-31'},
                    'Groups': [
                        {
                            'Keys': ['Amazon EC2-Instance'],
                            'Metrics': {
                                'BlendedCost': {'Amount': '100.50', 'Unit': 'USD'}
                            }
                        },
                        {
                            'Keys': ['Amazon S3'],
                            'Metrics': {
                                'BlendedCost': {'Amount': '25.75', 'Unit': 'USD'}
                            }
                        }
                    ]
                },
                {
                    'TimePeriod': {'Start': '2024-02-01', 'End': '2024-02-29'},
                    'Groups': [
                        {
                            'Keys': ['Amazon EC2-Instance'],
                            'Metrics': {
                                'BlendedCost': {'Amount': '120.00', 'Unit': 'USD'}
                            }
                        },
                        {
                            'Keys': ['Amazon S3'],
                            'Metrics': {
                                'BlendedCost': {'Amount': '30.25', 'Unit': 'USD'}
                            }
                        }
                    ]
                }
            ]
        }
    
    def test_process_cost_and_usage_response_success(self):
        """Test successful processing of AWS response"""
        df = self.processor.process_cost_and_usage_response(self.sample_response)
        
        assert not df.empty
        assert len(df) == 4  # 2 services × 2 time periods
        assert 'StartDate' in df.columns
        assert 'Service' in df.columns
        assert 'Amount' in df.columns
        assert df['Amount'].dtype == float
    
    def test_process_empty_response(self):
        """Test processing of empty response"""
        empty_response = {}
        df = self.processor.process_cost_and_usage_response(empty_response)
        
        assert df.empty
    
    def test_calculate_cost_trends(self):
        """Test cost trends calculation"""
        df = self.processor.process_cost_and_usage_response(self.sample_response)
        trends = self.processor.calculate_cost_trends(df)
        
        assert 'total_cost' in trends
        assert 'average_monthly_cost' in trends
        assert 'mom_change_percent' in trends
        assert trends['total_cost'] == 276.5  # Sum of all costs
        assert trends['periods'] == 2
    
    def test_get_top_services_by_cost(self):
        """Test top services calculation"""
        df = self.processor.process_cost_and_usage_response(self.sample_response)
        top_services = self.processor.get_top_services_by_cost(df, top_n=5)
        
        assert not top_services.empty
        assert len(top_services) == 2  # EC2 and S3
        assert top_services.iloc[0]['Service'] == 'Amazon EC2-Instance'  # Highest cost
        assert top_services.iloc[0]['Amount'] == 220.5  # 100.5 + 120.0
    
    def test_calculate_service_cost_trends(self):
        """Test service cost trends calculation"""
        df = self.processor.process_cost_and_usage_response(self.sample_response)
        trends_df = self.processor.calculate_service_cost_trends(df)
        
        assert not trends_df.empty
        assert 'StartDate' in trends_df.columns
        assert 'Amazon EC2-Instance' in trends_df.columns
        assert 'Amazon S3' in trends_df.columns
        assert len(trends_df) == 2  # 2 time periods
    
    def test_generate_cost_summary(self):
        """Test cost summary generation"""
        df = self.processor.process_cost_and_usage_response(self.sample_response)
        summary = self.processor.generate_cost_summary(df)
        
        assert 'total_cost' in summary
        assert 'service_count' in summary
        assert 'top_service' in summary
        assert summary['total_cost'] == 276.5
        assert summary['service_count'] == 2
        assert summary['top_service'] == 'Amazon EC2-Instance'
    
    def test_generate_cost_summary_empty_data(self):
        """Test cost summary with empty data"""
        empty_df = pd.DataFrame()
        summary = self.processor.generate_cost_summary(empty_df)
        
        assert summary['total_cost'] == 0
        assert summary['service_count'] == 0
        assert summary['top_service'] == 'N/A'
    
    def test_process_total_cost_response(self):
        """Test processing response without grouping"""
        total_response = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-31'},
                    'Total': {
                        'BlendedCost': {'Amount': '150.00', 'Unit': 'USD'}
                    }
                }
            ]
        }
        
        df = self.processor.process_cost_and_usage_response(total_response)
        
        assert not df.empty
        assert len(df) == 1
        assert df.iloc[0]['Service'] == 'Total'
        assert df.iloc[0]['Amount'] == 150.0