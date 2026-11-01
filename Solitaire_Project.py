# - - - - - - - - - - - - - - - - -
#           Importations
# - - - - - - - - - - - - - - - - -



import random
import json


# - - - - - - - - - - - - - - - - -
#           Sous-programme
# - - - - - - - - - - - - - - - - -

# Etape 1: création et initialisation des listes et dictinnaire :

fondation_1 = []
fondation_2 = []
fondation_3 = []
fondation_4 = []



pique = ["K♠️", "Q♠️", "J♠️","10♠️","9♠️","8♠️","7♠️","6♠️","5♠️","4♠️","3♠️","2♠️","A♠️"]
trefle = ["K♣️", "Q♣️", "J♣️","10♣️","9♣️","8♣️","7♣️","6♣️","5♣️","4♣️","3♣️","2♣️","A♣️"]
carreau = ["K♦️", "Q♦️", "J♦️","10♦️","9♦️","8♦️","7♦️","6♦️","5♦️","4♦️","3♦️","2♦️","A♦️"]
coeur = ["K♥️", "Q♥️", "J♥️","10♥️","9♥️","8♥️","7♥️","6♥️","5♥️","4♥️","3♥️","2♥️","A♥️"]

noir = trefle + pique
rouge = carreau + coeur

cartes = {"noir": {"trefle": trefle, "pique": pique}, "rouge": {"carreau": carreau, "coeur": coeur}}

colonne_1 = 1*[0]
colonne_2 = 2*[0]
colonne_3 = 3*[0]
colonne_4 = 4*[0]
colonne_5 = 5*[0]
colonne_6 = 6*[0]
colonne_7 = 7*[0]
pioche = []
defausse = []

colonne = [colonne_1, colonne_2, colonne_3, colonne_4,colonne_5,colonne_6,colonne_7]
fondation = [fondation_1, fondation_2, fondation_3, fondation_4]

paquet = noir + rouge

# Etape 2: Préparation de la distribution :

def distribution():

    for i in range(len(colonne)):

# On parcours une première fois la liste colonne pour choisir de quelle colonne on parle

        for j in range(len(colonne[i])):

# On parcours cette fois-ci les indices de la colonne choisie au dessus

            choix = random.choice(paquet)  # On choisit une carte au hasard
            colonne[i][j] = choix  # On remplace le 0 dans la colonne par la carte sortie
            paquet.remove(choix)  # On enlève la carte sortie du paquet de cartes restantes pour qu'il ne reste que les cartes non sorties

    while len(paquet) > 0:

# On mets les cartes restantes non sorties dans la pioche

        choix = random.choice(paquet)
        pioche.append(choix)
        paquet.remove(choix)


# Etape 3: Préparation de l'affichage que verra l'utilisateur sur sa console :

def affichage():

# On prépare la ligne du haut où s'afficheront les fondations, la pioche et la défausse

    f1 = "▯" if len(fondation_1) == 0 else fondation_1[-1]
    f2 = "▯" if len(fondation_2) == 0 else fondation_2[-1]
    f3 = "▯" if len(fondation_3) == 0 else fondation_3[-1]
    f4 = "▯" if len(fondation_4) == 0 else fondation_4[-1]
    d = "▯" if len(defausse) == 0 else defausse[-1]
    visuel_pioche = "▯" if len(pioche) == 0 else "🂠"

    ligne_du_haut = ""

    for l in [f1, f2, f3, f4, "  ", d, visuel_pioche]:

        espaces = 8 - len(l)  # 8 caractères par colonne max (7 colonnes * 8 = 56 caractères de large au total et 7 * 9 = 63, or cela dépasse la limite de 60 imposée)

        ligne_du_haut = ligne_du_haut + l + " " * espaces

    print(ligne_du_haut)
    print("-" * 56) # On affiche une ligne de "-" pour séparer l"espace dit du haut et les colonnes


# On prépare les lignes du bas où s'afficheront les colonnes

    for i in range(7):   # On regarde s'il y a une carte à cet étage i pour chaque colonne, sinon on met un vide

        c1 = colonne_1[i] if i < len(colonne_1) else "  "
        c2 = affichage_col2[i] if i < len(affichage_col2) else "  "
        c3 = affichage_col3[i] if i < len(affichage_col3) else "  "
        c4 = affichage_col4[i] if i < len(affichage_col4) else "  "
        c5 = affichage_col5[i] if i < len(affichage_col5) else "  "
        c6 = affichage_col6[i] if i < len(affichage_col6) else "  "
        c7 = affichage_col7[i] if i < len(affichage_col7) else "  "

# On construit la ligne case par case

        ligne = ""

        for c in [c1, c2, c3, c4, c5, c6, c7]:

            espaces = 8 - len(c)

            ligne = ligne + c + " " * espaces

        print(ligne)







# - - - - - - - - - - - - - - - - -
#           Programme Principal
# - - - - - - - - - - - - - - - - -

debut = input("Que voulez-vous faire ? (nouvelle partie / charger une partie) répondre par 'nouvelle' ou 'charger'")

if debut == "charger":
    try:

# On ouvre le fichier de sauvegarde

        with open('sauvegarde.json', 'r', encoding='utf-8') as file:
            sauvegarde = json.load(file)

