from apscheduler.schedulers.background import BackgroundScheduler
import os
import pytz
import logging
import time

# Import the main scraper function
from shared.scraper import run_scraper_and_email

# Set up logging for the worker service
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start_scheduler():
    """
    Initializes and starts the APScheduler to run the scraping task.
    Schedules runs for 08:00 AM and 18:00 PM IDT.
    """
    # Use 'Asia/Jerusalem' for Israel time
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Jerusalem'))

    # Schedule the job to run twice daily: 08:00 and 18:00
    logging.info("Scheduling job bot to run daily at 08:00 AM and 18:00 PM IDT...")
    scheduler.add_job(run_scraper_and_email, 'cron', hour=8, minute=0, id='morning_run', misfire_grace_time=600)
    scheduler.add_job(run_scraper_and_email, 'cron', hour=18, minute=0, id='evening_run', misfire_grace_time=600)

    scheduler.start()
    logging.info("Scheduler started. Waiting for scheduled runs...")

    # Keep the worker process alive indefinitely
    try:
        while True:
            time.sleep(2) # Keep the main thread alive
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler shutting down due to interrupt.")
        scheduler.shutdown()
    except Exception as e:
        logging.error(f"Worker main loop error: {e}", exc_info=True)
        scheduler.shutdown()

if __name__ == '__main__':
    logging.info("Worker service starting up.")
    # For local development, load .env variables
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        logging.info("Loaded environment variables from .env file (for local development).")

    start_scheduler()
