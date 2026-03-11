from flask import Flask, render_template, redirect, url_for
import sqlite3
import requests
import time

app = Flask(__name__)

DB_PATH = '/home/loic75/mysite/historique_ratp.db'
URL_API = "https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current_weather=true"

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
    url = "https://api.nationalize.io/?name=nathan"
    start_time = time.time()
    
    try:
        r = requests.get(url, timeout=10)
        latence = (time.time() - start_time) * 1000
        status = r.status_code
        data = r.json()
        
        # DEBUG : On vérifie précisément la présence de 'country'
        if status == 200 and "country" in data:
            est_valide = 1
            msg = f"OK ({len(data['country'])} pays trouvés)"
        else:
            est_valide = 0
            # Si c'est pas valide, on enregistre le début du JSON reçu pour comprendre
            msg = f"Erreur Format: {str(data)[:30]}"

    except Exception as e:
        latence, status, est_valide = 0, 0, 0
        msg = f"Erreur Reseau: {str(e)[:30]}"

    # Sauvegarde (inchangée)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO api_runs (endpoint_tested, status_code, latency_ms, contrat_valide, error_message) VALUES (?, ?, ?, ?, ?)", 
                   (url, status, latence, est_valide, msg))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
