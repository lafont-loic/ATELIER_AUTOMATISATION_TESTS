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

@app.route("/dashboard")
def dashboard():
    # Connexion à la base
    conn = sqlite3.connect('historique_ratp.db')
    conn.row_factory = sqlite3.Row # Pour accéder aux colonnes par nom
    
    # On récupère tous les tests
    runs = conn.execute('SELECT * FROM api_runs ORDER BY timestamp DESC').fetchall()
    
    # Calcul simple de la latence moyenne (QoS)
    latencies = [r['latency_ms'] for r in runs if r['latency_ms'] is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    conn.close()
    
    # On envoie les données au fichier HTML
    return render_template('dashboard.html', runs=runs, avg_latency=round(avg_latency, 2))


if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
