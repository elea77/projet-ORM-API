from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from flask_login import login_manager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt
import requests, json, datetime, random, os
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/avatars/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Instancier notre application dont le nom est __main__
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/bdd_orm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
Bootstrap(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(150), server_default="avatar.png", nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return '<User %r>' % self.username


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(80), nullable=False)
    overview = db.Column(db.Text(1200), nullable=True)

    def __repr__(self):
        return '<Movie %r>' % self.title


class User_Movie(db.Model):
    __tablename__ = 'user_movie'
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True) 

    def __repr__(self):
        return '<User_Movie %r>' % self.movie_id


# API
# r = requests.get('https://api.themoviedb.org/3/movie/550?api_key=6590c29cf14027ffe0cf70d4c826f104&append_to_response=videos,images')



#Page d'accueil : index.html
@app.route('/')
def home():
    titre = "Ceci est la page d'accueil du site"

    # Liste des genres de film
    r = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
    json_obj = r.json()
    genres = list(json_obj["genres"])

    # Liste des films à l'affiche
    r2 = requests.get("https://api.themoviedb.org/3/movie/now_playing?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR&page=1&region=fr")
    json_obj = r2.json()
    now_playing = list(json_obj["results"])

    # Liste des films les mieux notés
    r3 = requests.get("https://api.themoviedb.org/3/movie/top_rated?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR&page=1&region=fr")
    json_obj = r3.json()
    tops = list(json_obj["results"])

    # Liste des films populaire
    r4 = requests.get("https://api.themoviedb.org/3/movie/popular?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR&page=1&region=fr")
    json_obj = r4.json()
    populars = list(json_obj["results"])

    # Liste des films bientot disponible
    r5 = requests.get("https://api.themoviedb.org/3/movie/upcoming?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR&page=1&region=fr")
    json_obj = r5.json()
    upcomings = list(json_obj["results"])

    return render_template('pages/index.html', titre=titre, genres=genres, now_playing=now_playing, tops=tops, populars=populars, upcomings=upcomings)



# Recherche de film
@app.route('/movie_search', methods=["GET","POST"])
def movie_search():

    movie_title = request.form.get("movie_title")
    r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR&query=" + movie_title + "&page=1&include_adult=false&region=fr")
    json_obj = r.json()
    results = list(json_obj['results'])

    return render_template('pages/movieSearch.html', results=results, recherche=movie_title )



