import csv
import json
import statistics
import time
import urllib.request

API = "http://localhost:8000"

with open("data/sample_reviews.csv", encoding="utf-8") as f:
    textes = [ligne["texte"] for ligne in csv.DictReader(f)]


def appeler(route, corps):
    """Envoie un POST JSON à l'API et renvoie la réponse décodée."""
    req = urllib.request.Request(f"{API}{route}", data=json.dumps(corps).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        return json.load(response)


def mesurer_30_predict():
    """Temps (ms) pour 30 appels successifs à /predict."""
    debut = time.perf_counter()
    for texte in textes:
        appeler("/predict", {"texte": texte})
    fin = time.perf_counter()
    return (fin - debut) * 1000


def mesurer_batch():
    """Temps (ms) pour 1 appel /predict/batch avec les 30 textes."""
    debut = time.perf_counter()
    appeler("/predict/batch", {"textes": textes})
    fin = time.perf_counter()
    return (fin - debut) * 1000


temps_predict = [mesurer_30_predict() for _ in range(3)]
temps_batch = [mesurer_batch() for _ in range(3)]

print("30 /predict :", temps_predict, ": médiane", statistics.median(temps_predict))
print("/predict/batch :", temps_batch, ": médiane", statistics.median(temps_batch))