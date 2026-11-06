# - - - - - - - - - - - - - - - - -
#           Importations
# - - - - - - - - - - - - - - - - -

import random   # distribution aléatoire des cartes
import copy     # copie complète de la partie (pour pouvoir annuler un coup)
import json     # sauvegarde / chargement de la partie
from colorama import Fore, Style, init   # couleurs dans la console

# autoreset=True : la couleur redevient normale à la fin de chaque print
init(autoreset=True)


# - - - - - - - - - - - - - - - - -
#           Données du jeu
# - - - - - - - - - - - - - - - - -

FICHIER_DEFAUT = "partie_solitaire.json"

# Les 3 niveaux de difficulté
NIVEAUX = {
    "1": {"nom": "Facile (pioche de 1 carte, avec aide)", "nb_pioche": 1, "aide": True},
    "2": {"nom": "Moyen (pioche de 3 cartes, avec aide)", "nb_pioche": 3, "aide": True},
    "3": {"nom": "Difficile (pioche de 3 cartes, sans aide)", "nb_pioche": 3, "aide": False},
}

SYMBOLES = {"pique": "♠", "trefle": "♣", "carreau": "♦", "coeur": "♥"}
COULEURS = {"pique": "noir", "trefle": "noir", "carreau": "rouge", "coeur": "rouge"}

# Valeur de chaque carte (As = 1 ... Roi = 13)
VALEURS = {
    "A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13,
}


def creer_paquet():
    # Crée les 52 cartes.
    paquet = []
    for famille in ["pique", "trefle", "carreau", "coeur"]:
        for valeur, point in VALEURS.items():
            carte = {
                "famille": famille,
                "valeur": valeur,
                "point": point,
                "symbole": SYMBOLES[famille],
                "couleur": COULEURS[famille],
                "visible": False,
            }
            paquet.append(carte)
    return paquet


def distribution(niveau):
    # Distribue les cartes au hasard : 1 carte dans la colonne 1, 2 dans la 2, etc.
    # Les cartes restantes vont dans la pioche. Retourne l'état complet de la partie.
    paquet = creer_paquet()
    colonnes = [[], [], [], [], [], [], []]

    for i in range(7):
        for j in range(i + 1):
            choix = random.choice(paquet)   # on choisit une carte au hasard
            colonnes[i].append(choix)       # on la place dans la colonne
            paquet.remove(choix)            # on l'enlève du paquet
        colonnes[i][-1]["visible"] = True   # seule la dernière carte est visible

    # Les cartes restantes non distribuées forment la pioche
    pioche = []
    while len(paquet) > 0:
        choix = random.choice(paquet)
        pioche.append(choix)
        paquet.remove(choix)

    etat = {
        "pioche": pioche,
        "defausse": [],
        "defausse_affichees": 0,   # nombre de cartes de la défausse montrées au joueur
        "fondations": [[], [], [], []],
        "colonnes": colonnes,
        "niveau": niveau,
    }
    return etat


# - - - - - - - - - - - - - - - - -
#   Etape 2 : affichage
# - - - - - - - - - - - - - - - - -

def nom_carte(carte):
    # Texte simple d'une carte, sans couleur (ex : 'K♠').
    return carte["valeur"] + carte["symbole"]


def formater_carte(carte, largeur=0):
    # Texte coloré d'une carte.
    #   - None (emplacement vide)  -> ▯
    #   - carte cachée             -> 🂠
    #   - rouge pour ♥ et ♦, blanc pour ♠ et ♣
    if carte is None:
        return "▯".rjust(largeur)
    if not carte["visible"]:
        return "🂠".rjust(largeur)

    texte = nom_carte(carte).rjust(largeur)
    if carte["couleur"] == "rouge":
        return Fore.LIGHTRED_EX + texte + Style.RESET_ALL
    return Fore.WHITE + texte + Style.RESET_ALL


