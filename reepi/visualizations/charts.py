"""
Visualization components for the REEpy package.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Optional, Union

def plot_generation_mix(df: pd.DataFrame, title: str = "Electricity Generation Mix") -> go.Figure:
    """
    Create a stacked area chart for generation mix data.
    
    Args:
        df: DataFrame with generation data
        title: Title for the chart
        
    Returns:
        Plotly figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Format datetime if needed
    if 'datetime' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Create the figure
    fig = px.area(
        df, 
        x="datetime", 
        y="value", 
        color="type",
        title=title,
        labels={"value": "Production (MW)", "datetime": "Date", "type": "Source"}
    )
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    return fig

def plot_price_comparison(df: pd.DataFrame, title: str = "Electricity Price Evolution") -> go.Figure:
    """
    Create a line chart for price data.
    
    Args:
        df: DataFrame with price data
        title: Title for the chart
        
    Returns:
        Plotly figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Format datetime if needed
    if 'datetime' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Create the figure
    fig = px.line(
        df, 
        x="datetime", 
        y="value", 
        color="type",
        title=title,
        labels={"value": "Price (€/MWh)", "datetime": "Date", "type": "Market"}
    )
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    return fig

def plot_demand_curve(df: pd.DataFrame, title: str = "Electricity Demand") -> go.Figure:
    """
    Create a line chart for demand data.
    
    Args:
        df: DataFrame with demand data
        title: Title for the chart
        
    Returns:
        Plotly figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Format datetime if needed
    if 'datetime' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Create the figure
    fig = px.line(
        df, 
        x="datetime", 
        y="value", 
        color="type",
        title=title,
        labels={"value": "Demand (MW)", "datetime": "Date", "type": "Type"}
    )
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    return fig

def plot_renewable_percentage(df: pd.DataFrame, title: str = "Renewable Energy Percentage") -> go.Figure:
    """
    Create a gauge chart for renewable energy percentage.
    
    Args:
        df: DataFrame with generation data
        title: Title for the chart
        
    Returns:
        Plotly figure object
    """
    from reepi.utils.data_processing import calculate_renewable_percentage
    
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    renewable_pct = calculate_renewable_percentage(df)
    
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=renewable_pct,
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkblue"},
            "bar": {"color": "darkblue"},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "steps": [
                {"range": [0, 20], "color": "red"},
                {"range": [20, 40], "color": "orange"},
                {"range": [40, 60], "color": "yellow"},
                {"range": [60, 80], "color": "lightgreen"},
                {"range": [80, 100], "color": "green"}
            ],
        }
    ))
    
    fig.update_layout(height=400)
    
    return fig

def plot_co2_emissions(df: pd.DataFrame, title: str = "CO2 Emissions") -> go.Figure:
    """
    Create a bar chart for CO2 emissions data.
    
    Args:
        df: DataFrame with emissions data
        title: Title for the chart
        
    Returns:
        Plotly figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Format datetime if needed
    if 'datetime' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Create the figure
    fig = px.bar(
        df, 
        x="datetime", 
        y="value", 
        color="type",
        title=title,
        labels={"value": "CO2 (tCO2eq)", "datetime": "Date", "type": "Type"}
    )
    
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    return fig

def display_metric_cards(df: pd.DataFrame) -> None:
    """
    Display metric cards for key indicators.
    
    Args:
        df: DataFrame with generation data
    """
    if df.empty:
        st.warning("No data available for metrics")
        return
    
    from reepi.utils.data_processing import calculate_renewable_percentage
    
    # Get the latest data point for each type
    latest_data = df.sort_values('datetime').groupby('type').last().reset_index()
    
    # Calculate total generation
    total_generation = latest_data['value'].sum()
    
    # Calculate renewable percentage
    renewable_pct = calculate_renewable_percentage(latest_data)
    
    # Set up columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Generation",
            value=f"{total_generation:.1f} MW"
        )
    
    with col2:
        st.metric(
            label="Renewable Generation",
            value=f"{renewable_pct:.1f}%"
        )
    
    # Find the largest source
    if not latest_data.empty:
        max_source = latest_data.loc[latest_data['value'].idxmax()]
        with col3:
            st.metric(
                label="Largest Source",
                value=f"{max_source['type']}: {max_source['value']:.1f} MW"
            )
