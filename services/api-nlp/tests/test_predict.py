"""Tests de /predict."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

SENTIMENTS = {"négatif", "neutre", "positif"}
ETOILES = {"1 star", "2 stars", "3 stars", "4 stars", "5 stars"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_predict_cas_nominal_200(client):
    """Test avis classique"""
    r = client.post("/predict", json={"texte": "Personnel charmant, chambre impeccable, on reviendra !"})
    assert r.status_code == 200
    body = r.json()
    assert body["sentiment"] in SENTIMENTS
    assert set(body["scores_5_stars"]) == ETOILES


def test_predict_texte_vide_422(client):
    """Texte vide"""
    r = client.post("/predict", json={"texte": ""})
    assert r.status_code == 422

def test_predict_texte_trop_long_422(client):
    """Texte trop long"""
    r = client.post("/predict", json={"texte": "test" * 501})
    assert r.status_code == 422


@pytest.mark.parametrize(
    "texte, attendu",
    [
        ("Hôtel d'une médiocrité rare. Bruit de plomberie toute la nuit, "
         "et personne pour s'en occuper.", "négatif"),
        ("Petit déjeuner buffet correct mais sans surprise. Chambre propre, "
         "literie ferme. Standard.", "neutre"),
        ("Que dire à part que c'était parfait. Personnel, propreté, confort, "
         "calme. Tout y était. Bravo.", "positif"),
    ],
)
def test_predict_avis_du_csv(client, texte, attendu):
    """Test 3 avis du CSV"""
    r = client.post("/predict", json={"texte": texte})
    assert r.status_code == 200
    assert r.json()["sentiment"] == attendu


def test_predict_probabilities_equals_one(client) :
    """La somme des probabilités renvoyées doit valoir 1.0 (à 1e-9 près)."""
    r = client.post("/predict", json={"texte": "Personnel charmant, chambre impeccable, on reviendra !"})
    total = sum(r.json()["scores_5_stars"].values())
    assert total == pytest.approx(1.0, abs=1e-6)

def test_predict_missing_field_returns_422(client):
    """Un champ obligatoire absent doit être refusé par Pydantic (422)."""
    r = client.post("/predict", json={})
    assert r.status_code == 422

def test_batch_3_textes_200(client):
    """3 textes → 200, 3 résultats dans l'ordre d'envoi"""
    textes = [
        "Wifi quasi inexistant, climatisation poussive, petit-déjeuner aux abonnés absents. Évitez.",
        "Petit déjeuner buffet correct mais sans surprise. Chambre propre, literie ferme. Standard.",
        "Vue magnifique, lit confortable, calme absolu. Exactement ce qu'on cherchait pour un weekend.",
    ]
    r = client.post("/predict/batch", json={"textes": textes})
    assert r.status_code == 200
    body = r.json()
    assert len(body["sentiments"]) == 3
    sentiments_recus = [resultat["sentiment"] for resultat in body["sentiments"]]
    assert sentiments_recus == ["négatif", "neutre", "positif"] 

def test_predict_batch_textes_vide_422(client):
    """Textes vides"""
    r = client.post("/predict/batch", json={"textes": []})
    assert r.status_code == 422

def test_predict_batch_textes_trop_long_422(client):
    """Trop de textes dans le batch"""
    r = client.post("/predict/batch", json={"textes": ["test"] * 33})
    assert r.status_code == 422