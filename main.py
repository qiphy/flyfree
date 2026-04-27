import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser(description="FlyFree - Cheap Malaysian flight finder")
    parser.add_argument("--once", action="store_true", help="Run fetch once (all routes) and exit")
    parser.add_argument("--group", type=int, help="Fetch only route group (0-6) and exit")
    parser.add_argument("--schedule", action="store_true", help="Start scheduled fetching")
    parser.add_argument("--seed", action="store_true", help="Seed airports table only")
    args = parser.parse_args()

    if args.seed:
        from database import FlightDatabase
        from airports import AIRPORTS
        db = FlightDatabase()
        db.upsert_airports(AIRPORTS)
        print("Airports seeded.")

    elif args.group is not None:
        from scheduler import run_fetch_group
        run_fetch_group(args.group)

    elif args.once:
        from scheduler import run_fetch
        run_fetch()

    elif args.schedule:
        from scheduler import start_scheduler
        start_scheduler()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
