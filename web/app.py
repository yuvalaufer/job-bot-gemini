from flask import Flask, render_template, jsonify, request
import os
import logging
import threading
import datetime
import pytz

# Import the scraper function from the shared module
from shared.scraper import run_scraper_and_email

app = Flask(__name__, template_folder='templates')

# Set up logging for the web service
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# This is a global variable to store the last run status.
# It will be updated by the manual trigger but won't automatically reflect
# the worker's scheduled runs without a shared persistent storage.
job_counts = {"last_run_jobs": 0, "last_run_timestamp": "N/A", "status_message": "Ready"}

@app.route('/')
def index():
    """
    Renders the main dashboard page.
    """
    return render_template('index.html', job_counts=job_counts)

@app.route('/trigger_scan', methods=['POST'])
def trigger_scan():
    """
    Endpoint to manually trigger a job scan.
    Runs the scraper in a separate thread to avoid blocking the Flask app.
    """
    global job_counts # Declare that we intend to modify the global job_counts variable
    logging.info("Manual scan triggered via UI.")
    job_counts["status_message"] = "Scan in progress... please wait."
    job_counts["last_run_timestamp"] = "Scanning..." # Update status immediately

    # Define the background task function
    def run_scan_in_background():
        global job_counts # This is crucial: declare global inside the nested function too
        try:
            # The run_scraper_and_email function already handles logging and email
            jobs = run_scraper_and_email()
            job_counts["last_run_jobs"] = len(jobs)
            # Use pytz to get timezone-aware current time in Israel
            current_time_idt = datetime.datetime.now(pytz.timezone('Asia/Jerusalem'))
            job_counts["last_run_timestamp"] = current_time_idt.strftime('%Y-%m-%d %H:%M:%S IDT')
            job_counts["status_message"] = f"Scan complete. Found {len(jobs)} jobs."
            logging.info(f"Manual scan completed. Found {len(jobs)} jobs.")
        except Exception as e:
            job_counts["status_message"] = f"Error during manual scan: {e}"
            logging.error(f"Error during manual scan: {e}", exc_info=True)
            job_counts["last_run_jobs"] = "Error"

    # Start the scan in a new thread
    thread = threading.Thread(target=run_scan_in_background)
    thread.start()

    return jsonify({"status": "success", "message": "Manual scan initiated in background. Check back in a few minutes or check your email."}), 202 # 202 Accepted

@app.route('/status')
def get_status():
    """
    Endpoint to get the current status of the last scan.
    """
    return jsonify(job_counts)

if __name__ == '__main__':
    # Use environment variable for port in production (Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
