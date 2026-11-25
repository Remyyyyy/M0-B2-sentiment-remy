"""Compare plusieurs règles de découpage 5★ → 3 classes sur les 30 avis."""
import json
from pathlib import Path

liste_avis = json.loads((Path(__file__).parent / "scores_30_avis.json").read_text(encoding="utf-8"))
CLASSES = ["négatif", "neutre", "positif"]


def etoile_max(scores):
    """Renvoie l'étoile la plus probable, en nombre : '2 stars' -> 2."""
    label = max(scores, key=scores.get)
    return int(label[0])


def regle_A(scores):
    nb_etoiles = int(etoile_max(scores))
    if nb_etoiles in (1, 2):
        return "négatif"
    if nb_etoiles == 3:
        return "neutre"
    if nb_etoiles in (4, 5):
        return "positif"

def regle_B(scores):
    nb_etoiles = int(etoile_max(scores))
    if nb_etoiles == 1 :
        return "négatif"
    if nb_etoiles in (2,3):
        return "neutre"
    if nb_etoiles in (4, 5):
        return "positif"

def regle_C(scores):
    nb_etoiles = int(etoile_max(scores))
    if nb_etoiles in (1, 2):
        return "négatif"
    if nb_etoiles in (3,4):
        return "neutre"
    if nb_etoiles == 5:
        return "positif"

def regle_S(scores):
    totaux = {
        "négatif": scores["1 star"] + scores["2 stars"],
        "neutre": scores["3 stars"],
        "positif": scores["4 stars"] + scores["5 stars"],
    }
    return max(totaux, key=totaux.get)

def evaluer_regle(nom_regle, regle):
    bons = 0
    negatifs_manques = 0
    fausses_alertes = 0
    matrice = {}

    for avis in liste_avis:
        attendu = avis["attendu"]
        predit = regle(avis["scores_5_stars"])
        cle = (attendu, predit)
        matrice[cle] = matrice.get(cle, 0) + 1
        if predit == attendu:
            bons += 1
        if attendu == "négatif" and predit != "négatif":
            negatifs_manques += 1
        if attendu != "négatif" and predit == "négatif":
            fausses_alertes += 1

    print(f"=== Règle {nom_regle} ===")
    print(f"bons : {bons}")
    print(f"négatifs manqués : {negatifs_manques}")
    print(f"fausses alertes : {fausses_alertes}")
    classes = ["négatif", "neutre", "positif"]
    print("attendu / prédit  ", classes)
    for attendu in classes:
        ligne = []
        for predit in classes:
            ligne.append(matrice.get((attendu, predit), 0))
        print(f"{attendu}", ligne)


evaluer_regle("A", regle_A)
evaluer_regle("B", regle_B)
evaluer_regle("C", regle_C)
evaluer_regle("S", regle_S)
