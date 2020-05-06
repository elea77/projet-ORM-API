from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests, json


# Instancier notre application dont le nom est __main__
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/bdd_orm'
db = SQLAlchemy(app)

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
    
# L’application démarre à partir de cette ligne.
if __name__=='__main__':

	# Le mode debug est bien pratique pour développer, mais à ne surtout par laisser quand votre site sera disponible sur Internet.
    app.run(debug=True)

    # L'objet app est configurable. On peut par exemple lui configurer sa clé secrète (qui sera indispensable pour sécuriser les sessions des visiteurs).
    # app.secret_key = '6590c29cf14027ffe0cf70d4c826f104'

# On lance l’application à partir de la console (cmd et non un shell Python)
# python path\to_appFlask.py
#py -3 app.py / flask run / python3 app.py
# Un message indique qu’un serveur web écoute sur l’interface locale sur le port 5000. On peut Vérifier le contenu de la page avec un navigateur web.



