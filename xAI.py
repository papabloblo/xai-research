from semanticscholar import SemanticScholar
import pickle as pkl
import csv
import json
from difflib import SequenceMatcher as sm
from tqdm.notebook import tqdm
import pandas as pd
from collections import Counter

from tqdm import tqdm
from time import sleep
from semanticscholar import SemanticScholar  # Asegúrate de importar esta librería




def paper_to_dict(paper):
    result = {
        'title': getattr(paper, 'title', ''),  # Usamos getattr para evitar errores si el atributo no existe
        'abstract': getattr(paper, 'abstract', ''),
        'year': getattr(paper, 'year', ''),
        'venue': getattr(paper, 'venue', ''),
        'publicationVenue': getattr(paper, 'publicationVenue', ''),
        'externalIds': getattr(paper, 'externalIds', ''),
        'url': getattr(paper, 'url', ''),
        'journal': getattr(paper, 'journal', ''),
        'referenceCount': getattr(paper, 'referenceCount', ''),
        'citationCount': getattr(paper, 'citationCount', ''),
        'influentialCitationCount': getattr(paper, 'influentialCitationCount', ''),
        'fieldOfStudy': getattr(paper, 'fieldOfStudy', ''),
        's2FieldsOfStudy': getattr(paper, 'fieldOfStudy', ''),
        'publicationTypes': getattr(paper, 'publicationTypes', '')
    }

    for attr in ['authors', 'references', 'citations']:
        if getattr(paper, attr, []) is not None:
            result[attr] = [c._data for c in getattr(paper, attr, [])]
        else:
            result[attr] = []

    for attr in ['publicationVenue', 'journal']:
        if result[attr] is not None:
            result[attr] = result[attr]._data

    return result




ss = SemanticScholar()
fields = ['title', 'abstract', 'year', 'venue', 'publicationVenue', 'externalIds', 'url',
          'journal', 'referenceCount', 'citationCount', 'influentialCitationCount',
          'fieldsOfStudy', 'authors', 's2FieldsOfStudy', 'publicationTypes']

keywords_xai = [
    " xai ",
    "(xai)",
    "hcxai",
    "explainability",
    "interpretability",
    "explainable ai",
    "explainable artificial intelligence",
    "interpretable ml",
    "interpretable machine learning",
    "interpretable model",
    "feature attribution",
    "feature importance",
    "global explanation",
    "local explanation",
    "local interpretation",
    "global interpretation",
    "model explanation",
    "model interpretation",
    "saliency",
    "counterfactual explanation"
]

banned = ["/xai/xai", "xai-xai", "xai xai", "workshop", "proceedings"]

papers = {}

for query in keywords_xai:
    print("Retrieving papers with query:", query)
    try:
        res = ss.search_paper(query, fields=fields)
    except Exception as e:
        continue

    for i, x in tqdm(enumerate(res)):
        # *** NUEVO: ASEGURAR QUE `x` TIENE LOS ATRIBUTOS NECESARIOS ***
        try:
            title_lower = f" {x.title.lower()} {x.abstract.lower() if x.abstract else ''} "
        except AttributeError as e:
            print(f"Error al acceder a los atributos de `x`: {e}")
            continue  # Pasamos al siguiente elemento si no tiene los atributos esperados

        # Count relevant keywords
        count = 0
        for keyword in keywords_xai:
            if keyword in title_lower:
                count += 1
        for keyword in banned:
            if keyword in title_lower:
                count = 0

        # Skip papers with less than 2 relevant keywords
        if count < 2:
            continue

        # *** NUEVO: IGNORAR 'embedding' SIN ELIMINARLO ***
        # No intentamos eliminar 'embedding', simplemente ignoramos este atributo al procesar

        # Use the 'paperId' attribute to track papers
        try:
            paper_id = x.paperId  # Accedemos directamente al atributo `paperId`
            if paper_id not in papers:
                # papers[paper_id] = {
                #     'title': x.title,
                #     'abstract': x.abstract,
                #     'authors': [author.name for author in x.authors] if hasattr(x, 'authors') else [],
                #     'year': x.year if hasattr(x, 'year') else None,
                # }
                #
                papers[paper_id] = paper_to_dict(x)

        except AttributeError as e:
            print(f"Error al acceder a 'paperId': {e}")
            continue  # Pasamos al siguiente elemento si no tiene el atributo `paperId`

    print("# papers:", len(papers))


