import json
import os
import re
import time
from collections import Counter

import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from nlp_engine import extract_skills

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_OLLAMA = os.getenv("AI_USE_OLLAMA", "").lower() in ("1", "true", "yes")
OLLAMA_BASE_URL = os.getenv("AI_OLLAMA_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("AI_OLLAMA_MODEL", "llama3.2")
AI_MODEL = os.getenv("AI_SKILL_MODEL", "gpt-4o-mini")

SKILL_EXTRACTION_PROMPT = """Bu ilan metninden SADECE teknik yetenekleri çıkar. İstenenler:
- Programlama dilleri (Python, Java, SQL, R, Scala, Go, ...)
- Framework/araçlar (React, TensorFlow, Docker, AWS, Kafka, ...)
- Dil gereksinimleri: German/Deutsch → "Almanca", English → "English"
- Metodoloji (Agile, Scrum, Jira, ...)

YAPMA: Data Science, Machine Learning, Software Engineer gibi İŞ ROLÜ adlarını yetenek sayma.
YAPMA: "AI", "Artificial Intelligence", "KI" (Künstliche Intelligenz) gibi kavramları yetenek sayma.

İlan:
---
{text}
---

Sadece JSON array döndür, başka metin yok. Örnek: ["Python", "SQL", "Almanca", "Docker"]
"""


def _get_client():
    try:
        from openai import OpenAI
    except ImportError:
        return None

    if USE_OLLAMA:
        return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    return OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _call_llm(text: str, max_retries: int = 2) -> list[str]:
    client = _get_client()
    if not client:
        return []

    model = OLLAMA_MODEL if USE_OLLAMA else AI_MODEL
    prompt = SKILL_EXTRACTION_PROMPT.format(text=text[:4000])

    for attempt in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            content = resp.choices[0].message.content.strip()
            content = re.sub(r"^```\w*\n?", "", content)
            content = re.sub(r"\n?```$", "", content)
            skills = json.loads(content)
            if isinstance(skills, list):
                _EXCLUDE = {"ai", "artificial intelligence", "ki", "künstliche intelligenz"}
                return [str(s).strip() for s in skills if s and str(s).strip().lower() not in _EXCLUDE]
            return []
        except json.JSONDecodeError:
            if attempt == max_retries:
                return []
            time.sleep(1)
        except Exception as e:
            if attempt == max_retries:
                raise e
            time.sleep(2)
    return []


def extract_skills_with_ai(job: dict) -> list[str]:
    text = f"{job.get('title', '')} {job.get('description', '')}"
    regex_skills = set(extract_skills(text))
    ai_skills = _call_llm(text)
    combined = list(dict.fromkeys(list(regex_skills) + [s for s in ai_skills if s]))
    return combined


def run_ai_enrichment(
    jobs: list[dict],
    max_jobs: int = 100,
    delay_between_calls: float = 0.5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not USE_OLLAMA and not OPENAI_API_KEY:
        raise ValueError(
            "AI için OpenAI veya Ollama gerekli.\n"
            "• Ücretsiz (Ollama): .env'e AI_USE_OLLAMA=true ekleyin, ardından 'ollama run llama3.2'\n"
            "• Ücretli (OpenAI): .env'e OPENAI_API_KEY=sk-... ekleyin"
        )
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai paketi gerekli: pip install openai")

    all_skills_per_job: dict[str, list[str]] = {}
    for job in jobs:
        jid = str(job.get("id", ""))
        text = f"{job.get('title', '')} {job.get('description', '')}"
        all_skills_per_job[jid] = list(dict.fromkeys(extract_skills(text)))

    to_process = sorted(
        jobs,
        key=lambda j: len(all_skills_per_job.get(str(j.get("id", "")), [])),
    )[:max_jobs]

    for job in to_process:
        jid = str(job.get("id", ""))
        text = f"{job.get('title', '')} {job.get('description', '')}"
        ai_skills = _call_llm(text)
        existing = set(all_skills_per_job.get(jid, []))
        for s in ai_skills:
            if s and s not in existing:
                existing.add(s)
        all_skills_per_job[jid] = list(existing)
        time.sleep(delay_between_calls)

    all_skills_flat = []
    rows = []
    for job in jobs:
        jid = str(job.get("id", ""))
        skills = all_skills_per_job.get(jid, [])
        all_skills_flat.extend(skills)
        rows.append({
            "id": job.get("id"),
            "title": job.get("title", ""),
            "query": job.get("query", ""),
            "skills_found": " | ".join(skills[:15]) if skills else "",
        })

    counts = Counter(s.title() for s in all_skills_flat)
    from config import JOBS_PROCESSED, SKILLS_COUNTS

    df_jobs = pd.DataFrame(rows)
    df_skills = pd.DataFrame(counts.most_common(), columns=["skill", "count"])
    df_jobs.to_csv(JOBS_PROCESSED, index=False)
    df_skills.to_csv(SKILLS_COUNTS, index=False)
    return df_jobs, df_skills
