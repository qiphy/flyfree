from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
import logging

logger = logging.getLogger(__name__)


class FlightDatabase:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    def upsert_airports(self, airports: dict):
        records = [
            {"iata_code": code, "name": info["name"],
             "city": info["city"], "state": info.get("state", "")}
            for code, info in airports.items()
        ]
        self.client.table("airports").upsert(
            records, on_conflict="iata_code"
        ).execute()
        logger.info(f"Upserted {len(records)} airports")

    def insert_flights(self, flights: list[dict]) -> int:
        if not flights:
            return 0

        inserted = 0
        for i in range(0, len(flights), 100):
            batch = flights[i:i + 100]
            try:
                self.client.table("flights").upsert(
                    batch,
                    on_conflict="flight_number,flight_date,origin,destination,price_myr"
                ).execute()
                inserted += len(batch)
            except Exception as e:
                logger.error(f"Batch insert failed: {e}")
                for flight in batch:
                    try:
                        self.client.table("flights").upsert(
                            [flight],
                            on_conflict="flight_number,flight_date,origin,destination,price_myr"
                        ).execute()
                        inserted += 1
                    except Exception as e2:
                        logger.warning(f"Single insert failed for {flight.get('flight_number')}: {e2}")

        logger.info(f"Inserted/updated {inserted} flights")
        return inserted

    def start_fetch_run(self) -> str:
        result = self.client.table("fetch_runs").insert({
            "status": "running"
        }).execute()
        return result.data[0]["id"]

    def complete_fetch_run(self, run_id: str, flights_found: int,
                           routes_fetched: int, api_calls: int, errors: list[str]):
        self.client.table("fetch_runs").update({
            "status": "completed",
            "completed_at": "now()",
            "flights_found": flights_found,
            "routes_fetched": routes_fetched,
            "api_calls_used": api_calls,
            "errors": errors[:20],
        }).eq("id", run_id).execute()

    def fail_fetch_run(self, run_id: str, errors: list[str]):
        self.client.table("fetch_runs").update({
            "status": "failed",
            "completed_at": "now()",
            "errors": errors[:20],
        }).eq("id", run_id).execute()

    def cleanup_old_flights(self, days: int = 7):
        from datetime import date, timedelta
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        self.client.table("flights").delete().lt("flight_date", cutoff).execute()
        logger.info(f"Cleaned up flights older than {cutoff}")
