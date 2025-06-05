import logging
from shared.sources import upwork
from shared.sources import alljobs
from shared.sources import fiverr # <-- NEW: Import the Fiverr scraper
from shared.email_sender import send_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# You can move these to environment variables later for better security and flexibility
EMAIL_RECIPIENTS = ["your_email@example.com"] # REPLACE WITH YOUR EMAIL
SCRAPE_TERMS = [
    "remote piano session",
    "piano for song",
    "midi piano recording",
    "English to Hebrew translation",
    "translate English Hebrew",
    "remote virtual assistant",
    "Python developer remote",
    "data entry clerk remote"
]

def run_scraper_and_email():
    """
    Orchestrates the scraping process, aggregates jobs, and sends email notifications.
    """
    all_found_jobs = []
    
    logging.info("Starting job scraping process...")

    # Iterate over each search term and scrape from defined sources
    for term in SCRAPE_TERMS:
        logging.info(f"Scraping for term: '{term}'")

        # --- Upwork Scraping ---
        logging.info(f"  Scraping 'upwork' for term: '{term}'")
        upwork_jobs = upwork.scrape_upwork(term)
        logging.info(f"    Found {len(upwork_jobs)} raw jobs from upwork for '{term}'")
        all_found_jobs.extend(upwork_jobs)

        # --- AllJobs Scraping ---
        logging.info(f"  Scraping 'alljobs.co.il' for term: '{term}'")
        alljobs_jobs = alljobs.scrape_alljobs(term)
        logging.info(f"    Found {len(alljobs_jobs)} raw jobs from alljobs.co.il for '{term}'")
        all_found_jobs.extend(alljobs_jobs)

        # --- Fiverr Scraping ---
        logging.info(f"  Scraping 'fiverr.com' for term: '{term}'")
        fiverr_jobs = fiverr.scrape_fiverr(term) # <-- NEW: Call the Fiverr scraper
        logging.info(f"    Found {len(fiverr_jobs)} raw gigs from fiverr.com for '{term}'")
        all_found_jobs.extend(fiverr_jobs)

        # Add other scrapers here as you implement them (e.g., jobmaster, indeed, etc.)

    logging.info(f"Total jobs found across all sources and terms: {len(all_found_jobs)}")

    if all_found_jobs:
        # Format the jobs for the email
        email_body_html = "<h1>New Job Postings Found:</h1><ul>"
        for job in all_found_jobs:
            email_body_html += f"<li><a href='{job['link']}'>{job['title']}</a><br>{job['description'][:200]}...</li>"
        email_body_html += "</ul>"
        
        subject = f"New Job Postings - {len(all_found_jobs)} jobs found!"
        
        try:
            send_email(EMAIL_RECIPIENTS, subject, email_body_html)
            logging.info(f"Email sent to {', '.join(EMAIL_RECIPIENTS)} with {len(all_found_jobs)} job postings.")
        except Exception as e:
            logging.error(f"Failed to send email: {e}", exc_info=True)
    else:
        logging.info("No new job postings found. Email not sent.")

    return all_found_jobs

# This part is typically for local testing or if you want to run it directly
if __name__ == '__main__':
    logging.info("Running scraper manually (for testing purposes).")
    run_scraper_and_email()
