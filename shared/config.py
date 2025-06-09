# shared/config.py

# This file can be used for general configurations or constants.
# Specific search terms are now managed in shared/scraper.py's SCRAPE_TERMS.

# You can keep general categories here if you plan to use them for other filtering logic
# or for a more structured approach to defining job types, but they are not
# directly used for the SCRAPE_TERMS list.
JOB_CATEGORIES = {
    "English to Hebrew translation": ["English to Hebrew translation", "translate English Hebrew", "Hebrew English translator", "Hebrew translator", "English Hebrew localization"],
    "Song translation (light music)": ["song translation music", "light music translation", "music translation lyrics", "lyrics translation", "song adaptation"],
    "Piano recording (session musician)": ["piano recording", "session pianist", "remote piano session", "piano for song", "midi piano recording"],
    "Vocal recording (harmony recording)": ["vocal recording", "harmony vocalist", "backing vocals recording", "session singer harmony", "vocal harmony arrangements"],
}

# The ISRAELI_PLATFORM_TERMS dictionary was removed from here
# as SCRAPE_TERMS in scraper.py now handles all desired search terms.

# Email Configuration Placeholders (will be overridden by environment variables in Render)
# These are fallback values or for local testing without .env.
# In production on Render, environment variables (RENDER_EMAIL_USER, RENDER_EMAIL_PASS, EMAIL_RECIPIENT) should be used.
EMAIL_SENDER = "" # Change this or use env var
EMAIL_PASSWORD = "" # Change this or use env var
EMAIL_RECIPIENT = "" # Change this
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
