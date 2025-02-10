# backend/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from scraper.run_scrapers import run_all_scrapers
from .database import db
from datetime import datetime

def scheduled_job():
    items = run_all_scrapers()
    if items:
        db.pricing.delete_many({})
        db.pricing.insert_many(items)
    print(f"[{datetime.now()}] Scraper job done.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_job, 'cron', hour=2)  # 2 AM every day
    scheduler.start()
