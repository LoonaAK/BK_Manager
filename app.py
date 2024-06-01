# Importer les modules nécessaires à l'application Flask
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Importer le module Flask-MySQL pour la gestion de la base de données MySQL
from flask_mysqldb import MySQL

# Importer le module MySQLdb pour la connexion à la base de données MySQL
import MySQLdb.cursors

# Importer le module re pour la validation des chaînes de caractères
import re

# Importer le module hashlib pour le hachage des mots de passe
import hashlib

from flask_socketio import SocketIO, join_room

# Importer le module datetime pour la gestion des dates et des heures
from datetime import datetime, timedelta, time, date

# Import de la bibliothèque JSON pour la manipulation de données JSON
import json

# Import de la bibliothèque secrets pour la génération de nombres aléatoires sécurisés
import secrets

# Import de la bibliothèque smtplib pour l'envoi d'e-mails via le protocole SMTP
import smtplib

# Import de la classe MIMEMultipart de la bibliothèque email.mime.multipart pour créer des objets multipartes MIME
from email.mime.multipart import MIMEMultipart

# Import de la classe MIMEText de la bibliothèque email.mime.text pour créer des objets MIME de type texte
from email.mime.text import MIMEText

# Initialiser l'application Flask
app = Flask(__name__, static_url_path='', static_folder='static')

# Configurer une clé secrète pour l'application Flask
app.secret_key = '1a2b3c4d5e'

# Configurer les informations de connexion à la base de données MySQL
app.config['MYSQL_HOST'] = '141.94.37.252'
app.config['MYSQL_USER'] = 'bleona_db'
app.config['MYSQL_PASSWORD'] = '1Xayt12_4'
app.config['MYSQL_DB'] = 'bleona'

# Initialiser le module Flask-MySQL avec les configurations de l'application Flask
mysql = MySQL(app)

# Import de la classe SocketIO pour la gestion des connexions WebSocket
socketio = SocketIO(app)


# Définir la route d'accueil de l'application Flask pour la page de connexion
@app.route('/', methods=['GET', 'POST'])
def login():

    try:
        # Si l'utilisateur est déjà connecté, rediriger vers la page des projets
        if session['loggedin'] == True:
            return redirect(url_for('projets'))
            
    except:
        pass

    # Si une requête POST est envoyée avec un nom d'utilisateur et un mot de passe
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        # Récupérer le nom d'utilisateur et le mot de passe depuis la requête POST
        username = request.form['username']
        password = request.form['password']

        # Hacher le mot de passe en utilisant l'algorithme MD5
        result = hashlib.md5(password.encode('utf8')).hexdigest()
        
        # Exécuter une requête SELECT pour récupérer le compte correspondant au nom d'utilisateur et au mot de passe haché
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM clients WHERE username = %s AND password = %s', (username, result))
        compte = cursor.fetchone()
                
        if compte:

            # Si un compte est trouvé, enregistrer les informations de session de l'utilisateur et rediriger vers la page des projets
            session['loggedin'] = True
            session['id'] = compte['id']
            session['username'] = compte['username']
            session['nom'] = compte['nom']
            session['prenom'] = compte['prenom']
            session['email'] = compte['email']
            session['telephone'] = compte['telephone']
            session['groupe'] = compte['groupe']

            # Exécuter une requête SELECT pour récupérer le categorie correspondant à l'utilisateur
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM groupe WHERE nom = %s', [session['groupe']])
            categorie = cursor.fetchone()

            session['categorie'] = categorie['categorie']
            
            return redirect(url_for('projets'))
        else:

            # Si aucun compte n'est trouvé, afficher un message d'erreur flash et rester sur la page de connexion
            flash("Utilisateur ou mot de passe incorrects ", "danger")
            
    # Afficher la page de connexion
    return render_template('backend/connexion.html')


@app.route('/recuperation', methods=['GET', 'POST'])
def recuperation():
    # Traitement du formulaire de récupération
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        
        # Vérification si le champ email est vide
        if email == "":
            flash("Veuillez entrer votre adresse email pour continuer ", "danger")
        else:
            # Connexion à la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Vérification si l'email existe dans la table 'clients'
            cursor.execute("SELECT * FROM clients WHERE email = %s", [email])
            user_exist = cursor.fetchone()
            
            if user_exist:
                # Génération d'un nouveau mot de passe sécurisé
                newpassword = secrets.token_urlsafe(6)
                # Sujet et corps de l'email
                subject = "Réinitialiser le mot de passe"
                body = f"Demande de réinitialisation de mot de passe effectuée.\n\nVoici votre nouveau mot de passe :\n{newpassword}\n\nCordialement,\nL'équipe BK Manager !"
                # Informations de l'expéditeur et du destinataire de l'email
                sender = "bkmanager.noreply@gmail.com"
                recipients = email
                # Mot de passe de l'expéditeur (note : il est préférable de stocker ce mot de passe de manière sécurisée)
                password = "bvpkijvkwcpuodla"
                
                # Hashage du nouveau mot de passe
                newpasshash = hashlib.md5(newpassword.encode('utf8')).hexdigest()
                # Mise à jour du mot de passe dans la base de données
                cursor.execute('UPDATE clients SET password = %s WHERE email = %s', (newpasshash, email))
                mysql.connection.commit()
                
                # Fonction pour envoyer l'email
                def send_email(subject, body, sender, recipients, password):
                    msg = MIMEText(body)
                    msg['Subject'] = subject
                    msg['From'] = sender
                    msg['To'] = recipients
                    # Envoi de l'email via SMTP
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                        smtp_server.login(sender, password)
                        smtp_server.sendmail(sender, recipients, msg.as_string())

                # Appel de la fonction d'envoi d'email
                send_email(subject, body, sender, recipients, password)
                
                flash("Demande envoyée avec succès, veuillez vous connecter avec votre nouveau mot de passe ", "success")
                return redirect(url_for('login'))
            else:
                flash("Veuillez entrer une adresse email valide ", "danger")
    
    # Afficher la page de récupération de mot de passe
    return render_template('backend/motdepasseoublier.html')


