"""
Streamlit application for REEpy - Spanish Electricity Data Visualization.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from typing import Dict, Any, Optional

from reepi.api.client import REEClient
from reepi.utils.data_processing import (
    format_datetime, 
    calculate_renewable_percentage,
    aggregate_by_type,
    calculate_daily_average,
    extract_time_series
)
from reepi.visualizations.charts import (
    plot_generation_mix,
    plot_price_comparison,
    plot_demand_curve,
    plot_renewable_percentage,
    plot_co2_emissions,
    display_metric_cards
)
from reepi.utils.logger import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="REEpy - Spanish Electricity Data",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application title
st.title("⚡ REEpy - Spanish Electricity Data Visualization")
st.markdown("""
This application provides real-time and historical data about electricity production, 
consumption, and prices in Spain using data from Red Eléctrica Española (REE).
""")

# Initialize API client
@st.cache_resource
def get_client():
    return REEClient()

client = get_client()

# Sidebar for controls
st.sidebar.title("Controls")

# Date range selector
st.sidebar.subheader("Date Range")
today = datetime.now().date()
default_start_date = today - timedelta(days=7)

start_date = st.sidebar.date_input(
    "Start Date",
    value=default_start_date,
    max_value=today
)

end_date = st.sidebar.date_input(
    "End Date",
    value=today,
    min_value=start_date,
    max_value=today
)

# Time aggregation selector
time_trunc_options = {
    "Hourly": "hour",
    "Daily": "day",
    "Monthly": "month",
    "Yearly": "year"
}

time_trunc = st.sidebar.selectbox(
    "Time Aggregation",
    options=list(time_trunc_options.keys()),
    index=1  # Default to daily
)

time_trunc_value = time_trunc_options[time_trunc]

# Data type selector
data_type = st.sidebar.selectbox(
    "Data Type",
    options=["Generation Mix", "Electricity Prices", "Demand", "CO2 Emissions", "Dashboard"],
    index=4  # Default to Dashboard
)

# Format dates for API
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Function to load data based on selection
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(data_type, start_date, end_date, time_trunc):
    try:
        if data_type == "Generation Mix":
            data = client.get_generation_mix(start_date, end_date, time_trunc)
            df = client.parse_generation_data(data)
            return format_datetime(df)
        
        elif data_type == "Electricity Prices":
            data = client.get_electricity_prices(start_date, end_date, time_trunc)
            df = client.parse_price_data(data)
            return format_datetime(df)
        
        elif data_type == "Demand":
            data = client.get_demand_data(start_date, end_date, time_trunc)
            df = extract_time_series(data)
            return format_datetime(df)
        
        elif data_type == "CO2 Emissions":
            data = client.get_co2_emissions(start_date, end_date, time_trunc)
            df = extract_time_series(data)
            return format_datetime(df)
        
        elif data_type == "Dashboard":
            # Load all data types for dashboard
            gen_data = client.get_generation_mix(start_date, end_date, time_trunc)
            gen_df = format_datetime(client.parse_generation_data(gen_data))
            
            price_data = client.get_electricity_prices(start_date, end_date, time_trunc)
            price_df = format_datetime(client.parse_price_data(price_data))
            
            demand_data = client.get_demand_data(start_date, end_date, time_trunc)
            demand_df = format_datetime(extract_time_series(demand_data))
            
            return {
                "generation": gen_df,
                "prices": price_df,
                "demand": demand_df
            }
        
        return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"Error loading data: {e}")
        return pd.DataFrame() if data_type != "Dashboard" else {}

# Load data
with st.spinner("Loading data from REE API..."):
    data = load_data(data_type, start_date_str, end_date_str, time_trunc_value)

# Display data based on selection
if data_type == "Generation Mix":
    if not data.empty:
        st.subheader("Electricity Generation Mix")
        fig = plot_generation_mix(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show renewable percentage
        st.subheader("Renewable Energy Percentage")
        renewable_fig = plot_renewable_percentage(data)
        st.plotly_chart(renewable_fig, use_container_width=True)
        
        # Display data table
        with st.expander("View Data Table"):
            st.dataframe(data)
        
        # Download button
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"generation_mix_{start_date_str}_to_{end_date_str}.csv",
            mime="text/csv",
        )
    else:
        st.warning("No generation mix data available for the selected period.")

elif data_type == "Electricity Prices":
    if not data.empty:
        st.subheader("Electricity Prices")
        fig = plot_price_comparison(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display data table
        with st.expander("View Data Table"):
            st.dataframe(data)
        
        # Download button
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"electricity_prices_{start_date_str}_to_{end_date_str}.csv",
            mime="text/csv",
        )
    else:
        st.warning("No price data available for the selected period.")

elif data_type == "Demand":
    if not data.empty:
        st.subheader("Electricity Demand")
        fig = plot_demand_curve(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display data table
        with st.expander("View Data Table"):
            st.dataframe(data)
        
        # Download button
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"electricity_demand_{start_date_str}_to_{end_date_str}.csv",
            mime="text/csv",
        )
    else:
        st.warning("No demand data available for the selected period.")

elif data_type == "CO2 Emissions":
    if not data.empty:
        st.subheader("CO2 Emissions")
        fig = plot_co2_emissions(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display data table
        with st.expander("View Data Table"):
            st.dataframe(data)
        
        # Download button
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"co2_emissions_{start_date_str}_to_{end_date_str}.csv",
            mime="text/csv",
        )
    else:
        st.warning("No CO2 emissions data available for the selected period.")

elif data_type == "Dashboard":
    if data:
        st.subheader("Spanish Electricity Dashboard")
        
        # Display metrics if generation data is available
        if not data["generation"].empty:
            display_metric_cards(data["generation"])
        
        # Create a 2x2 grid for the charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Generation Mix
            if not data["generation"].empty:
                gen_fig = plot_generation_mix(data["generation"], "Generation Mix")
                st.plotly_chart(gen_fig, use_container_width=True)
            else:
                st.warning("No generation data available.")
                
            # Demand
            if not data["demand"].empty:
                demand_fig = plot_demand_curve(data["demand"], "Electricity Demand")
                st.plotly_chart(demand_fig, use_container_width=True)
            else:
                st.warning("No demand data available.")
        
        with col2:
            # Renewable Percentage
            if not data["generation"].empty:
                renewable_fig = plot_renewable_percentage(data["generation"])
                st.plotly_chart(renewable_fig, use_container_width=True)
            else:
                st.warning("No generation data available for renewable percentage.")
                
            # Prices
            if not data["prices"].empty:
                price_fig = plot_price_comparison(data["prices"], "Electricity Prices")
                st.plotly_chart(price_fig, use_container_width=True)
            else:
                st.warning("No price data available.")
        
        # Data tables in expanders
        st.subheader("Data Tables")
        
        tab1, tab2, tab3 = st.tabs(["Generation", "Prices", "Demand"])
        
        with tab1:
            if not data["generation"].empty:
                st.dataframe(data["generation"])
                csv = data["generation"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Generation Data",
                    data=csv,
                    file_name=f"generation_{start_date_str}_to_{end_date_str}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No generation data available.")
        
        with tab2:
            if not data["prices"].empty:
                st.dataframe(data["prices"])
                csv = data["prices"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Price Data",
                    data=csv,
                    file_name=f"prices_{start_date_str}_to_{end_date_str}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No price data available.")
        
        with tab3:
            if not data["demand"].empty:
                st.dataframe(data["demand"])
                csv = data["demand"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Demand Data",
                    data=csv,
                    file_name=f"demand_{start_date_str}_to_{end_date_str}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No demand data available.")
    else:
        st.warning("Failed to load dashboard data. Please try again.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "REEpy is a Python package that connects to the Red Eléctrica Española API "
    "to retrieve and visualize electricity data."
)
st.sidebar.markdown("[View on GitHub](https://github.com/ipveka/REEpy)")

# About section
with st.sidebar.expander("About"):
    st.write(
        "This app provides real-time and historical data about electricity "
        "production, consumption, and prices in Spain using data from "
        "Red Eléctrica Española (REE)."
    )
    st.write("Data Source: [REE API](https://www.ree.es/en/apidatos)")
