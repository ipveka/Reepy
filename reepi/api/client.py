"""
REE API Client for fetching electricity data from Red Eléctrica Española's e·sios API.
This client provides methods to interact with the e·sios API using the official documentation.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

from reepi.utils.logger import get_logger

# Load environment variables from .env file if it exists
load_dotenv()

logger = get_logger(__name__)

class REEClient:
    """
    Client for the Red Eléctrica Española e·sios API.
    
    This client provides methods to fetch various types of electricity data
    from the e·sios API, including generation, demand, prices, and more.
    
    To use this client, you need to obtain an API token from https://www.esios.ree.es/
    by sending a request for a personal token. Once you receive the token, you can
    either:
    1. Set it as an environment variable named REE_API_TOKEN
    2. Pass it directly to the client when initializing
    
    Official API documentation: https://api.esios.ree.es/
    """
    
    # Base URL for the e·sios API
    BASE_URL = "https://api.esios.ree.es"
    
    # Common indicator IDs for different data types
    # These are based on the e·sios API documentation
    INDICATORS = {
        # Hydro generation indicators
        "hydro_programmed_pbf_ugh": 1,  # Generación programada PBF Hidráulica UGH
        "hydro_programmed_pbf_no_ugh": 2,  # Generación programada PBF Hidráulica no UGH
        
        # Electricity market prices
        "price_spot": 1013,  # PVPC price (Precio Voluntario para el Pequeño Consumidor)
        "price_daily_market": 600,  # Daily market price
        "price_intraday_market": 612,  # Intraday market price
        
        # Demand indicators
        "demand_actual": 1293,    # Actual demand (Demanda real)
        "demand_forecast": 1292,   # Demand forecast (Previsión de demanda)
        "demand_programmed": 1295,  # Programmed demand (Demanda programada)
        
        # Generation indicators
        "generation_mix": 1125,  # Generation mix structure by technology
        "generation_renewable": 1036,  # Renewable generation
        "generation_non_renewable": 1037,  # Non-renewable generation
        
        # CO2 emissions
        "co2_emissions": 10033,  # CO2 emissions from electricity generation
        "co2_free_generation": 10034   # CO2-free generation percentage
    }
    
    # Geographic zone IDs
    GEO_IDS = {
        "spain_peninsula": 8741,
        "canary_islands": 8742,
        "balearic_islands": 8743,
        "ceuta": 8744,
        "melilla": 8745
    }
    
    def __init__(self, api_token: str = None, timeout: int = 30):
        """
        Initialize the REE API client.
        
        Args:
            api_token: API token for authentication. If None, will try to get from environment.
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        
        # Get API token either from parameter or environment variable
        self.api_token = api_token or os.environ.get("REE_API_TOKEN")
        
        if not self.api_token:
            logger.warning(
                "No API token provided. You need to obtain a token from https://www.esios.ree.es/"
                " by sending a personal token request. Once received, set it as an environment"
                " variable named REE_API_TOKEN or pass it directly to the client."
            )
            
        # Set up headers according to the official documentation
        self.session.headers.update({
            'Host': 'api.esios.ree.es',
            'x-api-key': self.api_token if self.api_token else ""
        })
        
        # Log initialization
        if self.api_token and len(self.api_token) > 8:
            masked_token = f"{self.api_token[:4]}...{self.api_token[-4:]}"
            logger.info(f"Initialized REEClient with API token: {masked_token}")
        else:
            logger.info("Initialized REEClient without API token")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to the e·sios API.
        
        Args:
            endpoint: API endpoint to request (without leading slash)
            params: Query parameters for the request
            
        Returns:
            Response data as a dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            # Log the request details
            logger.debug(f"Making request to {url} with params: {params}")
            
            # Make the request with proper authentication headers
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            # Log the response status
            logger.debug(f"Response status: {response.status_code}")
            
            # Check for success
            response.raise_for_status()
            
            # Return the response data as JSON
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            # Include the response content in the error message if available
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text[:200]}...")
            raise
    
    def get_all_indicators(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available indicators from the API.
        
        Returns:
            List of indicators with their metadata
        """
        try:
            data = self._make_request("indicators")
            if data and "indicators" in data:
                return data["indicators"]
            return []
        except Exception as e:
            logger.error(f"Error getting indicators: {e}")
            return []
    
    def get_indicator(self, indicator_id: int) -> Dict[str, Any]:
        """
        Get details for a specific indicator by ID.
        
        Args:
            indicator_id: The ID of the indicator to retrieve
            
        Returns:
            Indicator details including the most recent values
        """
        try:
            return self._make_request(f"indicators/{indicator_id}")
        except Exception as e:
            logger.error(f"Error getting indicator {indicator_id}: {e}")
            return {}
    
    def get_indicator_values(
        self, 
        indicator_id: int, 
        start_date: str = None, 
        end_date: str = None, 
        geo_ids: List[int] = None,
        group_by: str = "hour"
    ) -> Dict[str, Any]:
        """
        Get data for any indicator by ID with optional filtering.
        
        Args:
            indicator_id: ID of the indicator to fetch
            start_date: Start date in format YYYY-MM-DD, if None, uses current date
            end_date: End date in format YYYY-MM-DD, if None, uses current date
            geo_ids: List of geographic zone IDs to filter by, defaults to peninsular Spain
            group_by: Time aggregation ('hour', 'day', 'month', 'year')
            
        Returns:
            Indicator data
        """
        # Default dates to today if not provided
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            
        # Default geo_ids to peninsular Spain if not provided
        if not geo_ids:
            geo_ids = [self.GEO_IDS["spain_peninsula"]]
            
        # Set up parameters
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "geo_ids": geo_ids,
            "group_by": group_by
        }
        
        # Make the request
        return self._make_request(f"indicators/{indicator_id}", params)
    
    # Convenience methods for common indicators
    
    def get_hydro_generation(self, start_date: str = None, end_date: str = None, group_by: str = "day") -> Dict[str, Any]:
        """
        Get Hydro UGH generation data (Generación programada PBF Hidráulica UGH).
        
        Args:
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
            group_by: Time aggregation ('hour', 'day', 'month', 'year')
            
        Returns:
            Hydro generation data
        """
        return self.get_indicator_values(
            self.INDICATORS["hydro_programmed_pbf_ugh"],
            start_date,
            end_date,
            group_by=group_by
        )
    
    def get_electricity_prices(self, start_date: str = None, end_date: str = None, group_by: str = "hour") -> Dict[str, Any]:
        """
        Get electricity price data (PVPC).
        
        Args:
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
            group_by: Time aggregation ('hour', 'day', 'month', 'year')
            
        Returns:
            Electricity price data
        """
        return self.get_indicator_values(
            self.INDICATORS["price_spot"],
            start_date,
            end_date,
            group_by=group_by
        )
    
    def get_demand_data(self, start_date: str = None, end_date: str = None, group_by: str = "hour") -> Dict[str, Any]:
        """
        Get electricity demand data.
        
        Args:
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
            group_by: Time aggregation ('hour', 'day', 'month', 'year')
            
        Returns:
            Electricity demand data
        """
        return self.get_indicator_values(
            self.INDICATORS["demand_actual"],
            start_date,
            end_date,
            group_by=group_by
        )
    
    def get_generation_mix(self, start_date: str = None, end_date: str = None, group_by: str = "hour") -> Dict[str, Any]:
        """
        Get generation mix data by technology type.
        
        Args:
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
            group_by: Time aggregation ('hour', 'day', 'month', 'year')
            
        Returns:
            Generation mix data
        """
        return self.get_indicator_values(
            self.INDICATORS["generation_mix"],
            start_date,
            end_date,
            group_by=group_by
        )
    
    def get_co2_emissions(self, start_date: str = None, end_date: str = None, group_by: str = "day") -> Dict[str, Any]:
        """
        Get CO2 emissions data related to electricity generation.
        
        Args:
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
            group_by: Time aggregation ('hour', 'day', 'month', 'year')
            
        Returns:
            CO2 emissions data
        """
        return self.get_indicator_values(
            self.INDICATORS["co2_emissions"],
            start_date,
            end_date,
            group_by=group_by
        )
    
    # Data processing methods
    
    def to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert API response data to a pandas DataFrame.
        
        Args:
            data: API response from an indicator endpoint
            
        Returns:
            DataFrame containing the indicator values with processed columns
        """
        # Check if data has the expected structure
        if not data or "indicator" not in data or "values" not in data["indicator"]:
            logger.warning("Invalid data format from API response")
            return pd.DataFrame()
        
        # Extract values
        values = data["indicator"]["values"]
        
        # Handle empty values
        if not values:
            logger.warning("No values found in API response")
            return pd.DataFrame()
        
        # Create DataFrame from values
        df = pd.DataFrame(values)
        
        # Process datetime columns
        for col in df.columns:
            if "datetime" in col.lower():
                df[col] = pd.to_datetime(df[col])
        
        # Add indicator metadata
        indicator = data["indicator"]
        df["indicator_name"] = indicator.get("name", "Unknown")
        df["indicator_id"] = indicator.get("id", None)
        
        return df
    
    def get_real_time_data(self) -> Dict[str, Any]:
        """
        Get real-time generation mix data for the current day.
        
        Returns:
            Current generation mix data
        """
        # Get the current date 
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get generation mix for today
        return self.get_generation_mix(today, today, "hour")
