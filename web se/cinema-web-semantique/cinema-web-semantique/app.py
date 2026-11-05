import re
from flask import Flask, jsonify, request
from graph import G_BRUT, G_INFERE
import queries as q

app = Flask(__name__)
app.json.ensure_ascii = False  # accents lisibles dans le JSON


def graphe_choisi():
    """?inference=false -> graphe brut ; sinon graphe avec inférence."""
    if request.args.get("inference", "true").lower() == "false":
        return G_BRUT
    return G_INFERE


def entier_optionnel(nom):
    valeur = request.args.get(nom)
    if valeur is None:
        return None
    if not valeur.isdigit():
        raise ValueError(f"Le paramètre '{nom}' doit être un entier positif.")
    return int(valeur)


def reponse(liste):
    return jsonify({"nombre": len(liste), "resultats": liste})


@app.errorhandler(ValueError)
def erreur_400(e):
    return jsonify({"erreur": str(e)}), 400


@app.errorhandler(404)
def erreur_404(e):
    return jsonify({"erreur": "Ressource introuvable."}), 404


@app.errorhandler(500)
def erreur_500(e):
    return jsonify({"erreur": "Erreur interne du serveur."}), 500


@app.get("/")
def accueil():
    return jsonify({"api": [
        "/api/films?annee_min=2017&duree_min=90",
        "/api/films/<id>",
        "/api/genres/<nom>/films",
        "/api/realisateurs",
        "/api/acteurs/<nom>/films",
        "/api/salles?ville=Tunis",
        "/api/personnes?inference=false|true",
        "/api/inference/comparaison",
    ]})


# API 1 : liste des films (paramètres facultatifs)
@app.get("/api/films")
def api_films():
    return reponse(q.films(graphe_choisi(),
                           entier_optionnel("annee_min"),
                           entier_optionnel("duree_min")))


# API 2 : détail d'un film + équipe
@app.get("/api/films/<film_id>")
def api_film(film_id):
    if not re.fullmatch(r"[A-Za-z0-9_]+", film_id):
        raise ValueError("Identifiant de film invalide.")
    detail = q.film_detail(G_INFERE, film_id)
    if not detail:
        return jsonify({"erreur": f"Film '{film_id}' introuvable."}), 404
    resultat = detail[0]
    resultat["id"] = film_id
    resultat["equipe"] = q.equipe_film(G_INFERE, film_id)
    return jsonify(resultat)


# API 3 : films d'un genre
@app.get("/api/genres/<nom>/films")
def api_genre(nom):
    liste = q.films_par_genre(graphe_choisi(), nom)
    if not liste:
        return jsonify({"erreur": f"Aucun film pour le genre '{nom}'."}), 404
    return reponse(liste)


# API 4 : réalisateurs et nombre de films
@app.get("/api/realisateurs")
def api_realisateurs():
    return reponse(q.realisateurs(graphe_choisi()))


# API 5 : films d'un acteur
@app.get("/api/acteurs/<nom>/films")
def api_acteur(nom):
    liste = q.films_acteur(graphe_choisi(), nom)
    if not liste:
        return jsonify({"erreur": f"Aucun acteur trouvé pour '{nom}'."}), 404
    return reponse(liste)


# API 6 : salles (filtre ville facultatif)
@app.get("/api/salles")
def api_salles():
    return reponse(q.salles(graphe_choisi(), request.args.get("ville")))


# API 7 : personnes (montre l'effet de l'inférence)
@app.get("/api/personnes")
def api_personnes():
    return reponse(q.personnes(graphe_choisi()))


# API 8 : comparaison avec / sans inférence
@app.get("/api/inference/comparaison")
def api_comparaison():
    return jsonify({
        "triplets": {"sans_inference": len(G_BRUT), "avec_inference": len(G_INFERE)},
        "personnes_foaf": {"sans_inference": len(q.personnes(G_BRUT)),
                           "avec_inference": len(q.personnes(G_INFERE))},
        "acteurs": {"sans_inference": len(q.acteurs(G_BRUT)),
                    "avec_inference": len(q.acteurs(G_INFERE))},
        "participations": {"sans_inference": len(q.participations(G_BRUT)),
                           "avec_inference": len(q.participations(G_INFERE))},
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
