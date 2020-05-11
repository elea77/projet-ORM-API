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
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Instancier notre application dont le nom est __main__
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/bdd_orm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
Bootstrap(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=False, nullable=False)
    avatar = db.Column(db.String(120), unique=False, default='avatar.png', nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return '<User %r>' % self.username


class Favorite_movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_movie = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref("user", uselist=False))

    def __repr__(self):
        return '<Favorite_movie %r>' % self.id_movie


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.Text, unique=False, nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref("user", uselist=False))

    def __repr__(self):
        return '<Review %r>' % self.review



# API
# r = requests.get('https://api.themoviedb.org/3/movie/550?api_key=6590c29cf14027ffe0cf70d4c826f104&append_to_response=videos,images')


#Page d'accueil
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

    # Ajout d'un film à sa collection
    if request.method == "POST":
        if "username" in session:
            username = session["username"]
            iddata = db.session.execute("SELECT id FROM user WHERE username=:username", 
                {'username':username}).fetchone()
            

            for id_user in iddata:
                session["id_user"] = id_user
                id_user = session["id_user"]

            db.session.execute('INSERT INTO favorite_movie(id_movie, user_id) VALUES(:id, :id_user)',
                { 'id':id, 'id_user':id_user })
            db.session.commit()
        
        return redirect(url_for("collection"))

    return render_template('pages/movie.html', id=id, title=title, overview=overview, image = image, genres=genres, note=note, date=date)


# Affichage des films de la collection
@app.route('/collection')
def collection():
    if "id_user" in session:

        id_user = session["id_user"]
        iddata = db.session.execute("SELECT id_movie FROM favorite_movie WHERE user_id=:id_user", 
            {'id_user':id_user}).fetchall()
        
        for id_mov in iddata:

            id_movie = [item['id_movie'] for item in iddata]
            # i = 0
            # title = id_movie[0]
            # print(id_movie)
        # liste = [278, 514847, 495764, 585244, 278, 585244, 35]
        # for x in liste:
        #     print(x)

        # liste = []

        images = []
        titles = []
        for i in id_movie:
            # x = id_movie[i]
            # i = int(i)
            # x ='test'
            # print(id_movie[i])
            # print(id_movie[i])

        #     liste = []
        #     liste.append(i)
            # yield i
            
            # print(int(i))
            i = str(i)
            r = requests.get("https://api.themoviedb.org/3/movie/" + i + "?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
            json_obj = r.json()
            # x = list(json_obj)
            image = str(json_obj['poster_path'])
            title = str(json_obj['title'])
            images.append(image)
            titles.append(title)
            # print(x[0])
            # print('fin loop')
            # return render_template('pages/collection.html', id_movie=id_movie, image=image)
        print('fin')
        print(images)
        print(titles)
        # print(x[1])
        # title = 'tt'
        # image ='r'

        print(id_movie)
        #     title = str(json_obj['title'])
        #     print(i)
                # print(id_movie[i])
                # title = []
                # title.append(id_movie[i])
                # print(title)
                # print(i)
            

                # i += 1
            # title = [id_movie[i]]
            # for test in id_movie:
            #     # tests = id_movie[i]
            #     tests = []
            #     tests.append(id_movie[i])
            #     image = 'jepg'
            #     title='title'
            #     i += 1
            # x = 1
            # for item in id_movie:
            #     id = str(item[x])
            #     r = requests.get("https://api.themoviedb.org/3/movie/" + id + "?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
            #     json_obj = r.json()
            #     image = str(json_obj['poster_path'])
            #     title = str(json_obj['title']) 
            #     x +=1
            # session["id_movie"] = id_movie
            # id_movie = list(session["id_movie"])
            # id_movie = list(id_movie)
            # r = requests.get("https://api.themoviedb.org/3/movie/" + id_movie + "?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
            # json_obj = r.json()
            # image = list(json_obj['poster_path']) 
            # title = str(json_obj['title'])
            # id_movie = []
            # id_movie.append(id_mov)
            # for lettre in id_movie:
                
                # lettre = item['id_movie']
                # lettre = str(lettre)
                # r = requests.get("https://api.themoviedb.org/3/movie/" + lettre + "?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
                # json_obj = r.json()
                # image = str(json_obj['poster_path'])
                # title = str(json_obj['title']) 
            #     id_movie = lettre
            # id_movie = str(id_mov["id_movie"])
            # title = 'title'
            # image = 'test.jpg'

        return render_template('pages/collection.html', id_movie=id_movie, image=image, titles=titles, images=images)
    
    return render_template('pages/collection.html')




@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        secure_password = sha256_crypt.encrypt(str(password))

        if password == confirm:
            db.session.execute('INSERT INTO user(username, email, password) VALUES(:username, :email, :password)',
                { 'username':username, 'email':email, 'password':secure_password })
            db.session.commit()

            return redirect(url_for('login'))
        else:
            flash('Les mots de passe ne correspondent pas')
            return render_template('pages/register.html')

    return render_template('pages/register.html')




@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        usernamedata = db.session.execute('SELECT username FROM user WHERE username=:username', 
            {'username':username}).fetchone()
        passworddata = db.session.execute('SELECT password FROM user WHERE username=:username', 
            {'username':username}).fetchone()

        for password_data in passworddata:
            if sha256_crypt.verify(password, password_data):
                flash("Vous êtes maintenant connecté !","success")
                session["username"] = username
                return redirect(url_for("profile"))
            else:
                flash("Mot de passe incorrect","error")
                return render_template('pages/login.html')
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
    session.pop("id_user", None)
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

