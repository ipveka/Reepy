"""
Tests for the REEpy package.

These tests verify the functionality of the package components without requiring
an actual API token. API requests are mocked to simulate responses.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import pandas as pd
import json
import requests
from datetime import datetime, timedelta

# Add parent directory to path to allow imports from reepi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reepi.api.client import REEClient
from reepi.utils.data_processing import (
    format_datetime, 
    calculate_renewable_percentage,
    aggregate_by_type,
    calculate_daily_average,
    extract_time_series
)


class TestREEClient(unittest.TestCase):
    """Tests for the REE API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create client with dummy token
        self.client = REEClient(api_token="dummy_token_for_testing")
        
        # Update the client headers to match the correct format
        self.client.session.headers.update({
            'Host': 'api.esios.ree.es',
            'x-api-key': "dummy_token_for_testing"
        })
    
    @patch('requests.Session.get')
    def test_get_real_time_data(self, mock_get):
        """Test getting real-time data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "indicator": {
                "name": "Generation Mix",
                "values": [
                    {"datetime": "2023-01-01T12:00:00", "value": 1000.0, "percentage": 25.0},
                    {"datetime": "2023-01-01T13:00:00", "value": 1100.0, "percentage": 27.5}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Check that the correct headers are being used
        self.assertIn('Host', self.client.session.headers)
        self.assertEqual(self.client.session.headers['Host'], 'api.esios.ree.es')
        self.assertIn('x-api-key', self.client.session.headers)
        
        # Call the method
        result = self.client.get_real_time_data()
        
        # Assert the response was processed correctly
        self.assertIn("indicator", result)
        self.assertEqual(len(result["indicator"]["values"]), 2)
        
        # Also test the parsing
        df = self.client.to_dataframe(result)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["value"], 1000.0)
    
    @patch('requests.Session.get')
    def test_get_generation_mix(self, mock_get):
        """Test getting generation mix data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "indicator": {
                "name": "Generation Mix",
                "values": [
                    {"datetime": "2023-01-01T00:00:00", "value": 900.0, "percentage": 22.5},
                    {"datetime": "2023-01-02T00:00:00", "value": 950.0, "percentage": 23.8}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.client.get_generation_mix("2023-01-01", "2023-01-02", "day")
        
        # Assert the response was processed correctly
        self.assertIn("indicator", result)
        self.assertEqual(len(result["indicator"]["values"]), 2)
    
    @patch('requests.Session.get')
    def test_get_electricity_prices(self, mock_get):
        """Test getting electricity price data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "indicator": {
                "name": "PVPC Price",
                "values": [
                    {"datetime": "2023-01-01T00:00:00", "value": 150.5},
                    {"datetime": "2023-01-01T01:00:00", "value": 145.2}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.client.get_electricity_prices("2023-01-01", "2023-01-02", "hour")
        
        # Assert the response was processed correctly
        self.assertIn("indicator", result)
        self.assertEqual(len(result["indicator"]["values"]), 2)
        
        # Also test the parsing
        df = self.client.to_dataframe(result)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["value"], 150.5)
    
    @patch('requests.Session.get')
    def test_api_error_handling(self, mock_get):
        """Test that API errors are handled properly."""
        # Mock a failed API response
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.RequestException("API Error")
        mock_get.return_value = mock_response
        
        # Call the method and check that it raises the exception
        with self.assertRaises(requests.RequestException):
            self.client.get_real_time_data()
    
    def test_to_dataframe_empty(self):
        """Test converting empty API responses to DataFrame."""
        # Test with empty data structure
        df = self.client.to_dataframe({})
        self.assertTrue(df.empty)
        
        # Test with None
        df = self.client.to_dataframe(None)
        self.assertTrue(df.empty)
        
        # Test with missing values
        df = self.client.to_dataframe({"indicator": {"name": "Test"}})
        self.assertTrue(df.empty)
    
    def test_to_dataframe(self):
        """Test converting API response to DataFrame."""
        # Create a test API response
        data = {
            "indicator": {
                "id": 1,
                "name": "Test Indicator",
                "values": [
                    {"datetime": "2023-01-01T00:00:00", "value": 100.0, "geo_id": 8741},
                    {"datetime": "2023-01-02T00:00:00", "value": 200.0, "geo_id": 8741}
                ]
            }
        }
        
        # Convert to DataFrame
        df = self.client.to_dataframe(data)
        
        # Assert DataFrame was created correctly
        self.assertEqual(len(df), 2)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["datetime"]))
        self.assertEqual(df.iloc[0]["value"], 100.0)
        self.assertEqual(df.iloc[1]["value"], 200.0)
        self.assertEqual(df["indicator_name"].unique()[0], "Test Indicator")
        self.assertEqual(df["indicator_id"].unique()[0], 1)


class TestDataProcessing(unittest.TestCase):
    """Tests for the data processing utilities."""
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        # Create a test DataFrame
        df = pd.DataFrame({
            'datetime': ['2023-01-01T12:00:00', '2023-01-01T13:00:00'],
            'value': [100, 200]
        })
        
        # Format the datetime column
        result = format_datetime(df)
        
        # Check that the datetime column is now datetime type
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['datetime']))
    
    def test_calculate_renewable_percentage(self):
        """Test renewable percentage calculation."""
        # Create a test DataFrame with renewable and non-renewable types
        df = pd.DataFrame({
            'type': ['Wind', 'Solar PV', 'Nuclear', 'Coal'],
            'value': [200, 100, 400, 300]
        })
        
        # Calculate renewable percentage
        result = calculate_renewable_percentage(df)
        
        # Wind + Solar PV = 300, Total = 1000, so percentage should be 30%
        self.assertEqual(result, 30.0)
    
    def test_aggregate_by_type(self):
        """Test aggregation by type."""
        # Create a test DataFrame
        df = pd.DataFrame({
            'type': ['Wind', 'Wind', 'Solar PV', 'Solar PV'],
            'value': [100, 150, 200, 250]
        })
        
        # Aggregate by type
        result = aggregate_by_type(df)
        
        # Check that aggregation was done correctly
        self.assertEqual(len(result), 2)
        self.assertEqual(result[result['type'] == 'Wind']['value'].iloc[0], 250)
        self.assertEqual(result[result['type'] == 'Solar PV']['value'].iloc[0], 450)
    
    def test_calculate_daily_average(self):
        """Test daily average calculation."""
        # Create a test DataFrame with multiple days
        df = pd.DataFrame({
            'datetime': pd.to_datetime(['2023-01-01 12:00:00', '2023-01-01 18:00:00', 
                                       '2023-01-02 12:00:00', '2023-01-02 18:00:00']),
            'type': ['Wind', 'Wind', 'Wind', 'Wind'],
            'value': [100, 200, 300, 400]
        })
        
        # Calculate daily average
        result = calculate_daily_average(df)
        
        # Check that daily averages were calculated correctly
        self.assertEqual(len(result), 2)
        self.assertEqual(result[result['date'] == pd.Timestamp('2023-01-01').date()]['value'].iloc[0], 150)
        self.assertEqual(result[result['date'] == pd.Timestamp('2023-01-02').date()]['value'].iloc[0], 350)


def run_tests():
    """Run all tests."""
    print("Running REEpy tests...\n")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == '__main__':
    run_tests()
