# AI-Driven Job Scraper & Cover Letter Generator

Ein automatisiertes End-to-End-System zur Aggregation von Stellenanzeigen und zur dynamischen, KI-gestützten Generierung maßgeschneiderter Anschreiben für Masterarbeiten im Bereich Data Science.

The system automates the job search workflow by scraping listings, filtering relevant roles, and utilizing Large Language Models (LLMs) to construct contextualized cover letters without corporate buzzword redundancies.

## 🏗️ Systemarchitektur

1. **Extraction (Selenium):** Durchsucht Jobbörsen (z. B. Indeed), handhabt dynamische Inhalte und bietet verlängerte Timeouts für manuelle Authentifizierungs-Schnittstellen (Captchas/Logins).
2. **Analysis & Matching (Groq API / Llama 3.3):** Analysiert die extrahierte Stellenbeschreibung anhand eines hinterlegten Bewerberprofils und extrahiert strukturierte JSON-Daten (bereinigte Titel, dedizierte Aufgabenbereiche, Ansprechpartner).
3. **Document Generation (`python-docx` & `docx2pdf`):** Erstellt formatierte DIN-5008-konforme Anschreiben als `.docx` und exportiert diese direkt als `.pdf`.

## 📁 Projektstruktur

```text
├── coverLetters/           # Generierte Anschreiben, sortiert nach Datum
│   └── CL_YY-MM-DD/        # Tagesaktueller Output-Ordner
│       ├── Anschreiben_Firma_Titel.docx
│       └── Anschreiben_Firma_Titel.pdf
├── jobs_output/            # Extrahierte Job-Rohdaten aus dem Scraper
│   └── indeed_YY-MM-DD.json
├── generate_cover_letter.py # KI-Pipeline & Dokumentengenerierung
├── scraper_indeed.py       # Selenium-Scraper für Indeed
├── .env                    # Umgebungsvariablen (Groq API Key)
└── README.md
```