# Définir une route pour '/projets' avec la méthode GET
@app.route('/projets')
def projets():
    
    # Vérifier si l'utilisateur est connecté
    if session['loggedin'] == True:
        
        # Exécuter une requête pour sélectionner tous les projets
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM projet')
        projets = cursor.fetchall()

        # Exécuter une requête pour sélectionner toutes les catégories
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM categories')
        categories = cursor.fetchall()

        nbr_projets = cursor.execute('SELECT * FROM projet')
        nbr_tache_attente = cursor.execute('SELECT * FROM tache WHERE status = "En attente"')
        nbr_tache_cours = cursor.execute('SELECT * FROM tache WHERE status = "En cours"')
        nbr_projets_retard = 0

        # Créer une liste vide pour stocker les projets
        l_projet_1 = []

        # Parcourir tous les projets récupérés
        for projet in projets:
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute( "SELECT * FROM tache WHERE id_projet = %s", [projet['id']] )
            projet_tache = cursor.fetchall()

            # Calcul de la date de fin prévue pour le projet en utilisant la date de création et la durée des tâches
            date_th = 0
            for x in projet_tache:
                date_th = date_th + x['temps']
            
            date_th_d = projet['date_creation'] + timedelta(days=date_th)

            if date_th_d > projet['date_fin']:
                nbr_projets_retard = nbr_projets_retard + 1
            else:
                pass

            # Formater la date de fin de chaque projet pour l'afficher en jour/mois/année
            date_fin = projet['date_fin'].strftime("%d/%m/%Y")

            jfin = projet['date_fin'] - date.today()

            jtot = projet['date_fin'] - projet['date_creation']

            if jfin.days < 0:
                jprct = 100
            elif jtot.days == 1:
                jprct = 85
            elif jtot.days == 0:
                jprct = 100
            else:
                if date.today() == projet['date_creation']:
                    jprct = (1 / jtot.days) * 100
                else:
                    jprct = ((jtot.days - jfin.days) / jtot.days) * 100

            # Créer un dictionnaire pour stocker les informations de chaque projet
            l_projet_2 = {'id': projet['id'], 'nom': projet['nom'], 'description': projet['description'], 'categorie': projet['categorie'], 'date_fin': date_fin, 'budget': projet['budget'], 'date_creation': projet['date_creation'], 'jprct': jprct, 'jrest': jfin.days}

            # Ajouter les informations du projet à la liste 'l_projet_1'
            l_projet_1.append(l_projet_2)

        # Affichage de la page avec les projets et les catégories récupérés
        return render_template('backend/index.html', nbr_projets_retard=nbr_projets_retard, nbr_tache_cours=nbr_tache_cours, nbr_tache_attente=nbr_tache_attente, nbr_projets=nbr_projets, l_projet_1=l_projet_1, categories=categories)
    
    # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
    return redirect(url_for('login'))


# Définir la route pour la page d'affichage d'un projet spécifique
@app.route('/projet')
def projet():

    # Récupération de l'ID du projet à afficher à partir des arguments de la requête
    projet_id = request.args.get("projet_id")
    show_chat_modal = request.args.get("show_chat_modal")
    
    # Vérification de la connexion de l'utilisateur
    if session['loggedin'] == True:
        
        # Récupération des informations du projet à partir de la base de données
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute( "SELECT * FROM projet WHERE id = %s", [projet_id] )
        projet_info = cursor.fetchone()

        # Récupération des informations du projet à partir de la base de données
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute( "SELECT * FROM conversation WHERE id_projet = %s", [projet_id] )
        conversation = cursor.fetchall()

        # Récupération des achats associés à ce projet depuis la base de données
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute( "SELECT * FROM achat WHERE projet = %s", [projet_info['nom']] )
        projet_achat = cursor.fetchall()
        
        # Récupération des tâches associées à ce projet depuis la base de données
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute( "SELECT * FROM tache WHERE projet = %s", [projet_info['nom']] )
        projet_tache = cursor.fetchall()
        

        # Calcul de la date de fin prévue pour le projet en utilisant la date de création et la durée des tâches
        date_th = 0
        for x in projet_tache:
            date_th = date_th + x['temps']

        # Calcul du nombre total de tâches pour ce projet
        tache_total = 0
        for tache_a in projet_tache:
            tache_total += 1
        
        # Calcul du nombre de tâches finies pour ce projet
        tache_fini = 0
        for tache_b in projet_tache:
            if tache_b['status'] == "Fini":
                tache_fini += 1
        
        if tache_total == 0:
            tache_pourcent = 0
        else:
            # Calcul du pourcentage de tâches finies pour ce projet
            tache_pourcent = (tache_fini / tache_total) * 100

        # Formatage des dates pour l'affichage
        date_fin = projet_info['date_fin'].strftime("%d/%m/%Y")

        date_debut = projet_info['date_creation'].strftime("%d/%m/%Y")

        date_th_d = projet_info['date_creation'] + timedelta(days=date_th)

        date_th_d_g = date_th_d.strftime("%d/%m/%Y")

        session['projet_select'] = projet_info['id']

        th_d = False
        if date_th_d > projet_info['date_fin']:
            th_d = True
        else:
            th_d = False

        # Affichage des informations du projet, des achats et des tâches associées
        return render_template('backend/projet.html', conversation=conversation, date_debut=date_debut, show_chat_modal=show_chat_modal, projet_info=projet_info, projet_achat=projet_achat, projet_tache=projet_tache, date_fin=date_fin, date_th_g=date_th, tache_pourcent=tache_pourcent, th_d=th_d, date_th_d_g=date_th_d_g)
    
    # Redirection vers la page de connexion si l'utilisateur n'est pas connecté
    return redirect(url_for('login'))


