"""
Configuration settings for AWS Billing Dashboard
"""
from datetime import datetime, timedelta
from typing import Dict, List

# AWS Configuration
AWS_REGION = "us-east-1"
AWS_COST_EXPLORER_REGION = "us-east-1"  # Cost Explorer is only available in us-east-1

# Dashboard Configuration
DEFAULT_METRICS = ["BlendedCost", "UnblendedCost", "UsageQuantity"]
DEFAULT_GRANULARITY = "MONTHLY"
DEFAULT_GROUP_BY = [{"Type": "DIMENSION", "Key": "SERVICE"}]

# Date Configuration
DEFAULT_DAYS_BACK = 90
MAX_DAYS_BACK = 365

# Time Period Filters (like AWS Console)
TIME_PERIOD_OPTIONS = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 3 months": 90,
    "Last 6 months": 180,
    "Last 12 months": 365
}

# Granularity Configuration
GRANULARITY_LIMITS = {
    "HOURLY": 7,      # Max 7 days for hourly data
    "DAILY": 365,     # Max 365 days for daily data
    "WEEKLY": 365,    # Max 365 days for weekly data (processed from daily)
    "MONTHLY": 365    # Max 365 days for monthly data
}

# Chart Configuration
CHART_CONFIG: Dict = {
    "displayModeBar": False,
    "responsive": True,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "aws_billing_chart",
        "height": 500,
        "width": 700,
        "scale": 1
    }
}

# Color Palette for Charts
COLOR_PALETTE: List[str] = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]

# Top Services to Highlight
TOP_SERVICES_COUNT = 10

# Cache Configuration (in seconds)
CACHE_TTL = 3600  # 1 hour