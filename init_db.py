import sqlite3

def create_db():
    conn = sqlite3.connect('historique_ratp.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Base de données 'historique_ratp.db' créée avec succès !")

if __name__ == '__main__':
    create_db()
