import requests

def list_braunschweig_titles(keyword="Data Science", size=100):
    url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
    
    headers = {
        "X-API-Key": "jobboerse-jobsuche",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    params = {
        "was": keyword,
        "size": size,
        "page": 1
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Fehler: {response.status_code}")
        return
        
    data = response.json()
    # Wir greifen direkt auf die 'ergebnisliste' zu, die wir im Raw-JSON entdeckt haben
    jobs = data.get("ergebnisliste", [])
    
    print(f"📋 Gefundene Jobtitel für '{keyword}' in Braunschweig (Total Treffer: {data.get('maxErgebnisse')}):\n")
    print(f"{'#':<3} | {'Unternehmen':<30} | {'Jobtitel'}")
    print("-" * 80)
    
    for index, job in enumerate(jobs):
        # Nutzen der exakten Key-Namen aus dem Raw-Response
        title = job.get("stellenangebotsTitel", "Kein Titel")
        company = job.get("firma", "Unbekannte Firma")
        
        print(f"{index + 1:<3} | {company[:30]:<30} | {title}")

if __name__ == "__main__":
    list_braunschweig_titles(keyword="Masterarbeit Data Science")