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