import os
import time
import undetected_chromedriver as uc

def linkedin_manual_login():
    print("=== MANUELLER LINKEDIN LOGIN ===")
    
    project_path = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(project_path, "indeed_profile")
    
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    
    print(f"Nutze Profilordner: {profile_path}")
    print("Starte Browser... Bitte logge dich jetzt ein.")
    
    try:
        driver = uc.Chrome(
            options=options,
            version_main=149,
            user_data_dir=profile_path
        )
        
        # Rufe direkt die Login-Seite auf
        driver.get("https://www.linkedin.com/login")
        
        print("\n🔒 AKTION ERFORDERLICH:")
        print("1. Logge dich im geöffneten Chrome-Fenster bei LinkedIn ein.")
        print("2. Bestätige eventuelle Sicherheitsabfragen (2FA, E-Mail-Code, Captcha).")
        print("3. Sobald du deinen ganz normalen LinkedIn-Feed siehst, schließe das Skript hier im Terminal mit STRG + C.")
        
        # Hält den Browser offen, bis du im Terminal abbrichst
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n✅ Login-Session beendet. Deine Cookies wurden im Profil gespeichert!")
    except Exception as e:
        print(f"\n❌ Fehler beim Browser-Start: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    linkedin_manual_login()