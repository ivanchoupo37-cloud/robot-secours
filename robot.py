def observer(carte_reelle, carte_connue, position, victimes_detectees):
    ligne_robot, colonne_robot = position

    for ligne in range(ligne_robot - 1, ligne_robot + 2):
        for colonne in range(colonne_robot - 1, colonne_robot + 2):

            if 0 <= ligne < len(carte_reelle):
                if 0 <= colonne < len(carte_reelle[ligne]):

                    contenu = carte_reelle[ligne][colonne]
                    carte_connue[ligne][colonne] = contenu

                    if contenu == "V":
                        victimes_detectees.add((ligne, colonne))