import os
from dotenv import load_dotenv

load_dotenv()

# SerpAPI (Google Flights)
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Fetch settings
MAX_PRICE_MYR = float(os.environ.get("MAX_PRICE_MYR", "50"))
SEARCH_DAYS_AHEAD = int(os.environ.get("SEARCH_DAYS_AHEAD", "15"))
FETCH_INTERVAL_HOURS = int(os.environ.get("FETCH_INTERVAL_HOURS", "6"))