@app.route('/change_status', methods=['GET', 'POST'])
def change_status():

    # Récupérer l'identifiant de la tâche à partir de la requête GET
    tache_id = request.args.get("tache_id")

    # Vérification de la connexion de l'utilisateur
    if session['loggedin'] == True:

        # Si une requête POST est envoyée
        if request.method == 'POST':
            
            # Récupérer le status depuis la requête POST
            status = request.form['status']

            # Met à jour le statut de la tâche dans la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE tache SET status = %s WHERE id = %s', (status, tache_id))
            mysql.connection.commit()
            
            # Récupère les informations sur la tâche correspondant
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute( "SELECT * FROM tache WHERE id = %s", [tache_id] )
            tache_info = cursor.fetchone()

            # Récupère les informations sur le projet correspondant
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute( "SELECT * FROM projet WHERE nom = %s", [tache_info['projet']] )
            projet_info = cursor.fetchone()

            # Redirige vers la page du projet correspondant
            return redirect(url_for('projet', projet_id=projet_info['id']))


        elif request.method == 'POST':
            # Si la méthode est POST mais qu'il manque des informations dans le formulaire, affiche un message d'erreur
            flash("Merci de compléter le formulaire ", "danger")
    
    # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion
    return redirect(url_for('login'))


# Définition d'une route Flask qui gère l'ajout d'un achat
@app.route('/ajout_achat', methods=['GET', 'POST'])
def ajout_achat():

    # Récupération de l'identifiant du projet depuis les arguments de la requête
    projet_id = request.args.get("projet_id")

    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:

        # Vérification si la méthode HTTP utilisée est "POST" et si les champs "objet" et "prix" sont renseignés dans le formulaire
        if request.method == 'POST' and 'objet' in request.form and 'prix' in request.form:

            # Récupération des données du formulaire
            objet = request.form['objet']
            prix = request.form['prix']

            # Connexion à la base de données et récupération du projet associé à l'identifiant fourni
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute( "SELECT * FROM projet WHERE id = %s", [projet_id] )
            projet = cursor.fetchone()

            # Calcul du nouveau budget du projet en fonction du prix de l'achat
            nouveau_budget = int(projet['budget']) - int(prix)

            # Vérification si le budget restant est suffisant pour réaliser l'achat
            if nouveau_budget < 0:
                flash("Le projet n'a plus suffisamment de budget ", "danger")
                return redirect(url_for('projet', projet_id=projet_id))

            # Vérification si les champs "objet" et "prix" sont bien renseignés dans le formulaire
            elif objet == "" and prix == "":
                flash("Merci de compléter le formulaire ", "danger")
                return redirect(url_for('projet', projet_id=projet_id))

            else:
                # Mise à jour du budget du projet dans la base de données
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE projet SET budget = %s WHERE id = %s', (nouveau_budget, projet_id))
                mysql.connection.commit()

                # Ajout de l'achat dans la table "achat" de la base de données
                cursor.execute('INSERT INTO achat VALUES (NULL, %s, %s, %s)', (projet['nom'], objet, prix))
                mysql.connection.commit()

                # Message de confirmation de l'ajout de l'achat
                flash("Achat ajouté ", "success")

                # Redirection vers la page du projet
                return redirect(url_for('projet', projet_id=projet_id))

        # Vérification si la méthode HTTP utilisée est "POST" et si les champs "objet" et "prix" ne sont pas renseignés dans le formulaire
        elif request.method == 'POST':

            # Message d'erreur si les champs "objet" et "prix" ne sont pas renseignés dans le formulaire
            flash("Merci de compléter le formulaire ", "danger")

    # Redirection vers la page de connexion si l'utilisateur n'est pas connecté
    return redirect(url_for('login'))


# Définition de la route /profiles
@app.route('/profiles')
def profiles():
    
    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:
        
        # Exécution d'une requête SELECT pour récupérer tous les groupes
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM groupe')
        groupes = cursor.fetchall()

        # Exécution d'une requête SELECT pour récupérer tous les clients
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM clients')
        clients = cursor.fetchall()

        # Renvoi du template HTML 'profiles.html' avec les données clients et groupes
        return render_template('backend/profiles.html', clients=clients, groupes=groupes)
    
    # Si l'utilisateur n'est pas connecté, redirection vers la page de connexion
    return redirect(url_for('login'))


