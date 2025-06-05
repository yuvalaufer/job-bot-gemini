import requests
from bs4 import BeautifulSoup
import time
import logging
import random # Added for random delays

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_upwork(search_term):
    """
    Scrapes Upwork for job postings related to the given search term.
    Extracts job title, full description, direct link, and other relevant details.
    """
    jobs = []
    base_url = "https://www.upwork.com/nx/search/jobs/?q="
    url = f"{base_url}{requests.utils.quote(search_term)}&sort=recency"

    # Updated and more comprehensive headers to mimic a real browser more closely
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36', # Updated User-Agent
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com/', # Mimic coming from a search engine
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1', # Do Not Track
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        # Add some browser-specific client hints (adjust based on your User-Agent if different)
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    try:
        logging.info(f"  Attempting to scrape Upwork URL: {url}")
        # Add a random delay before making the request
        time.sleep(random.uniform(3, 7)) # Random delay between 3 to 7 seconds

        response = requests.get(url, headers=headers, timeout=20) # Increased timeout
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        job_listings = soup.find_all('section', class_='job-tile')
        if not job_listings:
            job_listings = soup.find_all('div', class_='air3-job-tile') # Alternative selector

        if not job_listings:
            logging.warning(f"    No job listings found on Upwork for '{search_term}' with current selectors. HTML might have changed or content loaded via JS.")
            # Consider saving HTML for debugging in local development:
            # with open(f"upwork_debug_{search_term.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            return []

        for job_card in job_listings:
            title_tag = job_card.find('h2', class_='job-title') or job_card.find('a', class_='air3-job-tile-title-link')
            link_tag = job_card.find('a', class_='job-title-link') or job_card.find('a', class_='air3-job-tile-title-link')
            description_tag = job_card.find('span', class_='job-description-text') or job_card.find('div', {'data-qa': 'job-description'})


            if title_tag and link_tag:
                job_title = title_tag.get_text(strip=True)
                job_link = link_tag.get('href')
                # Corrected line 68: Ensure the string literal is properly terminated
                if job_link and not job_link.startswith('http'):
                    job_link = "https://www.upwork.com" + job_link # <--- THIS IS THE CORRECTED LINE

                full_description = description_tag.get_text(strip=True) if description_tag else ""

                jobs.append({
                    "title": job_title,
                    "description": full_description,
                    "link": job_link,
                })
            else:
                logging.debug(f"    Skipping malformed job card on Upwork: {job_card.get_text(strip=True)[:100]}...")

    except requests.exceptions.RequestException as e:
        logging.error(f"  Network error scraping Upwork for '{search_term}': {e}")
    except Exception as e:
        logging.error(f"  Parsing or unexpected error for Upwork '{search_term}': {e}", exc_info=True)

    logging.info(f"  Finished scraping Upwork for '{search_term}'. Found {len(jobs)} raw jobs.")
    return jobs
