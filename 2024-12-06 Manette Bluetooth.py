# ===== INSTALLATIONS =====
# pip install pyo wxpython

# ===== IMPORTATIONS =====
import os
from pyo import *

# ===== FONCTIONS =====
def charger_musique(index):
    '''
    Entrée : index (entier) représentant le numéro de la chanson dans la liste de lecture
    Charge et joue une piste.
    '''
    global audio
    chemin_fichier = os.path.join(os.path.dirname(__file__), musique[index])
    audio = SfPlayer(chemin_fichier, speed=vitesse, loop=True, mul=0.8).out()

def changer_musique():
    '''
    Change de musique.
    '''
    global index_chanson_actuelle
    index_chanson_actuelle = (index_chanson_actuelle + 1) % len(musique)
    charger_musique(index_chanson_actuelle)

def ajuster_vitesse(adresse, *args):
    '''
    Entrées : adresse (string) désignant le chemin d'envoi des données du stick et args (float) représentant la valeur d'inclinaison du stick
    Fonction appelée à chaque message OSC reçu et qui ajuste la vitesse de la musique.
    '''
    if adresse == "/data/gameController/stick/right/y":
        print(f"Valeur du stick : {args[0]}")
        nouvelle_vitesse = args[0]+1
        vitesse.value = nouvelle_vitesse
    elif adresse == "/data/gameController/action/right" and args[0] == True:
        print("⏭  Changement de chanson")
        changer_musique()

# ===== CODE =====
# Liste des fichiers audio
musique = [
    "Chansons/Beyoncé ft. JAY-Z - Crazy In Love.mp3",
    "Chansons/Imagine Dragons - Believer.mp3",
    "Chansons/Jean-Jacques Goldman - Quand la musique est bonne.mp3",
    "Chansons/Joe Dassin - Dans les yeux d'Émilie.mp3",
    "Chansons/Johnny Hallyday - Allumer le feu.mp3",
    "Chansons/Los Del Rio - Macarena (Bayside Boys Remix) (Remasterizado).mp3",
    "Chansons/Michel Sardou - Les lacs du Connemara.mp3",
    "Chansons/Modern Talking - Cheri Cheri Lady.mp3",
    "Chansons/Philippe Katerine - Louxor j'adore.mp3",
    "Chansons/Queen - Bohemian Rhapsody.mp3",
    "Chansons/Rick Astley - Never Gonna Give You Up.mp3",
    "Chansons/Rihanna - S & M.mp3"
]
index_chanson_actuelle = 0  # Indice de la piste actuelle

# Initialisation du serveur audio
serveur = Server().boot().start()

# Variable pour ajuster la vitesse de lecture (partagée par toutes les pistes)
vitesse = SigTo(value=1, time=0.1)  # Transition lissée pour éviter les changements brusques

# Charger la première piste
charger_musique(index_chanson_actuelle)

# Réception des messages OSC
osc_vitesse = OscDataReceive(port=8000, address="*", function=ajuster_vitesse)

# Lancement de l'interface graphique
serveur.gui(locals())