def construire_graphe(carte):
    graphe = {}

    # Haut, bas, gauche, droite.
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for ligne in range(len(carte)):
        for colonne in range(len(carte[ligne])):

            # Une case traversable devient un sommet.
            if carte[ligne][colonne] in (".", "V"):
                sommet = (ligne, colonne)
                graphe[sommet] = {}

                for dl, dc in directions:
                    nl = ligne + dl
                    nc = colonne + dc

                    # Vérifier les limites de la carte.
                    if 0 <= nl < len(carte):
                        if 0 <= nc < len(carte[nl]):

                            # Ajouter une arête de poids 1.
                            if carte[nl][nc] in (".", "V"):
                                graphe[sommet][(nl, nc)] = 1

    return graphe