def afficher_jeu(etat):
    # Affiche le plateau.
    print("=" * 55)
    print(f" NIVEAU : {NIVEAUX[etat['niveau']]['nom']}")
    print("-" * 55)

    # Pioche et défausse (avec le nombre de cartes de chacune)
    if len(etat["pioche"]) > 0:
        texte_pioche = "🂠"
    else:
        texte_pioche = "▯"

    # On montre les cartes du dernier tirage (jusqu'à 3), mais seule la dernière peut être déplacée.
    nb_montrees = cartes_montrees(etat)
    if nb_montrees > 0:
        texte_defausse = ""
        for carte in etat["defausse"][-nb_montrees:]:
            texte_defausse += formater_carte(carte) + " "
        texte_defausse = texte_defausse.strip()
    else:
        texte_defausse = "▯"

    print(f" PIOCHE : {texte_pioche} ({len(etat['pioche'])})   "
          f"DEFAUSSE  : {texte_defausse} ({len(etat['defausse'])})")

    # Fondations (F1 à F4) : on affiche la carte du dessus de chaque pile
    ligne_fond = " FONDATIONS : "
    for idx, pile in enumerate(etat["fondations"]):
        label = f"F{idx+1}:"
        if len(pile) > 0:
            ligne_fond += f"{label}[" + formater_carte(pile[-1]) + "] "
        else:
            ligne_fond += f"{label}[▯] "
    print(ligne_fond)
    print("-" * 55)

    # Colonnes affichées verticalement
    entete = " "
    for i in range(1, 8):
        entete += ("C" + str(i)).rjust(4) + "  "
    print(entete)

    hauteur_max = 1
    for col in etat["colonnes"]:
        if len(col) > hauteur_max:
            hauteur_max = len(col)

    for ligne in range(hauteur_max):
        ligne_str = " "
        for col in etat["colonnes"]:
            if ligne < len(col):
                ligne_str += formater_carte(col[ligne], 4) + "  "
            elif ligne == 0:
                ligne_str += formater_carte(None, 4) + "  "   # colonne vide
            else:
                ligne_str += " " * 6
        print(ligne_str)
    print("=" * 55)


def afficher_commandes():
    # Mémo de toutes les commandes pour le joueur.
    print("""
---------------- COMMANDES ----------------
 Origines  : Colonnes 1 à 7 | Défausse : 8 | Fondations : f1 à f4

 piocher                : tire 1 ou 3 cartes (selon le niveau)
                          ou retourne la défausse quand la pioche est vide
 fondation X            : range la dernière carte de l'origine X sur une fondation
                          (exemple : fondation 3  ou  fondation 8)
 colonne X Y N          : déplace N cartes de l'origine X vers la colonne Y
                          (exemples : colonne 7 2 1 , colonne f1 3 , colonne 8 4)
 colonne X Y            : déplace 1 carte (exemple : colonne 8 4 ou colonne f2 5)
 colonne X Y tout       : déplace toutes les cartes visibles de la colonne X
 annuler                : annule le dernier déplacement
 aide                   : liste des déplacements possibles (niveaux 1 et 2)
 enregistrer            : sauvegarde la partie
 charger                : recharge la partie sauvegardée
 nouvelle               : recommence une partie
 commandes              : réaffiche ce mémo
 quitter                : quitte le jeu
--------------------------------------------
""")


# - - - - - - - - - - - - - - - - -
#   Etape 3 : règles de validation
# - - - - - - - - - - - - - - - - -

def peut_poser_sur_colonne(carte, cible):
    # Sur une colonne : couleur différente et valeur juste en dessous.
    # Sur une colonne vide : seulement un Roi.
    if cible is None:
        return carte["point"] == 13
    couleur_differente = carte["couleur"] != cible["couleur"]
    juste_en_dessous = cible["point"] - carte["point"] == 1
    return couleur_differente and juste_en_dessous


def peut_poser_sur_fondation(carte, pile):
    # Sur une fondation vide : seulement un As.
    # Sinon : même famille et valeur juste au dessus.
    if len(pile) == 0:
        return carte["point"] == 1
    meme_famille = carte["famille"] == pile[-1]["famille"]
    juste_au_dessus = carte["point"] - pile[-1]["point"] == 1
    return meme_famille and juste_au_dessus


def trouver_fondation(etat, carte):
    # Retourne le numéro (0 à 3) de la première fondation qui accepte la carte, sinon None.
    resultat = None
    for f in range(4):
        if resultat is None and peut_poser_sur_fondation(carte, etat["fondations"][f]):
            resultat = f
    return resultat


def compter_visibles(colonne):
    # Nombre de cartes visibles à la fin d'une colonne.
    nb = 0
    while nb < len(colonne) and colonne[-1 - nb]["visible"]:
        nb += 1
    return nb