# Définition de la route /taches
@app.route('/taches')
def taches():
    
    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:
        
        if session['categorie'] == "Direction":
            # Exécution d'une requête SELECT pour récupérer tous les projets
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM projet')
            projets = cursor.fetchall()
        else :
            # Exécution d'une requête SELECT pour récupérer tous les projets
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM projet WHERE categorie = %s', [session['categorie']])
            projets = cursor.fetchall()

        # Exécution d'une requête SELECT pour récupérer tous les groupes
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM groupe')
        groupes = cursor.fetchall()

        # Exécution d'une requête SELECT pour récupérer toutes les tâches
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tache')
        tache = cursor.fetchall()
        
        # Renvoi du template HTML 'taches.html' avec les données tache, groupes et projets
        return render_template('backend/taches.html', tache=tache, groupes=groupes, projets=projets)
    
    # Si l'utilisateur n'est pas connecté, redirection vers la page de connexion
    return redirect(url_for('login'))


# Définition de la route /ajout_tache
@app.route('/ajout_tache', methods=['GET', 'POST'])
def ajout_tache():
    
    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:

        # Vérification de la méthode de requête HTTP utilisée
        if request.method == 'POST' and 'description' in request.form:

            # Récupération des valeurs du formulaire
            groupe_pick = request.form['groupe_pick']
            projet_pick = request.form['projet_pick']
            description = request.form['description']
            temps = request.form['temps']

            # Vérification si le champ description et le champ temps sont vides
            if description == "" and temps == "":
                flash("Merci de compléter le formulaire ", "danger")
                return redirect(url_for('taches'))

            # Vérification si un projet a été sélectionné dans le formulaire
            elif projet_pick == "choix":
                flash("Merci de choisir un projet. Si aucun projet n'est disponible, veuillez en créer un ", "danger")
                return redirect(url_for('taches'))

            # Vérification si un groupe a été sélectionné dans le formulaire
            elif groupe_pick == "choix":
                flash("Merci de choisir un groupe. Si aucun projet n'est disponible, veuillez en créer un ", "danger")
                return redirect(url_for('taches'))

            # Si toutes les vérifications sont validées, insertion des données dans la base de données
            else:
                # Récupération des données de la table groupe
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM projet WHERE nom = %s', [projet_pick])
                projet_id = cursor.fetchone()
                
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO tache VALUES (NULL, %s, %s, %s, %s, %s, %s)', [description, groupe_pick, projet_pick, projet_id["id"], temps, "En attente"])
                mysql.connection.commit()
                
                flash("Tâche ajoutée ", "success")

                return redirect(url_for('taches'))
                
        # Si le formulaire est vide, affichage d'un message d'erreur
        elif request.method == 'POST':
            
            flash("Merci de compléter le formulaire ", "danger")
    
    # Si l'utilisateur n'est pas connecté, redirection vers la page de connexion
    return redirect(url_for('login'))
 

# Définition de la route pour voir les groupes
@app.route('/groupes')
def groupes():
    
    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:
        
        # Récupération des données de la table groupe
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM groupe')
        groupes = cursor.fetchall()

        # Récupération des données de la table catégorie
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM categories')
        categories = cursor.fetchall()

        # Créer une liste vide pour stocker les groupes
        l_groupe_1 = []

        for groupe in groupes: 

            # Récupération des données de la table groupe
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            clients = cursor.execute('SELECT * FROM clients WHERE groupe = %s', [groupe['nom']])

            # Créer un dictionnaire pour stocker les informations de chaque groupe
            l_groupe_2 = {'id': groupe['id'], 'nom': groupe['nom'], 'categorie': groupe['categorie'], 'nbr_client': clients}

            # Ajouter les informations du projet à la liste 'l_groupe_1'
            l_groupe_1.append(l_groupe_2)

        
        # Rendu de la page HTML avec les données récupérées
        return render_template('backend/groupes.html', l_groupe_1=l_groupe_1, categories=categories)

    # Redirection vers la page de connexion si l'utilisateur n'est pas connecté
    return redirect(url_for('login'))


# Définition de la route pour voir les catégories
@app.route('/categories')
def categories():
    
    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:
        
        # Récupération des données de la table categories
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM categories')
        categories = cursor.fetchall()

        # Récupération des données de la table projet
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM projet')
        projets = cursor.fetchall()
        
        # Rendu de la page HTML avec les données récupérées
        return render_template('backend/categories.html', categories=categories, projets=projets)

    # Redirection vers la page de connexion si l'utilisateur n'est pas connecté
    return redirect(url_for('login'))


# Définition de la route pour ajouter un catégorie
@app.route('/ajout_categorie', methods=['GET', 'POST'])
def ajout_categorie():
    
    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:

        if request.method == 'POST' and 'nom_cat' in request.form:

            # Récupération du nom de la catégorie entrée dans le formulaire
            nom_cat = request.form['nom_cat']

            # Vérification si la catégorie existe déjà dans la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute( "SELECT * FROM categories WHERE nom LIKE %s", [nom_cat] )
            cat_ex = cursor.fetchone()

            # Si la catégorie existe déjà, un message d'erreur est affiché
            if cat_ex:
                flash("La catégorie existe déjà ", "danger")
                return redirect(url_for('categories'))

            # Si le champ du nom de catégorie est vide, un message d'erreur est affiché
            elif nom_cat == "":
                flash("Merci de compléter le formulaire ", "danger")
                return redirect(url_for('categories'))

            # Si les conditions ci-dessus sont satisfaites, la nouvelle catégorie est insérée dans la base de données
            else:
                cursor.execute('INSERT INTO categories VALUES (NULL, %s)', [nom_cat])
                mysql.connection.commit()
                
                flash("Catégorie ajoutée ", "success")

                return redirect(url_for('categories'))
                
        elif request.method == 'POST':
            
            flash("Merci de compléter le formulaire ", "danger")
    
    return redirect(url_for('login'))


