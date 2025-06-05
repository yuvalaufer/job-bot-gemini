import datetime
import time
import logging
import pytz # For timezone

from shared.sources import upwork # Import other scrapers as you implement them
from shared.utils import is_relevant_job, remove_duplicates
from shared.emailer import send_email
from shared.config import JOB_CATEGORIES, ISRAELI_PLATFORM_TERMS

# Set up logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_scraper_and_email():
    """
    Orchestrates the scraping process, filters jobs, and sends an email report.
    """
    all_found_jobs = []
    
    # List of scraper functions to run. Add more as you implement them.
    # Each function should accept a search_term and return a list of job dicts.
    platforms_scrapers = [
        upwork.scrape_upwork,
        # freelancer.scrape_freelancer,
        # fiverr.scrape_fiverr,
        # xplace.scrape_xplace,
        # freelancerim.scrape_freelancerim,
        # alljobs.scrape_alljobs,
    ]

    logging.info("Starting scraping session...")
    
    for category_name, english_terms in JOB_CATEGORIES.items():
        logging.info(f"Processing category: '{category_name}'")

        for scraper_func in platforms_scrapers:
            platform_name = scraper_func.__name__.replace('scrape_', '') # e.g., 'upwork' from 'scrape_upwork'
            
            search_terms_for_platform = []
            if platform_name in ["xplace", "freelancerim", "alljobs"]:
                # Use Hebrew terms for Israeli platforms if available
                hebrew_terms = ISRAELI_PLATFORM_TERMS.get(platform_name.capitalize(), {}).get(category_name)
                if hebrew_terms:
                    search_terms_for_platform = hebrew_terms
                    logging.info(f"  Using Hebrew terms for {platform_name}: {hebrew_terms}")
                else:
                    logging.warning(f"  No specific Hebrew terms for '{category_name}' on {platform_name}. Skipping this platform for this category.")
                    continue # Skip if no specific Hebrew terms
            else:
                search_terms_for_platform = english_terms
                logging.info(f"  Using English terms for {platform_name}: {english_terms}")

            for term in search_terms_for_platform:
                logging.info(f"    Scraping '{platform_name}' for term: '{term}'")
                try:
                    jobs_from_platform = scraper_func(term)
                    logging.info(f"    Found {len(jobs_from_platform)} raw jobs from {platform_name} for '{term}'")

                    for job in jobs_from_platform:
                        # Add platform and search term metadata
                        job['platform'] = platform_name.capitalize()
                        job['search_term'] = term
                        job['timestamp'] = datetime.datetime.now(pytz.timezone('Asia/Jerusalem')).timestamp() # Add current time in IDT

                        if is_relevant_job(job.get('title', ''), job.get('description', ''), job['platform']):
                            all_found_jobs.append(job)
                        else:
                            logging.info(f"      Filtered out irrelevant job: '{job.get('title', 'N/A')}' on {job['platform']}")
                    time.sleep(2) # Be polite, add a delay between different search terms on the same platform

                except Exception as e:
                    logging.error(f"Error scraping {platform_name} for '{term}': {e}", exc_info=True)
                time.sleep(1) # Small delay between platforms for a given search term

    # Remove duplicates within this session
    final_jobs = remove_duplicates(all_found_jobs)
    num_jobs = len(final_jobs)
    logging.info(f"Scraping session finished. Total relevant and unique jobs found: {num_jobs}")

    # Prepare email body
    current_date = datetime.date.today().strftime('%Y-%m-%d')
    email_subject = f"Job Bot Report - {num_jobs} jobs - {current_date}"
    email_body = f"Job Bot Report - {num_jobs} jobs found on {current_date} (Israel Time)\n\n"

    if num_jobs > 0:
        for i, job in enumerate(final_jobs):
            email_body += f"--- Job {i+1} ---\n"
            email_body += f"Title: {job.get('title', 'N/A')}\n"
            email_body += f"Platform: {job.get('platform', 'N/A')}\n"
            email_body += f"Search Term: {job.get('search_term', 'N/A')}\n"
            email_body += f"Link: {job.get('link', 'N/A')}\n"
            
            # Format timestamp from Unix timestamp to human-readable
            if 'timestamp' in job and job['timestamp']:
                dt_object = datetime.datetime.fromtimestamp(job['timestamp'], tz=pytz.timezone('Asia/Jerusalem'))
                email_body += f"Timestamp: {dt_object.strftime('%Y-%m-%d %H:%M:%S IDT')}\n"
            else:
                email_body += f"Timestamp: N/A\n"

            # Truncate description for email to avoid overly long emails
            description_text = job.get('description', 'No description provided.')
            if len(description_text) > 500:
                email_body += f"Description: {description_text[:500]}...\n\n"
            else:
                email_body += f"Description: {description_text}\n\n"
    else:
        email_body += "No relevant jobs found in this session.\n\n"
        email_body += "Consider adjusting search terms or checking scraper implementations if this occurs frequently."

    send_email(email_subject, email_body)
    logging.info("Email report generation complete.")

    return final_jobs # Return for potential UI display/logging
