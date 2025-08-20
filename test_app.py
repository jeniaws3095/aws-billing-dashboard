#!/usr/bin/env python3
"""
Simple test to verify the application components work
"""
import sys
import traceback

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test core modules
        from src.aws_client import AWSBillingClient
        from src.data_processor import BillingDataProcessor
        from src.visualizations import BillingVisualizations
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_data_processing():
    """Test data processing with sample data"""
    try:
        print("Testing data processing...")
        
        from src.data_processor import BillingDataProcessor
        
        # Sample AWS response
        sample_response = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-31'},
                    'Groups': [
                        {
                            'Keys': ['Amazon EC2-Instance'],
                            'Metrics': {'BlendedCost': {'Amount': '100.50', 'Unit': 'USD'}}
                        }
                    ]
                }
            ]
        }
        
        processor = BillingDataProcessor()
        df = processor.process_cost_and_usage_response(sample_response)
        
        if not df.empty:
            print("✅ Data processing successful!")
            print(f"   Processed {len(df)} rows")
            return True
        else:
            print("❌ Data processing returned empty DataFrame")
            return False
            
    except Exception as e:
        print(f"❌ Data processing failed: {e}")
        traceback.print_exc()
        return False

def test_visualizations():
    """Test visualization creation"""
    try:
        print("Testing visualizations...")
        
        from src.visualizations import BillingVisualizations
        import pandas as pd
        from datetime import datetime
        
        viz = BillingVisualizations()
        
        # Sample data
        sample_data = pd.DataFrame({
            'StartDate': [datetime(2024, 1, 1)],
            'Amount': [100.0]
        })
        
        # Test chart creation
        fig = viz.create_cost_trend_chart(sample_data)
        
        if fig:
            print("✅ Visualization creation successful!")
            return True
        else:
            print("❌ Visualization creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Visualization creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Running AWS Billing Dashboard Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_processing,
        test_visualizations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo run the demo:")
        print("  python -m streamlit run demo.py")
        print("\nTo run with real AWS data:")
        print("  python -m streamlit run app.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())