# Définition de la route pour ajouter un groupe
@app.route('/ajout_groupe', methods=['GET', 'POST'])
def ajout_groupe():
    
    # Vérification de la session de connexion
    if session['loggedin'] == True:

        # Si la méthode est POST et que le formulaire est soumis avec le champ "nom_groupe" et "nom_cat"
        if request.method == 'POST' and 'nom_groupe' in request.form and 'nom_cat' in request.form:

            # Récupération de la valeur saisie pour le champ "nom_groupe" et "nom_cat"
            nom_groupe = request.form['nom_groupe']
            nom_cat = request.form['nom_cat']

            # Requête pour vérifier si le groupe existe déjà
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute( "SELECT * FROM groupe WHERE nom LIKE %s", [nom_groupe] )
            groupe_ex = cursor.fetchone()

            # Si le groupe existe déjà
            if groupe_ex:
                flash("Le groupe existe déjà ", "danger")
                return redirect(url_for('groupes'))

            # Si le champ "nom_groupe" est vide
            elif nom_groupe == "":
                flash("Merci de compléter le formulaire ", "danger")
                return redirect(url_for('groupes'))

            # Si le groupe n'existe pas et le champ "nom_groupe" est rempli
            else:
                
                # Requête pour ajouter un nouveau groupe à la base de données
                cursor.execute('INSERT INTO groupe VALUES (NULL, %s, %s)', [nom_groupe, nom_cat])
                mysql.connection.commit()
                
                # Message de confirmation de l'ajout du groupe
                flash("Groupe ajouté ", "success")

                return redirect(url_for('groupes'))
                
        # Si la méthode est POST et que le formulaire est soumis sans le champ "nom_groupe"
        elif request.method == 'POST':
            
            # Message d'erreur si le champ "nom_groupe" est vide
            flash("Merci de compléter le formulaire ", "danger")

    # Redirection vers la page de connexion si la session n'existe pas
    return redirect(url_for('login'))


# Définition de la route pour les informations personnelles
@app.route('/info_pers', methods=['GET', 'POST'])
def info_pers():
    
    # Vérifier si l'utilisateur est connecté 
    if session['loggedin'] == True:

        # Récupérer l'identifiant du profil à modifier depuis les paramètres GET
        profile_id = request.args.get("profile_id")

        # Si la méthode est POST et les champs de saisie sont remplis, mettre à jour les informations du profil
        if request.method == 'POST' and 'username' in request.form and 'nom' in request.form and 'prenom' in request.form:

            # Récupérer les nouvelles valeurs de nom, prénom, nom d'utilisateur et groupe depuis les champs de saisie
            username = request.form['username']
            groupe_pick = request.form['groupe_pick']
            nom = request.form['nom']
            prenom = request.form['prenom']

            # Mettre à jour les informations du profil dans la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE clients SET nom = %s, prenom = %s, groupe = %s, username = %s WHERE id = %s', (nom, prenom, groupe_pick, username, profile_id))
            mysql.connection.commit()

            # Récupérer les nouvelles informations du profil depuis la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM clients WHERE id = %s', [profile_id])
            compte = cursor.fetchone()

            # Vérifier si les nouvelles informations ont été correctement récupérées depuis la base de données
            if compte['id'] == profile_id:

                # Mettre à jour les informations de session avec les nouvelles informations du profil
                session['username'] = compte['username']
                session['nom'] = compte['nom']
                session['prenom'] = compte['prenom']
                session['groupe'] = compte['groupe']
                
            else: pass

            # Afficher un message de succès
            flash("Modification effectuée ", "success")
            
            # Rediriger vers la page du profil modifié
            return redirect(url_for("profile", profile_id=profile_id))

    # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
    return redirect(url_for('login'))


# Définition de la route pour changer le mot de passe
@app.route('/change_mdp', methods=['GET', 'POST'])
def change_mdp():
    
    # Vérifie que l'utilisateur est connecté
    if session['loggedin'] == True:

        # Récupère l'identifiant du profil utilisateur
        profile_id = request.args.get("profile_id")

        # Si la requête est de type POST et que les champs new_password et password_repeat sont présents dans le formulaire
        if request.method == 'POST' and 'new_password' in request.form and 'password_repeat' in request.form:

            # Récupère les valeurs des champs new_password et password_repeat du formulaire
            new_password = request.form['new_password']
            password_repeat = request.form['password_repeat']

            # Récupère les informations de l'utilisateur à partir de la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM clients WHERE id = %s', [profile_id])
            compte = cursor.fetchone()

            # Crypte le mot de passe répété pour comparaison
            result2 = hashlib.md5(password_repeat.encode('utf8')).hexdigest()

            # Si les mots de passe ne correspondent pas
            if new_password != password_repeat:
                flash("Les mots de passe ne correspondent pas ", "danger")
                return redirect(url_for("profile", profile_id=profile_id))

            # Sinon, si les mots de passe correspondent
            else:
                
                # Met à jour le mot de passe de l'utilisateur dans la base de données
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE clients SET password = %s WHERE id = %s', (result2, profile_id))
                mysql.connection.commit()

                # Affiche un message de confirmation
                flash("Modification effectuée. Veuillez vous connecter dès que possible avec votre nouveau mot de passe ", "success")
                
                # Redirige l'utilisateur vers la page de son profil
                return redirect(url_for("profile", profile_id=profile_id))

    # Si l'utilisateur n'est pas connecté, redirige-le vers la page de connexion
    return redirect(url_for('login'))


