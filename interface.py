import tkinter as tk
from time import perf_counter
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
    temps_calcul = 0.0
    delais_detection = {}

    def observer_et_mesurer():
        observer(
            carte_reelle,
            carte_connue,
            position_robot,
            victimes_detectees
        )

        # Enregistrer uniquement la première détection.
        for victime in victimes_detectees:
            if victime not in delais_detection:
                delais_detection[victime] = nombre_pas

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

                # Préparer le détail des premières détections.
        detections = []

        for victime, pas in sorted(delais_detection.items()):
            detections.append(
                f"Victime {victime} : découverte au pas {pas}"
            )

        texte_detections = "\n".join(detections)

        if not texte_detections:
            texte_detections = "Aucune victime détectée"

        # Actualiser les informations affichées.
        informations.config(
            text=(
                f"{etat}\n"
                f"Déplacements : {nombre_pas} | "
                f"Victimes détectées : {len(victimes_detectees)}\n"
                f"Temps de calcul : {temps_calcul:.4f} s\n\n"
                f"{texte_detections}"
            )
        )
    def un_pas():
        nonlocal position_robot, nombre_pas
        nonlocal etat, terminee, temps_calcul

        if terminee:
            return

        # Chronométrer les calculs sans inclure le dessin
        # ni l'attente entre deux déplacements.
        debut = perf_counter()

        observer_et_mesurer()

        graphe = construire_graphe(carte_connue)

        chemin, phase = choisir_chemin(
            carte_connue,
            graphe,
            position_robot,
            depart,
            strategie="score",
            poids_distance=1.0
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
            position_robot = chemin[0]
            nombre_pas += 1
            etat = phase

            observer_et_mesurer()

        temps_calcul += perf_counter() - debut

        dessiner()

        if terminee:
            afficher_bilan()

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
        nonlocal temps_calcul
        lecture = False

        if tache is not None:
            fenetre.after_cancel(tache)
            tache = None

        position_robot = depart
        nombre_pas = 0
        temps_calcul = 0.0
        delais_detection.clear()
        terminee = False
        etat = "Prêt"

        # Effacer la mémoire, en conservant le même bâtiment.
        for ligne in range(len(carte_connue)):
            for colonne in range(len(carte_connue[ligne])):
                carte_connue[ligne][colonne] = "?"

        victimes_detectees.clear()

        observer_et_mesurer()

        bouton_lecture.config(text="Lecture")
        dessiner()
    def afficher_bilan():
        print("\n--- Bilan de la simulation ---")
        print("État :", etat)
        print("Déplacements, retour inclus :", nombre_pas)
        print(f"Temps de calcul cumulé : {temps_calcul:.6f} s")
        print("Robot au départ :", position_robot == depart)

        # La carte réelle sert ici uniquement à évaluer les résultats.
        for ligne in range(len(carte_reelle)):
            for colonne in range(len(carte_reelle[ligne])):
                if carte_reelle[ligne][colonne] == "V":
                    victime = (ligne, colonne)

                    if victime in delais_detection:
                        print(
                            f"Victime {victime} : détectée après "
                            f"{delais_detection[victime]} pas"
                        )
                    else:
                        print(f"Victime {victime} : non détectée") 
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