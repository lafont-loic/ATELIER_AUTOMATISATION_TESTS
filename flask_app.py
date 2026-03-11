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
        # On augmente le timeout à 20s pour laisser une chance au proxy
        # On peut aussi désactiver la vérification SSL si c'est elle qui bloque (verify=False)
        response = requests.get(URL_API, timeout=20)
        status_code = response.status_code
        
        if status_code == 200:
            data = response.json()
            # Validation du contrat (Point A)
            if "result" in data:
                contrat_valide = True
                error_message = "Succès"
            else:
                error_message = "JSON mal formé"
        else:
            error_message = f"Erreur HTTP {status_code}"

    except requests.exceptions.Timeout:
        error_message = "Timeout (l'API est trop lente)"
    except Exception as e:
        error_message = f"Erreur : {str(e)}"

    # On calcule le temps écoulé, même en cas d'erreur
    latency_ms = (time.time() - start_time) * 1000

    # Sauvegarde
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
