from flask import Flask, render_template, redirect, url_for
import sqlite3
import requests
import time

app = Flask(__name__)

DB_PATH = '/home/loic75/mysite/historique_ratp.db'
URL_API = "https://api-ratp.pierre-grimaud.fr/v1/schedules/rers/a/nanterre+ville/A"

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
    # On tente 3 fois avec des timeouts progressifs
    for timeout_val in [5, 15, 25]:
        try:
            response = requests.get(URL_API, timeout=timeout_val)
            if response.status_code == 200:
                data = response.json()
                # On vérifie le contrat (Point A)
                if "result" in data:
                    status_code = 200
                    contrat_valide = True
                    error_message = f"Réussi après {timeout_val}s"
                    break # On a l'info, on arrête !
        except Exception:
            error_message = "Tentative échouée, on réessaie..."
            time.sleep(2) # Petite pause pour laisser respirer le proxy

    latency_ms = (time.time() - start_time) * 1000
    # ... (code de sauvegarde SQLite identique) ...
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
