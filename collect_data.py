# Source: Polygon.io

from dotenv import load_dotenv
import requests
import time
import json
import os


# Load the environment variables from .env file
load_dotenv()
API_KEY= os.environ.get('POLYGON_IO_API_KEY')




with open("acronyms.txt") as f:
    for line in f:
        stock = line.strip()
        print(f"Fetching: {stock}")
        url = (
            f'https://api.polygon.io/v2/aggs/ticker/{stock}/range/1/day/2020-06-01/2025-07-05'
            f'?adjusted=true&sort=asc&apiKey={API_KEY}'
        )
        response = requests.get(url)
        data = response.json()
        print(data)
        output_file = f"output_files/{stock}_STOCK.json"
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)
        time.sleep(15)  # delay to avoid rate limits
        