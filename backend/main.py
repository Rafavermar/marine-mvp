# backend/main.py
from fastapi import FastAPI, HTTPException
from typing import List

from datetime import datetime, time
from faker import Faker
from contextlib import asynccontextmanager

from backend.database import db
from backend.models import PriceQuery, PriceResponse, OccupancyQuery
from scraper.run_scrapers import run_all_scrapers  # relative import if needed
# from .scheduler import start_scheduler
app = FastAPI()
fake = Faker()


# @app.on_event("startup")
# def startup_event():
#    start_scheduler()



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    1) Each time the server starts, re-run scrapers.
    2) Insert fresh data into MongoDB, replacing older data.
    (Alternatively, you can use an APScheduler job for daily scraping.)
    """
    # SCRAPE
    items = run_all_scrapers()

    # CLEAR collection
    db.pricing.delete_many({})  # reset
    # INSERT
    if items:
        db.pricing.insert_many(items)

    # Generate mock occupancy
    db.occupancy.delete_many({})
    mock_data = []
    for _ in range(50):
        random_date = fake.date_between(start_date="-1M", end_date="+1M")
        random_datetime = datetime.combine(random_date, time(0, 0, 0))  # medianoche
        record = {
            "port_name": "Puerto Benalmadena" if fake.boolean(chance_of_getting_true=50) else "Puerto Marbella",
            "date": random_datetime,
            "boat_length": fake.random_int(min=5, max=30),
            "available": fake.boolean(chance_of_getting_true=70)  # ~70% chance free
        }
        mock_data.append(record)
    db.occupancy.insert_many(mock_data)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/calculate_price", response_model=PriceResponse)
def calculate_price(query: PriceQuery):
    """
    Find the appropriate pricing from the 'pricing' collection
    and compute total cost from arrival_date to departure_date.
    """
    # 1) Find relevant record(s)
    # Some websites store a single row per "range" of boat lengths
    # We'll look for a record that includes "port_name" and range
    # that can handle query.boat_length
    pipeline = [
        {"$match": {
            "port_name": query.port_name,
            "boat_length_min": {"$lte": query.boat_length},
            "boat_length_max": {"$gte": query.boat_length}
        }}
    ]
    docs = list(db.pricing.aggregate(pipeline))

    if not docs:
        raise HTTPException(status_code=404, detail="No pricing found for given criteria")

    doc = docs[0]  # assume only 1 relevant doc

    total_days = (query.departure_date - query.arrival_date).days
    if total_days < 1:
        total_days = 1  # If same-day, let's treat as 1 day

    # Decide if the date is in "low" or "high" season
    # For demonstration, let's consider:
    #   May - Sept => high
    #   otherwise => low
    # More advanced logic might break it up day by day if crossing months
    # but let's keep it simple:

    # We'll do a naive approach: check the arrival month only
    arrival_month = query.arrival_date.month
    if 5 <= arrival_month <= 9:
        daily_rate = doc["price_high_season"]
    else:
        daily_rate = doc["price_low_season"]

    # Add electricity / water if the user wants them and if not already included
    additional_cost = 0.0
    detail_info = f"Base daily rate: {daily_rate} x {total_days} days = {daily_rate * total_days}"

    # For simplicity, let's say each is +10 if not included
    # In real usage, parse from doc or a separate field
    if query.want_electricity and not doc["electricity_included"]:
        additional_cost += 10.0
        detail_info += " +10 for electricity"

    if query.want_water and not doc["water_included"]:
        additional_cost += 5.0
        detail_info += " +5 for water"

    total_cost = (daily_rate * total_days) + additional_cost

    # Check IVA if needed
    # doc["iva_included"] (boolean)
    # If not included, we might add e.g. 21%:
    if not doc["iva_included"]:
        total_cost *= 1.21
        detail_info += " (incl 21% IVA)"

    detail_info += f" = {total_cost:.2f}"

    return PriceResponse(
        total_price=round(total_cost, 2),
        detail=detail_info
    )

@app.post("/check_occupancy")
def check_occupancy(query: OccupancyQuery):
    """
    Return a mock monthly calendar with availability for that port & length.
    Just for demonstration, we return random data from the 'occupancy' collection.
    """
    # Filter in the next 30 days
    now = datetime.now().date()
    thirty_days_later = now.replace(day=now.day)  # naive approach but let's do a small range
    # We'll do a bigger range
    pipeline = [
        {"$match": {
            "port_name": query.port_name,
            "boat_length": {"$gte": query.boat_length - 2, "$lte": query.boat_length + 2}
        }},
        {"$project": {
            "_id": 0,
            "port_name": 1,
            "date": 1,
            "boat_length": 1,
            "available": 1
        }}
    ]
    docs = list(db.occupancy.aggregate(pipeline))

    # For demonstration, return them as is
    return docs

