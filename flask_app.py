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
    # On utilise l'URL Open-Meteo qui est dans la whitelist et sans limite
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current_weather=true"
    start_time = time.time()
    
    try:
        r = requests.get(url, timeout=10)
        latence = (time.time() - start_time) * 1000
        status = r.status_code
        data = r.json()
        
        # Test de contrat ultra-simple : si on reçoit du JSON, c'est OK
        if data: 
            est_valide = 1
            msg = "Données reçues"
        else:
            est_valide = 0
            msg = "Réponse vide"

    except Exception as e:
        latence = 0
        status = 0
        est_valide = 0
        msg = f"Erreur: {str(e)[:30]}"

    # Sauvegarde en base de données
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO api_runs (endpoint_tested, status_code, latency_ms, contrat_valide, error_message) 
        VALUES (?, ?, ?, ?, ?)
    """, (url, status, latence, est_valide, msg))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
