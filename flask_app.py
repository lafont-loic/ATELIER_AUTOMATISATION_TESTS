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

    try:
        # 1. Test de Connexion & QoS (Timeout 5s)
        response = requests.get(URL_API, timeout=5)
        status_code = response.status_code
        response.raise_for_status()
        
        # 2. Test du Contrat (Structure JSON)
        data = response.json()
        if "result" in data:
            contrat_valide = True
        else:
            error_message = "Clé 'result' manquante dans le JSON"
            
    except Exception as e:
        error_message = str(e)
        # Si on a eu une erreur de type 503 ou Timeout, on essaie de garder le code
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code

    # Calcul de la latence (ms)
    latency_ms = (time.time() - start_time) * 1000

    # 3. Sauvegarde dans la base de données
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO api_runs (endpoint_tested, status_code, latency_ms, contrat_valide, error_message)
        VALUES (?, ?, ?, ?, ?)
    """, (URL_API, status_code, latency_ms, contrat_valide, error_message))
    conn.commit()
    conn.close()

    # Redirection vers le dashboard pour voir le résultat
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
