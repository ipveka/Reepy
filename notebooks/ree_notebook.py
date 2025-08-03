"""
# REEpy - Data Visualization Example

This notebook demonstrates how to use the REEpy package to fetch and visualize 
electricity data from Red Eléctrica Española (REE).

## Setup

First, let's import the necessary libraries and initialize the REE client.
"""

# Add the Reepy project directory to the Python path
import sys
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))

# Add the project root to the Python path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create outputs directory if it doesn't exist
outputs_dir = os.path.join(project_root, 'outputs')
os.makedirs(outputs_dir, exist_ok=True)

# Import REEpy components
from reepi.api.client import REEClient
from reepi.utils.data_processing import (
    format_datetime,
    calculate_renewable_percentage,
    aggregate_by_type,
    calculate_daily_average,
    extract_time_series
)

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)

# Initialize the client
client = REEClient()
print(f"API Token loaded: {client.api_token is not None}")

"""
## 1. Fetching Electricity Generation Mix Data

Let's fetch data about the electricity generation mix for a week in December 2023.
"""

# Define date range with historical data (2023)
end_date = datetime(2023, 12, 31)  # Use a date in 2023
start_date = end_date - timedelta(days=7)

# Format dates for API
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

print(f"Fetching data from {start_date_str} to {end_date_str}")

# Fetch generation mix data
generation_data = client.get_generation_mix(start_date_str, end_date_str, "hour")

"""
### Parsing the API Response

The API response needs to be parsed into a pandas DataFrame for analysis.
"""

# Function to parse generation data
def parse_generation_data(data):
    """Parse generation data from the API response."""
    if not data or 'indicator' not in data:
        return pd.DataFrame()
        
    values = data['indicator']['values']
    
    # Prepare data for DataFrame
    records = []
    for value in values:
        datetime_str = value['datetime']
        value_data = value['value']
        
        # Handle different data structures
        if isinstance(value_data, list):
            # Original expected structure
            for gen_type in value_data:
                records.append({
                    'datetime': datetime_str,
                    'type': gen_type['type'],
                    'value': gen_type['value']
                })
        elif isinstance(value_data, (int, float)):
            # Alternative structure where value is a single number
            records.append({
                'datetime': datetime_str,
                'type': 'total',
                'value': value_data
            })
        elif isinstance(value_data, dict):
            # Alternative structure where value is a dictionary
            for type_name, type_value in value_data.items():
                records.append({
                    'datetime': datetime_str,
                    'type': type_name,
                    'value': type_value
                })
            
    return pd.DataFrame(records)

# Parse the data
generation_df = parse_generation_data(generation_data)

# Format datetime column
generation_df['datetime'] = pd.to_datetime(generation_df['datetime'])

# Display the first few rows
print("\nGeneration Mix Data (first 5 rows):")
generation_df.head()

"""
### Visualizing Generation Mix

Now let's create a visualization of the generation mix data.
"""

# Create a line chart for total generation
plt.figure(figsize=(14, 6))
plt.plot(generation_df['datetime'], generation_df['value'], 'b-', linewidth=2)
plt.title('Total Electricity Generation (Past Week)')
plt.xlabel('Date')
plt.ylabel('Production (MW)')
plt.grid(True)
plt.tight_layout()
plt.show()

"""
## 2. Fetching Electricity Demand Data

Next, let's fetch data about electricity demand for the same period.
"""

# Get demand indicator ID from the client
demand_indicator_id = client.INDICATORS.get('demand_actual', 1293)

# Fetch demand data
demand_data = client.get_indicator_values(
    demand_indicator_id, 
    start_date=start_date_str, 
    end_date=end_date_str,
    group_by="hour"
)

"""
### Parsing Indicator Data

Let's create a general function to parse indicator data from the API.
"""

# Function to parse indicator data
def parse_indicator_data(data):
    """Parse indicator data from the API response."""
    if not data or 'indicator' not in data:
        return pd.DataFrame()
        
    values = data['indicator']['values']
    
    # Prepare data for DataFrame
    records = []
    for value in values:
        records.append({
            'datetime': value['datetime'],
            'value': value['value']
        })
            
    return pd.DataFrame(records)

