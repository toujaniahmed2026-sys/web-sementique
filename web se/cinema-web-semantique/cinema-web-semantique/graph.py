from pathlib import Path
from rdflib import Graph
import owlrl

DOSSIER = Path(__file__).parent


def charger_graphe():
    """Charge le schéma RDFS et les données dans un graphe."""
    g = Graph()
    g.parse(DOSSIER / "schema.ttl", format="turtle")
    g.parse(DOSSIER / "data.ttl", format="turtle")
    return g


def appliquer_inference(g):
    """Copie le graphe puis applique les règles d'inférence RDFS."""
    gi = Graph()
    gi += g
    owlrl.DeductiveClosure(
        owlrl.RDFS_Semantics, axiomatic_triples=False, datatype_axioms=False
    ).expand(gi)
    return gi


G_BRUT = charger_graphe()          # sans inférence
G_INFERE = appliquer_inference(G_BRUT)  # avec inférence
