"""Logique d'inférence pour la classification de sentiment.

Le modèle CamemBERT chargé sort des labels 5 étoiles
(`'1 star'`, `'2 stars'`, ..., `'5 stars'`). Le métier (Aubergine Hôtels)
veut 3 classes (`négatif`, `neutre`, `positif`).

→ Ton travail dans ce fichier :
   1. Implémenter `predict_sentiment()` (récupère les scores 5★ + applique ta règle).
   2. Implémenter `map_stars_to_sentiment()` (mapping 5★ → 3 classes).
   3. Écrire ta règle dans le commentaire `# DECISION:` ci-dessous AVANT de coder.

Le pipeline transformers est chargé une seule fois au démarrage, dans
`main.py` (lifespan), et stocké dans `state["pipeline"]`. Tu le récupères
en argument.
"""
from __future__ import annotations

# DECISION:
#   Règle retenue : 1-2 étoiles -> négatif / 3 -> neutre / 4-5 -> positif, en prenant l'étoile la plus probable
#   Argument métier 1 : un client mécontent non repéré, c'est un client perdu qui ne revient pas et un problème (ex : douche qui fuit) qui n'est jamais réglé. On classe donc les 2 étoiles en négatif pour ne pas les rater.
#   Argument métier 2 : une alerte à tort surcharge le directeur d'avis qui sont en fait corrects, il ne lit plus les alertes. On laisse donc les 3 étoiles en neutre.



import time
from typing import Any

from app.schemas import Sentiment, SentimentOut


def map_stars_to_sentiment(star_label: str) -> Sentiment:
    """Mappe un label 5 étoiles ('1 star', ..., '5 stars') en 3 classes métier.

    À compléter par l'apprenant. **Le choix du mapping est un arbitrage
    métier**, pas une recette imposée : plusieurs découpages sont valides
    (cf. mini-cours `02_HuggingFace_Transformers_essentiel.md`, section
    "Justification du seuil de mapping").

    Ton travail : proposer **ton** mapping et **le justifier** dans le
    commentaire `# DECISION:` en haut de ce fichier, puis dans
    `rendu/<prenom>/ANALYSE.md` (coût d'un faux positif / faux négatif
    côté métier Aubergine Hôtels).

    Args:
        star_label: label produit par le modèle (ex: '4 stars').

    Returns:
        Sentiment 3 classes.

    Raises:
        ValueError: si `star_label` n'est pas dans le format attendu.
    """
    nb_etoiles = int(star_label[0])
    if nb_etoiles in (1, 2):
        return "négatif"
    if nb_etoiles == 3:
        return "neutre"
    if nb_etoiles in (4, 5):
        return "positif"
    raise ValueError(f"Label inattendu : {star_label}")


def predict_sentiment(pipeline: Any, text: str, model_name: str) -> SentimentOut:
    """Inférence de sentiment sur un texte FR.

    Args:
        pipeline: pipeline `transformers.pipeline("text-classification", ...)`
            chargé au démarrage de l'API.
        text: texte FR de la review.
        model_name: identifiant HF du modèle (passé pour traçabilité).

    Returns:
        SentimentOut avec sentiment 3 classes, scores 5★ bruts, et latence ms.
    """
    
    debut = time.perf_counter()
    raw = pipeline(text)
    fin = time.perf_counter()
    scores_5_stars = {item["label"]: item["score"] for item in raw[0]}

    top_label = max(raw[0], key=lambda x: x["score"])["label"]

    sentiment = map_stars_to_sentiment(top_label)

    return SentimentOut(
        sentiment=sentiment,
        scores_5_stars=scores_5_stars,
        model_name=model_name,
        latence_ms=(fin - debut) * 1000,
    )

def predict_sentiment_batch(pipeline: Any, texts: list[str], model_name: str) -> list[SentimentOut]:
    debut = time.perf_counter()
    raw = pipeline(texts)
    fin = time.perf_counter()   
    

    resultats = []
    for scores in raw:
        scores_5_stars = {item["label"]: item["score"] for item in scores}
        top_label = max(scores, key=lambda x: x["score"])["label"]
        
        sentiment = map_stars_to_sentiment(top_label)
        
        resultats.append(SentimentOut(
            sentiment=sentiment,
            scores_5_stars=scores_5_stars,
            model_name=model_name,
            latence_ms=(fin - debut) * 1000 / len(texts),
        ))
    return resultats
