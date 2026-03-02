# 🇩🇪 Tech-Stack NLP Analyzer

> Almanya'daki Data Science ve Yazılım iş ilanlarından **en çok aranan yetenekleri** otomatik olarak çıkaran NLP projesi. İş piyasası trendlerini veriye dayalı analiz eder.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Adzuna API](https://img.shields.io/badge/Adzuna%20API-Jobs%20Data-green)](https://developer.adzuna.com/)

---

## Proje Özeti

Bu proje, Almanya'daki Data Science, Software Engineering ve ilgili alanlardaki iş ilanlarını toplayarak **hangi teknik yeteneklerin en çok talep gördüğünü** NLP yöntemleriyle çıkarır. Erasmus, staj veya kariyer planlaması yapanlar için paha biçilmez bir veri kaynağı sunar.

### Çözülen Problem
- "Hangi yeteneklere yatırım yapmalıyım?" sorusuna veriye dayalı yanıt
- İlan metinlerinden Python, SQL, AWS, Docker vb. 70+ yeteneğin otomatik tespiti
- Almanca ve İngilizce karışık ilan metinlerinin işlenmesi

---

## Kullanılan Teknolojiler

### Backend & Veri İşleme
| Teknoloji | Kullanım Amacı |
|-----------|-----------------|
| **Python 3.10+** | Ana programlama dili |
| **Pandas** | Veri manipülasyonu, CSV işleme, DataFrame analizi |
| **Requests** | REST API çağrıları (Adzuna Jobs API) |
| **re (Regex)** | 70+ pattern ile yetenek çıkarma, bağlamsal eşleşme |
| **Collections.Counter** | Yetenek frekans analizi |

### NLP & Metin İşleme
| Teknoloji | Kullanım Amacı |
|-----------|-----------------|
| **Regex Pattern Matching** | Programlama dilleri, framework’ler, cloud araçları tespiti |
| **Keyword Fallback** | Regex ile kaçırılan yeteneklerin ikincil taraması |
| **Bilingual NLP** | Almanca (Deutschkenntnisse, fließend Deutsch) + İngilizce ifade tanıma |
| **OpenAI API / Ollama** | Opsiyonel: LLM ile eksik yetenek zenginleştirmesi |

### Frontend & Görselleştirme
| Teknoloji | Kullanım Amacı |
|-----------|-----------------|
| **Streamlit** | İnteraktif web dashboard |
| **Matplotlib** | Pasta grafik, yetenek dağılımı |
| **Streamlit Charts** | Bar chart, tablo görselleştirme |

### API & Harici Servisler
| Servis | Kullanım Amacı |
|--------|-----------------|
| **Adzuna Jobs API** | Almanya (de) iş ilanları – ücretsiz tier |
| **OpenAI API** (opsiyonel) | GPT-4o-mini ile yetenek çıkarma |
| **Ollama** (opsiyonel) | Yerel LLM (llama3.2, mistral) – ücretsiz |

### DevOps & Konfigürasyon
| Teknoloji | Kullanım Amacı |
|-----------|-----------------|
| **python-dotenv** | Ortam değişkenleri, API anahtarları yönetimi |
| **Pathlib** | Platform-bağımsız dosya yolu yönetimi |
| **JSON** | Ham ilan verisi depolama |

---

## Özellikler

- **3 Fazlı Veri Pipeline**: Veri çekme → NLP işleme → Dashboard
- **70+ Yetenek Tanıma**: Python, SQL, AWS, Docker, Kubernetes, TensorFlow, React, Almanca C1...
- **Çoklu Şehir Desteği**: Berlin, München, Hamburg, Frankfurt, Köln + tüm Almanya
- **Hybrid NLP**: Regex + opsiyonel AI zenginleştirmesi
- **Rate Limiting**: API çağrılarında gecikme ile güvenli kullanım
- **Tekil İlan Takibi**: `id` bazlı deduplication

---

## Mimari

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Adzuna API    │────▶│  data_fetcher   │────▶│ jobs_raw.json   │
│   (REST/JSON)   │     │  (Veri Madeni)   │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                       │
                                                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit      │◀────│  nlp_engine      │◀────│  Regex +        │
