# Les Importations

import pymysql as MySQLdb# nous importons le paquet Python capable d'interagir avec MYsqlite
import hashlib #pour hasher le mdp en md5


hostname = '141.94.37.252' #Hôte de la base de donnée
username = 'bleona_db' #Utilisateur de la base de donnée
password = '1Xayt12_4' #Mot de passe de la base de donnée
database = 'bleona' #Nom de la base de donnée
db_conn = MySQLdb.connect( host=hostname, user=username, passwd=password, db=database ) #Créer la connexion
db_cur = db_conn.cursor() #cursor pour pour les lignes



# Les Fonctions

#Fonction de connection a la base de donnée
def ConnectToDB():
    print("vous etes connecté a votre base de donnés")


#Fonction qui permet de créer un compte utilisateur
def CreateAccount():

    #Entrer pour les informations de l'utilisateur
    username = input("Entrez votre nom d'utilisateur : ")
    nom = input("Entrez votre nom : ")
    prenom = input("Entrez votre prénom : ")
    email = input("Entrez votre email : ")
    password = input("Entrez votre mot de passe : ")
    groupe = input("Entrez le nom du groupe : ")

    #Ajout d'une sécuriter au mot de passe en le hashant avec le protocol md5
    result = hashlib.md5(password.encode('utf8')).hexdigest()

    #Envoie des informations dans la base de données
    db_cur.execute('INSERT INTO clients (username, nom, prenom, email, password, groupe) VALUES (%s, %s, %s, %s, %s, %s)', (username, nom, prenom, email, result, groupe))
    db_conn.commit()

    #Message de succès
    print("vous avez créée un compte") 


#Fonction qui permet de supprimer un compte utilisateur
def RemoveAccount():

    #Entrer pour avoir l'utilisateur à supprimer
    username = input("Entrez l'username du client")

    #Vérification si le clients existe afin de pouvoir le supprimé
    db_cur.execute("SELECT * FROM clients WHERE username = (%s)",(username))
    account = db_cur.fetchone()
    if account :

        #Suppresion du client dans la base de donnée
        db_cur.execute( "DELETE FROM clients WHERE username = (%s)",(username))
        db_conn.commit()

        #Message de succés
        print("vous avez retiré un compte")

    else: 
        #Renvoie une erreur car l'utilisateur existe pas
        print("L'utilisateur n'existe pas")


#Fonction qui permet de afficher tout les comptes
def ShowAccount():
    #Récupération de tout les clients existant
    db_cur.execute( "select * from clients")
    all_clients = db_cur.fetchall()

    #Boucle afin de afficher chaque informations de chaque clients séparement
    for client in all_clients:
        print("Id = ", client[0], )
        print("Utilisateur = ", client[1])
        print("Nom  = ", client[2])
        print("Prénom  = ", client[3])
        print("Email = ", client[4], "\n")
    

#Fonction qui permet de ajouter de l'argent à un budget
def AddMoney():

    #Entrer pour avoir les informations du projet et la somme 
    nom_projet = input("Projet à qui la somme sera verser : ")
    somme = int(input("Entrez la somme à ajouter : "))

    #Vérification si le projet existe afin de pouvoir lui ajouter l'argent
    db_cur.execute("SELECT * FROM projet WHERE nom = (%s)",(nom_projet))
    project = db_cur.fetchone()
    if project : 

        #Calcule de la nouvelle somme
        amount = project[5] + somme

        #Modification de la somme dans la base de donnée
        db_cur.execute('UPDATE projet SET budget = %s WHERE nom = %s', (amount, nom_projet))
        db_conn.commit()
    
    else: 
        #Renvoie une erreur car le projet existe pas
        print("Le projet n'existe pas")


#Fonction qui permet de enlever de l'argent un à budget
def RemoveMoney():

    #Entrer pour avoir les informations du projet et la somme 
    nom_projet = input("Projet à qui la somme sera enlever : ")
    somme = int(input("Entrez la somme à enlever : "))

    #Vérification si le projet existe afin de pouvoir lui enlever l'argent
    db_cur.execute("SELECT * FROM projet WHERE nom = (%s)",(nom_projet))
    projet = db_cur.fetchone()
    if projet : 

        #Calcule de la nouvelle somme
        amount = projet[5] - somme

        #Modification de la somme dans la base de donnée
        db_cur.execute('UPDATE projet SET budget = %s WHERE nom = %s', (amount, nom_projet))
        db_conn.commit()
    
    else: 
        #Renvoie une erreur car le projet existe pas
        print("Le projet n'existe pas")


