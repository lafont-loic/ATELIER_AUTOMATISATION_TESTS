from flask import Flask, render_template, redirect, url_for
import sqlite3
import requests
import time

app = Flask(__name__)

DB_PATH = '/home/loic75/mysite/historique_ratp.db'
URL_API = "https://api-ratp.pierre-grimaud.fr/v1/schedules/rers/a/chatelet+les+halles/A"

@app.route("/")
def consignes():
    return render_template('consignes.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT run_date, status_code, latency_ms, contrat_valide, error_message FROM api_runs ORDER BY run_date DESC")
    runs = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', runs=runs)

@app.route('/run')
def run():
    start_time = time.time()
    status_code = None
    contrat_valide = False
    error_message = None
    
    # On définit 2 tentatives (1 initiale + 1 retry)
    max_attempts = 2
    
    for attempt in range(max_attempts):
        try:
            # On passe à 10s de timeout pour être plus tolérant
            response = requests.get(URL_API, timeout=10)
            status_code = response.status_code
            response.raise_for_status()
            
            data = response.json()
            if "result" in data:
                contrat_valide = True
                error_message = f"Réussi à l'essai {attempt + 1}"
                break  # Succès ! On sort de la boucle de retry
            else:
                error_message = "Structure JSON invalide"
                
        except Exception as e:
            error_message = f"Essai {attempt + 1} échoué: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            # Si c'est le premier échec, on attend une petite seconde avant de retenter
            if attempt == 0:
                time.sleep(1)

    latency_ms = (time.time() - start_time) * 1000

    # Sauvegarde du résultat final
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO api_runs (endpoint_tested, status_code, latency_ms, contrat_valide, error_message)
        VALUES (?, ?, ?, ?, ?)
    """, (URL_API, status_code, latency_ms, contrat_valide, error_message))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
