"""p2j notebooks/reepy_example_notebook.py -o notebooks/reepy_example.ipynb
REEpy - Data Visualization Example

This script demonstrates how to use the REEpy package to fetch and visualize 
electricity data from Red Eléctrica Española (REE).
All outputs are saved to the 'outputs' folder.
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
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

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

# ===== 1. Fetching Electricity Generation Mix Data =====
print("\n1. Fetching Electricity Generation Mix Data")

# Define date range with historical data (2023)
end_date = datetime(2023, 12, 31)  # Use a date in 2023
start_date = end_date - timedelta(days=7)

# Format dates for API
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

print(f"Fetching data from {start_date_str} to {end_date_str}")

# Fetch generation mix data
generation_data = client.get_generation_mix(start_date_str, end_date_str, "hour")

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
print(generation_df.head())

# Save the data to CSV
generation_csv_path = os.path.join(outputs_dir, 'generation_data.csv')
generation_df.to_csv(generation_csv_path, index=False)
print(f"Generation data saved to {generation_csv_path}")

# ===== 2. Visualizing Generation Mix =====
print("\n2. Visualizing Generation Mix")

# Since we only have 'total' type in the current API response, 
# we'll create a simple line chart instead of a stacked area chart

# Create a line chart for total generation
plt.figure(figsize=(14, 6))
plt.plot(generation_df['datetime'], generation_df['value'], 'b-', linewidth=2)
plt.title('Total Electricity Generation (Past Week)')
plt.xlabel('Date')
plt.ylabel('Production (MW)')
plt.grid(True)
plt.tight_layout()

# Save the plot to the outputs directory
total_generation_path = os.path.join(outputs_dir, 'total_generation.png')
plt.savefig(total_generation_path)
print(f"Created visualization: {total_generation_path}")

# ===== 3. Fetching Electricity Demand Data =====
print("\n3. Fetching Electricity Demand Data")

# For demonstration, let's fetch demand data for the same period
try:
    # Get demand indicator ID from the client
    demand_indicator_id = client.INDICATORS.get('demand_actual', 1293)
    
    # Fetch demand data
    demand_data = client.get_indicator_values(
        demand_indicator_id, 
        start_date=start_date_str, 
        end_date=end_date_str,
        group_by="hour"
    )
    
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
    
    if not demand_df.empty:
        # Format datetime column
        demand_df['datetime'] = pd.to_datetime(demand_df['datetime'])
        
        # Display the first few rows
        print("\nDemand Data (first 5 rows):")
        print(demand_df.head())
        
        # Save the data to CSV
        demand_csv_path = os.path.join(outputs_dir, 'demand_data.csv')
        demand_df.to_csv(demand_csv_path, index=False)
        print(f"Demand data saved to {demand_csv_path}")
        
        # Create a line chart for demand
        plt.figure(figsize=(14, 6))
        plt.plot(demand_df['datetime'], demand_df['value'], 'r-', linewidth=2)
        plt.title('Electricity Demand (Past Week)')
        plt.xlabel('Date')
        plt.ylabel('Demand (MW)')
        plt.grid(True)
        plt.tight_layout()
        
        # Save the plot to the outputs directory
        demand_path = os.path.join(outputs_dir, 'demand.png')
        plt.savefig(demand_path)
        print(f"Created visualization: {demand_path}")
    else:
        print("No demand data available for the selected period.")
except Exception as e:
    print(f"Error fetching demand data: {e}")

# ===== 4. Fetching Electricity Price Data =====
print("\n4. Fetching Electricity Price Data")

try:
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
    
    if not price_df.empty:
        # Format datetime column
        price_df['datetime'] = pd.to_datetime(price_df['datetime'])
        
        # Display the first few rows
        print("\nPrice Data (first 5 rows):")
        print(price_df.head())
        
        # Save the data to CSV
        price_csv_path = os.path.join(outputs_dir, 'price_data.csv')
        price_df.to_csv(price_csv_path, index=False)
        print(f"Price data saved to {price_csv_path}")
        
        # Create a line chart for price
        plt.figure(figsize=(14, 6))
        plt.plot(price_df['datetime'], price_df['value'], 'g-', linewidth=2)
        plt.title('Electricity Price (Past Week)')
        plt.xlabel('Date')
        plt.ylabel('Price (€/MWh)')
        plt.grid(True)
        plt.tight_layout()
        
        # Save the plot to the outputs directory
        price_path = os.path.join(outputs_dir, 'price.png')
        plt.savefig(price_path)
        print(f"Created visualization: {price_path}")
    else:
        print("No price data available for the selected period.")
except Exception as e:
    print(f"Error fetching price data: {e}")

# ===== 5. Combined Visualization =====
print("\n5. Creating Combined Visualization")

try:
    # Create a combined visualization if we have multiple datasets
    datasets_available = []
    
    if not generation_df.empty:
        datasets_available.append('generation')
    
    if 'demand_df' in locals() and not demand_df.empty:
        datasets_available.append('demand')
    
    if 'price_df' in locals() and not price_df.empty:
        datasets_available.append('price')
    
    if len(datasets_available) > 1:
        # Create a figure with multiple y-axes
        fig, ax1 = plt.subplots(figsize=(16, 8))
        
        # Plot generation data on the first axis
        color = 'tab:blue'
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Generation (MW)', color=color)
        ax1.plot(generation_df['datetime'], generation_df['value'], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        
        # Create a second axis for demand if available
        if 'demand' in datasets_available:
            ax2 = ax1.twinx()
            color = 'tab:red'
            ax2.set_ylabel('Demand (MW)', color=color)
            ax2.plot(demand_df['datetime'], demand_df['value'], color=color)
            ax2.tick_params(axis='y', labelcolor=color)
        
        # Create a third axis for price if available
        if 'price' in datasets_available and len(datasets_available) > 2:
            ax3 = ax1.twinx()
            # Offset the right spine of ax3
            ax3.spines['right'].set_position(('outward', 60))
            color = 'tab:green'
            ax3.set_ylabel('Price (€/MWh)', color=color)
            ax3.plot(price_df['datetime'], price_df['value'], color=color)
            ax3.tick_params(axis='y', labelcolor=color)
        
        # Add a title
        plt.title('Combined Electricity Data (Past Week)')
        fig.tight_layout()
        
        # Save the plot to the outputs directory
        combined_path = os.path.join(outputs_dir, 'combined_data.png')
        plt.savefig(combined_path)
        print(f"Created visualization: {combined_path}")
    else:
        print("Not enough datasets available for combined visualization.")
except Exception as e:
    print(f"Error creating combined visualization: {e}")

# ===== 6. Save API Response for Reference =====
print("\n6. Saving API Response for Reference")

# Save the raw API responses for reference
api_responses = {
    'generation_data': generation_data
}

if 'demand_data' in locals():
    api_responses['demand_data'] = demand_data

if 'price_data' in locals():
    api_responses['price_data'] = price_data

api_response_path = os.path.join(outputs_dir, 'api_responses.json')
with open(api_response_path, 'w') as f:
    json.dump(api_responses, f, indent=2)
print(f"API responses saved to {api_response_path}")

print("\nScript execution completed successfully!")
print(f"All outputs have been saved to the '{outputs_dir}' directory.")
