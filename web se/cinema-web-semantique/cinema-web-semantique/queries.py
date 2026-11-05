from rdflib import Literal

NS = "http://example.org/cinema#"

PREFIXES = """
PREFIX cin:  <http://example.org/cinema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""


def convertir(valeur):
    """Transforme un résultat SPARQL en valeur JSON simple."""
    if isinstance(valeur, Literal):
        return valeur.toPython()
    texte = str(valeur)
    return texte[len(NS):] if texte.startswith(NS) else texte


def executer(g, requete):
    return [
        {cle: convertir(val) for cle, val in ligne.asdict().items()}
        for ligne in g.query(PREFIXES + requete)
    ]


def lit(texte):
    """Littéral SPARQL échappé (évite les injections)."""
    return Literal(texte).n3()


# Q1 : liste des films (avec filtres facultatifs)
def films(g, annee_min=None, duree_min=None):
    filtres = ""
    if annee_min is not None:
        filtres += f"FILTER(?annee >= {int(annee_min)})\n"
    if duree_min is not None:
        filtres += f"FILTER(?duree >= {int(duree_min)})\n"
    return executer(g, f"""
SELECT ?id ?titre ?annee ?duree WHERE {{
  ?id a cin:Film ; cin:titre ?titre ; cin:anneeSortie ?annee ; cin:duree ?duree .
  {filtres}
}} ORDER BY ?annee""")


# Q2 : films d'un genre donné
def films_par_genre(g, genre):
    return executer(g, f"""
SELECT ?id ?titre ?annee WHERE {{
  ?id a cin:Film ; cin:titre ?titre ; cin:anneeSortie ?annee ; cin:aGenre ?g .
  ?g rdfs:label ?nomGenre .
  FILTER(LCASE(STR(?nomGenre)) = LCASE({lit(genre)}))
}} ORDER BY ?annee""")


# Q3 : réalisateurs et nombre de films (GROUP BY + COUNT)
def realisateurs(g):
    return executer(g, """
SELECT ?nom (COUNT(?film) AS ?nbFilms) WHERE {
  ?r a cin:Realisateur ; foaf:name ?nom ; cin:realise ?film .
} GROUP BY ?nom ORDER BY DESC(?nbFilms) ?nom""")


# Q4 : films d'un acteur (recherche par nom)
def films_acteur(g, nom):
    return executer(g, f"""
SELECT ?acteur ?id ?titre WHERE {{
  ?a foaf:name ?acteur ; cin:joueDans ?id .
  ?id cin:titre ?titre .
  FILTER(CONTAINS(LCASE(?acteur), LCASE({lit(nom)})))
}} ORDER BY ?titre""")


# Q5 : salles avec nombre de films projetés (OPTIONAL + COUNT)
def salles(g, ville=None):
    filtre = f"FILTER(LCASE(?ville) = LCASE({lit(ville)}))" if ville else ""
    return executer(g, f"""
SELECT ?id ?nom ?ville (COUNT(?film) AS ?nbFilms) WHERE {{
  ?id a cin:Salle ; rdfs:label ?nom ; cin:ville ?ville .
  OPTIONAL {{ ?film cin:projeteDans ?id . }}
  {filtre}
}} GROUP BY ?id ?nom ?ville ORDER BY ?nom""")


# Q6 : détail d'un film (GROUP_CONCAT des genres)
def film_detail(g, film_id):
    return executer(g, f"""
SELECT ?titre ?annee ?duree (GROUP_CONCAT(?nomGenre; separator=", ") AS ?genres) WHERE {{
  cin:{film_id} a cin:Film ; cin:titre ?titre ; cin:anneeSortie ?annee ;
                cin:duree ?duree ; cin:aGenre ?g .
  ?g rdfs:label ?nomGenre .
}} GROUP BY ?titre ?annee ?duree""")


# Q7 : équipe d'un film (réalisateurs + acteurs) -> utilise participeA (INFÉRENCE)
def equipe_film(g, film_id):
    return executer(g, f"""
SELECT ?nom ?role WHERE {{
  ?p cin:participeA cin:{film_id} ; foaf:name ?nom .
  BIND(IF(EXISTS {{ ?p a cin:Realisateur }}, "Réalisateur", "Acteur") AS ?role)
}} ORDER BY ?role ?nom""")


# Q8 : toutes les personnes foaf:Person (INFÉRENCE)
def personnes(g):
    return executer(g, """
SELECT ?nom WHERE { ?p a foaf:Person ; foaf:name ?nom . } ORDER BY ?nom""")


# Q9 : tous les acteurs (INFÉRENCE : Hend Sabri)
def acteurs(g):
    return executer(g, """
SELECT ?nom WHERE { ?p a cin:Acteur ; foaf:name ?nom . } ORDER BY ?nom""")


# Q10 : toutes les participations personne -> film (INFÉRENCE)
def participations(g):
    return executer(g, """
SELECT ?nom ?titre WHERE {
  ?p cin:participeA ?f ; foaf:name ?nom . ?f cin:titre ?titre .
} ORDER BY ?titre ?nom""")