#Fonction qui permet de ajouter de l'argent à un budget
def ShowMoney():

    #Entrer pour avoir les informations du projet
    nom_projet = input("Nom du projet a vérifier : ")

    #Vérification si le projet existe afin de récuperer les informations de celui-ci
    db_cur.execute("SELECT * FROM projet WHERE nom = (%s)",(nom_projet))
    projet = db_cur.fetchone()

    if projet : 
        print("Le projet '", projet[1], "' à la somme de",projet[5], "€")
    
    else: 
        #Renvoie une erreur car le projet existe pas
        print("Le projet n'existe pas")


#Fonction qui permet de modifier le compte d'un utilisateur
def ModifyAccount():

    #Entrer pour avoir les informations du clients qui sera modifier
    username = input("Utilisateur du compte a vérifier : ")

    #Vérification si le clients existe afin de récuperer les informations de celui-ci
    db_cur.execute("SELECT * FROM clients WHERE username = (%s)",(username))
    account = db_cur.fetchone()

    if account :
        print("Si un champs n'as pas besoin d'être modifier veuillez le laisser vide ( ENTRER )")

        #Entrer avec les nouvelles informations
        username_mod = input("Nouveau nom d'utilisateur : ")
        nom = input("Nouveau nom : ")
        prenom = input("Nouveau prénom : ")
        email = input("Nouvelle email : ")
        password = input("Nouveau mot de passe : ") 
        groupe = input("Nouveau groupe de l'utilisateur : ")
        
        #Verification si le champs nom est vide
        if nom == "":
            pass
        else: 
            #Modification du nom dans la base de donnée
            db_cur.execute('UPDATE clients SET nom = %s WHERE username = %s', (nom, username))
            db_conn.commit()
        
        #Verification si le champs prenom est vide
        if prenom == "":
            pass
        else: 
            #Modification du prénom dans la base de donnée
            db_cur.execute('UPDATE clients SET prenom = %s WHERE username = %s', (prenom, username))
            db_conn.commit()
        
        #Verification si le champs email est vide
        if email == "":
            pass
        else: 
            #Modification de l'email dans la base de donnée
            db_cur.execute('UPDATE clients SET email = %s WHERE username = %s', (email, username))
            db_conn.commit()
        
        #Verification si le champs mot de passe est vide
        if password == "":
            pass
        else: 
            
            #Ajout d'une sécuriter au mot de passe en le hashant avec le protocol md5
            result = hashlib.md5(password.encode('utf8')).hexdigest()

            #Modification du mot de passe dans la base de donnée
            db_cur.execute('UPDATE clients SET password = %s WHERE username = %s', (result, username))
            db_conn.commit()
        
        #Verification si le champs groupe est vide
        if groupe == "":
            pass
        else: 
            #Modification du groupe dans la base de donnée
            db_cur.execute('UPDATE clients SET groupe = %s WHERE username = %s', (groupe, username))
            db_conn.commit()
        
        #Verification si le champs nom d'utilisateur est vide
        if username_mod == "":
            pass
        else: 
            #Modification du nom d'utilisateur dans la base de donnée
            db_cur.execute('UPDATE clients SET username = %s WHERE username = %s', (username_mod, username))
            db_conn.commit()

    else: 
        #Renvoie une erreur car l'utilisateur existe pas
        print("L'utilisateur n'existe pas")


#Fonction qui permet de créer un projet
def CreateProject():

    #Entrer pour les informations du projet a créer
    nom = input("Entrez le nom du projet : ")
    categorie = input("Entrez la catégorie : ")
    fin = input("Entrez la date de fin ( JJ/MM/AAAA ) : ")
    groupe = input("Entrez le groupe assigné : ")
    budget = input("Entrez le budget du projet : ")

    #Envoie des informations dans la base de données
    db_cur.execute('INSERT INTO projet (nom, categorie, date_fin, groupe, budget) VALUES (%s, %s, %s, %s, %s)', (nom, categorie, fin, groupe, budget))
    db_conn.commit()

    #Message de succès
    print("vous avez créée un projet") 


