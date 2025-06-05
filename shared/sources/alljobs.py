import requests
from bs4 import BeautifulSoup
import time
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_alljobs(search_term):
    """
    Scrapes AllJobs.co.il for job postings.
    Note: AllJobs can be challenging to scrape due to dynamic content and anti-bot measures.
    This is a basic attempt that might require further refinement.
    """
    jobs = []
    # AllJobs URL structure for search, often involves encoded terms and categories.
    # This URL is a simplified example and might need adjustment for specific search behavior.
    # It's better to observe network requests in a browser when searching AllJobs manually
    # to get the exact URL parameters they use.
    base_url = "https://www.alljobs.co.il/SearchResults.aspx?page={page_num}&freeText={search_term_encoded}"
    
    # Example: How AllJobs might encode search terms (replace spaces with '+')
    search_term_encoded = requests.utils.quote(search_term.replace(" ", "+"), safe='')

    # We'll try to scrape the first few pages
    for page_num in range(1, 3): # Scrape first 2 pages (adjust as needed)
        url = base_url.format(page_num=page_num, search_term_encoded=search_term_encoded)

        # Using a more robust User-Agent and common browser headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.alljobs.co.il/', # Mimic coming from the main page
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin', # Changed to same-origin for internal links
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        try:
            logging.info(f"  Attempting to scrape AllJobs URL: {url}")
            time.sleep(random.uniform(5, 10)) # Longer, random delay for AllJobs

            response = requests.get(url, headers=headers, timeout=30) # Increased timeout
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # AllJobs often uses divs with specific classes for job listings.
            # You might need to inspect the AllJobs website manually to find the exact selectors.
            # Look for elements that consistently contain job title, company, link, and description.
            # Example selectors (these might need adjustment after inspection):
            job_listings = soup.find_all('div', class_='job-item') # Common class for job listings
            if not job_listings:
                job_listings = soup.find_all('article', class_='job-ad') # Another common class

            if not job_listings:
                logging.warning(f"    No job listings found on AllJobs for '{search_term}' on page {page_num}. HTML might have changed or content loaded via JS.")
                # Optional: Save HTML for debugging locally
                # with open(f"alljobs_debug_{search_term.replace(' ', '_')}_page_{page_num}.html", "w", encoding="utf-8") as f:
                #     f.write(response.text)
                continue # Try next page

            for job_card in job_listings:
                title_tag = job_card.find(['h2', 'h3', 'a'], class_=['job-title', 'JobTitle']) # Adapt to actual AllJobs HTML
                link_tag = job_card.find('a', class_=['job-link', 'JobUrl']) # Adapt to actual AllJobs HTML
                description_tag = job_card.find('div', class_=['job-description', 'JobDescription']) # Adapt to actual AllJobs HTML

                if title_tag and link_tag:
                    job_title = title_tag.get_text(strip=True)
                    job_link = link_tag.get('href')
                    if job_link and not job_link.startswith('http'):
                        # AllJobs links are often relative, need to prepend base URL
                        job_link = "https://www.alljobs.co.il" + job_link

                    full_description = description_tag.get_text(strip=True) if description_tag else ""

                    jobs.append({
                        "title": job_title,
                        "description": full_description,
                        "link": job_link,
                    })
                else:
                    logging.debug(f"    Skipping malformed job card on AllJobs: {job_card.get_text(strip=True)[:100]}...")

        except requests.exceptions.RequestException as e:
            logging.error(f"  Network error scraping AllJobs for '{search_term}' on page {page_num}: {e}")
            break # Stop trying further pages on network error
        except Exception as e:
            logging.error(f"  Parsing or unexpected error for AllJobs '{search_term}' on page {page_num}: {e}", exc_info=True)
            break # Stop trying further pages on parsing error

    logging.info(f"  Finished scraping AllJobs for '{search_term}'. Found {len(jobs)} raw jobs.")
    return jobs
