import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the same directory as this config file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Config:
    POLYGON_IO_API_KEY = os.environ.get('POLYGON_IO_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    # Add other keys here as needed
    # NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

config = Config()
