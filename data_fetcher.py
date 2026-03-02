import json
import time

import requests

from config import APP_ID, APP_KEY, JOBS_RAW, SEARCH_QUERIES, CITIES


def fetch_jobs(app_id: str, app_key: str, what: str, where: str = "", page: int = 1) -> dict:
    url = f"https://api.adzuna.com/v1/api/jobs/de/search/{page}"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": what,
        "results_per_page": 50,
    }
    if where:
        params["where"] = where
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def collect_all_jobs(app_id: str, app_key: str, max_pages: int = 3) -> list[dict]:
    all_jobs = []
    seen_ids = set()

    for query in SEARCH_QUERIES:
        for city in CITIES + [""]:
            for page in range(1, max_pages + 1):
                try:
                    loc = city or "Tüm Almanya"
                    print(f"  {query} | {loc} | sayfa {page}...", end=" ", flush=True)
                    data = fetch_jobs(app_id, app_key, what=query, where=city, page=page)
                    results = data.get("results", [])
                    print(f"✓ {len(results)} ilan")
                    for job in results:
                        jid = job.get("id")
                        if jid and jid not in seen_ids:
                            seen_ids.add(jid)
                            all_jobs.append({
                                "id": jid,
                                "title": job.get("title", ""),
                                "description": job.get("description", ""),
                                "company": job.get("company", {}).get("display_name", ""),
                                "location": job.get("location", {}).get("display_name", ""),
                                "url": job.get("redirect_url", ""),
                                "query": query,
                                "city": city or "All",
                            })
                    if not results:
                        break
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  Hata ({query}, {city}, sayfa {page}): {e}")
                    break

    return all_jobs


def run_fetcher():
    if not APP_ID or not APP_KEY:
        print("ADZUNA_APP_ID ve ADZUNA_APP_KEY gerekli.")
        print("  .env dosyası oluşturun veya: export ADZUNA_APP_ID=... ADZUNA_APP_KEY=...")
        return []

    print("Almanya iş ilanları çekiliyor (Adzuna API)...")
    jobs = collect_all_jobs(APP_ID, APP_KEY, max_pages=2)
    print(f"  Toplam: {len(jobs)} ilan")

    JOBS_RAW.parent.mkdir(exist_ok=True)
    with open(JOBS_RAW, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"  Kaydedildi: {JOBS_RAW}")
    return jobs


if __name__ == "__main__":
    run_fetcher()
