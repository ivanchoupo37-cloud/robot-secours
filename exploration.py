from collections import deque

# Ordre d'examen : droite, bas, gauche, haut.
DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def voisines(carte, case):
    """Fournir les voisines situées dans la grille."""
    ligne, colonne = case

    for dl, dc in DIRECTIONS:
        l = ligne + dl
        c = colonne + dc

        if 0 <= l < len(carte):
            if 0 <= c < len(carte[l]):
                yield (l, c)


def est_frontiere(carte, case):
    """Une frontière est inconnue et touche un passage connu."""
    ligne, colonne = case

    if carte[ligne][colonne] != "?":
        return False

    return any(
        carte[l][c] in (".", "V")
        for l, c in voisines(carte, case)
    )


def extraire_groupe(carte, depart, affectees):
    """BFS intérieur : regrouper les cases de frontière voisines."""
    file = deque([depart])
    affectees.add(depart)
    groupe = []

    while file:
        case = file.popleft()
        groupe.append(case)

        for voisine in voisines(carte, case):
            if voisine not in affectees:
                if est_frontiere(carte, voisine):
                    affectees.add(voisine)
                    file.append(voisine)

    return groupe


def detecter_frontieres(carte, depart):
    """BFS extérieur : parcourir les passages connus accessibles."""
    file = deque([depart])
    ajoutees = {depart}
    affectees = set()
    frontieres = []

    while file:
        case = file.popleft()

        for voisine in voisines(carte, case):
            l, c = voisine

            if carte[l][c] in (".", "V"):
                if voisine not in ajoutees:
                    ajoutees.add(voisine)
                    file.append(voisine)

            elif voisine not in affectees:
                if est_frontiere(carte, voisine):
                    groupe = extraire_groupe(
                        carte, voisine, affectees
                    )
                    frontieres.append(groupe)

    return frontieres


def chercher_chemin(graphe, depart, cibles):
    """BFS : atteindre la plus proche des cibles accessibles."""
    if depart not in graphe:
        return None

    file = deque([depart])

    # Mémoriser le parent permet de reconstruire le chemin.
    parents = {depart: None}

    while file:
        sommet = file.popleft()

        if sommet in cibles:
            chemin = []

            # Le chemin exclut le départ et inclut la cible.
            while sommet != depart:
                chemin.append(sommet)
                sommet = parents[sommet]

            chemin.reverse()
            return chemin

        for voisin in graphe[sommet]:
            if voisin not in parents:
                parents[voisin] = sommet
                file.append(voisin)

    # Aucune cible accessible.
    return None


def choisir_chemin(carte, graphe, position, depart):
    """Choisir un passage près d'une frontière, sinon rentrer."""
    frontieres = detecter_frontieres(carte, position)
    cibles = set()

    for groupe in frontieres:
        for case in groupe:
            for voisine in voisines(carte, case):

                # La destination doit être un sommet connu.
                if voisine in graphe:
                    cibles.add(voisine)

    if cibles:
        chemin = chercher_chemin(graphe, position, cibles)
        return chemin, "Exploration"

    chemin = chercher_chemin(graphe, position, {depart})
    return chemin, "Retour"