def reveler_sommet(colonne):
    # Retourne la dernière carte d'une colonne si elle est cachée.
    if len(colonne) > 0 and not colonne[-1]["visible"]:
        colonne[-1]["visible"] = True


def verifier_victoire(etat):
    # Victoire 1 : les 52 cartes sont dans les fondations
    total = 0
    for pile in etat["fondations"]:
        total += len(pile)
    if total == 52:
        return True

    # Victoire 2 : pioche et défausse vides + toutes les cartes des colonnes sont visibles

    if len(etat["pioche"]) == 0 and len(etat["defausse"]) == 0:
        for col in etat["colonnes"]:
            for carte in col:
                if not carte["visible"]:
                    return False
        return True

    return False

# - - - - - - - - - - - - - - - - -
#   Etape 4 : mouvements
# - - - - - - - - - - - - - - - - -

def piocher(etat):
    # Pioche 1 ou 3 cartes (selon le niveau) vers la défausse.
    nb_pioche = NIVEAUX[etat["niveau"]]["nb_pioche"]

    if len(etat["pioche"]) == 0:
        if len(etat["defausse"]) == 0:
            return False, "Vous n'avez plus de pioche, veuillez choisir une autre action."
        # On retourne la défausse pour refaire la pioche
        etat["pioche"] = etat["defausse"][::-1]
        etat["defausse"] = []
        etat["defausse_affichees"] = 0
        for carte in etat["pioche"]:
            carte["visible"] = False
        return True, "La pioche est vide. Retournement de la défausse..."

    nb = min(nb_pioche, len(etat["pioche"]))
    for _ in range(nb):
        carte = etat["pioche"].pop()
        carte["visible"] = True
        etat["defausse"].append(carte)
    etat["defausse_affichees"] = nb   # on montre les cartes qui viennent d'être tirées
    return True, f"Vous piochez {nb} carte(s)..."


def pile_source(etat, type_src, indice):
    # Retourne la liste correspondant à l'origine : colonne (C), défausse (D) ou fondation (F).
    if type_src == "C":
        return etat["colonnes"][indice]
    elif type_src == "D":
        return etat["defausse"]
    elif type_src == "F":
        return etat["fondations"][indice]
    return []


def cartes_montrees(etat):
    # Nombre de cartes de la défausse visibles par le joueur.
    if NIVEAUX[etat["niveau"]]["nb_pioche"] == 1:
        return min(1, len(etat["defausse"]))
    return min(etat["defausse_affichees"], len(etat["defausse"]))


def retirer_carte_montree(etat):
    # Appelé quand la carte du dessus de la défausse est déplacée.
    etat["defausse_affichees"] = max(0, etat["defausse_affichees"] - 1)


def deplacer_vers_fondation(etat, type_src, indice):
    # Défausse -> Fondation ou Colonne -> Fondation.
    if type_src == "F":
        return False, "Une carte est déjà sur une fondation !"

    pile = pile_source(etat, type_src, indice)
    if len(pile) == 0 or (type_src == "D" and cartes_montrees(etat) == 0):
        return False, "Cette origine est vide !"

    f = trouver_fondation(etat, pile[-1])
    if f is None:
        return False, "Mouvement non autorisé."

    etat["fondations"][f].append(pile.pop())
    if type_src == "C":
        reveler_sommet(pile)
    else:
        retirer_carte_montree(etat)
    return True, "Carte déplacée avec succès vers une fondation !"


