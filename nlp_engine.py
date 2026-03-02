import re
from collections import Counter

import pandas as pd

SKILLS_PATTERNS: list[tuple[str, str | None]] = [
    (r"\bPython\b", None), (r"\bPython3\b", "Python"), (r"\bPython\s*3\b", "Python"),
    (r"\bJava\b", None), (r"\bJavaScript\b", None), (r"\bTypeScript\b", None),
    (r"\bR\b", None), (r"\bScala\b", None), (r"\bGo\b", None), (r"\bGolang\b", "Go"),
    (r"\bRust\b", None), (r"\bC\+\+\b", None), (r"\bC#\b", None), (r"\bPHP\b", None),
    (r"\bKotlin\b", None), (r"\bSwift\b", None), (r"\bNode\.?js\b", "Node.js"),
    (r"\bNodeJS\b", "Node.js"),     (r"\bNext\.?js\b", "Next.js"),
    (r"\bSQL\b", None), (r"\bNoSQL\b", None), (r"\bPostgreSQL\b", None), (r"\bPostgres\b", "PostgreSQL"),
    (r"\bMongoDB\b", None), (r"\bMongo\b", "MongoDB"), (r"\bRedis\b", None),
    (r"\bTensorFlow\b", None), (r"\bPyTorch\b", None), (r"\bKeras\b", None),
    (r"\bScikit-learn\b", None), (r"\bscikit-learn\b", None), (r"\bsklearn\b", "Scikit-learn"),
    (r"\bPandas\b", None), (r"\bNumPy\b", None), (r"\bNumpy\b", "NumPy"),
    (r"\bNLP\b", None), (r"\bComputer Vision\b", None), (r"\bDeep Learning\b", None),
    (r"\bHugging\s*Face\b", "Hugging Face"),     (r"\bOpenAI\b", None), (r"\bLLM\b", None),
    (r"\bML\b", None), (r"\bAnalytics\b", "Analytics"), (r"\banalytics\b", "Analytics"),
    (r"\b(?:data pipeline|data pipelines)\b", "Data Pipelines"),
    (r"\bDatenanalyse\b", "Data Analysis"), (r"\bData Analysis\b", None),
    (r"\bAWS\b", None), (r"\bAzure\b", None), (r"\bGCP\b", None), (r"\bGoogle Cloud\b", None),
    (r"\bDocker\b", None), (r"\bKubernetes\b", None), (r"\bK8s\b", "Kubernetes"),
    (r"\bTerraform\b", None), (r"\bCI/CD\b", None), (r"\bCICD\b", "CI/CD"),
    (r"\bJenkins\b", None), (r"\bGit\b", None), (r"\bGitLab\b", None), (r"\bGitHub\b", None),
    (r"\bBitbucket\b", None), (r"\bLinux\b", None),     (r"\bUnix\b", None),
    (r"\bApache Spark\b", None), (r"\bSpark\b", None), (r"\bKafka\b", None),
    (r"\bAirflow\b", None), (r"\bETL\b", None), (r"\bDatabricks\b", None),
    (r"\bSnowflake\b", None), (r"\bdbt\b", None),     (r"\bBig Data\b", None),
    (r"\bREST\b", None), (r"\bRESTful\b", "REST"), (r"\bAPI\b", None),
    (r"\bAPIs\b", "API"), (r"\bGraphQL\b", None), (r"\bMicroservices\b", None),
    (r"\bReact\b", None), (r"\bAngular\b", None), (r"\bVue\b", None), (r"\bVue\.?js\b", "Vue"),
    (r"\bSvelte\b", None),     (r"\bNext\.?js\b", "Next.js"),
    (r"\bTableau\b", None), (r"\bPower\s*BI\b", "Power BI"), (r"\bPowerBI\b", "Power BI"),
    (r"\bExcel\b", None), (r"\bLooker\b", None),     (r"\bMetabase\b", None),
    (r"\bScrum\b", None), (r"\bAgile\b", None), (r"\bJira\b", None),
    (r"\bConfluence\b", None),
    (r"\b(?:in|auf)\s+(?:Deutsch|German)\b", "Almanca"),
    (r"\bdeutschsprachig\b", "Almanca"), (r"\bdeutschsprachigen\b", "Almanca"),
    (r"\bGerman\s+(?:A1|A2|B1|B2|C1|C2)\b", "Almanca"),
    (r"\bDeutsch\s+(?:A1|A2|B1|B2|C1|C2)\b", "Almanca"),
    (r"\b(?:fluent|proficient|native|business)\s+(?:in\s+)?(?:German|Deutsch)\b", "Almanca"),
    (r"\b(?:German|Deutsch)\s+(?:fluent|proficient|native|speaking)\b", "Almanca"),
    (r"\bGerman\s+speaking\b", "Almanca"), (r"\bGerman\s+speaker\b", "Almanca"),
    (r"\bDeutschkenntnisse\b", "Almanca"), (r"\bDeutschkenntnissen\b", "Almanca"),
    (r"\b(?:fließend|verhandlungssicher)\s+Deutsch\b", "Almanca"),
    (r"\bDeutsch\s+(?:fließend|verhandlungssicher)\b", "Almanca"),
    (r"\b(?:German|Deutsch)\s+(?:language|skills?|required|mandatory)\b", "Almanca"),
    (r"\b(?:knowledge|command)\s+of\s+(?:German|Deutsch)\b", "Almanca"),
    (r"\bFluent\s+German\b", "Almanca"), (r"\bAlmanca\b", "Almanca"),
    (r"\bGerman\b", "Almanca"),     (r"\bDeutsch\b", "Almanca"),
    (r"\bexperience\s+with\s+(Python|Java|SQL|AWS|Azure|Docker|React|Spark|Kafka)\b", None),
    (r"\b(Python|Java|SQL|AWS|Azure|TensorFlow|PyTorch|React)\s+experience\b", None),
    (r"\bproficient\s+in\s+(Python|Java|SQL|React|JavaScript|R)\b", None),
    (r"\b(?:knowledge|background)\s+in\s+(Python|Java|SQL|R|Scala)\b", None),
    (r"\bErfahrung(?:\w*)\s+mit\s+(Python|Java|SQL|R|Scala|AWS|Azure|Docker|React|Spark)\b", None),
    (r"\bKenntnisse(?:\w*)\s+(?:im|in)\s+(?:Bereich\s+)?(Python|Java|SQL|Forecasting|Statistik)\b", None),
    (r"\b(?:sicher\s+)?(?:im\s+Umgang\s+mit|Umgang\s+mit)\s+(Python|Java|SQL)\b", None),
    (r"\bDatenbank\b", "SQL"), (r"\bDatenbanksysteme\b", "SQL"),
    (r"\bForecasting\b", None), (r"\bStatistik\b", "Statistics"),
    (r"\bEnglischkenntnisse\b", "English"), (r"\bEnglischkenntnissen\b", "English"),
    (r"\bDeutsch-?\s*und\s+Englischkenntnisse\b", "Almanca"),
    (r"\bEnglish\s+(?:A1|A2|B1|B2|C1|C2|fluent|native|proficient|business)\b", None),
    (r"\bFluent\s+English\b", "English"), (r"\bBilingual\b", None),
]