# Définition de la route pour les informations des contacts de l'utilisateur
@app.route('/description', methods=['GET', 'POST'])
def description():
    
    # Vérifie si l'utilisateur est connecté
    if session['loggedin'] == True:

        objet_id = request.args.get("objet_id")

        # Si la requête est une requête POST et que les champs "telephone" et "email" sont dans le formulaire
        if request.method == 'POST' and 'description' in request.form:

            # Récupère les valeurs des champs "telephone" et "email" depuis le formulaire
            description = request.form['description']

            # Effectue la mise à jour de la base de données avec les nouvelles valeurs
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE projet SET description = %s WHERE id = %s', (description, objet_id))
            mysql.connection.commit()

            # Redirige l'utilisateur vers la page de profil
            return redirect(url_for("projet", projet_id=objet_id))
            
    # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion
    return redirect(url_for('login'))


# Définition de la route pour les informations des contacts de l'utilisateur
@app.route('/info_contact', methods=['GET', 'POST'])
def info_contact():
    
    # Vérifie si l'utilisateur est connecté
    if session['loggedin'] == True:

        # Si la requête est une requête POST et que les champs "telephone" et "email" sont dans le formulaire
        if request.method == 'POST' and 'telephone' in request.form and 'email' in request.form:

            # Récupère les valeurs des champs "telephone" et "email" depuis le formulaire
            telephone = request.form['telephone']
            email = request.form['email']
            profile_id = request.args.get("profile_id")

            # Effectue la mise à jour de la base de données avec les nouvelles valeurs
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE clients SET telephone = %s, email = %s WHERE id = %s', (telephone, email, profile_id))
            mysql.connection.commit()

            # Récupère les informations du compte modifié
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM clients WHERE id = %s', [profile_id])
            compte = cursor.fetchone()
            
            # Vérifie si les informations récupérées correspondent bien au compte modifié
            if compte['id'] == profile_id:

                # Met à jour les informations de la session avec les nouvelles valeurs
                session['email'] = compte['email']
                session['telephone'] = compte['telephone']
                
            else: pass
            
            # Affiche un message de succès
            flash("Modification effectuée ", "success")
            
            # Redirige l'utilisateur vers la page de profil
            return redirect(url_for("profile", profile_id=profile_id))
            
    # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion
    return redirect(url_for('login'))


# Définition de la route pour le profile
@app.route('/profile')
def profile():
    
    # On vérifie si l'utilisateur est connecté
    if session['loggedin'] == True:

        # On récupère l'id du profil à afficher
        profile_id = request.args.get("profile_id")

        # Si l'utilisateur connecté est un directeur
        if session['groupe'] == "Directeur":

            # On récupère les informations du profil à afficher depuis la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM clients WHERE id = %s', [profile_id])
            compte = cursor.fetchone()

            # On récupère les différents groupes disponibles depuis la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM groupe')
            groupes = cursor.fetchall()

            # Si le profil à afficher existe dans la base de données
            if compte:

                # On affiche la page de modification de profil avec les informations du profil et les différents groupes disponibles
                return render_template('app/profiles-parametres.html', compte=compte, groupes=groupes)
            else:

                # Si le profil n'existe pas dans la base de données, on redirige vers la page de liste des profils
                return redirect(url_for('profiles'))
        else:
            # Si l'utilisateur connecté n'est pas un directeur, on affiche la page de modification de son propre profil
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM clients WHERE id = %s', [session['id']])
            compte = cursor.fetchone()

            # Si les informations du profil de l'utilisateur connecté sont disponibles dans la base de données
            if compte:

                # On affiche la page de modification de profil avec les informations de l'utilisateur connecté
                return render_template('app/profiles-parametres.html', compte=compte)
            else:

                # Si les informations du profil de l'utilisateur connecté ne sont pas disponibles dans la base de données, on redirige vers la page de liste des profils
                return redirect(url_for('profiles'))
        
    # Si l'utilisateur n'est pas connecté, on redirige vers la page de connexion
    return redirect(url_for('login'))


