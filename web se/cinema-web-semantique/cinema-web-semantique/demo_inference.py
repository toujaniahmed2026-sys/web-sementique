from rdflib import RDF, RDFS, URIRef
from graph import G_BRUT, G_INFERE
import queries as q


def ligne(titre, sans, avec):
    print(f"{titre:<35} sans inférence : {sans:>3} | avec inférence : {avec:>3}")


print("=== COMPARAISON ===")
ligne("Nombre de triplets", len(G_BRUT), len(G_INFERE))
ligne("Personnes (foaf:Person)", len(q.personnes(G_BRUT)), len(q.personnes(G_INFERE)))
ligne("Acteurs (cin:Acteur)", len(q.acteurs(G_BRUT)), len(q.acteurs(G_INFERE)))
ligne("Participations (cin:participeA)", len(q.participations(G_BRUT)), len(q.participations(G_INFERE)))

print("\n=== EXEMPLES DE TRIPLETS INFÉRÉS ===")
for s, p, o in sorted(G_INFERE - G_BRUT):
    if isinstance(s, URIRef) and str(s).startswith(q.NS) and o != RDFS.Resource \
            and p in (RDF.type, URIRef(q.NS + "participeA")):
        court = lambda x: str(x).split("#")[-1].split("/")[-1]
        print(f"{court(s)}  {court(p)}  {court(o)}")