import json
from tqdm import tqdm
from time import sleep
from semanticscholar import SemanticScholar  # Asegúrate de importar esta librería

# Parámetros configurables
MAX_REFERENCES = 10  # Limita el número de referencias/citas procesadas por paper
SAVE_EVERY = 50  # Guarda el progreso cada 50 papers procesados
SLEEP_TIME = 1  # Tiempo de espera entre peticiones (para evitar bloqueos)

# Diccionario para almacenar los resultados
expanded_papers = {}

fields = ['title', 'abstract', 'year', 'venue', 'publicationVenue', 'externalIds', 'url',
          'journal', 'referenceCount', 'citationCount', 'influentialCitationCount',
          'fieldsOfStudy', 'authors', 's2FieldsOfStudy', 'publicationTypes']




# def paper_to_dict(paper):
#     result = {
#         'title': getattr(paper, 'title', ''),  # Usamos getattr para evitar errores si el atributo no existe
#         'abstract': getattr(paper, 'abstract', ''),
#         'year': getattr(paper, 'year', '')
#     }
#
#     for attr in ['authors', 'references', 'citations']:
#         if getattr(paper, attr, []) is not None:
#             result[attr] = [c._data for c in getattr(paper, attr, [])]
#         else:
#             result[attr] = []
#
#     return result

# Iterar sobre cada paper en el conjunto inicial
for index, pid in enumerate(tqdm(papers, desc="Expandiendo citas")):
    try:
        # Recuperar detalles completos del paper
        full_paper = ss.get_paper(pid)

        if full_paper is None:
            print(f"Paper con ID {pid} no encontrado. Continuando con el siguiente.")
            continue  # Si no se encuentra el paper, saltamos al siguiente

        # Guardar el paper en formato serializable
        expanded_papers[pid] = paper_to_dict(full_paper)
        # print(f"Procesado paper ID {pid} - Título: {getattr(full_paper, 'title', 'Sin título')}")  # Mostrar progreso

        # Obtener referencias y citas (limitar a MAX_REFERENCES)
        refs = getattr(full_paper, 'references', [])[:MAX_REFERENCES]

        cites = getattr(full_paper, 'citations', [])[:MAX_REFERENCES]

        # Procesar referencias y citas
        for paper in refs + cites:
            pid2 = getattr(paper, 'paperId', None)
            if not pid2 or pid2 in expanded_papers or pid2 in papers:
                continue

            title = getattr(paper, 'title', '')
            abstract = getattr(paper, 'abstract', '')

            # Asegurar que `title` y `abstract` sean cadenas antes de aplicar `.lower()`
            title_lower = f" {title.lower()} " if isinstance(title, str) else ""
            abstract_lower = f" {abstract.lower()} " if isinstance(abstract, str) else ""

            count = 0
            for keyword in keywords_xai:
                if keyword in title_lower:
                    count += 1
            for keyword in banned:
                if keyword in title_lower:
                    count = 0

            if count >= 2:
                expanded_papers[pid2] = paper_to_dict(paper)


                # print(f"  Añadido Paper ID {pid2} - Título: {getattr(paper, 'title', 'No Title')}")

        # Guardar el progreso periódicamente
        if (index + 1) % SAVE_EVERY == 0:
            with open("expanded_papers.json", "w") as f:
                json.dump(expanded_papers, f, indent=4)
            print(f"Progreso guardado: {index + 1} papers procesados.")

        # Añadir un pequeño retraso entre peticiones para evitar bloqueos
        # sleep(SLEEP_TIME)

    except Exception as e:
        print(f"Error al procesar paper con ID {pid}: {str(e)}")