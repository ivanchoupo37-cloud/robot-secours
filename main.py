from environnement import generer_batiment
from interface import lancer_interface


def main():
    # Créer le bâtiment.
    carte_reelle, depart = generer_batiment(
        lignes=15,
        colonnes=21,
        proportion_murs=0.25,
        nombre_victimes=4,
        graine=42
    )

    # Placer le robot au départ.
    position_robot = depart

    # Créer sa mémoire : toutes les cases sont inconnues.
    carte_connue = [
        ["?" for colonne in range(len(carte_reelle[0]))]
        for ligne in range(len(carte_reelle))
    ]

    # Aucune victime détectée au départ.
    victimes_detectees = set()

    # Lancer l'interface et les commandes d'exploration.
    lancer_interface(
        carte_reelle,
        carte_connue,
        depart,
        position_robot,
        victimes_detectees
    )


if __name__ == "__main__":
    main()