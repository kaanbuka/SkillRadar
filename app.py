import json
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from config import JOBS_RAW, JOBS_PROCESSED, SKILLS_COUNTS
from nlp_engine import run_nlp

try:
    from ai_skill_extractor import run_ai_enrichment
    import ai_skill_extractor as ai_mod
    AI_AVAILABLE = True
    AI_CONFIGURED = ai_mod.USE_OLLAMA or bool(ai_mod.OPENAI_API_KEY)
except ImportError:
    AI_AVAILABLE = False
    AI_CONFIGURED = False

st.set_page_config(page_title="SkillRadar", page_icon="🇩🇪", layout="wide")


def load_data():
    jobs = []
    if JOBS_RAW.exists():
        with open(JOBS_RAW, encoding="utf-8") as f:
            jobs = json.load(f)
    if not jobs:
        sample = Path(__file__).parent / "data" / "sample_jobs.json"
        if sample.exists():
            with open(sample, encoding="utf-8") as f:
                jobs = json.load(f)
    df_jobs = pd.read_csv(JOBS_PROCESSED) if JOBS_PROCESSED.exists() else pd.DataFrame()
    df_skills = pd.read_csv(SKILLS_COUNTS) if SKILLS_COUNTS.exists() else pd.DataFrame()
    return jobs, df_jobs, df_skills


def main():
    st.title("SkillRadar – Almanya Yetenek Analizi")
    st.markdown("*Almanya veri bilimi / yazılım ilanlarından en çok aranan yetenekler*")

    jobs, df_jobs, df_skills = load_data()

    if not jobs and df_skills.empty:
        st.warning("Veri bulundu ama işlenmemiş. 'NLP Çalıştır' ile yetenekleri çıkarın.")
    elif not jobs:
        st.info(
            "Veri yok. Önce `python data_fetcher.py` ile Adzuna API'den veri çekin. "
            "ADZUNA_APP_ID ve ADZUNA_APP_KEY gerekli ([developer.adzuna.com](https://developer.adzuna.com/))."
        )
        return

    st.caption(f"{len(jobs)} ilan yüklendi")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 NLP ile Yetenekleri Çıkar"):
            with st.spinner("İşleniyor..."):
                df_jobs, df_skills = run_nlp(jobs)
                st.success("Tamamlandı!")
                st.rerun()
    with col2:
        if AI_AVAILABLE:
            with st.expander("AI ile Zenginleştir", expanded=False):
                mode = "Ollama (ücretsiz)" if ai_mod.USE_OLLAMA else "OpenAI"
                st.caption(f"Mod: {mode}")
                ai_max = st.slider("İşlenecek ilan sayısı", 10, 150, 50, 10,
                    help="Az = hızlı. Önce 0 skill'li ilanlara uygulanır.")
                if st.button("AI ile Eksik Yetenekleri Bul"):
                    if not AI_CONFIGURED:
                        st.error("AI_USE_OLLAMA=true veya OPENAI_API_KEY gerekli (.env)")
                    else:
                        with st.spinner("AI ilanları okuyor..."):
                            try:
                                df_jobs, df_skills = run_ai_enrichment(jobs, max_jobs=ai_max)
                                st.success(f"{ai_max} ilan zenginleştirildi!")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
        else:
            st.caption("AI: pip install openai")

    if not df_skills.empty:
        top_n = st.slider("Top yetenek sayısı", 5, 25, 10)
        top = df_skills.head(top_n)

        st.subheader(f"Almanya'da En Çok Aranan {top_n} Yetenek")

        st.bar_chart(top.set_index("skill")["count"])

        st.dataframe(top, use_container_width=True, hide_index=True)

        st.subheader("Yetenek Dağılımı")
        if plt is not None:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(top["count"], labels=top["skill"], autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)
            plt.close()

    if not df_jobs.empty:
        with st.expander("İlan Önizlemesi (ilk 10)"):
            preview = df_jobs.head(10).copy()
            preview["skills_found"] = preview["skills_found"].fillna("").replace("", "—")
            st.dataframe(preview, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