# Définition de la route pour ajouté un projet
@app.route('/ajout_projet', methods=['GET', 'POST'])
def ajout_projet():
    
    # Vérifie si l'utilisateur est connecté
    if session['loggedin'] == True:
        # Si une requête POST est soumise et les champs 'projet', 'description' et 'budget' sont renseignés
        if request.method == 'POST' and 'projet' in request.form and 'description' in request.form and 'budget' in request.form:

            # Récupère les valeurs des champs dans la requête POST
            projet = request.form['projet']
            description = request.form['description']
            cat_pick = request.form['cat_pick']
            echeance = request.form['echeance']
            budget = request.form['budget']

            # Recherche dans la base de données si un projet avec le même nom existe déjà
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute( "SELECT * FROM projet WHERE nom LIKE %s", [projet] )
            projet_ex = cursor.fetchone()

            # Si un projet avec le même nom existe déjà, renvoie un message d'erreur
            if projet_ex:
                flash("Le projet existe déjà ", "danger")
                return redirect(url_for('projets'))

            # Si les champs requis ne sont pas remplis, renvoie un message d'erreur
            elif projet == "" or description == "" or echeance == "" or budget == "":
                flash("Merci de compléter le formulaire ", "danger")
                return redirect(url_for('projets'))

            # Si aucune catégorie n'est sélectionnée, renvoie un message d'erreur
            elif cat_pick == "choix":
                flash("Merci de choisir une catégorie. Si aucune catégorie n'est disponible, veuillez en créer une ", "danger")
                return redirect(url_for('projets'))

            else:
                # Insère le nouveau projet dans la base de données
                cursor.execute('INSERT INTO projet VALUES (NULL, %s, %s, %s, %s, %s, %s)', (projet, description, cat_pick, echeance, budget, datetime.now().date()))
                mysql.connection.commit()
                
                flash("Projet ajouté ", "success")

                # Redirige vers la page des projets
                return redirect(url_for('projets'))
                
        elif request.method == 'POST':
            
            # Si la requête POST ne contient pas les champs requis, renvoie un message d'erreur
            flash("Merci de compléter le formulaire ", "danger")
    
    # Si l'utilisateur n'est pas connecté, renvoie vers la page de connexion
    return redirect(url_for('login'))


# Définition de la route pour ajouté un utilisateur
@app.route('/ajout_utilisateur', methods=['GET', 'POST'])
def ajout_utilisateur():
    
    # Vérifier si l'utilisateur est connecté
    if session['loggedin'] == True:

        # Vérifier si le formulaire est soumis et si tous les champs sont présents
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'telephone' in request.form and 'nom' in request.form and 'prenom' in request.form and 'email' in request.form:

            # Récupérer les valeurs des champs du formulaire
            username = request.form['username']
            password = request.form['password']
            telephone = request.form['telephone']
            nom = request.form['nom']
            prenom = request.form['prenom']
            groupe_pick = request.form['groupe_pick']
            email = request.form['email']

            # Vérifier si l'utilisateur ou l'email existe déjà dans la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute( "SELECT * FROM clients WHERE nom LIKE %s OR email LIKE %s", [username, email] )
            client_ex = cursor.fetchone()

            # Si l'utilisateur existe déjà, afficher un message d'erreur et rediriger vers la page profiles
            if client_ex:
                flash("L'utilisateur existe déjà ", "danger")
                return redirect(url_for('profiles'))

            # Si un champ est manquant, afficher un message d'erreur et rediriger vers la page profiles
            elif username == "" or password == "" or telephone == "" or nom == "" or prenom == "" or email == "":
                flash("Merci de compléter le formulaire ", "danger")
                return redirect(url_for('profiles'))

            # Si aucun groupe n'a été sélectionné, afficher un message d'erreur et rediriger vers la page profiles
            elif groupe_pick == "choix":
                flash("Merci de choisir un groupe. Si aucun groupe n'est disponible, veuillez en créer un ", "danger")
                return redirect(url_for('profiles'))

            else:
                # Hasher le mot de passe avant de l'ajouter à la base de données
                result = hashlib.md5(password.encode('utf8')).hexdigest()
                
                # Ajouter les données à la table clients dans la base de données
                cursor.execute('INSERT INTO clients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', (username, nom, prenom, email, telephone, result, groupe_pick))
                mysql.connection.commit()
                
                # Afficher un message de succès et rediriger vers la page profiles
                flash("Utilisateur ajouté ", "success")
                return redirect(url_for('profiles'))
                
        # Si le formulaire est soumis mais incomplet, afficher un message d'erreur et rediriger vers la page profiles
        elif request.method == 'POST':
            flash("Merci de compléter le formulaire ", "danger")
    
    # Si l'utilisateur n'est pas connecté, rediriger vers la page de connexion
    return redirect(url_for('login'))


@app.route('/suppresion', methods=['GET', 'POST'])
def suppresion():
    # Récupération des paramètres de requête 'objet_id' et 'objet_type' depuis l'URL
    objet_id = request.args.get("objet_id")
    objet_type = request.args.get("objet_type")
    
    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:
        # Connexion à la base de données
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Suppression en fonction du type d'objet
        if objet_type == "Projet":
            # Suppression du projet et des tâches associées
            cursor.execute('DELETE FROM projet WHERE id = %s', [objet_id])
            cursor.execute('DELETE FROM tache WHERE id_projet = %s', [objet_id])

            # Validation des modifications dans la base de données
            mysql.connection.commit()
            # Notification de succès
            flash(f"{objet_type} ID : {objet_id} supprimé avec succès", "success")
            # Redirection vers la page appropriée
            return redirect(url_for('projets'))

        elif objet_type == "Utilisateur":
            # Suppression de l'utilisateur
            cursor.execute('DELETE FROM clients WHERE id = %s', [objet_id])

            # Validation des modifications dans la base de données
            mysql.connection.commit()
            # Notification de succès
            flash(f"{objet_type} ID : {objet_id} supprimé avec succès", "success")
            # Redirection vers la page appropriée
            return redirect(url_for('profiles'))

        elif objet_type == "Tâche":
            # Suppression de la tâche
            projet_id = request.args.get("projet_id")
            cursor.execute('DELETE FROM tache WHERE id = %s', [objet_id])

            # Validation des modifications dans la base de données
            mysql.connection.commit()
            # Notification de succès
            flash(f"{objet_type} ID : {objet_id} supprimée avec succès", "success")
            # Redirection vers la page appropriée
            return redirect(url_for('projet', projet_id=projet_id))

        elif objet_type == "Groupe":
            # Suppression du groupe
            cursor.execute('DELETE FROM groupe WHERE id = %s', [objet_id])

            # Validation des modifications dans la base de données
            mysql.connection.commit()
            # Notification de succès
            flash(f"{objet_type} ID : {objet_id} supprimé avec succès", "success")
            # Redirection vers la page appropriée
            return redirect(url_for('groupes'))

        elif objet_type == "Catégorie":
            # Suppression de la catégorie
            cursor.execute('DELETE FROM categories WHERE id = %s', [objet_id])

            # Validation des modifications dans la base de données
            mysql.connection.commit()
            # Notification de succès
            flash(f"{objet_type} ID : {objet_id} supprimée avec succès", "success")
            # Redirection vers la page appropriée
            return redirect(url_for('categories'))

        else:
            return redirect(url_for('login'))
    
    # Redirection vers la page de login si l'utilisateur n'est pas connecté
    return redirect(url_for('login'))


