# Source: Polygon.io

from dotenv import load_dotenv
import requests
import json
import os


# Load the environment variables from .env file
load_dotenv()
API_KEY= os.environ.get('POLYGON_IO_API_KEY')


output_file = "APPLE_STOCK.json"

url = (
    'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-06-01/2025-07-05'
    f'?adjusted=true&sort=asc&apiKey=' + API_KEY
)

response = requests.get(url)
data = response.json()

with open(output_file, "w") as file:
    json.dump(data, file, indent=4)

print(data)