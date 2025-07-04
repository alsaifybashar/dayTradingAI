# Source: Polygon.io

from dotenv import load_dotenv
import os
import requests

# Load the environment variables from .env file
load_dotenv()

API_KEY= os.environ.get('POLYGON_IO_API_KEY')

url = (
    'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-06-01/2025-06-30'
    f'?adjusted=true&sort=asc&apiKey=' + API_KEY
)

response = requests.get(url)
data = response.json()

print(data)