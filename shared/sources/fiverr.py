import requests
from bs4 import BeautifulSoup
import time
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_fiverr(search_term):
    """
    Scrapes Fiverr for gig listings related to the given search term.
    Note: Fiverr can be challenging to scrape due to dynamic content and anti-bot measures.
    This is a basic attempt that might require further refinement.
    """
    jobs = [] # We'll use 'jobs' list to keep consistency, but these are actually 'gigs'
    
    # Fiverr search URL for gigs
    base_url = "https://www.fiverr.com/search/gigs?query="
    url = f"{base_url}{requests.utils.quote(search_term)}"

    # Using robust User-Agent and common browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://www.fiverr.com/', # Mimic coming from the main page
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
        logging.info(f"  Attempting to scrape Fiverr URL: {url}")
        time.sleep(random.uniform(5, 10)) # Longer, random delay for Fiverr

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Fiverr gig cards typically have specific structures.
        # You'll likely need to inspect Fiverr manually to find the exact selectors
        # (e.g., div class for a gig card, h3 for title, a for link, etc.).
        # These are common examples, might need adjustment:
        gig_listings = soup.find_all('div', class_='gig-card-layout') # Common class for a gig card container
        if not gig_listings:
            gig_listings = soup.find_all('article', class_='gig-card') # Another potential class

        if not gig_listings:
            logging.warning(f"    No gig listings found on Fiverr for '{search_term}'. HTML might have changed or content loaded via JS.")
            # Optional: Save HTML for debugging locally
            # with open(f"fiverr_debug_{search_term.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            return []

        for gig_card in gig_listings:
            title_tag = gig_card.find('h3', class_='gig-card-title') or gig_card.find('a', class_='gig-card-link')
            link_tag = gig_card.find('a', class_='gig-card-link')
            # Fiverr gigs typically don't have a full description on the search page,
            # so we'll just use the title as a short description for now.
            # A full description would require clicking into each gig page.
            description_text = title_tag.get_text(strip=True) if title_tag else ""

            if title_tag and link_tag:
                gig_title = title_tag.get_text(strip=True)
                gig_link = link_tag.get('href')
                if gig_link and not gig_link.startswith('http'):
                    gig_link = "https://www.fiverr.com" + gig_link

                jobs.append({
                    "title": gig_title,
                    "description": description_text, # Using title as description for simplicity
                    "link": gig_link,
                })
            else:
                logging.debug(f"    Skipping malformed gig card on Fiverr: {gig_card.get_text(strip=True)[:100]}...")

    except requests.exceptions.RequestException as e:
        logging.error(f"  Network error scraping Fiverr for '{search_term}': {e}")
    except Exception as e:
        logging.error(f"  Parsing or unexpected error for Fiverr '{search_term}': {e}", exc_info=True)

    logging.info(f"  Finished scraping Fiverr for '{search_term}'. Found {len(jobs)} raw gigs.")
    return jobs
