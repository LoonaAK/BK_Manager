## BK-Manager le gestionnaire de portefeuille fait pour vous !

### Exigences (minimales)

Téléchargez et installez Python,  assurez-vous de cocher la case Ajouter Python à PATH sur l'écran de configuration de l'installation. </p>

 
### Installation
Accédez au répertoire de votre projet actuel dans ce cas, ce sera **BK_Manager**. <br>

### 1 .Cloner le fichier dans votre machine locale
```
git clone https://github.com/LoonaAK/BK_Manager.git
```
          
### 2 .Créer un environnement
          
```
cd BK_Manager
py -3 -m venv venv
```

### 3. Activer l'environnement

```venv\Scripts\activate```

### 4. Installez les exigences

```pip install -r requirements.txt```
  
### 5. Configuration de l'application

> Configuration de la base de donnée dans le fichier app.py
```
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
```

> Configuration de la base de donnée dans le fichier db.py
```
MYSQL_HOST = ''
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_DB = ''
```

Ainsi que lancer le fichier db.py afin de mettre en route la base de données
```python db.py```


### 6. Run the application 

```
flask run
```