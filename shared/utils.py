import re
from langdetect import detect, DetectorFactory
import hashlib

# Ensures consistent language detection results
DetectorFactory.seed = 0

def is_relevant_job(job_title, job_description, platform_name):
    """
    Applies smart filtering to eliminate irrelevant gigs based on common patterns.
    """
    title = job_title.lower()
    description = job_description.lower()

    # Rule 1: Eliminate "I will..." or "I offer..." type posts (seller offers)
    # These are common patterns for providers offering services, not clients seeking them.
    seller_patterns = [
        r"i will\s+\w+",
        r"i offer\s+\w+",
        r"i provide\s+\w+",
        r"offering\s+\w+",
        r"provide\s+\w+\s+service",
        r"אני אתרגם", # Hebrew seller patterns
        r"מציע שירותי",
        r"למתן שירותי"
    ]
    for pattern in seller_patterns:
        if re.search(pattern, title) or re.search(pattern, description):
            return False

    # Rule 2: Specific Fiverr seller filter (client seeks provider)
    # Fiverr is notorious for seller gigs. We look for phrases indicating a client need.
    if platform_name.lower() == "fiverr":
        if not (re.search(r"i need|looking for|seeking|require|want to hire", title) or \
                re.search(r"i need|looking for|seeking|require|want to hire", description)):
            return False

    # Rule 3: Basic language detection (if description is long enough)
    # Only try to detect language if there's enough text to go on.
    # If detection fails or isn't English, filter it out.
    if len(description) > 50: # Arbitrary length for more reliable detection
        try:
            if detect(description) != 'en':
                return False
        except Exception:
            # If language detection fails (e.g., text too short/weird), don't filter based on it
            pass
    elif len(title) > 20: # Try with title if description is too short
        try:
            if detect(title) != 'en':
                return False
        except Exception:
            pass


    # Rule 4: Keywords that often indicate irrelevance, regardless of seller patterns
    irrelevant_keywords = [
        "gig", "kwork", "profile creation", "resume writing", "data entry",
        "virtual assistant", "web research", "pdf conversion", "typing",
        "lead generation", "social media manager", "content writer", # Exclude general content writing, focus on translation
        "logo design", "web development", "app development", "marketing",
        "אייפון", "אנדרואיד", "עיצוב", "קידום אתרים", "בינה מלאכותית", "בונה אתרים"
    ]
    for keyword in irrelevant_keywords:
        if keyword in title or keyword in description:
            return False

    # Rule 5: Ensure at least one core category keyword is present (positive filtering)
    # This helps catch jobs that slipped through other filters but are generally off-topic.
    # We define relevant keywords from the categories.
    relevant_core_keywords = [
        "translate", "translation", "translator", "localization", "hebrew", "english",
        "song", "lyrics", "music", "piano", "pianist", "recording", "session", "vocal", "harmony", "singer"
    ]
    found_relevant_keyword = False
    for keyword in relevant_core_keywords:
        if keyword in title or keyword in description:
            found_relevant_keyword = True
            break
    if not found_relevant_keyword:
        return False

    return True

def generate_job_id(job_data):
    """Generates a unique ID for a job based on its key attributes."""
    # Using a hash of concatenated key fields to create a consistent, unique ID
    # This helps in de-duplication across sessions if we add persistent storage.
    unique_string = f"{job_data['platform']}-{job_data['title']}-{job_data['link']}".encode('utf-8')
    return hashlib.md5(unique_string).hexdigest()

def remove_duplicates(jobs):
    """
    Removes duplicate jobs from a list based on a generated unique ID.
    This handles de-duplication within a single scraping run.
    For cross-run de-duplication, a persistent storage would be needed.
    """
    unique_jobs = []
    seen_ids = set()

    for job in jobs:
        job_id = generate_job_id(job)
        if job_id not in seen_ids:
            unique_jobs.append(job)
            seen_ids.add(job_id)
    return unique_jobs