def deplacer_vers_colonne(etat, type_src, indice, dest, nb):
    # Colonne/Défausse/Fondation -> Colonne. nb = nombre de cartes à déplacer.
    col_dst = etat["colonnes"][dest]
    cible = col_dst[-1] if len(col_dst) > 0 else None

    if type_src == "C":
        if indice == dest:
            return False, "L'origine et la destination sont identiques."
        col_src = etat["colonnes"][indice]
        if nb < 1 or nb > len(col_src):
            return False, "Nombre de cartes invalide pour cette colonne."

        bloc = col_src[-nb:]
        for carte in bloc:
            if not carte["visible"]:
                return False, "Vous ne pouvez pas déplacer des cartes cachées."

        if not peut_poser_sur_colonne(bloc[0], cible):
            return False, "Mouvement non autorisé."

        del col_src[-nb:]
        col_dst.extend(bloc)
        reveler_sommet(col_src)
        return True, f"{nb} carte(s) déplacée(s) vers la colonne {dest + 1}."

    if type_src == "F":
        if nb != 1:
            return False, "On ne déplace qu'une carte à la fois depuis une fondation."
        pile_fond = etat["fondations"][indice]
        if len(pile_fond) == 0:
            return False, "Cette fondation est vide !"
        if not peut_poser_sur_colonne(pile_fond[-1], cible):
            return False, "Mouvement non autorisé."

        col_dst.append(pile_fond.pop())
        return True, f"Carte déplacée de la fondation F{indice + 1} vers la colonne {dest + 1}."

    # Depuis la défausse : une seule carte à la fois
    if nb != 1:
        return False, "On ne déplace qu'une carte à la fois depuis la défausse."
    if len(etat["defausse"]) == 0 or cartes_montrees(etat) == 0:
        return False, "Cette origine est vide !"
    if not peut_poser_sur_colonne(etat["defausse"][-1], cible):
        return False, "Mouvement non autorisé."

    col_dst.append(etat["defausse"].pop())
    retirer_carte_montree(etat)
    return True, f"Carte déplacée vers la colonne {dest + 1}."


# - - - - - - - - - - - - - - - - -
#   Lecture et vérification des saisies
# - - - - - - - - - - - - - - - - -

def lire_origine(texte):
    # Convertit '1' à '7' (colonne), '8' (défausse) ou 'f1' à 'f4' (fondation) en (type, indice).
    if texte in ("1", "2", "3", "4", "5", "6", "7"):
        return ("C", int(texte) - 1)
    if texte == "8":
        return ("D", 0)
    if texte in ("f1", "f2", "f3", "f4"):
        return ("F", int(texte[1]) - 1)
    return None


def lire_colonne(texte):
    # Convertit '1' à '7' en indice de colonne (0 à 6). Retourne None si invalide.
    if texte in ("1", "2", "3", "4", "5", "6", "7"):
        return int(texte) - 1
    return None


# - - - - - - - - - - - - - - - - -
#   Etape 5 : aide (déplacements possibles, priorisés)
# - - - - - - - - - - - - - - - - -

def trouver_tous_les_coups(etat):
    # Liste tous les coups possibles sous la forme (priorité, description).
    # Priorité 1 : ranger sur une fondation
    # Priorité 2 : déplacer entre colonnes en dévoilant une carte cachée
    # Priorité 3 : autres déplacements vers une colonne (colonne/défausse/fondation)
    # Priorité 4 : piocher
    coups = []

    # Priorité 1 : colonne -> fondation
    for i in range(7):
        col = etat["colonnes"][i]
        if len(col) > 0 and trouver_fondation(etat, col[-1]) is not None:
            coups.append((1, f"Ranger {nom_carte(col[-1])} de la colonne {i + 1} sur une fondation"))

    # Priorité 1 : défausse -> fondation
    if cartes_montrees(etat) > 0:
        carte = etat["defausse"][-1]
        if trouver_fondation(etat, carte) is not None:
            coups.append((1, f"Ranger {nom_carte(carte)} de la défausse sur une fondation"))

    # Priorités 2 et 3 : colonne -> colonne
    for i in range(7):
        col_src = etat["colonnes"][i]
        for k in range(1, compter_visibles(col_src) + 1):
            premiere = col_src[-k]
            roi_inutile = (k == len(col_src) and premiere["point"] == 13)
            vide_deja_propose = False
            if not roi_inutile:
                for j in range(7):
                    col_dst = etat["colonnes"][j]
                    cible = col_dst[-1] if len(col_dst) > 0 else None
                    deja = (cible is None and vide_deja_propose)
                    if i != j and not deja and peut_poser_sur_colonne(premiere, cible):
                        if cible is None:
                            vide_deja_propose = True
                        if len(col_src) > k and not col_src[-k - 1]["visible"]:
                            priorite = 2
                        else:
                            priorite = 3
                        coups.append((priorite,
                                      f"Déplacer {k} carte(s) de la colonne {i + 1} vers la colonne {j + 1}"
                                      f"  --> 'colonne {i + 1} {j + 1} {k}'"))

    # Priorité 3 : défausse -> colonne
    if cartes_montrees(etat) > 0:
        carte = etat["defausse"][-1]
        vide_deja_propose = False
        for j in range(7):
            col_dst = etat["colonnes"][j]
            cible = col_dst[-1] if len(col_dst) > 0 else None
            deja = (cible is None and vide_deja_propose)
            if not deja and peut_poser_sur_colonne(carte, cible):
                if cible is None:
                    vide_deja_propose = True
                coups.append((3, f"Poser {nom_carte(carte)} de la défausse sur la colonne {j + 1}"
                                 f"  --> 'colonne 8 {j + 1}'"))

    # Priorité 3 : fondation -> colonne
    for f in range(4):
        pile_fond = etat["fondations"][f]
        if len(pile_fond) > 0:
            carte = pile_fond[-1]
            vide_deja_propose = False
            for j in range(7):
                col_dst = etat["colonnes"][j]
                cible = col_dst[-1] if len(col_dst) > 0 else None
                deja = (cible is None and vide_deja_propose)
                if not deja and peut_poser_sur_colonne(carte, cible):
                    if cible is None:
                        vide_deja_propose = True
                    coups.append((3, f"Déplacer {nom_carte(carte)} de la fondation F{f + 1} sur la colonne {j + 1}"
                                     f"  --> 'colonne f{f + 1} {j + 1}'"))

    # Priorité 4 : piocher
    if len(etat["pioche"]) > 0 or len(etat["defausse"]) > 0:
        coups.append((4, "Piocher (ou retourner la défausse)  --> 'piocher'"))

    coups.sort(key=lambda coup: coup[0])   # tri par priorité (1 = le plus intéressant)
    return coups


