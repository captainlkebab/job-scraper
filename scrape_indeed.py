import os
import re
import time
import random
import json
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import getpass

def slugify(text):
    """Bereinigt Strings, falls wir später doch Dateinamen brauchen."""
    text = text.strip().replace('\n', '').replace('\r', '')
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    return text[:60]


def load_all_scraped_ids(directory):
    """
    Scant den Ausgabeordner nach allen bisherigen 'indeed_*.json' Dateien
    und extrahiert alle bereits gescrapten Job-IDs.
    """
    scraped_ids = set()
    if not os.path.exists(directory):
        return scraped_ids
        
    for filename in os.listdir(directory):
        if filename.startswith("indeed_") and filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    jobs = json.load(f)
                    for job in jobs:
                        if "id" in job:
                            scraped_ids.add(job["id"])
            except Exception as e:
                print(f"⚠️ Konnte Datei {filename} nicht für Historie lesen: {e}")
                
    return scraped_ids

def scrape_indeed_to_json():
    output_dir = "jobs_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Load History
    known_ids = load_all_scraped_ids(output_dir)
    print(f"History loaded: {len(known_ids)} bereits bekannte Job-Ids registriert")

    print("Starte getarnten Chrome-Browser für schlanke JSON-Pipeline...")
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')

    project_path = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(project_path, "indeed_profile")
    
    driver = uc.Chrome(options=options, version_main=149, user_data_dir=profile_path)
    
    pages_to_scrape = 5
    scraped_jobs_list = []
    
    try:
        base_url = "https://de.indeed.com/jobs?q=Masterarbeit+Data+Science&l=Deutschland&sort=date"            
        print(f"\n🚀 Rufe Startseite auf...")
        driver.get(base_url)
        time.sleep(random.uniform(6.0, 8.0))
        
        try:
            driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
            print("Cookie-Banner akzeptiert.")
            time.sleep(1.5)
        except:
            pass

        for page in range(pages_to_scrape):
            print(f"\n Verarbeite aktuell Seite {page + 1 }...")

            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.ID, "mosaic-provider-jobcards"))
                )
            except:
                print("Ende der Ergebnisse oder Ladefehler auf dieser Seite.")
                break
        
            job_cards = driver.find_elements(By.XPATH, "//li//a[@data-jk]")
            print(f"Gefundene Karten auf Seite {page + 1}: {len(job_cards)}")
            
            for index, card in enumerate(job_cards):
                try:
                    jk_id = card.get_attribute("data-jk")
                    if not jk_id:
                        continue
                    
                    # Duplicate Check
                    if jk_id in known_ids: 
                        print(f" [Duplikat] ID {jk_id} beretis in Historie vorhanden. Wird übersprungen.")
                        continue

                    # Titel direkt aus dem inneren Span holen
                    try:
                        job_title = card.find_element(By.TAG_NAME, "span").text.strip().replace('\n', ' ')
                    except:
                        continue # Wenn kein Titel lesbar ist, ist es keine valide Karte

                    if not job_title or len(job_title) < 3:
                        continue

                    print(f"   -> [{len(scraped_jobs_list) + 1}] {job_title}")

                    # Scrollen & Klicken für das rechte Beschreibungs-Panel
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(random.uniform(0.5, 1.2))
                    try:
                        card.click()
                    except:
                        driver.execute_script("arguments[0].click();", card)
                    
                    time.sleep(random.uniform(3.5, 4.5))
                    
                    # Vollständige Beschreibung auslesen
                    try:
                        description = driver.find_element(By.ID, "jobDescriptionText").text.strip()
                    except:
                        description = "Beschreibung konnte nicht geladen werden."
                    
                    # Bewerbungs-Link abgreifen
                    try:
                        apply_link_element = driver.find_element(By.XPATH, "//div[@id='applyButtonLinkContainer']//button | //a[contains(@class, 'ia-ApplyButton')]")
                        apply_url = apply_link_element.get_attribute("href") or card.get_attribute("href")
                    except:
                        apply_url = card.get_attribute("href")
                        
                    if apply_url and apply_url.startswith("/"):
                        apply_url = "https://de.indeed.com" + apply_url

                    # JSON-Objekt befüllen
                    job_data = {
                        "id": jk_id,
                        "title": job_title,
                        "apply_url": apply_url,
                        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "description": description
                    }
                    
                    scraped_jobs_list.append(job_data)
                        
                except Exception as item_error:
                    continue

            # echte pagination
            if page < pages_to_scrape - 1 :
                try:
                    print(f"\n -> Umblättern zur Seite {page + 2}")

                    next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next Page' or @aria-label='Weiter' or contains(@data-testid, 'pagination-page-next')]")
                    
                    # Zum Element scrollen, um Interaktionsfehler zu vermeiden
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(random.uniform(1.5, 2.5))
                    
                    try:
                        next_button.click()
                    except:
                        driver.execute_script("arguments[0].click();", next_button)
                    
                    # Pause für den Seitenaufbau
                    time.sleep(random.uniform(6.0, 8.5))
                    
                except Exception as e:
                    print(f"🛑 Kein 'Weiter'-Button mehr vorhanden oder das Ende des Feeds wurde erreicht.")
                    break

        # --- SPEICHERN ALS JSON MIT DATUM IM NAMEN ---
        if scraped_jobs_list:
            # Formatiert das Datum exakt zu YY-MM-DD (z.B. 26-06-13)
            date_str = datetime.now().strftime("%y-%m-%d")
            json_filename = f"{output_dir}/indeed_{date_str}.json"
            
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(scraped_jobs_list, json_file, indent=4, ensure_ascii=False)
                
            print(f"\n🎉 FERTIG! {len(scraped_jobs_list)} Jobs erfolgreich in '{json_filename}' exportiert.")
        else:
            print("\n⚠️ Keine Jobs zum Speichern gefunden.")
            
    except Exception as e:
        print(f"❌ Kritischer Pipeline-Fehler: {e}")
    finally:
        print("Schließe Browser...")
        try:
            driver.close()
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    scrape_indeed_to_json()