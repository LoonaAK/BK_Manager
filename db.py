import pymysql
import hashlib

MYSQL_HOST = ''
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_DB = ''

# Création de la table "achat"
def create_tables():
    # Se connecter à la base de données
    connection = pymysql.connect(host=MYSQL_HOST,
                             user=MYSQL_USER,
                             password=MYSQL_PASSWORD,
                             database=MYSQL_DB,
                             cursorclass=pymysql.cursors.DictCursor)

    # Création du curseur
    cursor = connection.cursor()

    # Définition de la requête SQL pour créer la table "achat"
    cursor.execute("CREATE TABLE achat (id INT AUTO_INCREMENT PRIMARY KEY, projet TEXT, objet TEXT, prix INT)")

    # Définition de la requête SQL pour créer la table "categories"
    cursor.execute("CREATE TABLE categories (id INT AUTO_INCREMENT PRIMARY KEY, nom TEXT)")

    # Définition de la requête SQL pour créer la table "clients"
    cursor.execute("CREATE TABLE clients (id INT AUTO_INCREMENT PRIMARY KEY, username TEXT, nom TEXT, prenom TEXT, email TEXT, telephone TEXT, password TEXT, groupe TEXT)")

    # Définition de la requête SQL pour créer la table "groupe"
    cursor.execute("CREATE TABLE groupe (id INT AUTO_INCREMENT PRIMARY KEY, nom TEXT, categorie TEXT)")

    # Définition de la requête SQL pour créer la table "projet"
    cursor.execute("CREATE TABLE projet (id INT AUTO_INCREMENT PRIMARY KEY, nom TEXT, description TEXT, categorie TEXT, date_fin DATE, budget INT, date_creation DATE)")

    # Définition de la requête SQL pour créer la table "tache"
    cursor.execute("CREATE TABLE tache (id INT AUTO_INCREMENT PRIMARY KEY, description TEXT, groupe TEXT, projet TEXT, temps INT, status TEXT)")

    # Définition de la requête SQL pour créer la catégorie de base "Direction"
    cursor.execute('INSERT INTO categories VALUES (NULL, %s)', ["Direction"])

    # Définition de la requête SQL pour créer le groupe de base "Directeur"
    cursor.execute('INSERT INTO groupe VALUES (NULL, %s, %s)', ["Directeur", "Direction"])

    print("Table de donnée créer avec succès !")
    print("Afin de finir l'initialisation veuillez créer le compte de Direction.\n")

    username = input("Nom d'utilisateur (Sans espace) : ")
    nom = input("Nom : ")
    prenom = input("Prénom : ")
    email = input("Email : ")
    telephone = input("Téléphone : ")
    passtohash = input("Mot de passe : ")
    password = hashlib.md5(passtohash.encode('utf8')).hexdigest()
    # Définition de la requête SQL pour créer l'utilisateur de base "admin"
    cursor.execute('INSERT INTO clients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', [username, nom, prenom, email, telephone, password, "Directeur"])

    print("\nLe compte à été créer avec succès, maintenant vous pouvez votre application à la base de données !")


    # Fermeture du curseur et de la connexion
    connection.commit()
    cursor.close()
    connection.close()

# Appel de la fonction pour créer les tables
create_tables()