#Fonction qui permet de modifier le projet
def ModifyProject():

    #Entrer pour avoir les informations du projet qui sera modifier
    id_projet = input("Projet à modifié ( ID ): ")

    #Vérification si le projet existe afin de récuperer les informations de celui-ci
    db_cur.execute("SELECT * FROM projet WHERE id = (%s)",(id_projet))
    projet = db_cur.fetchone()

    if projet :
        print("Si un champs n'as pas besoin d'être modifier veuillez le laisser vide ( ENTRER )")

        #Entrer avec les nouvelles informations
        nom = input("Nouveau nom de projet : ")
        fin = input("Nouvelle date de fin ( JJ/MM/AAAA ) : ")
        categorie = input("Assigné une autre catégorie : ")
        groupe = input("Assigné un autre groupe : ")
        
        #Verification si le champs nom est vide
        if nom == "":
            pass
        else: 
            #Modification du nom dans la base de donnée
            db_cur.execute('UPDATE projet SET nom = %s WHERE id = %s', (nom, id_projet))
            db_conn.commit()
        
        #Verification si le champs prenom est vide
        if fin == "":
            pass
        else: 
            #Modification du prénom dans la base de donnée
            db_cur.execute('UPDATE clients SET date_fin = %s WHERE id = %s', (fin, id_projet))
            db_conn.commit()
        
        #Verification si le champs email est vide
        if categorie == "":
            pass
        else: 
            #Modification de l'email dans la base de donnée
            db_cur.execute('UPDATE clients SET categorie = %s WHERE id = %s', (categorie, id_projet))
            db_conn.commit()
        
        #Verification si le champs mot de passe est vide
        if groupe == "":
            pass
        else: 
            #Modification du mot de passe dans la base de donnée
            db_cur.execute('UPDATE clients SET groupe = %s WHERE id = %s', (groupe, id_projet))
            db_conn.commit()

    else: 
        #Renvoie une erreur car l'utilisateur existe pas
        print("Le projet n'existe pas")


#Fonction qui permet de afficher tout les projets
def ShowProject():
    #Récupération de tout les projets existant
    db_cur.execute( "select * from projet")
    all_projects = db_cur.fetchall()

    #Boucle afin de afficher chaque informations de chaque projet séparement
    for project in all_projects:
        print("Id = ", project[0], )
        print("Nom du projet = ", project[1])
        print("Catégorie = ", project[2])
        print("Date de fin  = ", project[3])
        print("Groupe assigné = ", project[4])
        print("Budget = ", project[5], "€\n")


#Fonction qui permet de supprimer un projet
def RemoveProject():

    #Entrer pour avoir le projet à supprimer
    id_projet = input("Projet à supprimé ( ID ) : ")

    #Vérification si le projet existe afin de pouvoir le supprimé
    db_cur.execute("SELECT * FROM projet WHERE id = (%s)",(id_projet))
    account = db_cur.fetchone()
    if account :

        #Suppresion du projet dans la base de donnée
        db_cur.execute( "DELETE FROM projet WHERE id = (%s)",(id_projet))
        db_conn.commit()

        #Message de succés
        print("vous avez supprimé le projet")

    else: 
        #Renvoie une erreur car le projet existe pas
        print("Le projet n'existe pas")
    

#Fonction qui permet de créer un groupe
def CreateGroupe():

    #Entrer pour les informations du groupe a créer
    nom = input("Entrez le nom du groupe : ")
    description = input("Entrez la description du groupe : ")

    #Envoie des informations dans la base de données
    db_cur.execute('INSERT INTO groupe (nom, description) VALUES (%s, %s)', (nom, description))
    db_conn.commit()

    #Message de succès
    print("vous avez créée un groupe") 


#Fonction qui permet de supprimer un groupe
def RemoveGroupe():

    #Entrer pour avoir le groupe à supprimer
    nom_groupe = input("Entrez le nom du groupe : ")

    #Vérification si le groupe existe afin de pouvoir le supprimé
    db_cur.execute("SELECT * FROM groupe WHERE nom = (%s)",(nom_groupe))
    groupe = db_cur.fetchone()
    if groupe :

        #Suppresion du groupe dans la base de donnée
        db_cur.execute("DELETE FROM groupe WHERE nom = (%s)",(nom_groupe))
        db_conn.commit()

        #Message de succés
        print("vous avez retiré un groupe")

    else: 
        #Renvoie une erreur car le groupe existe pas
        print("L'utilisateur n'existe pas")

