   from rdflib import URIRef
   from graph import G_BRUT, G_INFERE

   print(len(G_BRUT), len(G_INFERE))

   hend = URIRef("http://example.org/cinema#HendSabri")
   print("--- SANS inférence ---")
   for p, o in G_BRUT.predicate_objects(hend):
       print(p, o)
   print("--- AVEC inférence ---")
   for p, o in G_INFERE.predicate_objects(hend):
       print(p, o)