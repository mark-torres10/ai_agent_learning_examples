import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('../.env')

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
