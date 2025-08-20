"""
Tests for AWS Client module
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError

from src.aws_client import AWSBillingClient


class TestAWSBillingClient:
    """Test cases for AWSBillingClient"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = AWSBillingClient()
    
    @patch('boto3.client')
    def test_client_initialization(self, mock_boto_client):
        """Test client initialization"""
        mock_ce_client = Mock()
        mock_boto_client.return_value = mock_ce_client
        
        # Access client property to trigger initialization
        client = self.client.client
        
        mock_boto_client.assert_called_once_with('ce', region_name='us-east-1')
        assert client == mock_ce_client
    
    @patch('boto3.client')
    def test_validate_credentials_success(self, mock_boto_client):
        """Test successful credential validation"""
        mock_ce_client = Mock()
        mock_boto_client.return_value = mock_ce_client
        mock_ce_client.get_cost_and_usage.return_value = {'ResultsByTime': []}
        
        result = self.client.validate_credentials()
        
        assert result is True
        mock_ce_client.get_cost_and_usage.assert_called_once()
    
    @patch('boto3.client')
    def test_validate_credentials_failure(self, mock_boto_client):
        """Test credential validation failure"""
        mock_ce_client = Mock()
        mock_boto_client.return_value = mock_ce_client
        mock_ce_client.get_cost_and_usage.side_effect = NoCredentialsError()
        
        result = self.client.validate_credentials()
        
        assert result is False
    
    @patch('boto3.client')
    def test_get_cost_and_usage_success(self, mock_boto_client):
        """Test successful cost and usage retrieval"""
        mock_ce_client = Mock()
        mock_boto_client.return_value = mock_ce_client
        
        expected_response = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-31'},
                    'Total': {'BlendedCost': {'Amount': '100.00', 'Unit': 'USD'}}
                }
            ]
        }
        mock_ce_client.get_cost_and_usage.return_value = expected_response
        
        result = self.client.get_cost_and_usage('2024-01-01', '2024-01-31')
        
        assert result == expected_response
        mock_ce_client.get_cost_and_usage.assert_called_once()
    
    @patch('boto3.client')
    def test_get_cost_and_usage_with_group_by(self, mock_boto_client):
        """Test cost and usage retrieval with grouping"""
        mock_ce_client = Mock()
        mock_boto_client.return_value = mock_ce_client
        mock_ce_client.get_cost_and_usage.return_value = {'ResultsByTime': []}
        
        group_by = [{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        
        self.client.get_cost_and_usage(
            '2024-01-01', 
            '2024-01-31',
            group_by=group_by
        )
        
        call_args = mock_ce_client.get_cost_and_usage.call_args[1]
        assert 'GroupBy' in call_args
        assert call_args['GroupBy'] == group_by
    
    @patch('boto3.client')
    def test_get_services_list_success(self, mock_boto_client):
        """Test successful services list retrieval"""
        mock_ce_client = Mock()
        mock_boto_client.return_value = mock_ce_client
        
        expected_response = {
            'DimensionValues': [
                {'Value': 'Amazon EC2-Instance'},
                {'Value': 'Amazon S3'}
            ]
        }
        mock_ce_client.get_dimension_values.return_value = expected_response
        
        result = self.client.get_services_list('2024-01-01', '2024-01-31')
        
        expected_services = ['Amazon EC2-Instance', 'Amazon S3']
        assert result == expected_services
    
    @patch('boto3.client')
    def test_get_cost_by_service(self, mock_boto_client):
        """Test cost by service retrieval"""
        mock_ce_client = Mock()
        mock_boto_client.return_value = mock_ce_client
        mock_ce_client.get_cost_and_usage.return_value = {'ResultsByTime': []}
        
        self.client.get_cost_by_service('2024-01-01', '2024-01-31')
        
        call_args = mock_ce_client.get_cost_and_usage.call_args[1]
        assert 'GroupBy' in call_args
        assert call_args['GroupBy'] == [{'Type': 'DIMENSION', 'Key': 'SERVICE'}]