def afficher_aide(etat):
    # Affiche tous les coups possibles, du plus au moins prioritaire.
    if not NIVEAUX[etat["niveau"]]["aide"]:
        print("L'aide est désactivée au niveau difficile.")
    else:
        coups = trouver_tous_les_coups(etat)
        print("--- COUPS POSSIBLES (P1 = le plus intéressant, P4 = le moins) ---")
        for numero in range(len(coups)):
            priorite, description = coups[numero]
            print(f" {numero + 1:>2}. [P{priorite}] {description}")


# - - - - - - - - - - - - - - - - -
#   Etape 6 : sauvegarde / chargement
# - - - - - - - - - - - - - - - - -

def sauvegarder_partie(etat):
    # Enregistre la partie au format JSON.
    try:
        with open(FICHIER_DEFAUT, "w", encoding="utf-8") as fichier:
            json.dump(etat, fichier, indent=4, ensure_ascii=False)
        return f"Partie sauvegardée avec succès dans '{FICHIER_DEFAUT}' !"
    except OSError:
        return "Impossible d'écrire le fichier de sauvegarde."


def etat_valide(etat):
    # Vérifie qu'un fichier chargé ressemble bien à une partie de Solitaire.
    if not isinstance(etat, dict):
        return False
    for cle in ["pioche", "defausse", "defausse_affichees", "fondations", "colonnes", "niveau"]:
        if cle not in etat:
            return False
    if etat["niveau"] not in NIVEAUX:
        return False
    if len(etat["colonnes"]) != 7 or len(etat["fondations"]) != 4:
        return False
    total = len(etat["pioche"]) + len(etat["defausse"])
    for pile in etat["colonnes"] + etat["fondations"]:
        total += len(pile)
    return total == 52


def charger_partie():
    # Charge la partie sauvegardée. Retourne (état ou None, message).
    try:
        with open(FICHIER_DEFAUT, "r", encoding="utf-8") as fichier:
            etat = json.load(fichier)
    except FileNotFoundError:
        return None, f"Aucune sauvegarde trouvée ('{FICHIER_DEFAUT}')."
    except (json.JSONDecodeError, OSError):
        return None, "Le fichier de sauvegarde est illisible."

    if not etat_valide(etat):
        return None, "La sauvegarde est invalide ou corrompue."
    return etat, "Partie chargée avec succès !"


# - - - - - - - - - - - - - - - - -
#           Programme principal
# - - - - - - - - - - - - - - - - -

def choisir_niveau():
    # Demande le niveau de jeu tant que la saisie n'est pas valide.
    for numero, infos in NIVEAUX.items():
        print(f" {numero} : {infos['nom']}")
    choix = ""
    while choix not in NIVEAUX:
        choix = input("Choisissez un niveau (1, 2 ou 3) : ").strip()
        if choix not in NIVEAUX:
            print("Saisie invalide : tapez 1, 2 ou 3.")
    return choix


