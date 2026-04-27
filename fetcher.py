import requests
from datetime import date, timedelta
import time
import logging
from config import SERPAPI_KEY, MAX_PRICE_MYR, SEARCH_DAYS_AHEAD
from airports import DOMESTIC_ROUTES

logger = logging.getLogger(__name__)

BASE_URL = "https://serpapi.com/search"

# Split routes into 7 groups (one per hour on a rolling cycle)
NUM_GROUPS = 7


def get_route_group(group_index: int) -> list[tuple]:
    """Get the route subset for a given group index (0-based)."""
    return [r for i, r in enumerate(DOMESTIC_ROUTES) if i % NUM_GROUPS == group_index]


def _serpapi_get(params: dict, timeout: int = 60) -> dict | None:
    """Make a SerpAPI request with 429 backoff."""
    params["api_key"] = SERPAPI_KEY
    for attempt in range(3):
        try:
            resp = requests.get(BASE_URL, params=params, timeout=timeout)
            if resp.status_code == 429:
                wait = 10 * (attempt + 1)
                logger.warning(f"Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"SerpAPI request failed: {e}")
            if attempt < 2:
                time.sleep(5)
    return None


class FlightFetcher:
    def __init__(self):
        self.api_calls_used = 0
        self.errors = []

    def search_flights(self, origin: str, destination: str,
                       depart_date: str) -> list[dict]:
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": depart_date,
            "currency": "MYR",
            "gl": "my",
            "hl": "en",
            "adults": 1,
            "stops": 0,
            "max_price": int(MAX_PRICE_MYR),
            "type": 2,  # one-way
        }

        data = _serpapi_get(params)
        self.api_calls_used += 1

        if not data:
            self.errors.append(f"Search {origin}->{destination} on {depart_date}: no response")
            return []

        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])
        all_results = best_flights + other_flights

        return self._parse_flights(all_results, origin, destination, depart_date)

    def fetch_route(self, origin: str, destination: str,
                    start_date: date = None) -> list[dict]:
        if start_date is None:
            start_date = date.today() + timedelta(days=1)

        all_flights = []
        end_date = start_date + timedelta(days=SEARCH_DAYS_AHEAD)

        current = start_date
        while current < end_date:
            flights = self.search_flights(origin, destination, current.isoformat())
            all_flights.extend(flights)
            time.sleep(2)
            current += timedelta(days=1)

        return all_flights

    def fetch_routes(self, routes: list[tuple], start_date: date = None) -> list[dict]:
        """Fetch a subset of routes."""
        if start_date is None:
            start_date = date.today() + timedelta(days=1)

        all_flights = []
        for i, (origin, dest) in enumerate(routes):
            logger.info(f"Fetching {origin}->{dest} ({i + 1}/{len(routes)})")

            flights = self.fetch_route(origin, dest, start_date)
            all_flights.extend(flights)

            logger.info(f"  Found {len(flights)} flights under RM{MAX_PRICE_MYR}")
            time.sleep(2)

        logger.info(
            f"Fetched {len(all_flights)} cheap flights, "
            f"used {self.api_calls_used} API calls"
        )
        return all_flights

    def fetch_all_routes(self, start_date: date = None) -> list[dict]:
        """Fetch all routes (for --once full run)."""
        return self.fetch_routes(DOMESTIC_ROUTES, start_date)

    def fetch_group(self, group_index: int, start_date: date = None) -> list[dict]:
        """Fetch only the routes belonging to a group."""
        routes = get_route_group(group_index)
        logger.info(f"Fetching group {group_index} ({len(routes)} routes)")
        return self.fetch_routes(routes, start_date)

    def _parse_flights(self, flights: list, origin: str,
                       destination: str, flight_date: str) -> list[dict]:
        results = []
        for flight in flights:
            price_raw = flight.get("price", 999)
            try:
                price_myr = float(price_raw)
            except (ValueError, TypeError):
                continue

            if price_myr > MAX_PRICE_MYR:
                continue

            legs = flight.get("flights", [])
            if not legs:
                continue

            first_leg = legs[0]
            airline_code = first_leg.get("airline_code", "") or first_leg.get("airline", "")
            airline_name = first_leg.get("airline", "")
            flight_number = first_leg.get("flight_number", "")

            departure = first_leg.get("departure_airport", {})
            arrival = legs[-1].get("arrival_airport", {}) if legs else {}

            dep_time = departure.get("time", "")
            arr_time = arrival.get("time", "")

            dep_iso = f"{flight_date}T{dep_time}:00" if dep_time else ""
            arr_iso = f"{flight_date}T{arr_time}:00" if arr_time else ""

            results.append({
                "origin": origin,
                "destination": destination,
                "airline_code": airline_code,
                "airline_name": airline_name,
                "flight_number": f"{airline_code}{flight_number}" if flight_number else "",
                "departure_time": dep_iso,
                "arrival_time": arr_iso,
                "price_myr": price_myr,
                "price_original_currency": "MYR",
                "price_original_amount": price_myr,
                "booking_url": flight.get("booking_token", ""),
                "source_api": "serpapi_google_flights",
                "flight_date": flight_date,
            })

        return results
