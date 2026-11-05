
import random
from collections import deque
from graphe import construire_graphe
def generer_batiment(
    lignes,
    colonnes,
    proportion_murs,
    nombre_victimes,
    graine=None
):
    if lignes < 3 or colonnes < 3:
        raise ValueError("La carte doit mesurer au moins 3 × 3.")

    generateur = random.Random(graine)
    depart = (1, 1)

    # 1. Créer la grille de cases libres.
    carte = [
        ["." for colonne in range(colonnes)]
        for ligne in range(lignes)
    ]

    # 2. Créer les murs sur les bordures.
    for ligne in range(lignes):
        carte[ligne][0] = "#"
        carte[ligne][colonnes - 1] = "#"

    for colonne in range(colonnes):
        carte[0][colonne] = "#"
        carte[lignes - 1][colonne] = "#"

    # 3. Créer des blocs de murs de 2 × 2 cases.
    # Un passage sépare les emplacements des blocs.
    for ligne in range(2, lignes - 2, 3):
        for colonne in range(2, colonnes - 2, 3):

            if generateur.random() < 0.75:
                for dl in range(2):
                    for dc in range(2):
                        carte[ligne + dl][colonne + dc] = "#"

    # 4. Garantir un départ libre.
    carte[depart[0]][depart[1]] = "."

    # 5. Construire le graphe.
    graphe = construire_graphe(carte)

    # 6. Trouver les cases accessibles avec BFS.
    file = deque([depart])
    accessibles = {depart}

    while file:
        sommet = file.popleft()

        for voisin in graphe[sommet]:
            if voisin not in accessibles:
                accessibles.add(voisin)
                file.append(voisin)

    # 7. Choisir les positions des victimes.
    emplacements = sorted(accessibles - {depart})

    if not 0 <= nombre_victimes <= len(emplacements):
        raise ValueError(
            f"Choisis entre 0 et {len(emplacements)} victimes."
        )

    victimes = generateur.sample(emplacements, nombre_victimes)

    for ligne, colonne in victimes:
        carte[ligne][colonne] = "V"

    return carte, depart
 # Carte réelle du bâtiment : chaque chaîne représente une ligne.
carte_reelle, depart = generer_batiment(
    lignes=10,
    colonnes=15,
    proportion_murs=0.15,
    nombre_victimes=4,
    graine=42
)

