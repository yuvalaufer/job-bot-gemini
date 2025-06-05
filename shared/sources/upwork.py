import requests
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_upwork(search_term):
    """
    Scrapes Upwork for job postings related to the given search term.
    Extracts job title, full description, direct link, and other relevant details.
    """
    jobs = []
    # Upwork's search URL. This is a common pattern, but might need adjustment
    # if Upwork changes its site structure or query parameters.
    # We use 'quote' to properly encode the search term for URLs.
    # Adjust filters in the URL as needed (e.g., freelance, hourly/fixed, experience level)
    # This example uses a very basic search, you might want to add more specific filters
    # by inspecting Upwork's search results page.
    base_url = "https://www.upwork.com/nx/search/jobs/?q="
    url = f"{base_url}{requests.utils.quote(search_term)}&sort=recency" # Sort by recency

    # Mimic a real browser to avoid being blocked.
    # The User-Agent string should be updated periodically as browsers evolve.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        logging.info(f"  Attempting to scrape Upwork URL: {url}")
        response = requests.get(url, headers=headers, timeout=15) # Increased timeout
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Upwork's HTML structure is complex and uses a lot of JavaScript.
        # Direct BeautifulSoup parsing might miss jobs loaded dynamically.
        # If this scraper consistently misses jobs, Playwright/Selenium would be necessary.
        
        # Look for job list containers or individual job cards.
        # These selectors are based on common Upwork HTML patterns, but may change.
        # You'll need to inspect the live Upwork job search page to verify these.
        job_listings = soup.find_all('section', class_='job-tile') # Common class for job cards
        if not job_listings:
            # Try alternative selectors if the primary one fails
            job_listings = soup.find_all('div', class_='air3-job-tile') # Another common class

        if not job_listings:
            logging.warning(f"    No job listings found on Upwork for '{search_term}' with current selectors. HTML might have changed.")
            # For debugging, you might want to save the HTML response:
            # with open(f"upwork_debug_{search_term.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            return []

        for job_card in job_listings:
            title_tag = job_card.find('h2', class_='job-title') # Or 'air3-job-tile-title'
            link_tag = job_card.find('a', class_='job-title-link') # Or 'air3-job-tile-title-link' or similar
            description_tag = job_card.find('span', class_='job-description-text') # Or 'air3-job-tile-description-text' or similar

            if title_tag and link_tag:
                job_title = title_tag.get_text(strip=True)
                # Upwork links can be relative, ensure it's an absolute URL
                job_link = link_tag.get('href')
                if job_link and not job_link.startswith('http'):
                    job_link = "https://www.upwork.com" + job_link

                full_description = description_tag.get_text(strip=True) if description_tag else ""

                jobs.append({
                    "title": job_title,
                    "description": full_description,
                    "link": job_link,
                    # Platform and search_term will be added in shared/scraper.py
                    # Timestamp will be added in shared/scraper.py
                })
            else:
                logging.debug(f"    Skipping malformed job card on Upwork: {job_card.get_text(strip=True)[:100]}...")

    except requests.exceptions.RequestException as e:
        logging.error(f"  Network error scraping Upwork for '{search_term}': {e}")
    except Exception as e:
        logging.error(f"  Parsing or unexpected error for Upwork '{search_term}': {e}", exc_info=True)

    logging.info(f"  Finished scraping Upwork for '{search_term}'. Found {len(jobs)} raw jobs.")
    return jobs
