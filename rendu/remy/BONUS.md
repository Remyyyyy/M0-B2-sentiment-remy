# Bonus — M0-B2 Sentiment Aubergine Hôtels (Rémy)

## H — Mesurer l'effet d'un autre découpage 5★ → 3 classes

Scripts : [`recuperer_scores.py`](recuperer_scores.py) (récupère une fois les scores 5★ des 30 avis
via l'API) et [`comparer_mappings.py`](comparer_mappings.py) (applique les 4 règles sur
[`scores_30_avis.json`](scores_30_avis.json)).

| Règle | Étoile retenue | Négatif | Neutre | Positif |
|---|---|---|---|---|
| A (la mienne) | la plus probable | 1-2 | 3 | 4-5 |
| B | la plus probable | 1 | 2-3 | 4-5 |
| C | la plus probable | 1-2 | 3-4 | 5 |
| S | somme des probabilités par groupe (1-2 / 3 / 4-5) | | | |

### Sortie du script

```
$ python3 rendu/remy/comparer_mappings.py
=== Règle A ===
bons : 24
négatifs manqués : 3
fausses alertes : 1
attendu / prédit   ['négatif', 'neutre', 'positif']
négatif [8, 2, 1]
neutre [1, 6, 1]
positif [0, 1, 10]
=== Règle B ===
bons : 21
négatifs manqués : 7
fausses alertes : 0
attendu / prédit   ['négatif', 'neutre', 'positif']
négatif [4, 6, 1]
neutre [0, 7, 1]
positif [0, 1, 10]
=== Règle C ===
bons : 21
négatifs manqués : 3
fausses alertes : 1
attendu / prédit   ['négatif', 'neutre', 'positif']
négatif [8, 3, 0]
neutre [1, 7, 0]
positif [0, 5, 6]
=== Règle S ===
bons : 25
négatifs manqués : 1
fausses alertes : 2
attendu / prédit   ['négatif', 'neutre', 'positif']
négatif [10, 0, 1]
neutre [2, 5, 1]
positif [0, 1, 10]
```

### Résumé

| Règle | Bien classés | Négatifs manqués | Fausses alertes |
|---|---|---|---|
| A (la mienne) | 24/30 (80 %) | 3 | 1 |
| B | 21/30 (70 %) | 7 | 0 |
| C | 21/30 (70 %) | 3 | 1 |
| **S** | **25/30 (83,3 %)** | **1** | 2 |

### 1. Quelle règle classe le plus d'avis correctement ? Laquelle manque le moins de négatifs ? Est-ce la même ?

Oui, c'est la même : la règle S classe le mieux les avis parmi les 4 règles (25/30) et rate
aussi le moins de négatifs (1). En contrepartie, elle fait une fausse alerte de plus que A (2 contre 1).

### 2. Combien d'avis séparent la meilleure règle de la mienne ? Est-ce suffisant pour changer ?

Il y a un seul bon avis d'écart entre ma règle A et la règle S : 80 % pour A contre 83,3 % pour S.

Il faudrait voir selon le panel d'avis que l'on gère : 3 négatifs manqués pour la règle A sur
30 avis, c'est 10 % du total. Sur des milliers d'avis, ça commencerait à faire beaucoup d'avis
négatifs oubliés, mais rien ne dit que ces 10 % de négatifs oubliés soient constants.

Donc non, un seul avis d'écart ne suffit pas à lui seul pour changer de règle.

### 3. Comment le sentiment attendu a-t-il été fabriqué ? Qu'est-ce que ça implique ?

Le sentiment attendu a été construit à partir de la note du client, sur le même principe que la
règle A (1-2★ → négatif, 3★ → neutre, 4-5★ → positif).

Cela implique que la règle A devrait être la règle la plus adaptée pour être en adéquation avec
ce qui est attendu comme résultat, et pourtant la règle S offre de meilleurs résultats.

### 4. Le score de la règle gagnante est-il fiable à annoncer au client ?

Ce score n'est pas forcément fiable. Comme dit plus haut, on teste sur un panel de 30 avis, donc
on n'est pas sûr qu'avec 1 000 avis par exemple la règle S gagne encore. De plus, le modèle a été
entraîné sur des avis Amazon et Allociné, pas sur des avis d'hôtels : le vocabulaire n'est pas le même.

