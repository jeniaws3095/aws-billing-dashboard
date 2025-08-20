"""
Visualization components for AWS billing dashboard
Creates interactive charts using Plotly following DRY principles
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
import streamlit as st

from config.settings import COLOR_PALETTE, CHART_CONFIG


class BillingVisualizations:
    """
    Creates interactive visualizations for billing data
    Follows Single Responsibility and Open/Closed principles
    """
    
    def __init__(self):
        """Initialize visualization component"""
        self.color_palette = COLOR_PALETTE
        self.chart_config = CHART_CONFIG
    
    def create_cost_trend_chart(
        self,
        df: pd.DataFrame,
        title: str = "Cost Trends Over Time",
        granularity: str = "DAILY"
    ) -> go.Figure:
        """
        Create line chart showing cost trends over time
        
        Args:
            df: DataFrame with StartDate and Amount columns
            title: Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")
        
        fig = px.line(
            df,
            x='StartDate',
            y='Amount',
            title=title,
            labels={'Amount': 'Cost (USD)', 'StartDate': 'Date'},
            color_discrete_sequence=self.color_palette
        )
        
        # Customize x-axis based on granularity
        if granularity == "HOURLY":
            xaxis_title = "Date & Time"
            date_format = "%Y-%m-%d %H:%M"
        elif granularity == "WEEKLY":
            xaxis_title = "Week Starting"
            date_format = "%Y-%m-%d"
        elif granularity == "MONTHLY":
            xaxis_title = "Month"
            date_format = "%Y-%m"
        else:  # DAILY
            xaxis_title = "Date"
            date_format = "%Y-%m-%d"
        
        fig.update_layout(
            xaxis_title=xaxis_title,
            yaxis_title="Cost (USD)",
            hovermode='x unified',
            showlegend=False
        )
        
        fig.update_traces(
            line=dict(width=3),
            hovertemplate=f'<b>%{{x|{date_format}}}</b><br>Cost: $%{{y:,.2f}}<extra></extra>'
        )
        
        return fig
    
    def create_service_cost_pie_chart(
        self,
        df: pd.DataFrame,
        title: str = "Cost Distribution by Service"
    ) -> go.Figure:
        """
        Create pie chart showing cost distribution by service
        
        Args:
            df: DataFrame with Service and Amount columns
            title: Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")
        
        fig = px.pie(
            df,
            values='Amount',
            names='Service',
            title=title,
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Cost: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(showlegend=True)
        
        return fig
    
    def create_service_cost_bar_chart(
        self,
        df: pd.DataFrame,
        title: str = "Top Services by Cost"
    ) -> go.Figure:
        """
        Create horizontal bar chart for service costs
        
        Args:
            df: DataFrame with Service and Amount columns
            title: Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")
        
        # Sort by amount for better visualization
        df_sorted = df.sort_values('Amount', ascending=True)
        
        fig = px.bar(
            df_sorted,
            x='Amount',
            y='Service',
            orientation='h',
            title=title,
            labels={'Amount': 'Cost (USD)', 'Service': 'AWS Service'},
            color='Amount',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Cost (USD)",
            yaxis_title="AWS Service",
            showlegend=False,
            height=max(400, len(df_sorted) * 30)  # Dynamic height based on number of services
        )
        
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Cost: $%{x:,.2f}<extra></extra>'
        )
        
        return fig
    
    def create_service_trend_chart(
        self,
        df: pd.DataFrame,
        services: List[str] = None,
        title: str = "Service Cost Trends"
    ) -> go.Figure:
        """
        Create multi-line chart showing trends for multiple services
        
        Args:
            df: DataFrame with StartDate as index and services as columns
            services: List of services to include (if None, includes all)
            title: Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")
        
        fig = go.Figure()
        
        # Select services to display
        if services is None:
            services = [col for col in df.columns if col != 'StartDate']
        
        # Limit to top services to avoid cluttered chart
        services = services[:10]
        
        for i, service in enumerate(services):
            if service in df.columns:
                color = self.color_palette[i % len(self.color_palette)]
                fig.add_trace(
                    go.Scatter(
                        x=df['StartDate'],
                        y=df[service],
                        mode='lines+markers',
                        name=service,
                        line=dict(color=color, width=2),
                        hovertemplate=f'<b>{service}</b><br>Date: %{{x}}<br>Cost: $%{{y:,.2f}}<extra></extra>'
                    )
                )
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Cost (USD)",
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_cost_comparison_chart(
        self,
        current_period: float,
        previous_period: float,
        title: str = "Cost Comparison"
    ) -> go.Figure:
        """
        Create comparison chart between two periods
        
        Args:
            current_period: Current period cost
            previous_period: Previous period cost
            title: Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        categories = ['Previous Period', 'Current Period']
        values = [previous_period, current_period]
        
        colors = ['#ff7f0e', '#1f77b4']  # Orange for previous, blue for current
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                text=[f'${v:,.2f}' for v in values],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title="Period",
            yaxis_title="Cost (USD)",
            showlegend=False
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Cost: $%{y:,.2f}<extra></extra>'
        )
        
        return fig
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """
        Create empty chart with message
        
        Args:
            message: Message to display
            
        Returns:
            go.Figure: Empty Plotly figure
        """
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            xanchor='center',
            yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            plot_bgcolor='white'
        )
        return fig
    
    def display_metrics_cards(self, summary: Dict) -> None:
        """
        Display key metrics in card format using Streamlit
        
        Args:
            summary: Dictionary containing summary metrics
        """
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Cost",
                value=f"${summary.get('total_cost', 0):,.2f}"
            )
        
        with col2:
            st.metric(
                label="Services Used",
                value=summary.get('service_count', 0)
            )
        
        with col3:
            st.metric(
                label="Top Service",
                value=summary.get('top_service', 'N/A')
            )
        
        with col4:
            st.metric(
                label="Top Service Cost",
                value=f"${summary.get('top_service_cost', 0):,.2f}"
            )