# On réaffecte TOUTES les variables globales avec les données sauvegardées

        fondation_1 = sauvegarde["fondation_1"]
        fondation_2 = sauvegarde["fondation_2"]
        fondation_3 = sauvegarde["fondation_3"]
        fondation_4 = sauvegarde["fondation_4"]

        colonne_1 = sauvegarde["colonne_1"]
        colonne_2 = sauvegarde["colonne_2"]
        colonne_3 = sauvegarde["colonne_3"]
        colonne_4 = sauvegarde["colonne_4"]
        colonne_5 = sauvegarde["colonne_5"]
        colonne_6 = sauvegarde["colonne_6"]
        colonne_7 = sauvegarde["colonne_7"]

        affichage_col2 = sauvegarde["affichage_col2"]
        affichage_col3 = sauvegarde["affichage_col3"]
        affichage_col4 = sauvegarde["affichage_col4"]
        affichage_col5 = sauvegarde["affichage_col5"]
        affichage_col6 = sauvegarde["affichage_col6"]
        affichage_col7 = sauvegarde["affichage_col7"]

        pioche = sauvegarde["pioche"]
        defausse = sauvegarde["defausse"]

        # On met à jour la liste des colonnes pour le reste du jeu
        colonne = [colonne_1, colonne_2, colonne_3, colonne_4, colonne_5, colonne_6, colonne_7]

        print("Partie chargée avec succès !")

    except FileNotFoundError:
        print("Aucune sauvegarde trouvée. Lancement d'une nouvelle partie par défaut...")
        distribution()

else:

# On lance la distribution
    distribution()



# On prépare le visuel masqué pour les colonnes
    affichage_col2 = ["🂠"] * (len(colonne_2) - 1) + [colonne_2[-1]]
    affichage_col3 = ["🂠"] * (len(colonne_3) - 1) + [colonne_3[-1]]
    affichage_col4 = ["🂠"] * (len(colonne_4) - 1) + [colonne_4[-1]]
    affichage_col5 = ["🂠"] * (len(colonne_5) - 1) + [colonne_5[-1]]
    affichage_col6 = ["🂠"] * (len(colonne_6) - 1) + [colonne_6[-1]]
    affichage_col7 = ["🂠"] * (len(colonne_7) - 1) + [colonne_7[-1]]



# On affiche les fondations, la pioche et la défausse
    affichage()



# On définit notre condition de départ
    en_jeu = True


# La boucle tourne tant que en_jeu est vrai
    while en_jeu:


        print("\n--- À VOTRE TOUR ---")
        action = input("Que voulez-vous faire ? (piocher / fondation / colonne / enregistrer / quitter / nouvelle partie) : ").strip().lower()

        if action == "piocher":

            if len(pioche) == 0:

                if len(defausse) == 0:

                    print("Vous n'avez plus de pioche, veuillez choisir une autre action")

                else:

                    print("La pioche est vide. Retournement de la défausse...")
                    pioche = defausse[::-1]  # On inverse l'ordre des cartes qui étaient dans la defausse
                    defausse = []  # On vide la défausse pour la suite
                    affichage()

            else:

                print("Vous piochez une carte...")
                carte_piochee = pioche[0]  # On prend la carte du dessus
                defausse.append(carte_piochee)  # On la met dans la défausse
                pioche.remove(carte_piochee)  # On la retire de la pioche

                affichage()

        elif action == "fondation":
            print("Déplacement vers la fondation...")

            origine = input("Quelle est la colonne d'origine (écrire le chiffre seulement ?")
            destination = input("Quelle est la colonne de destination de la carte ?")

            for f in fondation:

                if fondation[f] = "":

                    fondation[f] = colonne[origine-1][-1]

                else:

                    if colonne[origine-1][-1] in rouge:

                        if rouge in fondation[f]:





            affichage()


        elif action == "colonne":
            print("Veuillez saisir le déplacement souhaité sous la forme 'colonne initiale / colonne d'arrivée'")

            origine = input("Quelle est la colonne d'origine ?")
            destination = input("Quelle est la colonne de destination de la carte ?")
            taille = input("Quelle est la taille du bloc de cartes à déplacer ?")

            colonne[origine -1][-taille]



            affichage()

        elif action == "enregistrer":
            print("Sauvegarde de la partie en cours...")

# On regroupe toutes les variables du jeu dans un dictionnaire

            partie_solitaire = {
                "fondation_1": fondation_1,
                "fondation_2": fondation_2,
                "fondation_3": fondation_3,
                "fondation_4": fondation_4,
                "colonne_1": colonne_1,
                "colonne_2": colonne_2,
                "colonne_3": colonne_3,
                "colonne_4": colonne_4,
                "colonne_5": colonne_5,
                "colonne_6": colonne_6,
                "colonne_7": colonne_7,
                "affichage_col2": affichage_col2,
                "affichage_col3": affichage_col3,
                "affichage_col4": affichage_col4,
                "affichage_col5": affichage_col5,
                "affichage_col6": affichage_col6,
                "affichage_col7": affichage_col7,
                "pioche": pioche,
            "   defausse": defausse }

# On enregistre le dictionnaire

            with open('partie_solitaire.json', 'w+', encoding='utf-8') as file:
                json.dump(partie_solitaire, file, ensure_ascii=False)

            print("Partie sauvegardée avec succès dans 'partie_solitaire.json' !")




        elif action == "quitter":
                print("Merci d'avoir joué !")
                en_jeu = False  # On passe la variable à False pour stopper la boucle

        elif action == "nouvelle partie":

            set debut == "nouvelle"


        else:
            print("Commande non reconnue, veuillez réessayer.")


