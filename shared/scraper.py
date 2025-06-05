import logging
# from shared.sources import upwork # Upwork is disabled due to persistent 403 errors
from shared.sources import alljobs
# from shared.sources import fiverr # Fiverr is disabled due to persistent 403 errors
# from shared.sources import jobmaster # JobMaster is disabled due to persistent 404 errors
from shared.sources import janglo
from shared.email_sender import send_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
EMAIL_RECIPIENTS = ["your_email@example.com"] # REPLACE WITH YOUR EMAIL
SCRAPE_TERMS = [
    # English terms (for platforms like Fiverr, and potentially international listings)
    "english hebrew translation",
    "english to hebrew translator",
    "hebrew translation",
    "english hebrew song translation",
    "song translation hebrew",
    "music translation hebrew",
    "piano recording",
    "pianist recording",
    "piano session musician",
    "vocal recording",
    "vocalist recording",
    "singer recording",
    "voice recording",
    
    # Hebrew terms (CRUCIAL for Israeli platforms like AllJobs, Janglo, XPlace, Freelancerim)
    "תרגום אנגלית עברית",
    "מתרגם מאנגלית לעברית",
    "תרגום שירים",
    "תרגום שירים לאנגלית",
    "תרגום שירים לעברית",
    "מתרגם שירים",
    "הקלטת פסנתר",
    "פסנתרן לליווי",
    "פסנתרן להקלטות",
    "הקלטת שירה",
    "הקלטת קולות שניים",
    "הרמוניות שירה",
    "זמר לאולפן",
    "זמרת לאולפן"
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

        # --- AllJobs Scraping ---
        logging.info(f"  Scraping 'alljobs.co.il' for term: '{term}'")
        alljobs_jobs = alljobs.scrape_alljobs(term)
        logging.info(f"    Found {len(alljobs_jobs)} raw jobs from alljobs.co.il for '{term}'")
        all_found_jobs.extend(alljobs_jobs)

        # --- Janglo Scraping ---
        logging.info(f"  Scraping 'janglo.net' for term: '{term}'")
        janglo_jobs = janglo.scrape_janglo(term)
        logging.info(f"    Found {len(janglo_jobs)} raw jobs from janglo.net for '{term}'")
        all_found_jobs.extend(janglo_jobs)

        # Note: Upwork, Fiverr, and JobMaster are temporarily disabled due to persistent scraping issues.
        # If you'd like to re-enable them in the future, we may need to explore more advanced
        # scraping techniques (e.g., headless browsers) or debug their specific site structures.

    logging.info(f"Total jobs found across all sources and terms: {len(all_found_jobs)}")

    if all_found_jobs:
        email_body_html = "<h1>New Job Postings Found:</h1><ul>"
        for job in all_found_jobs:
            # Ensuring the link is present before creating the anchor tag
            job_link_html = f"<a href='{job['link']}'>{job['title']}</a>" if job.get('link') else job['title']
            email_body_html += f"<li>{job_link_html}<br>{job['description'][:200]}...</li>"
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

if __name__ == '__main__':
    logging.info("Running scraper manually (for testing purposes).")
    run_scraper_and_email()
