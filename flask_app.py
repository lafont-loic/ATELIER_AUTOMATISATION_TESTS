from flask import Flask, render_template, redirect, url_for
import sqlite3
import requests
import time

app = Flask(__name__)

DB_PATH = '/home/loic75/mysite/historique_ratp.db'
URL_API = "https://pokeapi.co/api/v2/pokemon/ditto"

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
    # INITIALISATION : Crucial pour éviter l'erreur 500
    status_code = None
    contrat_valide = False
    error_message = "Échec total des 3 tentatives"

    # Boucle de tentatives
    for timeout_val in [5, 15, 25]:
        try:
            response = requests.get(URL_API, timeout=timeout_val)
            status_code = response.status_code
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    contrat_valide = True
                    error_message = f"Réussi (timeout {timeout_val}s)"
                    break 
            else:
                error_message = f"Code HTTP {status_code}"
        except Exception as e:
            error_message = f"Dernière erreur : {str(e)}"
            time.sleep(2) 

    latency_ms = (time.time() - start_time) * 1000

    # SAUVEGARDE : Ne pas oublier cette partie !
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_runs (endpoint_tested, status_code, latency_ms, contrat_valide, error_message)
            VALUES (?, ?, ?, ?, ?)
        """, (URL_API, status_code, latency_ms, contrat_valide, error_message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erreur SQL : {e}")

    return redirect(url_for('dashboard'))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
