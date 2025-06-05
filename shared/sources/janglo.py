import requests
from bs4 import BeautifulSoup
import time
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_janglo(search_term):
    """
    Scrapes Janglo.net for job postings.
    Janglo's search might be simpler, but selectors might need adjustment.
    """
    jobs = []
    # Janglo's search URL. Example: https://www.janglo.net/jobs/search?search_text=remote+piano
    base_url = "https://www.janglo.net/jobs/search?search_text="
    url = f"{base_url}{requests.utils.quote(search_term.replace(' ', '+'))}"

    # Using robust User-Agent and common browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://www.janglo.net/',
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
        logging.info(f"  Attempting to scrape Janglo URL: {url}")
        time.sleep(random.uniform(3, 7)) # Random delay for Janglo

        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Janglo's job listings might be structured simply.
        # You'll need to inspect Janglo manually to find the exact selectors.
        # Common patterns: div/li with a specific class for an ad unit.
        job_listings = soup.find_all('div', class_='listing-item') # Common class for a listing on Janglo
        if not job_listings:
            job_listings = soup.find_all('article', class_='job-post') # Another potential class

        if not job_listings:
            logging.warning(f"    No job listings found on Janglo for '{search_term}'. HTML might have changed or content loaded via JS.")
            # Optional: Save HTML for debugging locally
            # with open(f"janglo_debug_{search_term.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            return []

        for job_card in job_listings:
            title_tag = job_card.find('h2', class_='listing-title') or job_card.find('a', class_='listing-link')
            link_tag = job_card.find('a', class_='listing-link')
            description_tag = job_card.find('div', class_='listing-content') # Or p, span for descriptions

            if title_tag and link_tag:
                job_title = title_tag.get_text(strip=True)
                job_link = link_tag.get('href')
                if job_link and not job_link.startswith('http'):
                    job_link = "https://www.janglo.net" + job_link # Janglo links are often relative

                full_description = description_tag.get_text(strip=True) if description_tag else ""

                jobs.append({
                    "title": job_title,
                    "description": full_description,
                    "link": job_link,
                })
            else:
                logging.debug(f"    Skipping malformed job card on Janglo: {job_card.get_text(strip=True)[:100]}...")

    except requests.exceptions.RequestException as e:
        logging.error(f"  Network error scraping Janglo for '{search_term}': {e}")
    except Exception as e:
        logging.error(f"  Parsing or unexpected error for Janglo '{search_term}': {e}", exc_info=True)

    logging.info(f"  Finished scraping Janglo for '{search_term}'. Found {len(jobs)} raw jobs.")
    return jobs
