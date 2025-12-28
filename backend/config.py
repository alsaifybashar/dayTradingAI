import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
# Assuming .env is in the parent directory of 'backend' or in 'backend' itself. 
# We'll look in common locations.
load_dotenv()

class Config:
    POLYGON_IO_API_KEY = os.environ.get('POLYGON_IO_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    USE_MOCK_DATA = os.environ.get('USE_MOCK_DATA', 'False').lower() == 'true'
    
    # Add other keys here as needed
    # NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

config = Config()