def demarrage():
    # Nouvelle partie ou chargement d'une partie sauvegardée.
    debut = ""
    while debut != "nouvelle" and debut != "charger":
        debut = input("Que voulez-vous faire ? (nouvelle partie / charger une partie) "
                      "répondre par 'nouvelle' ou 'charger' : ").strip().lower()
        if debut != "nouvelle" and debut != "charger":
            print("Saisie invalide : répondez par 'nouvelle' ou 'charger'.")

    etat = None
    if debut == "charger":
        etat, message = charger_partie()
        print(message)
        if etat is None:
            print("Lancement d'une nouvelle partie par défaut...")

    if etat is None:
        etat = distribution(choisir_niveau())
    return etat


def main():
    etat = demarrage()
    historique = []   # pile des états précédents (pour annuler)

    print("Tapez 'commandes' pour voir toutes les actions.")
    en_jeu = True

    while en_jeu:
        afficher_jeu(etat)

        if verifier_victoire(etat):
            print("FÉLICITATIONS ! Vous avez gagné la partie !")
            en_jeu = False
        else:
            print("--- À VOTRE TOUR ---")
            saisie = input("Que voulez-vous faire ? (piocher / fondation X / colonne X Y N / "
                           "enregistrer / charger / annuler / quitter / nouvelle) : ").strip().lower()
            mots = saisie.split()

            copie_avant = copy.deepcopy(etat)   # pour annuler si le coup réussit
            succes = False

            if len(mots) == 0:
                print("Saisie vide, veuillez réessayer.")

            elif mots[0] == "quitter":
                print("Merci d'avoir joué !")
                en_jeu = False

            elif mots[0] == "commandes":
                afficher_commandes()

            elif mots[0] == "aide":
                afficher_aide(etat)

            elif mots[0] == "annuler":
                if len(historique) > 0:
                    etat = historique.pop()
                    print("Dernier déplacement annulé.")
                else:
                    print("Aucun déplacement à annuler.")

            elif mots[0] == "enregistrer":
                print(sauvegarder_partie(etat))

            elif mots[0] == "charger":
                etat_charge, message = charger_partie()
                print(message)
                if etat_charge is not None:
                    etat = etat_charge
                    historique = []

            elif mots[0] == "nouvelle":
                print("Lancement d'une nouvelle partie...")
                etat = distribution(choisir_niveau())
                historique = []

            elif mots[0] == "piocher":
                succes, message = piocher(etat)
                print(message)

            elif mots[0] == "fondation":
                # Format attendu : fondation X
                if len(mots) != 2:
                    print("Format attendu : fondation X (exemple : fondation 3).")
                else:
                    origine = lire_origine(mots[1])
                    if origine is None:
                        print("Origine invalide (colonne 1 à 7 ou défausse 8).")
                    else:
                        succes, message = deplacer_vers_fondation(etat, origine[0], origine[1])
                        print(message)

            elif mots[0] == "colonne":
                # Format attendu : colonne X Y N (N est facultatif et vaut 1 par défaut)
                if len(mots) < 3 or len(mots) > 4:
                    print("Format attendu : colonne X Y N (exemple : colonne 7 2 1 ou colonne f1 3).")
                else:
                    origine = lire_origine(mots[1])
                    destination = lire_colonne(mots[2])
                    nb = 1
                    erreur = ""

                    if origine is None:
                        erreur = "Origine invalide (colonne 1 à 7, défausse 8 ou fondation f1 à f4)."
                    elif destination is None:
                        erreur = "Destination invalide (colonne 1 à 7)."
                    elif len(mots) == 4:
                        if mots[3] == "tout" and origine[0] == "C":
                            nb = compter_visibles(etat["colonnes"][origine[1]])
                        elif mots[3].isdecimal():
                            nb = int(mots[3])
                        else:
                            erreur = "La taille du bloc doit être un entier ou 'tout'."

                    if erreur != "":
                        print(erreur)
                    else:
                        succes, message = deplacer_vers_colonne(
                            etat, origine[0], origine[1], destination, nb)
                        print(message)

            else:
                print("Commande non reconnue, tapez 'commandes' pour voir la liste.")

            # Si un coup a réussi, on mémorise l'état d'avant pour pouvoir l'annuler
            if succes:
                historique.append(copie_avant)


if __name__ == "__main__":
    main()
