# AWS Billing Dashboard

A lightweight Streamlit application for analyzing AWS billing data with interactive dashboards and insights.

## Features

- 📊 Interactive billing dashboards
- 📈 Cost trend analysis
- 🔍 Service-wise cost breakdown
- 📅 Customizable date ranges
- 🎯 Developer and business leader friendly interface

## Quick Start

1. **Navigate to project folder:**
   ```bash
   cd aws-billing-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials:**
   - Use AWS CLI: `aws configure`
   - Or set environment variables:
     ```bash
     export AWS_ACCESS_KEY_ID=your_access_key
     export AWS_SECRET_ACCESS_KEY=your_secret_key
     export AWS_DEFAULT_REGION=us-east-1
     ```

4. **Run the application:**
   ```bash
   # Demo with sample data (no AWS credentials needed)
   python start_demo.py
   
   # Or with real AWS data
   python start_app.py
   
   # Or manually
   streamlit run app.py
   ```

## Project Structure

```
├── app.py                 # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── aws_client.py      # AWS service client
│   ├── data_processor.py  # Data processing logic
│   └── visualizations.py # Chart and graph components
├── tests/
│   ├── __init__.py
│   ├── test_aws_client.py
│   ├── test_data_processor.py
│   └── test_visualizations.py
├── config/
│   └── settings.py        # Application configuration
└── requirements.txt
```

## Testing

Run tests with:
```bash
pytest tests/ -v
```

## AWS Permissions Required

The application requires the following AWS permissions:
- `ce:GetCostAndUsage`
- `ce:GetUsageReport`
- `ce:GetDimensionValues`

## License

MIT License