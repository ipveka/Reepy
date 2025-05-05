"""
Data processing utilities for the REEpy package.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

def format_datetime(df: pd.DataFrame, datetime_col: str = 'datetime') -> pd.DataFrame:
    """
    Format datetime column in a DataFrame.
    
    Args:
        df: Input DataFrame
        datetime_col: Name of the datetime column
        
    Returns:
        DataFrame with formatted datetime column
    """
    df_copy = df.copy()
    if datetime_col in df_copy.columns:
        df_copy[datetime_col] = pd.to_datetime(df_copy[datetime_col])
    return df_copy

def calculate_renewable_percentage(df: pd.DataFrame) -> float:
    """
    Calculate the percentage of renewable energy from generation data.
    
    Args:
        df: DataFrame containing generation data
        
    Returns:
        Percentage of renewable energy
    """
    renewable_types = [
        'Hydro', 'Wind', 'Solar PV', 'Solar thermal', 'Hydroeólica', 
        'Geothermal', 'Biomass', 'Other renewables'
    ]
    
    if df.empty:
        return 0.0
    
    renewable_df = df[df['type'].isin(renewable_types)]
    renewable_sum = renewable_df['value'].sum()
    total_sum = df['value'].sum()
    
    if total_sum == 0:
        return 0.0
    
    return (renewable_sum / total_sum) * 100.0

def aggregate_by_type(df: pd.DataFrame, value_col: str = 'value') -> pd.DataFrame:
    """
    Aggregate data by type.
    
    Args:
        df: Input DataFrame
        value_col: Name of the value column
        
    Returns:
        Aggregated DataFrame
    """
    if df.empty:
        return df
    
    return df.groupby('type')[value_col].sum().reset_index()

def calculate_daily_average(df: pd.DataFrame, datetime_col: str = 'datetime', value_col: str = 'value') -> pd.DataFrame:
    """
    Calculate daily average of values.
    
    Args:
        df: Input DataFrame
        datetime_col: Name of the datetime column
        value_col: Name of the value column
        
    Returns:
        DataFrame with daily averages
    """
    df_copy = format_datetime(df, datetime_col)
    
    if df_copy.empty:
        return df_copy
    
    df_copy['date'] = df_copy[datetime_col].dt.date
    daily_avg = df_copy.groupby(['date', 'type'])[value_col].mean().reset_index()
    
    return daily_avg

def extract_time_series(data: Dict[str, Any], indicator: str = None) -> pd.DataFrame:
    """
    Extract time series data from REE API response.
    
    Args:
        data: REE API response data
        indicator: Optional indicator to filter by
        
    Returns:
        DataFrame with time series data
    """
    if not data or 'included' not in data:
        return pd.DataFrame()
    
    result = []
    
    for item in data['included']:
        if indicator and item['attributes'].get('title') != indicator:
            continue
            
        for value in item['attributes']['values']:
            entry = {
                'datetime': value['datetime'],
                'type': item['attributes']['title'],
                'value': value['value'],
            }
            # Add additional fields if they exist
            for key, val in value.items():
                if key not in ['datetime', 'value']:
                    entry[key] = val
                    
            result.append(entry)
    
    return pd.DataFrame(result)