# Parse the demand data
demand_df = parse_indicator_data(demand_data)

# Format datetime column
demand_df['datetime'] = pd.to_datetime(demand_df['datetime'])

# Display the first few rows
print("\nDemand Data (first 5 rows):")
demand_df.head()

"""
### Visualizing Demand Data

Let's create a visualization of the demand data.
"""

# Create a line chart for demand
plt.figure(figsize=(14, 6))
plt.plot(demand_df['datetime'], demand_df['value'], 'r-', linewidth=2)
plt.title('Electricity Demand (Past Week)')
plt.xlabel('Date')
plt.ylabel('Demand (MW)')
plt.grid(True)
plt.tight_layout()
plt.show()

"""
## 3. Fetching Electricity Price Data

Now let's fetch data about electricity prices for the same period.
"""

# Get price indicator ID from the client
price_indicator_id = client.INDICATORS.get('price_daily_market', 600)

# Fetch price data
price_data = client.get_indicator_values(
    price_indicator_id, 
    start_date=start_date_str, 
    end_date=end_date_str,
    group_by="hour"
)

# Parse the price data
price_df = parse_indicator_data(price_data)

# Format datetime column
price_df['datetime'] = pd.to_datetime(price_df['datetime'])

# Display the first few rows
print("\nPrice Data (first 5 rows):")
price_df.head()

"""
### Visualizing Price Data

Let's create a visualization of the price data.
"""

# Create a line chart for price
plt.figure(figsize=(14, 6))
plt.plot(price_df['datetime'], price_df['value'], 'g-', linewidth=2)
plt.title('Electricity Price (Past Week)')
plt.xlabel('Date')
plt.ylabel('Price (€/MWh)')
plt.grid(True)
plt.tight_layout()
plt.show()

"""
## 4. Combined Visualization

Finally, let's create a combined visualization of all the data we've collected.
"""

# Create a figure with multiple y-axes
fig, ax1 = plt.subplots(figsize=(16, 8))

# Plot generation data on the first axis
color = 'tab:blue'
ax1.set_xlabel('Date')
ax1.set_ylabel('Generation (MW)', color=color)
ax1.plot(generation_df['datetime'], generation_df['value'], color=color, label='Generation')
ax1.tick_params(axis='y', labelcolor=color)

# Create a second axis for demand
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Demand (MW)', color=color)
ax2.plot(demand_df['datetime'], demand_df['value'], color=color, label='Demand')
ax2.tick_params(axis='y', labelcolor=color)

# Create a third axis for price
ax3 = ax1.twinx()
# Offset the right spine of ax3
ax3.spines['right'].set_position(('outward', 60))
color = 'tab:green'
ax3.set_ylabel('Price (€/MWh)', color=color)
ax3.plot(price_df['datetime'], price_df['value'], color=color, label='Price')
ax3.tick_params(axis='y', labelcolor=color)

# Add a title
plt.title('Combined Electricity Data (Past Week)')
fig.tight_layout()
plt.show()

"""
## 5. Saving Data to Files

Let's save our data and visualizations to files in the outputs directory.
"""

# Save the data to CSV
generation_df.to_csv(os.path.join(outputs_dir, 'generation_data.csv'), index=False)
demand_df.to_csv(os.path.join(outputs_dir, 'demand_data.csv'), index=False)
price_df.to_csv(os.path.join(outputs_dir, 'price_data.csv'), index=False)

print(f"Data files saved to {outputs_dir}")

# Save the raw API responses for reference
api_responses = {
    'generation_data': generation_data,
    'demand_data': demand_data,
    'price_data': price_data
}

with open(os.path.join(outputs_dir, 'api_responses.json'), 'w') as f:
    json.dump(api_responses, f, indent=2)

print(f"API responses saved to {os.path.join(outputs_dir, 'api_responses.json')}")

"""
## 6. Conclusion

In this notebook, we've demonstrated how to:
1. Fetch electricity generation, demand, and price data from the REE API
2. Parse and process the API responses
3. Visualize the data using matplotlib
4. Save the data and visualizations to files

The REEpy package provides a convenient interface to the REE API, making it easy to access and analyze electricity data from the Spanish electricity system.
"""
