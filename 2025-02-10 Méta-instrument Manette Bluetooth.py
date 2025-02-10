# ===== INSTALLATIONS =====
# pip install pyo wxpython

# ===== IMPORTATIONS =====
import os
from pyo import *

# ===== FONCTIONS =====
def jouer_chanson(index):
    '''
    Entrée : index (entier) représentant le numéro de la chanson dans la file de lecture
    Joue une chanson et surveille sa progression pour enchaîner automatiquement.
    '''
    global source_audio, filtre_audio, selecteur_audio, index_chanson_actuelle

    index_chanson_actuelle = index % len(musiques)
    chemin_fichier = musiques[index_chanson_actuelle]

    print(f"🎵 Lecture de : {chemin_fichier}")

    # Arrêter l’ancienne source
    try:
        source_audio.stop()
    except NameError:
        pass # Si c'est la première lecture, il n'y a pas encore de source définie

    # Chargement de la chanson
    source_audio = SfPlayer(chemin_fichier, speed=vitesse, loop=False, mul=0.8)
    
    # Définition du filtre passe-bande
    filtre_audio = ButBP(source_audio, freq=frequence, q=2, mul=1.0)
    
    # Sélectionneur pour basculer entre changement de vitesse et son filtré
    selecteur_audio = Selector([source_audio, filtre_audio], voice=0).out()

    # Lancer le thread de surveillance
    threading.Thread(target=surveiller_fin_chanson, daemon=True).start()

def surveiller_fin_chanson():
    '''
    Vérifie en continu si la chanson est terminée en fonction de la vitesse.
    '''
    lecture_active = True
    duree_originale = sndinfo(musiques[index_chanson_actuelle])[1] # Durée en secondes de la chanson

    debut = time.time()
    while lecture_active:
        duree_adaptee = duree_originale / vitesse.value # Ajustement en fonction de la vitesse
        temps_ecoule = time.time() - debut

        if temps_ecoule >= duree_adaptee:
            jouer_chanson(index_chanson_actuelle + 1)
            break

        time.sleep(0.1)

def ajuster_parametres(address, *args):
    '''
    Entrées : address (string) désignant le chemin d'envoi des données OSC et args (float) représentant la valeur de l'adresse
    Gère les ajustements des paramètres de la chanson en fonction des données OSC reçues.
    '''
    global verrouiller_vitesse, vitesse_fixe

    if address == "/data/gameController/stick/left/y":
        valeur_joystick = args[0]  # Valeur entre -1 et 1
        nouvelle_vitesse = (valeur_joystick + 1)  # Conversion en échelle [0, 2]

        if not verrouiller_vitesse:  # Mise à jour de la vitesse seulement si pas verrouillé
            print(f"Vitesse de la musique : {nouvelle_vitesse}")
            vitesse.value = nouvelle_vitesse
        else:
            print(f"Vitesse verrouillée à {vitesse_fixe}")
    
    elif address == "/data/gameController/shoulder/left" and args[0] == True:
        # Interrupteur : chaque appui inverse l'état du verrouillage
        verrouiller_vitesse = not verrouiller_vitesse

        if verrouiller_vitesse:
            vitesse_fixe = vitesse.value  # On stocke la vitesse actuelle
            print(f"🔒 Vitesse verrouillée à {vitesse_fixe}")
        else:
            print("🔓 Vitesse déverrouillée, retour au contrôle par joystick")

    elif address == "/data/gameController/options" and args[0] == True:
        print("⏭  Changement de chanson")
        jouer_chanson(index_chanson_actuelle + 1)

# ===== CODE =====
# Initialisation
dossier_chansons = os.path.join(os.path.dirname(__file__), "Chansons") # Chemin du dossier contenant les chansons
musiques = [os.path.join(dossier_chansons, f) for f in os.listdir(dossier_chansons) if f.endswith(".mp3")] # Récupération des chansons
serveur = Server().boot().start() # Initialisation du serveur audio

# Variables de contrôle
index_chanson_actuelle = 0 # Indice de la première chanson
vitesse = SigTo(value=1, time=0.1) # Variable pour ajuster la vitesse de la musique
verrouiller_vitesse = False # Définition d'une variable pour gérer le verrouillage de la vitesse
vitesse_fixe = 1 # Définition d'une vitesse figée pour le verrouillage
frequence = SigTo(value=1000, time=0.1) # Variable pour ajuster le filtre passe-bande

# Réception des messages OSC
osc_vitesse = OscDataReceive(port=8000, address="*", function=ajuster_parametres)

# Jouer la première chanson
jouer_chanson(index_chanson_actuelle)

# Lancement de l'interface graphique
serveur.gui(locals())