from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date, timedelta
import logging

from fetcher import FlightFetcher, NUM_GROUPS
from database import FlightDatabase
from airports import AIRPORTS
from config import FETCH_INTERVAL_HOURS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_fetch():
    db = FlightDatabase()
    fetcher = FlightFetcher()

    run_id = db.start_fetch_run()
    logger.info(f"Starting full fetch run {run_id}")

    try:
        db.upsert_airports(AIRPORTS)

        flights = fetcher.fetch_all_routes(
            start_date=date.today() + timedelta(days=1)
        )

        inserted = db.insert_flights(flights)

        db.complete_fetch_run(
            run_id=run_id,
            flights_found=inserted,
            routes_fetched=fetcher.api_calls_used,
            api_calls=fetcher.api_calls_used,
            errors=fetcher.errors,
        )

        db.cleanup_old_flights()

        logger.info(f"Fetch run {run_id} complete: {inserted} flights stored")

    except Exception as e:
        logger.error(f"Fetch run {run_id} failed: {e}")
        db.fail_fetch_run(run_id, [str(e)])
        raise


def run_fetch_group(group_index: int):
    db = FlightDatabase()
    fetcher = FlightFetcher()

    from airports import DOMESTIC_ROUTES
    from fetcher import get_route_group

    routes = get_route_group(group_index)
    run_id = db.start_fetch_run()
    logger.info(f"Starting group {group_index} fetch run {run_id} ({len(routes)} routes)")

    try:
        db.upsert_airports(AIRPORTS)

        flights = fetcher.fetch_routes(
            routes,
            start_date=date.today() + timedelta(days=1)
        )

        inserted = db.insert_flights(flights)

        db.complete_fetch_run(
            run_id=run_id,
            flights_found=inserted,
            routes_fetched=len(routes),
            api_calls=fetcher.api_calls_used,
            errors=fetcher.errors,
        )

        db.cleanup_old_flights()

        logger.info(f"Group {group_index} run {run_id} complete: {inserted} flights stored")

    except Exception as e:
        logger.error(f"Group {group_index} run {run_id} failed: {e}")
        db.fail_fetch_run(run_id, [str(e)])
        raise


def start_scheduler():
    scheduler = BlockingScheduler()

    scheduler.add_job(
        run_fetch,
        "interval",
        hours=FETCH_INTERVAL_HOURS,
        id="flight_fetch",
        name="Fetch cheap Malaysian domestic flights",
        max_instances=1,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        run_fetch,
        id="initial_fetch",
        name="Initial fetch on startup",
    )

    logger.info(f"Scheduler started, fetching every {FETCH_INTERVAL_HOURS} hours")
    scheduler.start()