_FALLBACK_SKILLS = [
    "Python", "Java", "SQL", "AWS", "Azure", "Docker", "Kubernetes", "Git",
    "React", "Angular", "JavaScript", "TypeScript", "Scala", "Spark", "Kafka",
    "TensorFlow", "PyTorch", "Linux", "Agile", "Scrum", "REST", "API",
    "PostgreSQL", "MongoDB", "Redis", "Excel", "Tableau", "ETL", "CI/CD",
    "German", "Deutsch", "Analytics", "ML", "NLP",
    "Datenbank", "Forecasting", "Statistik",
]

_FALLBACK_NORMALIZE = {"Datenbank": "SQL", "Statistik": "Statistics", "Forecasting": "Forecasting"}


def _extract_skills_loose(text: str) -> list[str]:
    if not text:
        return []
    found = []
    for skill in _FALLBACK_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            s = _FALLBACK_NORMALIZE.get(skill, skill)
            if s == skill and skill in ("German", "Deutsch"):
                s = "Almanca"
            found.append(s)
    return found


def extract_skills(text: str) -> list[str]:
    if not text or not isinstance(text, str):
        return []
    text = text.replace("\n", " ").replace("\r", " ")
    skills = []
    for pat, norm in SKILLS_PATTERNS:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            s = (norm if norm else (m if isinstance(m, str) else (m[0] if isinstance(m, (list, tuple)) else str(m))))
            if s:
                skill = s.strip() if isinstance(s, str) else str(s)
                if skill:
                    skills.append(skill)
    if not skills:
        skills = _extract_skills_loose(text)
    return skills


def process_jobs(jobs: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_skills = []
    rows = []
    for job in jobs:
        desc = job.get("description", "") or ""
        title = job.get("title", "") or ""
        combined = f"{title} {desc}"
        skills = list(dict.fromkeys(extract_skills(combined)))
        all_skills.extend(skills)
        rows.append({
            "id": job.get("id"),
            "title": job.get("title", ""),
            "query": job.get("query", ""),
            "skills_found": " | ".join(skills[:15]) if skills else "",
        })

    _ACRONYMS = {"ml", "api", "nlp", "sql", "etl", "rest", "ci/cd", "aws", "gcp"}
    def _norm(s: str) -> str:
        return s.upper() if s.strip().lower() in _ACRONYMS else s.strip().title()
    counts = Counter(_norm(s) for s in all_skills)
    return pd.DataFrame(rows), pd.DataFrame(counts.most_common(), columns=["skill", "count"])


def run_nlp(jobs: list[dict] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    import json
    from config import JOBS_RAW, JOBS_PROCESSED, SKILLS_COUNTS

    if jobs is None:
        if not JOBS_RAW.exists():
            raise FileNotFoundError(f"Önce veri çekin: python data_fetcher.py\nBeklenen: {JOBS_RAW}")
        with open(JOBS_RAW, encoding="utf-8") as f:
            jobs = json.load(f)

    df_jobs, df_skills = process_jobs(jobs)
    df_jobs.to_csv(JOBS_PROCESSED, index=False)
    df_skills.to_csv(SKILLS_COUNTS, index=False)
    return df_jobs, df_skills
