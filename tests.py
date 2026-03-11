import requests
import time
import sqlite3

url = "https://api-ratp.pierre-grimaud.fr/v1/schedules/rers/a/chatelet+les+halles/A"

# Ton test reste le même
response = requests.get(url)
# ... le reste de ton code pour enregistrer en base ..."

def run_test():
    start_time = time.time()
    status_code = None
    contrat_valide = False
    error_message = None

    # Robustesse : 1 retry max (donc 2 tentatives en tout)
    for attempt in range(2):
        try:
            # Timeout de 3 secondes
            response = requests.get(URL, timeout=3)
            status_code = response.status_code
            
            # Gestion 429 (Rate Limit)
            if status_code == 429:
                error_message = "Rate limit atteint (429)"
                time.sleep(2) # Backoff avant le retry
                continue
                
            response.raise_for_status()
            data = response.json()
            
            # Contrat (Vérification des champs attendus)
            assert "total_count" in data
            assert "results" in data
            assert isinstance(data["results"], list)
            
            contrat_valide = True
            error_message = None
            break # Si on arrive ici, tout est bon, on sort de la boucle de retry
            
        except AssertionError:
            error_message = "Le JSON ne respecte pas le contrat attendu."
            break # Inutile de retry si le format des données a changé
        except requests.exceptions.Timeout:
            error_message = "Timeout (l'API a mis plus de 3s à répondre)."
        except requests.exceptions.RequestException as e:
            error_message = f"Erreur réseau ou HTTP : {str(e)}"
        
        # Courte pause avant le retry en cas d'erreur
        time.sleep(1)

    # QoS : Calcul de la latence
    latency_ms = (time.time() - start_time) * 1000

    # Sauvegarde dans la base de données
    conn = sqlite3.connect('historique_ratp.db')
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
