import requests
from bs4 import BeautifulSoup
import time
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_jobmaster(search_term):
    """
    Scrapes JobMaster.co.il for job postings.
    """
    jobs = []
    # JobMaster's search URL structure might vary.
    # A common pattern is /jobs/search/keyword or similar.
    # It's best to perform a manual search on JobMaster and capture the URL.
    # This example assumes a simple search parameter 'q'.
    base_url = "https://www.jobmaster.co.il/jobs/search?q="
    url = f"{base_url}{requests.utils.quote(search_term)}"

    # Using robust User-Agent and common browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://www.jobmaster.co.il/',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    try:
        logging.info(f"  Attempting to scrape JobMaster URL: {url}")
        time.sleep(random.uniform(4, 8)) # Random delay for JobMaster

        response = requests.get(url, headers=headers, timeout=25)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # JobMaster's HTML structure can be complex.
        # You'll likely need to inspect JobMaster manually to find the exact selectors.
        # Look for elements that consistently contain job title, link, and description.
        # These are educated guesses for common patterns:
        job_listings = soup.find_all('div', class_='job-item') # Common class for a job listing
        if not job_listings:
            job_listings = soup.find_all('li', class_='job-ad') # Another common class

        if not job_listings:
            logging.warning(f"    No job listings found on JobMaster for '{search_term}'. HTML might have changed or content loaded via JS.")
            # Optional: Save HTML for debugging locally
            # with open(f"jobmaster_debug_{search_term.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            return []

        for job_card in job_listings:
            title_tag = job_card.find('h2', class_='job-title') or job_card.find('a', class_='job-link')
            link_tag = job_card.find('a', class_='job-link')
            description_tag = job_card.find('div', class_='job-description')

            if title_tag and link_tag:
                job_title = title_tag.get_text(strip=True)
                job_link = link_tag.get('href')
                if job_link and not job_link.startswith('http'):
                    # JobMaster links are often relative
                    job_link = "https://www.jobmaster.co.il" + job_link

                full_description = description_tag.get_text(strip=True) if description_tag else ""

                jobs.append({
                    "title": job_title,
                    "description": full_description,
                    "link": job_link,
                })
            else:
                logging.debug(f"    Skipping malformed job card on JobMaster: {job_card.get_text(strip=True)[:100]}...")

    except requests.exceptions.RequestException as e:
        logging.error(f"  Network error scraping JobMaster for '{search_term}': {e}")
    except Exception as e:
        logging.error(f"  Parsing or unexpected error for JobMaster '{search_term}': {e}", exc_info=True)

    logging.info(f"  Finished scraping JobMaster for '{search_term}'. Found {len(jobs)} raw jobs.")
    return jobs

