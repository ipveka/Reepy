# Ree-Py

A Python package to fetch and visualize electricity data from the Spanish Electricity Network (Red Eléctrica de España) e·sios API.

## Overview

Ree-Py is a production-ready Python package that connects to the e·sios API provided by Red Eléctrica de España (REE) to retrieve and analyze data related to electricity production, consumption, prices, and more. With Ree-Py, you can easily access over 1,000 indicators in the Spanish electricity system and process them for analysis or visualization.

The package also includes a Streamlit application for interactive visualization of the data.

## Features

- Access the full range of e·sios API indicators (1,000+ available indicators)
- Retrieve electricity data including:
  - Electricity prices (PVPC, daily market, etc.)
  - Electricity demand (actual, forecasted, programmed)
  - Generation by source (hydro, wind, solar, nuclear, etc.)
  - CO2 emissions data
- Process data into easy-to-use pandas DataFrames
- Apply time aggregations (hourly, daily, monthly)
- Interactive data visualization with Streamlit
- Export data to CSV or Excel formats

## Installation

```bash
# Clone the repository
git clone https://github.com/ipveka/Reepy.git
cd Reepy

# Install the package and dependencies
pip install -e .
```

## API Token

To use the e·sios API, you need to obtain a personal API token. Follow these steps:

1. Visit the [e·sios website](https://api.esios.ree.es/)
2. Click on "Personal token request" and follow the process to request a token
3. Once you receive your token via email, you can use it with Ree-Py

Store your token in a `.env` file in the project root:

```
REE_API_TOKEN="your_api_token_here"
```

## Usage

### Running the Streamlit Application

```bash
# Navigate to the project directory
cd Reepy

# Start the Streamlit app
streamlit run reepi/app.py
```

### Using the API Client

```python
from reepi.api.client import REEClient
import pandas as pd
from datetime import datetime, timedelta

# Initialize the client
client = REEClient()  # Will read token from .env file
# or specify directly: client = REEClient(api_token="your_token_here")

# Get a list of all available indicators
indicators = client.get_all_indicators()
print(f"Found {len(indicators)} indicators")

# Get real-time generation mix data for today
real_time_data = client.get_real_time_data()

# Convert to DataFrame
df = client.to_dataframe(real_time_data)
print(df.head())

# Get hydro generation data for the last month
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
hydro_data = client.get_hydro_generation(
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d"),
    group_by="day"
)

# Get electricity prices for specific dates
prices = client.get_electricity_prices(
    start_date="2023-01-01", 
    end_date="2023-01-07",
    group_by="hour"
)

# Convert to DataFrame and analyze
prices_df = client.to_dataframe(prices)
daily_avg = prices_df.groupby(prices_df['datetime'].dt.date)['value'].mean()
print("Daily average prices:", daily_avg)
```

### Common Indicators

The REEClient provides convenient methods for accessing commonly used indicators:

| Method | Description | Indicator ID |
|--------|-------------|--------------|
| `get_hydro_generation()` | Hydro UGH generation data | 1 |
| `get_electricity_prices()` | PVPC electricity prices | 1013 |
| `get_demand_data()` | Actual electricity demand | 1293 |
| `get_generation_mix()` | Generation mix by technology | 1125 |
| `get_co2_emissions()` | CO2 emissions data | 10033 |

For other indicators, use the generic method:

```python
# Get data for any indicator by ID
indicator_id = 600  # Daily market price
data = client.get_indicator_values(
    indicator_id=indicator_id,
    start_date="2023-01-01",
    end_date="2023-01-31",
    group_by="day"
)
```

## API Documentation

### REEClient Methods

#### General Methods

- `get_all_indicators()`: Get a list of all available indicators
- `get_indicator(indicator_id)`: Get details for a specific indicator 
- `get_indicator_values(indicator_id, start_date, end_date, group_by, geo_ids)`: Get data for any indicator
- `to_dataframe(data)`: Convert API response to pandas DataFrame

#### Convenience Methods

- `get_real_time_data()`: Get real-time generation mix data
- `get_hydro_generation(start_date, end_date, group_by)`: Get hydro generation data
- `get_electricity_prices(start_date, end_date, group_by)`: Get electricity prices
- `get_demand_data(start_date, end_date, group_by)`: Get demand data
- `get_generation_mix(start_date, end_date, group_by)`: Get generation mix by technology
- `get_co2_emissions(start_date, end_date, group_by)`: Get CO2 emissions data

### Parameters

- `start_date`: Start date in format "YYYY-MM-DD"
- `end_date`: End date in format "YYYY-MM-DD"
- `group_by`: Time aggregation ('hour', 'day', 'month', 'year')
- `geo_ids`: Geographic zone IDs (default is peninsular Spain)

### Geographic Zones

- Spain Peninsula: 8741
- Canary Islands: 8742
- Balearic Islands: 8743
- Ceuta: 8744
- Melilla: 8745

## Official API Information

For detailed documentation on the e·sios API, visit [https://api.esios.ree.es/](https://api.esios.ree.es/). The API follows REST conventions and requires a personal token for authentication.

**Authentication Headers:**
```
Host: api.esios.ree.es
x-api-key: YOUR_TOKEN
```

## Troubleshooting

### Common Issues

- **403 Forbidden**: This usually means your API token is invalid or has expired. Request a new token from e·sios.
- **Missing Data**: Some indicators may not have data for certain dates. Try broadening your date range.
- **Token Request Delay**: When you request a token, it may take some time to receive it by email.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
