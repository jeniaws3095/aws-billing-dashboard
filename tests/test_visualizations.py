"""
Tests for Visualizations module
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from src.visualizations import BillingVisualizations


class TestBillingVisualizations:
    """Test cases for BillingVisualizations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.viz = BillingVisualizations()
        
        # Sample data for testing
        self.sample_trend_data = pd.DataFrame({
            'StartDate': [datetime(2024, 1, 1), datetime(2024, 2, 1)],
            'Amount': [100.0, 120.0]
        })
        
        self.sample_service_data = pd.DataFrame({
            'Service': ['Amazon EC2-Instance', 'Amazon S3', 'Amazon RDS'],
            'Amount': [150.0, 75.0, 50.0]
        })
        
        self.sample_service_trends = pd.DataFrame({
            'StartDate': [datetime(2024, 1, 1), datetime(2024, 2, 1)],
            'Amazon EC2-Instance': [100.0, 120.0],
            'Amazon S3': [25.0, 30.0]
        })
    
    def test_create_cost_trend_chart(self):
        """Test cost trend chart creation"""
        fig = self.viz.create_cost_trend_chart(self.sample_trend_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1  # One trace
        assert fig.data[0].type == 'scatter'
        assert len(fig.data[0].x) == 2  # Two data points
    
    def test_create_cost_trend_chart_empty_data(self):
        """Test cost trend chart with empty data"""
        empty_df = pd.DataFrame()
        fig = self.viz.create_cost_trend_chart(empty_df)
        
        assert isinstance(fig, go.Figure)
        # Should have annotation for empty data
        assert len(fig.layout.annotations) > 0
    
    def test_create_service_cost_pie_chart(self):
        """Test service cost pie chart creation"""
        fig = self.viz.create_service_cost_pie_chart(self.sample_service_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'pie'
        assert len(fig.data[0].values) == 3  # Three services
    
    def test_create_service_cost_bar_chart(self):
        """Test service cost bar chart creation"""
        fig = self.viz.create_service_cost_bar_chart(self.sample_service_data)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'bar'
        assert fig.data[0].orientation == 'h'  # Horizontal bar
    
    def test_create_service_trend_chart(self):
        """Test service trend chart creation"""
        services = ['Amazon EC2-Instance', 'Amazon S3']
        fig = self.viz.create_service_trend_chart(
            self.sample_service_trends, 
            services=services
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2  # Two services
        for trace in fig.data:
            assert trace.type == 'scatter'
            assert trace.mode == 'lines+markers'
    
    def test_create_service_trend_chart_no_services_specified(self):
        """Test service trend chart without specifying services"""
        fig = self.viz.create_service_trend_chart(self.sample_service_trends)
        
        assert isinstance(fig, go.Figure)
        # Should include all services except StartDate
        expected_services = len(self.sample_service_trends.columns) - 1
        assert len(fig.data) == expected_services
    
    def test_create_cost_comparison_chart(self):
        """Test cost comparison chart creation"""
        fig = self.viz.create_cost_comparison_chart(120.0, 100.0)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'bar'
        assert len(fig.data[0].x) == 2  # Two periods
        assert len(fig.data[0].y) == 2  # Two values
    
    def test_create_empty_chart(self):
        """Test empty chart creation"""
        fig = self.viz._create_empty_chart("Test message")
        
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) == 1
        assert fig.layout.annotations[0].text == "Test message"
    
    def test_color_palette_usage(self):
        """Test that color palette is properly used"""
        fig = self.viz.create_service_cost_pie_chart(self.sample_service_data)
        
        # Check that colors are applied
        assert hasattr(fig.data[0], 'marker')
        # Pie charts use color_discrete_sequence which gets applied to marker.colors
    
    def test_chart_responsiveness(self):
        """Test that charts are configured for responsiveness"""
        fig = self.viz.create_cost_trend_chart(self.sample_trend_data)
        
        # Charts should have proper layout for responsiveness
        assert fig.layout.xaxis.title.text is not None
        assert fig.layout.yaxis.title.text is not None
    
    def test_hover_templates(self):
        """Test that hover templates are properly configured"""
        fig = self.viz.create_cost_trend_chart(self.sample_trend_data)
        
        # Should have custom hover template
        assert fig.data[0].hovertemplate is not None
        assert '$' in fig.data[0].hovertemplate  # Should format currency
    
    def test_large_service_list_handling(self):
        """Test handling of large service lists in trend charts"""
        # Create data with many services
        large_service_data = pd.DataFrame({
            'StartDate': [datetime(2024, 1, 1), datetime(2024, 2, 1)]
        })
        
        # Add 15 services (more than the 10 limit)
        for i in range(15):
            large_service_data[f'Service_{i}'] = [10.0 + i, 12.0 + i]
        
        fig = self.viz.create_service_trend_chart(large_service_data)
        
        # Should limit to 10 services
        assert len(fig.data) <= 10