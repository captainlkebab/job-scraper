import os
import json
import pandas as pd
import streamlit as str

str.set_page_config(page_title="Masterarbeit Data Science Tracker", layout="wide")

def get_latest_processed_file(directory):
    """Findet die neueste processed_jobs_YY-MM-DD.json."""
    files = [f for f in os.listdir(directory) if f.startswith("processed_jobs_") and f.endswith(".json")]
    if not files:
        return None
    files.sort(reverse=True) # Neueste Datei nach Datum zuerst
    return os.path.join(directory, files[0])

str.title("🎯 Masterarbeit Data Science - Job-Pipeline")
str.markdown("Dieses Dashboard zeigt dir die am besten passenden Ausschreibungen, basierend auf deinem Tech-Score.")

input_dir = "jobs_output"
latest_file = get_latest_processed_file(input_dir)

if not latest_file:
    str.warning("Keine verarbeiteten Job-Dateien im Ordner 'jobs_output' gefunden. Lass zuerst process_jobs.py laufen!")
else:
    str.info(f"📂 Lade aktuelle Daten aus: `{latest_file}`")
    
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if not data:
        str.success("Für heute wurden alle Jobs ausgefiltert (keine relevanten Masterarbeiten).")
    else:
        # Daten für die Tabelle aufbereiten
        display_data = []
        for job in data:
            display_data.append({
                "Score": job["score"],
                "Titel": job["title"],
                "High Matches": ", ".join(job["tech_matches"]["high"]),
                "Med Matches": ", ".join(job["tech_matches"]["medium"]),
                "Gescrapt am": job["scraped_at"],
                "Link": job["apply_url"],
                "id": job["id"],
                "description": job["description"]
            })
            
        df = pd.DataFrame(display_data)
        
        # --- UI-FILTER ---
        score_filter = str.slider("Mindest-Score filtern:", min_value=int(df["Score"].min()), max_value=int(df["Score"].max()), value=0)
        df_filtered = df[df["Score"] >= score_filter]
        
        # --- TABELLEN-ÜBERSICHT ---
        str.subheader(f"Gefundene Stellen ({len(df_filtered)})")
        
        # Spalten-Konfiguration für klickbare Links
        str.dataframe(
            df_filtered[["Score", "Titel", "High Matches", "Med Matches", "Gescrapt am"]],
            use_container_width=True
        )
        
        # --- DETAIL-ANSICHT & LLM-VORSCHAU ---
        str.markdown("---")
        str.subheader("🔍 Job-Details & Beschreibung einsehen")
        
        selected_job_title = str.selectbox("Wähle einen Job für die Volltext-Anzeige:", df_filtered["Titel"].tolist())
        
        if selected_job_title:
            job_details = df_filtered[df_filtered["Titel"] == selected_job_title].iloc[0]
            
            col1, col2 = str.columns([1, 2])
            with col1:
                str.metric(label="Berechneter Tech-Score", value=int(job_details["Score"]))
                str.markdown(f"**Bewerbungs-Link:** [Direkt zu Indeed]({job_details['Link']})")
                str.markdown(f"**Interne ID:** `{job_details['id']}`")
                
                # Hier bereiten wir den Platzhalter für den AI-Copiloten vor
                str.info("🤖 **AI-Copilot Status:** Bereit für Anschreiben-Generierung.")
                if str.button("✨ Anschreiben entwerfen (LLM)"):
                    str.write("*Hier klinken wir im nächsten Schritt die KI ein...*")
                    
            with col2:
                str.markdown("**Vollständige Jobbeschreibung:**")
                str.text_area("", job_details["description"], height=400)