Il nous faudrait un plus grand panel (quelques centaines à un millier d'avis), avec de vrais avis
Aubergine qui n'ont pas servi à choisir la règle.

### Décision

Je choisis finalement la règle S. C'est la règle avec le moins de négatifs ratés, et de mon point
de vue un client mécontent non repéré est un client qui ne revient pas, car on n'a pas vu ce qui
n'allait pas. Dans ce cas, il vaut mieux avoir quelques fausses alertes et rater moins de négatifs.
Ce choix reste à confirmer sur un panel d'avis plus grand.

---

## G — « Pourquoi pas un LLM généraliste ? »

| Critère | Côté CamemBERT (mesuré / observé) | Côté LLM généraliste |
|---|---|---|
| **Latence** | 20-30 ms par avis | *Supposition* : plutôt de l'ordre de la seconde |
| **Coût** | Tourne sur un PC portable, sans GPU : aucun coût par avis. | Estimation pour 10 000 avis/mois (voir calcul ci-dessous) |
| **Format de sortie** | Toujours `négatif`, `neutre` ou `positif` | Répond en texte libre : il faudrait imposer un format de sortie (JSON avec schéma), le valider et gérer les réponses hors format. |
| **Reproductibilité** | Même avis envoyé 3 fois : mêmes scores à l'identique, seule la latence varie. | *Supposition* : un LLM peut formuler ou classer différemment le même avis d'un appel à l'autre. |
| **Données** | Les avis ne sortent pas du conteneur, sur la machine d'Aubergine. | Les avis (qui peuvent contenir des noms, des numéros de chambre) partent chez un fournisseur externe : question RGPD et confidentialité. |

### Calcul du coût

Source : page de prix de l'API Claude, https://platform.claude.com/docs/en/about-claude/pricing
(consultée le 25 novembre 2026).

Hypothèses : ~200 tokens en entrée par avis (instructions + avis) et ~20 tokens en sortie (la classe dans un petit JSON), soit 2 M tokens en entrée et 0,2 M en sortie pour 10 000 avis.

| Modèle | Prix entrée / sortie (par million de tokens) | Coût pour 10 000 avis/mois |
|---|---|---|
| Claude Haiku 5.5 | 0,10 $ / 0,50 $ | ≈ 0,30 $ |
| Claude Sonnet 5.5 | 2 $ / 10 $ | ≈ 6 $ |
| Claude Opus 5.5 | 4 $ / 20 $ | ≈ 12 $ |
| Claude Opus 5 | 5 $ / 25 $ | ≈ 15 $ |

Calcul : (2 M × prix entrée) + (0,2 M × prix sortie). Exemple pour Opus 5.5 : 2 × 4 $ + 0,2 × 20 $ = 12 $.

À ce volume, le coût n'est donc pas l'argument décisif : les vraies différences sont la latence, le format garanti, la reproductibilité et la confidentialité des données.

### Recommandation pour Aubergine Hôtels

Garder CamemBERT : il est rapide, gratuit à l'usage, toujours dans le bon format et les avis restent en interne, ce qui suffit pour trier des milliers d'avis. Je changerais d'avis si les erreurs d'ironie et de comparatif (avis n°5, 8, 12 de l'ANALYSE) devenaient trop coûteuses : on pourrait alors envoyer à un LLM uniquement les avis où CamemBERT hésite, après avoir anonymisé les noms et numéros de chambre.

---

## F — Endpoint /predict/batch

### Pourquoi limiter le lot à 32 ?

Car le temps de réponse serait trop long pour trop d'avis, en sachant qu'on a un timeout de 10 secondes dans Streamlit. Pareil pour la mémoire, qui serait surchargée avec trop d'avis, ce qui pourrait planter l'application.
En moyenne, un avis est predict en 30ms donc 32 avis ont une valeur de 1s de predict.

### Mesures

Script : [`mesurer_batch.py`](mesurer_batch.py). Les 30 avis du CSV, chaque mesure faite 3 fois, médiane retenue, temps mesuré côté client.

| Mesure | Médiane |
|---|---|
| A : 30 `/predict` | ≈ 900-920 ms (921 au 1er lancement, 899 au 2ᵉ) |
| B : `/predict/batch` v1 (boucle) | ≈ 860 ms |
| C : `/predict/batch` v2 (pipeline en lot) | ≈ 832 ms |

### Explication de l'écart

L'écart entre A et B/C s'explique par le nombre d'appels (30 contre 1).
Mais les écarts sont petits car tout se passe sur mon poste et pas sur un serveur distant, où l'écart serait beaucoup plus creusé entre `/predict` et `/predict/batch`, car pour le deuxième on envoie tout d'un coup.