@app.route('/chat/ajout', methods=['GET', 'POST'])
def chat_ajout():
    # Récupération des paramètres de requête 'projet_id' depuis l'URL et du formulaire 'message'
    projet_id = request.args.get("projet_id")
    message = request.form['message']
    
    # Vérification si l'utilisateur est connecté
    if session['loggedin'] == True:
        # Connexion à la base de données
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Insertion d'un nouveau message dans la table 'conversation'
        cursor.execute('INSERT INTO conversation VALUES (NULL, %s, %s, %s, %s)', 
                       (projet_id, session['username'], message, datetime.now()))
        
        # Validation des modifications dans la base de données
        mysql.connection.commit()
        
        # Affichage du modal de chat après la redirection
        show_chat_modal = True
        # Redirection vers la page du projet avec le modal de chat affiché
        return redirect(url_for('projet', projet_id=projet_id, show_chat_modal=show_chat_modal))
    
    # Redirection vers la page de login si l'utilisateur n'est pas connecté
    else:
        return redirect(url_for('login'))


@socketio.on('message')
def handle_message(msg):
    # Récupération des informations du message
    project_id = msg['project_id']
    conversation = msg['conversation']
    
    # Vérification si la conversation est vide
    if conversation == "":
        pass
    else:
        # Connexion à la base de données
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Insertion d'un nouveau message dans la table 'conversation'
        cursor.execute('INSERT INTO conversation VALUES (NULL, %s, %s, %s, %s)', 
                       (project_id, session['username'], conversation, datetime.now()))
        
        # Validation des modifications dans la base de données
        mysql.connection.commit()
        
        # Récupération de l'heure actuelle formatée
        time = datetime.now().strftime("%H:%M %d/%m/%Y")
        
        # Emission d'un nouveau message à l'utilisateur actuel
        socketio.emit('new_message', 
                      {'time': time, 'utilisateur': session['username'], 'conversation': conversation, 
                       'project_id': project_id, 'is_current_user': True}, 
                      room=request.sid)
        
        # Préparation du message à envoyer aux autres utilisateurs
        emit_to_others = {'time': time, 'utilisateur': session['username'], 'conversation': conversation, 
                          'project_id': project_id, 'is_current_user': False}
        
        # Emission du nouveau message aux autres utilisateurs dans la salle du projet, sauf l'utilisateur actuel
        socketio.emit('new_message', emit_to_others, room=f"project_{project_id}", skip_sid=request.sid)


@socketio.on('connect')
def handle_connect():
    # Récupération de l'identifiant du projet sélectionné depuis la session
    project_id = session.get('projet_select')
    
    if project_id is not None:
        # Création du nom de la salle de discussion pour le projet
        room_name = f"project_{project_id}"
        
        # Ajout de l'utilisateur à la salle de discussion du projet
        join_room(room_name)
        
        # Vérification si la conversation du projet a déjà été chargée pour cette session
        if session.get(room_name) is None:
            # Connexion à la base de données
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Récupération de l'historique des messages de la conversation du projet
            cursor.execute("SELECT * FROM conversation WHERE id_projet = %s", [project_id])
            conversation = cursor.fetchall()
            
            # Envoi de chaque message de l'historique à l'utilisateur connecté
            for message in conversation:
                # Formatage de la date et de l'heure du message
                time = message['date'].strftime("%H:%M %d/%m/%Y")
                
                # Détermination si l'utilisateur actuel est l'auteur du message
                is_current_user = (session['username'] == message['utilisateur'])
                
                # Emission du message à l'utilisateur connecté
                socketio.emit('new_message', {
                    'time': time,
                    'utilisateur': message['utilisateur'],
                    'conversation': message['message'],
                    'project_id': project_id,
                    'is_current_user': is_current_user
                }, room=request.sid)
            
            # Marquage dans la session que la conversation du projet a été chargée
            session[room_name] = True
        
        
# Définition de la route pour se déconnecté
@app.route('/deconnexion')
def deconnexion():

    # Efface toutes les informations de session
    session.clear()

    # Définit la variable 'loggedin' à False
    session['loggedin'] = False

    # Redirige vers la page de connexion
    return redirect(url_for('login'))


if __name__ =='__main__':
    # Démarre l'application Flask en mode debug
    app.run(Debug=True)
    socketio.run(app)