#Fonction qui permet de afficher tout les groupes
def ShowGroupe():
    #Récupération de tout les groupes existant
    db_cur.execute( "select * from groupe")
    all_groupes = db_cur.fetchall()

    #Boucle afin de afficher chaque informations de chaque groupe séparement
    for groupe in all_groupes:
        print("Id = ", groupe[0])
        print("Nom = ", groupe[1])
        print("Description = ", groupe[2], "\n")


#Fonction qui permet de modifier le groupe
def ModifyGroupe():

    #Entrer pour avoir les informations du groupe qui sera modifier
    id_groupe = input("Groupe à modifié ( ID ): ")

    #Vérification si le groupe existe afin de récuperer les informations de celui-ci
    db_cur.execute("SELECT * FROM groupe WHERE id = (%s)",(id_groupe))
    groupe = db_cur.fetchone()

    if groupe :
        print("Si un champs n'as pas besoin d'être modifier veuillez le laisser vide ( ENTRER )")

        #Entrer avec les nouvelles informations
        nom = input("Nouveau nom de groupe : ")
        description = input("Nouvelle description : ")
        
        #Verification si le champs nom est vide
        if nom == "":
            pass
        else: 
            #Modification du nom dans la base de donnée
            db_cur.execute('UPDATE groupe SET nom = %s WHERE id = %s', (nom, id_groupe))
            db_conn.commit()
        
        #Verification si le champs prenom est vide
        if description == "":
            pass
        else: 
            #Modification du prénom dans la base de donnée
            db_cur.execute('UPDATE groupe SET description = %s WHERE id = %s', (description, id_groupe))
            db_conn.commit()

    else: 
        #Renvoie une erreur car l'utilisateur existe pas
        print("Le projet n'existe pas")


#Boucle avec le menu de navigation
while True:
    print("Gestion de project")
    print("Menu - Accueil\n\n0 - Quitter\n1 - Projet\n2 - Utilisateur | Groupe\n3 - Budget")

    mainChoice = input("\n\nChoix : ")

    if mainChoice == "0":
        break

    elif mainChoice == "1":
        print("Menu - Projet\n\n0 - Quitter\n1 - Créer un projet\n2 - Supprimer un projet\n3 - Modifier un projet\n4 - Lister les projets")

        Choice = input("\n\nChoix : ")

        if Choice == "0":
            break

        elif Choice == "1":
            CreateProject()

        elif Choice == "2":
            RemoveProject()

        elif Choice == "3":
            ModifyProject()
        
        elif Choice == "4":
            ShowProject()

    elif mainChoice == "2":
        print("Menu - Utilisateur\n\n0 - Quitter\n1 - Créer un utilisateur\n2 - Supprimer un utilisateur\n3 - Modifier un utilisateur\n4 - Lister les utilisateurs\n\n5 - Créer un groupe\n6 - Supprimer un groupe\n7 - Modifier un groupe\n8 - Lister les groupes")

        Choice = input("\n\nChoix : ")

        if Choice == "0":
            break

        elif Choice == "1":
            CreateAccount()

        elif Choice == "2":
            RemoveAccount()
            
        elif Choice == "3":
            ModifyAccount()
        
        elif Choice == "4":
            ShowAccount()
        
        elif Choice == "5":
            CreateGroupe()
        
        elif Choice == "6":
            RemoveGroupe()

        elif Choice == "7":
            ModifyGroupe()

        elif Choice == "8":
            ShowGroupe()

        else : 
            "L'option n'existe pas"
    
    elif mainChoice == "3":
        print("Menu - Budget\n\n0 - Quitter\n1 - Ajouter du budget\n2 - Enlever du budget\n3 - Afficher le budget d'un projet")

        Choice = input("\n\nChoix : ")

        if Choice == "0":
            break

        elif Choice == "1":
            AddMoney()

        elif Choice == "2":
            RemoveMoney()
        
        elif Choice == "3":
            ShowMoney()

        else : 
            "L'option n'existe pas"

    else : 
        "L'option n'existe pas"
