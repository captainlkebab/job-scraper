import os
import json
import re
import random
from datetime import datetime

# Importiere deine beiden modularen Teilskripte
from scrape_indeed import scrape_indeed_to_json 
from generate_cover_letter import create_cover_letter_files

def run_automated_application_pipeline():
    print("=== STARTE AUTOMATISIERTE BEWERBUNGS-PIPELINE ===")
    
    # 1. INDEED SCRAPER STARTEN
    print("\n[Schritt 1] Starte Indeed-Scraper...")
    try:
        scrape_indeed_to_json()
    except Exception as e:
        print(f"⚠️ Fehler beim Scraping: {e}")
        print("Versuche, mit bestehenden Scandaten fortzufahren...")

    # 2. HEUTIGE EXPORTDATEI SUCHEN
    date_str = datetime.now().strftime("%y-%m-%d")
    json_path = f"jobs_output/indeed_{date_str}.json"
    
    if not os.path.exists(json_path):
        print(f"❌ Keine aktuelle Scraping-Datei unter {json_path} gefunden. Pipeline abgebrochen.")
        return

    # JSON-Daten laden
    with open(json_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    if not jobs:
        print("ℹ️ Keine Jobs in der heutigen Datei gefunden.")
        return

    print(f"Loaded {len(jobs)} Stellenanzeigen aus dem heutigen Scrape.")

    # 3. FILTERN UND ANSCHREIBEN GENERIEREN
    print("\n[Schritt 2] Filterung und KI-Generierung gestartet...")
    
    # Der Filter sucht nach Masterarbeit, Masterand, Master Thesis oder Abschlussarbeit im Titel
    title_filter = re.compile(r'(masterarbeit|masterand|master\s*thesis|abschlussarbeit)', re.IGNORECASE)
    processed_count = 0

    for job in jobs:
        job_title = job.get("title", "Unbekannter Titel")
        
        # Check, ob der Stellentitel passt
        if not title_filter.search(job_title):
            continue
            
        print(f"\n🎯 Treffer gefunden: '{job_title}'")
        processed_count += 1
        
        # Jobbeschreibung auslesen
        job_description = job.get("description", "")
        
        # Übergabe an dein Anschreiben-Modul (erstellt Word + PDF)
        try:
            pdf_path = create_cover_letter_files(job_title, job_description)
            if pdf_path:
                print(f"✅ Pipeline erfolgreich beendet für: {pdf_path}")
        except Exception as e:
            print(f"❌ Fehler bei der Verarbeitung von '{job_title}': {e}")
            continue
        
        # Kurze Pause einlegen, um die Groq-API-Rate-Limits nicht zu triggern
        delay = random.uniform(2.0, 4.0)
        print(f"Warte {delay:.1f} Sekunden...")

    print(f"\n=== PIPELINE BEENDET ===")
    print(f"Es wurden insgesamt {processed_count} passende Anschreiben generiert.")

if __name__ == "__main__":
    run_automated_application_pipeline()