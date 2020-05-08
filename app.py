from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from passlib.hash import sha256_crypt
import requests, json



# Instancier notre application dont le nom est __main__
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/bdd_orm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
Bootstrap(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=False, nullable=False)
    avatar = db.Column(db.String(120), unique=False, nullable=True)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return '<User %r>' % self.username


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.Text, unique=False, nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref("user", uselist=False))

    def __repr__(self):
        return '<Review %r>' % self.review


class Favorite_movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_movie = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref("user", uselist=False))

    def __repr__(self):
        return '<Favorite_movie %r>' % self.id_movie


# API
# r = requests.get('https://api.themoviedb.org/3/movie/550?api_key=6590c29cf14027ffe0cf70d4c826f104&append_to_response=videos,images')


@app.route('/')
def index():
    titre = "Ceci est la page d'accueil du site"
    r = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
    json_obj = r.json()
    genres = list(json_obj["genres"])

    r2 = requests.get("https://api.themoviedb.org/3/movie/top_rated?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR&page=1&region=us")
    json_obj = r2.json()
    tops = list(json_obj["results"])
    
    return render_template('pages/index.html', titre=titre, genres=genres, tops=tops)


@app.route('/movie', methods=["GET","POST"])
def movie():
    movie_id = request.form.get("id")
    r = requests.get("https://api.themoviedb.org/3/movie/" + movie_id + "?api_key=6590c29cf14027ffe0cf70d4c826f104&language=fr-FR")
    json_obj = r.json()
    title = str(json_obj['original_title'])
    overview = str(json_obj['overview'])
    image = str(json_obj['poster_path']) 
    return render_template('pages/movie.html', id=movie_id, title=title, overview=overview, image = image)



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
                flash("You are now login","success")
                return redirect(url_for("index"))
            else:
                flash("Incorrect password","danger")
                render_template('pages/login.html')

    return render_template('pages/login.html')



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

