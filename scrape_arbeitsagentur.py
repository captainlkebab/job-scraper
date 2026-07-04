import os
import json
import base64
import time
import requests
from datetime import datetime

def fetch_full_arbeitsagentur_jobs(keyword="Masterarbeit Data Science", size=50):
    print(f"🔍 Starte bundesweite Tiefen-Suche nach: '{keyword}'...")
    
    url_search = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
    headers = {
        "X-API-Key": "jobboerse-jobsuche",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    params = {
        "was": keyword,
        "size": size,
        "page": 1,
        "prio": "datum"
    }
    
    try:
        response = requests.get(url_search, headers=headers, params=params, timeout=12)
        response.raise_for_status()
        search_data = response.json()
    except Exception as e:
        print(f"❌ Fehler bei der initialen Suche: {e}")
        return []
        
    raw_jobs = search_data.get("ergebnisliste", [])
    total_found = search_data.get("maxErgebnisse", 0)
    print(f"🎯 {len(raw_jobs)} Treffer auf Seite 1 gefunden (Gesamt-Datenbanktreffer: {total_found}).")
    
    detailed_jobs = []
    
    for index, job in enumerate(raw_jobs):
        ref_nr = job.get("referenznummer")
        title = job.get("stellenangebotsTitel", "Kein Titel")
        company = job.get("firma", "Unbekanntes Unternehmen")
        
        if not ref_nr:
            continue
            
        print(f"   ↳ [{index + 1}/{len(raw_jobs)}] Rufe Tiefen-Details ab für ID {ref_nr}...")
        
        # Referenznummer für die v4-Detail-API in Base64 umwandeln
        ref_encoded = base64.b64encode(ref_nr.encode('utf-8')).decode('utf-8')
        url_detail = f"https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/{ref_encoded}"
        
        try:
            detail_response = requests.get(url_detail, headers=headers, timeout=10)
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                
                # HTML-Beschreibung dekodieren und säubern
                raw_desc = detail_data.get("stellenangebotsBeschreibung", "")
                clean_desc = requests.utils.unquote(raw_desc)
                
                # Wir mergen die Metadaten aus der Suche mit den vollen API-Details
                full_job_info = {
                    "id": ref_nr,
                    "title": title,
                    "company": company,
                    "description": clean_desc,
                    "source": "Arbeitsagentur",
                    "scraped_at": datetime.now().isoformat(),
                    # Hier speichern wir das komplette, ungefilterte Detail-Objekt der API ab
                    "api_raw_details": detail_data 
                }
                
                detailed_jobs.append(full_job_info)
            else:
                print(f"   ⚠️ Detail-API gab Status {detail_response.status_code} zurück.")
        except Exception as e:
            print(f"   ⚠️ Fehler beim Laden der Details: {e}")
            
        # Höfliches Delay für das Bundes-Backend
        time.sleep(0.6)
        
    return detailed_jobs

if __name__ == "__main__":
    output_dir = "jobs_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Extraktion ausführen
    jobs_list = fetch_full_arbeitsagentur_jobs(keyword="Masterarbeit Data Science", size=50)
    
    # Speichern unter Arbeitsamt_YY-MM-DD.json
    date_str = datetime.now().strftime("%y-%m-%d")
    output_path = f"{output_dir}/Arbeitsamt_{date_str}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs_list, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Daten erfolgreich exportiert!")
    print(f"📂 Speicherort: {output_path}")
    print(f"📊 Datensätze mit vollständiger Beschreibung: {len(jobs_list)}")