│   Dashboard      │     │  (NLP Pipeline)   │     │  Fallback       │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │ ai_skill_extractor    │
                    │ (Opsiyonel LLM)        │
                    │ OpenAI / Ollama        │
                    └───────────────────────┘
```

---

## Kurulum

```bash
git clone https://github.com/KULLANICI/Tech-Stack-NLP-Analyzer.git
cd Tech-Stack-NLP-Analyzer
pip install -r requirements.txt
```

### Ortam Değişkenleri

`.env` dosyası oluşturun:

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

**Ücretsiz API anahtarı:** [developer.adzuna.com](https://developer.adzuna.com/) → Create Application → Jobs API

---

## 📖 Kullanım

### 1. Veri Toplama
```bash
python data_fetcher.py
```
→ `data/jobs_raw.json` oluşturulur (~500+ ilan)

### 2. NLP İşleme
```bash
python run_nlp.py
```
veya Dashboard üzerinden **"NLP ile Yetenekleri Çıkar"** butonuna tıklayın.
→ `data/jobs_processed.csv`, `data/skills_counts.csv` oluşturulur

### 3. Dashboard
```bash
streamlit run app.py
```
→ `http://localhost:8501`

### 4. (Opsiyonel) AI Zenginleştirme

| Mod | Kurulum | Maliyet |
|-----|---------|---------|
| **Ollama** | `ollama run llama3.2` + `.env` → `AI_USE_OLLAMA=true` | Ücretsiz |
| **OpenAI** | `.env` → `OPENAI_API_KEY=sk-...` | Ücretli |

Dashboard’da **"AI ile Eksik Yetenekleri Bul"** ile regex’in kaçırdığı yetenekler LLM ile tamamlanır.

---

## Proje Yapısı

```
Tech-Stack-NLP-Analyzer/
├── config.py              # API anahtarları, path’ler, arama sorguları
├── data_fetcher.py        # Faz 1: Adzuna API ile veri çekme
├── nlp_engine.py          # Faz 2: Regex + fallback yetenek çıkarma
├── ai_skill_extractor.py  # Opsiyonel: LLM ile yetenek zenginleştirme
├── app.py                 # Faz 3: Streamlit dashboard
├── run_nlp.py             # CLI: NLP pipeline tek komutla çalıştırma
├── data/
│   ├── jobs_raw.json      # Ham ilan verisi
│   ├── jobs_processed.csv # İşlenmiş ilanlar + yetenekler
│   └── skills_counts.csv  # Yetenek frekans tablosu
├── .env                   # API keys (gitignore)
└── requirements.txt
```

---

## NLP Detayları

### Tanınan Yetenek Kategorileri
- **Diller:** Python, Java, SQL, R, Scala, Go, TypeScript...
- **Cloud & DevOps:** AWS, Azure, GCP, Docker, Kubernetes, Terraform...
- **Veri:** Pandas, Spark, Kafka, Airflow, Databricks, Snowflake...
- **ML/AI:** TensorFlow, PyTorch, Scikit-learn, Hugging Face...
- **Web:** React, Angular, Vue, REST API, GraphQL...
- **BI:** Tableau, Power BI, Excel, Looker...
- **Dil Gereksinimleri:** Almanca (A1–C2), English, Deutschkenntnisse...
- **Metodoloji:** Agile, Scrum, Jira, Confluence

### Almanca Desteği
- `Deutschkenntnisse`, `fließend Deutsch`, `German B2`
- `Erfahrung mit Python`, `Kenntnisse in SQL`
- `Datenanalyse`, `Datenbank`, `Statistik`

---

## Gelecek Geliştirmeler

- [ ] spaCy `de_core_news_sm` ile Named Entity Recognition
- [ ] ESCO ontology ile yetenek standardizasyonu
- [ ] Zaman serisi: yetenek trend analizi
- [ ] Şehir bazlı karşılaştırma (Berlin vs München)

---

## Lisans

Bu proje eğitim ve portföy amaçlıdır. Adzuna API kullanım şartlarına uyun.

