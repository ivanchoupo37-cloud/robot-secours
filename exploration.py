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


def gain_information(carte, cible):
    """Compter les cases inconnues dans le carré 3 × 3."""
    ligne, colonne = cible
    gain = 0

    for l in range(ligne - 1, ligne + 2):
        for c in range(colonne - 1, colonne + 2):
            if 0 <= l < len(carte):
                if 0 <= c < len(carte[l]):
                    if carte[l][c] == "?":
                        gain += 1

    return gain


def parcours_distances(graphe, depart):
    """Un seul BFS pour calculer les distances et les parents."""
    file = deque([depart])
    distances = {depart: 0}
    parents = {depart: None}

    while file:
        sommet = file.popleft()

        # Trier les voisins garantit un ordre fixe.
        for voisin in sorted(graphe[sommet]):
            if voisin not in distances:
                distances[voisin] = distances[sommet] + 1
                parents[voisin] = sommet
                file.append(voisin)

    return distances, parents


def choisir_chemin(
    carte,
    graphe,
    position,
    depart,
    strategie="proche",
    poids_distance=1.0
):
    if strategie not in ("proche", "score"):
        raise ValueError("Stratégie attendue : proche ou score.")

    if poids_distance < 0:
        raise ValueError("Le poids de la distance doit être positif ou nul.")

    if position not in graphe:
        return None, "Erreur"

    # Calculer les distances sur le graphe connu.
    distances, parents = parcours_distances(graphe, position)

    # Détecter les frontières avec WFD.
    frontieres = detecter_frontieres(carte, position)
    cibles = set()

    for groupe in frontieres:
        for case in groupe:
            for voisine in voisines(carte, case):

                # La cible doit être connue et accessible.
                if voisine in distances:
                    if gain_information(carte, voisine) > 0:
                        cibles.add(voisine)

    if cibles:
        if strategie == "proche":
            # Distance minimale, puis coordonnées en cas d'égalité.
            cible = min(
                cibles,
                key=lambda case: (distances[case], case)
            )

        else:
            # Score maximal :
            # gain d'information - poids × distance.
            # En cas d'égalité : distance minimale, puis coordonnées.
            cible = min(
                cibles,
                key=lambda case: (
                    -(
                        gain_information(carte, case)
                        - poids_distance * distances[case]
                    ),
                    distances[case],
                    case
                )
            )

        phase = "Exploration"

    else:
        cible = depart
        phase = "Retour"

    if cible not in distances:
        return None, phase

    # Reconstruire le chemin vers la cible choisie.
    chemin = []
    case = cible

    while case != position:
        chemin.append(case)
        case = parents[case]

    chemin.reverse()

    return chemin, phase