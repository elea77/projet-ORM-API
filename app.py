from flask import Flask, render_template
import requests


# Instancier notre application dont le nom est __main__
app = Flask(__name__)

# API
# r = requests.get('https://api.themoviedb.org/3/movie/550?api_key=6590c29cf14027ffe0cf70d4c826f104&append_to_response=videos,images')


@app.route('/')
def index():
    titre = "Ceci est la page d'accueil du site"
    return render_template('pages/index.html', titre=titre)
    
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



