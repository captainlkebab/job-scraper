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
from selenium.webdriver.common.keys import Keys

def load_all_scraped_ids(directory):
    """Lädt alle bereits bekannten IDs plattformübergreifend."""
    scraped_ids = set()
    if not os.path.exists(directory):
        return scraped_ids
        
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    jobs = json.load(f)
                    for job in jobs:
                        if "id" in job:
                            scraped_ids.add(job["id"])
            except:
                pass
    return scraped_ids

def scrape_linkedin_to_json():
    output_dir = "jobs_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Historie laden (verhindert doppelte Bearbeitung)
    known_ids = load_all_scraped_ids(output_dir)
    print(f"History loaded: {len(known_ids)} bereits bekannte Job-Ids registriert.")

    print("Starte getarnten Chrome-Browser für LinkedIn...")
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')

    project_path = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(project_path, "indeed_profile") # Nutzt dein eingeloggtes Profil
    
    driver = uc.Chrome(options=options, version_main=149, user_data_dir=profile_path)
    
    scraped_jobs_list = []
    
    try:
        print("🌍 Rufe LinkedIn Startseite auf, um Login-Cookies zu aktivieren...")
        driver.get("https://www.linkedin.com")
        time.sleep(random.uniform(4.0, 5.0))
        
        # Wir tasten uns durch die ersten 3 Seiten (kannst du oben anpassen)
        pages_to_scrape = 3
        
        for page in range(pages_to_scrape):
            print(f"\n📄 [LinkedIn] Verarbeite aktuell Seite {page + 1}...")
            
            if page == 0:
                base_url = "https://www.linkedin.com/jobs/search/?keywords=Master%20Thesis%20Data%20Science&location=Deutschland&sortBy=DD"
                driver.get(base_url)
            
            time.sleep(random.uniform(6.0, 8.5))
            
            # 1. ROBUSTES SCROLLEN: Wir nutzen die Job-Karten selbst zum Scrollen!
            print("Triggere Lazy Loading über Karten-Scroll...")
            try:
                # Suche nach allen aktuell verfügbaren Kartenelementen
                temp_cards = driver.find_elements(By.XPATH, "//li[@data-job-id] | //div[@data-job-id]")
                # Scrolle zu jeder 5. Karte, um den Infinite Scroll sanft auszulösen
                for i in range(0, len(temp_cards), 5):
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", temp_cards[i])
                    time.sleep(random.uniform(0.8, 1.2))
            except Exception as scroll_err:
                print(f"⚠️ Alternatives Scrollen aktiv...")
                # Fallback: Schicke einfach 5-mal "Bild-Abwärts" an die Seite
                for _ in range(5):
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                    time.sleep(1.0)

            # 2. Alle geladenen Job-Karten einsammeln
            job_elements = driver.find_elements(By.XPATH, "//li[@data-job-id] | //div[@data-job-id] | //a[contains(@class, 'job-card-list__title')]")
            
            unique_elements = []
            seen_card_ids = set()
            
            for el in job_elements:
                jid = el.get_attribute("data-job-id")
                if not jid and el.tag_name == "a":
                    href = el.get_attribute("href")
                    match = re.search(r'/view/(\d+)', href) if href else None
                    if match:
                        jid = match.group(1)
                
                if jid and jid not in seen_card_ids:
                    seen_card_ids.add(jid)
                    unique_elements.append((jid, el))

            print(f"Echte, eindeutige Karten auf Seite {page + 1} erkannt: {len(unique_elements)}")
            
            title_whitelist = re.compile(r'(masterarbeit|master\s*thesis|abschlussarbeit|masterand)', re.IGNORECASE)
            
            # 3. Karten verarbeiten
            for linkedin_id, element in unique_elements:
                try:
                    if linkedin_id in known_ids:
                        continue
                    
                    job_title = "Unbekannter Titel"
                    try:
                        job_title = element.text.split('\n')[0].strip()
                        if len(job_title) < 5:
                            job_title = element.find_element(By.XPATH, ".//a[contains(@class, 'job-card-list__title') or contains(@class, 'job-card-container__link')]").text.strip()
                    except:
                        pass

                    if not title_whitelist.search(job_title):
                        print(f"   [Skipped] {job_title}")
                        continue

                    print(f"   🔥 [RELEVANT] -> [{len(scraped_jobs_list) + 1}] {job_title}")
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(random.uniform(0.6, 1.2))
                    
                    try:
                        element.click()
                    except:
                        driver.execute_script("arguments[0].click();", element)
                    
                    time.sleep(random.uniform(4.0, 5.5))
                    
                    description = "Beschreibung konnte nicht geladen werden."
                    for selector in ["job-details", "jobs-description-content__text", "jobs-box__html-content"]:
                        try:
                            desc_el = driver.find_element(By.ID, selector) if selector == "job-details" else driver.find_element(By.CLASS_NAME, selector)
                            txt = desc_el.text.strip()
                            if len(txt) > 50:
                                description = txt
                                break
                        except:
                            continue
                    
                    apply_url = f"https://www.linkedin.com/jobs/view/{linkedin_id}/"
                    
                    job_data = {
                        "id": linkedin_id,
                        "title": job_title,
                        "apply_url": apply_url,
                        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "description": description
                    }
                    
                    scraped_jobs_list.append(job_data)
                    known_ids.add(linkedin_id)
                    
                except Exception as item_error:
                    continue

            # 4. ECHTE PAGINATION (Umblättern zur nächsten Seite)
            if page < pages_to_scrape - 1:
                try:
                    print(f"\n➔ Versuche umzublättern auf die nächste LinkedIn-Seite...")
                    # LinkedIn nutzt ein aria-label mit der Seitennummer für die Buttons
                    next_page_num = page + 2
                    next_button = driver.find_element(By.XPATH, f"//button[@aria-label='Seite {next_page_num}' or @aria-label='Page {next_page_num}']")
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(random.uniform(1.5, 2.5))
                    
                    try:
                        next_button.click()
                    except:
                        driver.execute_script("arguments[0].click();", next_button)
                    
                    print(f"Klick erfolgreich. Warte auf den Aufbau von Seite {next_page_num}...")
                    
                except Exception as page_err:
                    print(f"🛑 Keine weitere Seitenschaltfläche gefunden oder Ende des Feeds erreicht.")
                    break
                
        # 4. Ergebnisse abspeichern
        if scraped_jobs_list:
            date_str = datetime.now().strftime("%y-%m-%d")
            json_filename = f"{output_dir}/linkedin_{date_str}.json"
            
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(scraped_jobs_list, json_file, indent=4, ensure_ascii=False)
                
            print(f"\n🎉 FERTIG! {len(scraped_jobs_list)} LinkedIn-Jobs erfolgreich exportiert in '{json_filename}'.")
        else:
            print("\n⚠️ Keine neuen LinkedIn-Jobs gefunden.")
            
    except Exception as e:
        print(f"❌ Kritischer Fehler im LinkedIn-Scraper: {e}")
    finally:
        print("Schließe Browser...")
        try:
            driver.close()
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    scrape_linkedin_to_json()