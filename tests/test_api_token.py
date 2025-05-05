"""
Test script to verify that the real API token in the .env file works with the e·sios API.
This script makes actual API calls.
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path to allow imports from reepi
# This is crucial for finding the reepi module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reepi.api.client import REEClient
from reepi.utils.logger import get_logger

logger = get_logger(__name__)

def test_token():
    """Test if the API token in .env works with the e·sios API."""
    print("\n=== Testing e·sios API Token ===\n")
    
    # Load environment variables from .env
    load_dotenv()
    
    # Get token
    token = os.environ.get("REE_API_TOKEN")
    if not token:
        print("Error: No API token found in .env file")
        return False
    
    # Display masked token
    if len(token) > 8:
        masked_token = token[:4] + "*" * (len(token) - 8) + token[-4:]
    else:
        masked_token = "****"
    print(f"Using token: {masked_token}")
    
    # Create client with token
    client = REEClient()
    
    # Test 1: Get available indicators
    print("\nTest 1: Getting available indicators...")
    try:
        indicators = client.get_available_indicators()
        if indicators:
            print(f"SUCCESS! Found {len(indicators)} indicators")
            print("\nSample indicators:")
            for i, indicator in enumerate(indicators[:3]):
                print(f"  {i+1}. {indicator.get('name')} (ID: {indicator.get('id')})")
            test1_success = True
        else:
            print("Failed to get indicators or no indicators available")
            test1_success = False
    except Exception as e:
        print(f"Error: {e}")
        test1_success = False

    # Test 2: Get specific indicator (Hydro generation)
    print("\nTest 2: Getting Hydro generation data (indicator 1)...")
    try:
        # Get data for last month
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        print(f"Fetching hydro generation data for {start_date_str} to {end_date_str}...")
        hydro_data = client.get_hydro_generation(start_date_str, end_date_str, "day")
        
        if hydro_data and "indicator" in hydro_data:
            print(f"SUCCESS! Retrieved data for indicator: {hydro_data['indicator'].get('name')}")
            
            # Check if there are values
            values = hydro_data["indicator"].get("values", [])
            if values:
                print(f"Retrieved {len(values)} data points")
                
                # Parse the data into a DataFrame
                df = client.parse_data_to_dataframe(hydro_data)
                if not df.empty:
                    print(f"Successfully parsed data into DataFrame with {len(df)} rows")
                    print("Data columns:", df.columns.tolist())
                    
                    # Show a sample value if available
                    if len(df) > 0:
                        print("\nSample data point:")
                        print(df.iloc[0].to_dict())
                else:
                    print("Failed to parse data into DataFrame")
            test2_success = True
        else:
            print("Failed to get hydro generation data or data is in unexpected format")
            print(f"Response keys: {list(hydro_data.keys()) if hydro_data else 'None'}")
            test2_success = False
    except Exception as e:
        print(f"Error: {e}")
        test2_success = False
    
    # Test 3: Get electricity prices
    print("\nTest 3: Getting electricity price data...")
    try:
        # Get price data for yesterday
        yesterday = datetime.now() - timedelta(days=1)
        
        start_date = yesterday.strftime("%Y-%m-%d")
        end_date = yesterday.strftime("%Y-%m-%d")
        
        print(f"Fetching price data for {start_date}...")
        price_data = client.get_electricity_prices(start_date, end_date)
        
        if price_data and "indicator" in price_data:
            print(f"SUCCESS! Retrieved data for indicator: {price_data['indicator'].get('name')}")
            
            # Check if there are values
            values = price_data["indicator"].get("values", [])
            if values:
                print(f"Retrieved {len(values)} data points")
                
                # Parse the data into a DataFrame
                df = client.parse_data_to_dataframe(price_data)
                if not df.empty:
                    print(f"Successfully parsed data into DataFrame with {len(df)} rows")
                    print("Data columns:", df.columns.tolist())
                    
                    # Show a sample value if available
                    if len(df) > 0:
                        print("\nSample data point:")
                        print(df.iloc[0].to_dict())
                else:
                    print("Failed to parse data into DataFrame")
            test3_success = True
        else:
            print("Failed to get price data or data is in unexpected format")
            print(f"Response keys: {list(price_data.keys()) if price_data else 'None'}")
            test3_success = False
    except Exception as e:
        print(f"Error: {e}")
        test3_success = False
    
    # Summary
    print("\n=== Summary ===")
    tests_passed = sum([test1_success, test2_success, test3_success])
    print(f"Tests passed: {tests_passed}/3")
    
    if tests_passed == 3:
        print("\nSUCCESS! Your API token is working correctly with the e·sios API.\n")
        return True
    elif tests_passed > 0:
        print("\nPARTIAL SUCCESS. Some API calls worked but not all.\n")
        return True
    else:
        print("\nFAILURE. Your API token is not working properly with the e·sios API.\n")
        return False

if __name__ == "__main__":
    test_token()
