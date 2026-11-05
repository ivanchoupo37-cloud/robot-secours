import tkinter as tk

from robot import observer
from graphe import construire_graphe
from exploration import choisir_chemin


def lancer_interface(
    carte_reelle,
    carte_connue,
    depart,
    position_robot,
    victimes_detectees
):
    taille_case = 40
    nombre_pas = 0

    # Temps entre deux déplacements, en millisecondes.
    delai = 250

    lecture = False
    terminee = False
    tache = None
    etat = "Prêt"

    couleurs = {
        "#": "#36566B",
        ".": "#FFFFFF",
        "V": "#F18BAA",
        "?": "#CCD9DF"
    }

    fenetre = tk.Tk()
    fenetre.title("Exploration automatique")

    tk.Label(
        fenetre,
        text="Robot de secours",
        font=("Arial", 16)
    ).pack(pady=10)

    canvas = tk.Canvas(
        fenetre,
        width=len(carte_connue[0]) * taille_case,
        height=len(carte_connue) * taille_case,
        highlightthickness=0
    )
    canvas.pack(padx=20, pady=10)

    commandes = tk.Frame(fenetre)
    commandes.pack(pady=5)

    informations = tk.Label(fenetre)
    informations.pack(pady=10)

    tk.Label(
        fenetre,
        text=(
            "Cyan : robot | Vert : départ | Rose : victime\n"
            "Bleu : mur | Gris : inconnu"
        )
    ).pack(pady=5)

    def dessiner():
        canvas.delete("all")

        for ligne in range(len(carte_connue)):
            for colonne in range(len(carte_connue[ligne])):
                contenu = carte_connue[ligne][colonne]
                couleur = couleurs[contenu]

                if (ligne, colonne) == depart:
                    couleur = "#32B88A"

                x = colonne * taille_case
                y = ligne * taille_case

                canvas.create_rectangle(
                    x, y,
                    x + taille_case,
                    y + taille_case,
                    fill=couleur,
                    outline="#D5DFE5"
                )

        ligne, colonne = position_robot
        x = colonne * taille_case
        y = ligne * taille_case

        canvas.create_oval(
            x + 10, y + 10,
            x + taille_case - 10,
            y + taille_case - 10,
            fill="#00BCD4",
            outline=""
        )

        informations.config(
            text=(
                f"{etat} | Pas : {nombre_pas} | "
                f"Victimes détectées : {len(victimes_detectees)}"
            )
        )

    def un_pas():
        nonlocal position_robot, nombre_pas
        nonlocal etat, terminee

        if terminee:
            return

        # Actualiser la mémoire avant toute décision.
        observer(
            carte_reelle,
            carte_connue,
            position_robot,
            victimes_detectees
        )

        # La décision utilise seulement les passages connus.
        graphe = construire_graphe(carte_connue)

        chemin, phase = choisir_chemin(
            carte_connue,
            graphe,
            position_robot,
            depart
        )

        if chemin is None:
            etat = "Erreur : aucune route accessible"
            terminee = True

        elif not chemin:
            if phase == "Retour" and position_robot == depart:
                etat = "Mission terminée : retour effectué"
            else:
                etat = "Arrêt : aucun déplacement utile"

            terminee = True

        else:
            # Exécuter seulement le premier pas du chemin.
            position_robot = chemin[0]
            nombre_pas += 1
            etat = phase

            observer(
                carte_reelle,
                carte_connue,
                position_robot,
                victimes_detectees
            )

        dessiner()

    def boucle():
        nonlocal tache, lecture

        tache = None

        if not lecture:
            return

        un_pas()

        if terminee:
            lecture = False
            bouton_lecture.config(text="Lecture")
        else:
            # Planifier la suite sans bloquer la fenêtre.
            tache = fenetre.after(delai, boucle)

    def lecture_pause():
        nonlocal lecture, tache

        if terminee:
            return

        lecture = not lecture

        if lecture:
            bouton_lecture.config(text="Pause")
            boucle()
        else:
            bouton_lecture.config(text="Lecture")

            if tache is not None:
                fenetre.after_cancel(tache)
                tache = None

    def pas_manuel():
        # Éviter de superposer lecture et commande manuelle.
        if not lecture:
            un_pas()

    def recommencer():
        nonlocal position_robot, nombre_pas
        nonlocal lecture, terminee, tache, etat

        lecture = False

        if tache is not None:
            fenetre.after_cancel(tache)
            tache = None

        position_robot = depart
        nombre_pas = 0
        terminee = False
        etat = "Prêt"

        # Effacer la mémoire, en conservant le même bâtiment.
        for ligne in range(len(carte_connue)):
            for colonne in range(len(carte_connue[ligne])):
                carte_connue[ligne][colonne] = "?"

        victimes_detectees.clear()

        observer(
            carte_reelle,
            carte_connue,
            position_robot,
            victimes_detectees
        )

        bouton_lecture.config(text="Lecture")
        dessiner()

    tk.Button(
        commandes,
        text="Un déplacement",
        command=pas_manuel
    ).pack(side=tk.LEFT, padx=5)

    bouton_lecture = tk.Button(
        commandes,
        text="Lecture",
        command=lecture_pause
    )
    bouton_lecture.pack(side=tk.LEFT, padx=5)

    tk.Button(
        commandes,
        text="Recommencer",
        command=recommencer
    ).pack(side=tk.LEFT, padx=5)

    # Faire la première observation avant l'affichage.
    observer(
        carte_reelle,
        carte_connue,
        position_robot,
        victimes_detectees
    )

    dessiner()
    fenetre.mainloop()