#Affichage des informations d'un film
@app.route('/movie/<id>', methods=["GET","POST"])
def movie(id):
    r = requests.get("https://api.themoviedb.org/3/movie/" + id + "?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
    json_obj = r.json()

    # Récupération des infos de l'API
    title = str(json_obj['title'])
    overview = str(json_obj['overview'])
    image = str(json_obj['poster_path']) 
    genres = list(json_obj['genres'])
    note = str(json_obj['vote_average'])
    date = str(json_obj['release_date'])

    message = 'Null'

    if 'user_id' in session :
        user_id = session["user_id"]

        # Verifier si le film fait parti de la collection 
        iddata = db.session.execute("SELECT movie_id FROM user_movie WHERE user_id=:user_id AND movie_id=:id", 
            { 'id':id, 'user_id':user_id}).fetchone()

        
        
        if iddata :
            message = 'True' # Le film est deja dans la collection
        else :
            message = 'False' # Le film n'est pas dans la collection


    # Ajout ou Suprression d'un film de sa collection
    if request.method == "POST":
        if "user_id" in session:
            bouton = request.form.get('btn')

            if bouton == 'add' :

                movie = db.session.execute("SELECT id FROM movie WHERE id=:id", 
                    { 'id':id}).fetchone()
        
                if not movie :
                    db.session.execute('INSERT INTO movie(id, title, overview) VALUES(:id, :title, :overview)',
                    { 'id':id, 'title':title, 'overview':overview })

                db.session.execute('INSERT INTO user_movie(movie_id, user_id) VALUES(:id, :user_id)',
                    { 'id':id, 'user_id':user_id })

                db.session.commit()  

            if bouton == 'del':

                user_movie = db.session.execute('DELETE FROM user_movie WHERE user_id=:user_id AND movie_id=:id', 
                { 'id':id, 'user_id':user_id })
                db.session.commit()
                
        return redirect(url_for("collection"))

    return render_template('pages/movie.html', id=id, title=title, overview=overview, image = image, genres=genres, note=note, date=date, message=message)


# Affichage des films de la collection <=> Favorite Movies
@app.route('/collection')
def collection():
    if "user_id" in session:

        user_id = session["user_id"]
        
        iddata = db.session.execute("SELECT movie_id FROM user_movie WHERE user_id=:user_id", 
            {'user_id':user_id}).fetchall()

        
        if not iddata :
            message = 'Votre collection est vide'
            return render_template('pages/collection.html', message=message)
        
        else:
            for id_mov in iddata:

                movie_id = [item['movie_id'] for item in iddata]

            images = []
            titles = []
            for i in movie_id:
                i = str(i)
                r = requests.get("https://api.themoviedb.org/3/movie/" + i + "?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
                json_obj = r.json()
                image = str(json_obj['poster_path'])
                title = str(json_obj['title'])
                images.append(image)
                titles.append(title)

            zipped = zip(movie_id,images, titles)

            liste = list(zipped)

        return render_template('pages/collection.html', movie_id=movie_id, liste=liste)
    else :
        return redirect(url_for('login'))
    
    return render_template('pages/collection.html')




@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        secure_password = sha256_crypt.encrypt(str(password))

        # On vérifie si le pseudo est disponible
        usernamedata = db.session.query(User).filter(User.username == username).first()

        #Si le pseudo est disponible ..
        if usernamedata == None : 

            # On vérifie si l'email est disponible
            emaildata = db.session.query(User).filter(User.email == email).first()

            #Si l'email est disponible ..
            if emaildata == None :

                if password == confirm:
                    db.session.execute('INSERT INTO user(username, email, password) VALUES(:username, :email, :password)',
                        { 'username':username, 'email':email, 'password':secure_password })
                    db.session.commit()

                    return redirect(url_for('login'))
                else:
                    flash('Les mots de passe ne correspondent pas')
                    return redirect(url_for("register"))
            else :
                flash('Cette adresse email est déjà prise')
                return redirect(url_for("register"))
        else :
            flash('Ce pseudo est déjà pris')
            return redirect(url_for("register"))

    return render_template('pages/register.html')




@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        data = db.session.query(User).filter(User.username == username).first()

        if data != None:
            
            passworddata = data.password

            if passworddata != None :

                if sha256_crypt.verify(password, passworddata):
                    flash("Vous êtes maintenant connecté !","success")
                    session["username"] = username

                    user_id = data.id

                    session["user_id"] = user_id
                    user_id = session["user_id"]

                    return redirect(url_for("profile"))
                else :
                    flash("Mot de passe incorrect","error")
                    return redirect(url_for("login"))
        else :
            flash("Pseudo inexistant","error")
            return redirect(url_for("login"))
    else :
        if "username" in session:
            return redirect(url_for("home"))

    return render_template('pages/login.html')





def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile', methods=["GET","POST"])
def profile():
    if "username" in session:
        username = session["username"]

        emaildata = db.session.execute("SELECT email FROM user WHERE username=:username", 
            {'username':username}).fetchone()

        datedata = db.session.execute("SELECT date FROM user WHERE username=:username", 
            {'username':username}).fetchone()

        avatardata = db.session.execute("SELECT avatar FROM user WHERE username=:username", 
            {'username':username}).fetchone()

        for email in emaildata:
            session["email"] = email
            email = session["email"]

        for date in datedata:
            session["date"] = date
            date = session["date"]

        for avatar in avatardata:
            session["avatar"] = avatar
            avatar = session["avatar"]

        if request.method == 'POST':
            file = request.files['file']

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                db.session.execute('UPDATE user SET avatar=:filename WHERE username=:username',
                    { 'username':username, 'filename':filename })
                db.session.commit()

                return redirect(url_for('profile'))

            return render_template('pages/profile.html', username=username, email=email, date=date, avatar=avatar)

        return render_template('pages/profile.html', username=username, email=email, date=date, avatar=avatar)
    return render_template('pages/login.html')




@app.route('/logout')
def logout():
    session.pop("username", None)
    session.pop("user_id", None)
    return redirect(url_for("login"))



@app.errorhandler(404)
def page_not_found(error):
    return render_template('pages/404.html')
    

if __name__=='__main__':
    app.secret_key = '6590c29cf14027ffe0cf70d4c826f104'
    app.run(debug=True)
    # L'objet app est configurable. On peut par exemple lui configurer sa clé secrète (qui sera indispensable pour sécuriser les sessions des visiteurs).
    

# On lance l’application à partir de la console (cmd et non un shell Python)
# python path\to_appFlask.py
# Un message indique qu’un serveur web écoute sur l’interface locale sur le port 5000. On peut Vérifier le contenu de la page avec un navigateur web.

