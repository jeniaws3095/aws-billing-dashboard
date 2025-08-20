# AWS Billing Dashboard - Technical Documentation

## Architecture Overview

The AWS Billing Dashboard follows SOLID principles and clean architecture patterns:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  Dashboard App   │────│  Visualizations │
│   (app.py)      │    │  (Orchestrator)  │    │  (Charts/Graphs)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │                 │
                ┌──────▼──────┐   ┌──────▼──────┐
                │ AWS Client  │   │ Data        │
                │ (boto3)     │   │ Processor   │
                └─────────────┘   └─────────────┘
```

## Design Principles Applied

### 1. Single Responsibility Principle (SRP)
- **AWSBillingClient**: Only handles AWS API interactions
- **BillingDataProcessor**: Only processes and transforms data
- **BillingVisualizations**: Only creates charts and visualizations
- **BillingDashboard**: Only orchestrates the UI flow

### 2. Open/Closed Principle (OCP)
- Easy to extend with new chart types in `BillingVisualizations`
- New AWS services can be added without modifying existing code
- Configuration-driven approach allows customization without code changes

### 3. Liskov Substitution Principle (LSP)
- All visualization methods return `go.Figure` objects
- Consistent interfaces across all data processing methods

### 4. Interface Segregation Principle (ISP)
- Each class has focused, minimal interfaces
- No class depends on methods it doesn't use

### 5. Dependency Inversion Principle (DIP)
- High-level modules don't depend on low-level modules
- Configuration is externalized in `config/settings.py`

## DRY (Don't Repeat Yourself) Implementation

### Configuration Centralization
```python
# config/settings.py - Single source of truth
DEFAULT_METRICS = ["BlendedCost", "UnblendedCost", "UsageQuantity"]
COLOR_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", ...]
```

### Reusable Components
- Chart creation methods are parameterized and reusable
- Data processing functions handle multiple data formats
- Error handling patterns are consistent across modules

### Template Methods
```python
def _create_empty_chart(self, message: str) -> go.Figure:
    """Reusable empty chart template"""
```

## Module Documentation

### src/aws_client.py
**Purpose**: AWS Cost Explorer API integration

**Key Methods**:
- `validate_credentials()`: Validates AWS access
- `get_cost_and_usage()`: Retrieves cost data with flexible parameters
- `get_cost_by_service()`: Specialized method for service-wise costs

**Error Handling**: Graceful handling of AWS credential and API errors

### src/data_processor.py
**Purpose**: Data transformation and analysis

**Key Methods**:
- `process_cost_and_usage_response()`: Converts AWS response to DataFrame
- `calculate_cost_trends()`: Computes trends and insights
- `get_top_services_by_cost()`: Identifies highest-cost services

**Data Flow**: AWS JSON → pandas DataFrame → Analysis metrics

### src/visualizations.py
**Purpose**: Interactive chart generation

**Key Methods**:
- `create_cost_trend_chart()`: Time series visualization
- `create_service_cost_pie_chart()`: Service distribution
- `create_service_cost_bar_chart()`: Service comparison

**Features**: Responsive design, hover templates, color consistency

## Testing Strategy

### Test Structure
```
tests/
├── test_aws_client.py      # AWS integration tests
├── test_data_processor.py  # Data processing logic tests
└── test_visualizations.py  # Chart generation tests
```

### Test Types
1. **Unit Tests**: Individual method testing
2. **Integration Tests**: Component interaction testing
3. **Mock Tests**: AWS API simulation using moto

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific test file
pytest tests/test_aws_client.py -v

# Run with coverage
pytest --cov=src tests/
```

## Configuration Management

### Environment Variables
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### Application Settings
- **Cache TTL**: 1 hour for AWS data
- **Date Limits**: Maximum 365 days lookback
- **Chart Colors**: Consistent color palette
- **Top Services**: Configurable count (default: 10)

## Performance Optimizations

### Caching Strategy
```python
@st.cache_data(ttl=3600)  # 1 hour cache
def _load_billing_data(self, date_range, granularity):
    # Expensive AWS API calls are cached
```

### Data Processing
- Pandas operations for efficient data manipulation
- Lazy loading of AWS client
- Minimal data transfer from AWS APIs

### UI Responsiveness
- Progressive loading with spinners
- Efficient chart rendering with Plotly
- Responsive layout design

## Security Considerations

### AWS Credentials
- Never hardcode credentials
- Support for multiple credential methods:
  - AWS CLI configuration
  - Environment variables
  - IAM roles (for EC2/ECS deployment)

### Required AWS Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetUsageReport",
                "ce:GetDimensionValues"
            ],
            "Resource": "*"
        }
    ]
}
```

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Docker Deployment
```bash
docker-compose up -d
```

### Cloud Deployment
- **Streamlit Cloud**: Direct GitHub integration
- **AWS ECS**: Container-based deployment
- **Heroku**: Platform-as-a-Service option

## Monitoring and Logging

### Application Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.error(f"AWS credential validation failed: {e}")
```

### Health Checks
- Docker health check endpoint
- AWS connectivity validation
- Data freshness monitoring

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Solution: Configure AWS CLI or set environment variables

2. **No Cost Data Available**
   - Solution: Check date range and AWS account activity

3. **Permission Denied**
   - Solution: Ensure Cost Explorer permissions are granted

4. **Slow Loading**
   - Solution: Reduce date range or check AWS API limits

### Debug Mode
```bash
streamlit run app.py --logger.level=debug
```

## Future Enhancements

### Planned Features
- [ ] Budget alerts integration
- [ ] Cost forecasting
- [ ] Multi-account support
- [ ] Export to PDF reports
- [ ] Scheduled email reports

### Extensibility Points
- New chart types in `BillingVisualizations`
- Additional AWS services in `AWSBillingClient`
- Custom data processors for specific use cases
- Plugin architecture for third-party integrations

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maintain test coverage above 80%
- Document all public methods

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request with description

## License

MIT License - see LICENSE file for details.