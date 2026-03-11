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
    # 1. Configuration de base
    url = "https://api.nationalize.io/?name=nathan"
    start_time = time.time()
    
    try:
        # 2. Appel API (le proxy laisse passer car c'est dans ta liste)
        r = requests.get(url, timeout=10)
        latence = (time.time() - start_time) * 1000
        
        # 3. Test de contrat ultra-simple
        data = r.json()
        est_valide = 1 if "country" in data else 0
        msg = "OK" if est_valide else "Erreur Format"
        status = r.status_code

    except Exception as e:
        # En cas de plantage (proxy, coupure, etc.)
        latence = 0
        status = 0
        est_valide = 0
        msg = str(e)[:50] # On coupe le message s'il est trop long

    # 4. Enregistrement en base de données
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
