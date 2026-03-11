from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)

@app.get("/")
def consignes():
     return render_template('consignes.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('/home/loic75/mysite/historique_ratp.db')
    cursor = conn.cursor()
    # On récupère tout : date, code, latence, contrat, erreur
    cursor.execute("SELECT run_date, status_code, latency_ms, contrat_valide, error_message FROM api_runs ORDER BY run_date DESC")
    runs = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', runs=runs)
     
@app.route('/run')
def run():
    # ... tout le code de test (requests, time, etc.) ...
    
    # À la fin, après le conn.close()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
