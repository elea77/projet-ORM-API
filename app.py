from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import requests, json



# Instancier notre application dont le nom est __main__
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/bdd_orm'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)
    avatar = db.Column(db.String(120), unique=False, nullable=False)
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
    return render_template('pages/test.html', id=movie_id, title=title, overview=overview, image = image)

    

@app.errorhandler(404)
def page_not_found(error):
    return render_template('pages/404.html')
    

if __name__=='__main__':
    app.run(debug=True)