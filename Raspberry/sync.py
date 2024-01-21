import requests
import psycopg2

# Paramètres de connexion à la base de données PostgreSQL
dbname = "bfc"
user = "user"
password = "password"
host = "localhost"
sync_ip = "http://192.168.0.145:1880/api/authorizations"

# Fonction pour créer la table si elle n'existe pas
def create_table_if_not_exists(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authorizations (
            id SERIAL PRIMARY KEY,
            plate VARCHAR(255),
            expiration TIMESTAMP,
            model VARCHAR(255)
        )
    """)
    db_conn.commit()
    cursor.close()

# Fonction pour afficher toutes les valeurs dans la base de données
def display_all_values(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id, plate, expiration, model FROM authorizations")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Plate: {row[1]}, Expiration: {row[2]}, Model: {row[3]}")
    cursor.close()

# Fonction pour insérer ou mettre à jour les données dans la base de données
def insert_or_update(db_conn, data):
    cursor = db_conn.cursor()
    for entry in data:
        id = entry['id']
        plate = entry['plate']
        expiration = entry['expiration']
        model = entry.get('model')

        # Vérifier si l'entrée existe déjà
        cursor.execute("SELECT id FROM authorizations WHERE id = %s", (id,))
        if cursor.fetchone():
            # Mise à jour
            cursor.execute("UPDATE authorizations SET plate = %s, expiration = %s, model = %s WHERE id = %s",
                           (plate, expiration, model, id))
        else:
            # Insertion
            cursor.execute("INSERT INTO authorizations (id, plate, expiration, model) VALUES (%s, %s, %s, %s)",
                           (id, plate, expiration, model))

    db_conn.commit()
    cursor.close()

# Connexion à l'API
response = requests.get(sync_ip)
if response.status_code == 200:
    data = response.json()

    # Connexion à la base de données PostgreSQL
    with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
        create_table_if_not_exists(conn)
        insert_or_update(conn, data)
        display_all_values(conn)
else:
    print("Erreur lors de la connexion à l'API")
