import os
import json
import requests
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables (VERBWIRE_API_KEY, etc.)
load_dotenv()
VERBWIRE_API_KEY = os.getenv("VERBWIRE_API_KEY")

VERBWIRE_BASE_URL = "https://api.verbwire.com/v1"