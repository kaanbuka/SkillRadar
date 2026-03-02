import json

from config import JOBS_RAW
from nlp_engine import run_nlp

if __name__ == "__main__":
    if not JOBS_RAW.exists():
        print(f"Önce veri çekin: python data_fetcher.py")
        print(f"Beklenen dosya: {JOBS_RAW}")
        exit(1)
    with open(JOBS_RAW, encoding="utf-8") as f:
        jobs = json.load(f)
    print(f"{len(jobs)} ilan işleniyor...")
    df_jobs, df_skills = run_nlp(jobs)
    print("En çok aranan 10 yetenek:")
    print(df_skills.head(10).to_string(index=False))
    print(f"\nKaydedildi: data/jobs_processed.csv, data/skills_counts.csv")
