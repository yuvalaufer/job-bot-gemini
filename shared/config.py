JOB_CATEGORIES = {
    "English to Hebrew translation": ["English to Hebrew translation", "translate English Hebrew", "Hebrew English translator", "Hebrew translator", "English Hebrew localization"],
    "Song translation (light music)": ["song translation music", "light music translation", "music translation lyrics", "lyrics translation", "song adaptation"],
    "Piano recording (session musician)": ["piano recording", "session pianist", "remote piano session", "piano for song", "midi piano recording"],
    "Vocal recording (harmony recording)": ["vocal recording", "harmony vocalist", "backing vocals recording", "session singer harmony", "vocal harmony arrangements"],
}

# Add more specific search terms if needed, e.g., for Israeli platforms
ISRAELI_PLATFORM_TERMS = {
    "XPlace": {
        "English to Hebrew translation": ["תרגום אנגלית עברית", "מתרגם עברית אנגלית"],
        "Song translation (light music)": ["תרגום שירים", "תרגום מוזיקה"],
        "Piano recording (session musician)": ["הקלטת פסנתר", "פסנתרן סשן"],
        "Vocal recording (harmony recording)": ["הקלטת קולות", "קולות רקע"],
    },
    "Freelancerim": {
        "English to Hebrew translation": ["תרגום מאמרים", "תרגום טקסטים", "מתרגם אנגלית"],
        "Song translation (light music)": ["תרגום שירה", "כתיבת מילים"],
        "Piano recording (session musician)": ["נגן פסנתר", "הקלטת מנגינה"],
        "Vocal recording (harmony recording)": ["זמר ליווי", "הקלטת שירה"],
    },
    "AllJobs": {
        "English to Hebrew translation": ["מתרגם", "תרגום"],
        "Song translation (light music)": ["יוצר תוכן", "כתיבה מוזיקלית"], # AllJobs is less specific for these
        "Piano recording (session musician)": ["מוזיקאי", "נגן"],
        "Vocal recording (harmony recording)": ["זמר", "מקליט שירה"],
    }
}


# Email Configuration Placeholders (will be overridden by environment variables in Render)
EMAIL_SENDER = "" # Change this or use env var
EMAIL_PASSWORD = "" # Change this or use env var
EMAIL_RECIPIENT = "" # Change this
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
