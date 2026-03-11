import requests
import time
import sqlite3

# 1. L'URL en MAJUSCULES (Variable globale)
URL = "https://api-ratp.pierre-grimaud.fr/v1/schedules/rers/a/chatelet+les+halles/A"

def run_test():
    start_time = time.time()
    status_code = None
    contrat_valide = False
    error_message = None

    for attempt in range(2):
        try:
            # On utilise URL (majuscules)
            response = requests.get(URL, timeout=5) 
            status_code = response.status_code
            
            if status_code == 429:
                error_message = "Rate limit atteint (429)"
                time.sleep(2)
                continue
                
            response.raise_for_status()
            data = response.json()
            
            # Vérification du contrat simplifiée pour le proxy de Pierre Grimaud
            # On vérifie juste si on a bien une clé 'result' ou 'schedules'
            contrat_valide = "result" in data
            error_message = None
            break 
            
        except requests.exceptions.Timeout:
            error_message = "Timeout (> 5s)"
        except Exception as e:
            error_message = f"Erreur : {str(e)}"
        
        time.sleep(1)

    latency_ms = (time.time() - start_time) * 1000

    # 2. Utilise le chemin COMPLET pour éviter l'erreur "no such table"
    conn = sqlite3.connect('/home/loic75/mysite/historique_ratp.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO api_runs (endpoint_tested, status_code, latency_ms, contrat_valide, error_message)
        VALUES (?, ?, ?, ?, ?)
    """, (URL, status_code, latency_ms, contrat_valide, error_message))
    
    conn.commit()
    conn.close()
    
    print(f"🏁 Test terminé | Succès : {contrat_valide} | Latence : {latency_ms:.0f}ms")

if __name__ == '__main__':
    run_test()
