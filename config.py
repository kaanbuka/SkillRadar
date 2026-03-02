import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from pathlib import Path

APP_ID = os.getenv("ADZUNA_APP_ID", "")
APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

DATA_DIR = Path(__file__).parent / "data"
JOBS_RAW = DATA_DIR / "jobs_raw.json"
JOBS_PROCESSED = DATA_DIR / "jobs_processed.csv"
SKILLS_COUNTS = DATA_DIR / "skills_counts.csv"

DATA_DIR.mkdir(exist_ok=True)

SEARCH_QUERIES = [
    "Data Science",
    "Data Engineer",
    "Machine Learning",
    "Computer Science",
    "Software Engineer",
    "Python Developer",
    "Backend Developer",
]

CITIES = ["Berlin", "München", "Hamburg", "Frankfurt", "Köln"]
