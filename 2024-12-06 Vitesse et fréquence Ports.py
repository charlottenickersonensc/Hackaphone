# ===== IMPORTATIONS =====
import os
from pyo import *

# ===== FONCTIONS =====
def boussole_vers_vitesse(valeur):
    '''
    Entrée : valeur (float) représentant en degrés la valeur de la boussole
    Interpole la vitesse en fonction de la direction.
    0 -> 0.5x, 90/270 -> 1x, 180 -> 2x
    '''
    if valeur <= 90:
        return 0.5 + (valeur / 90) * 0.5
    elif valeur <= 180:
        return 1 + ((valeur - 90) / 90) * 1
    elif valeur <= 270:
        return 2 - ((valeur - 180) / 90) * 1
    else:
        return 1 - ((valeur - 270) / 90) * 0.5

def ajuster_vitesse(adresse, *args):
    '''
    Entrées : adresse (string) désignant le chemin d'envoi des données de la boussole et args (float) représentant en degrés la valeur de la boussole
    Fonction appelée à chaque message OSC reçu et qui ajuste la vitesse de la musique.
    '''
    if adresse == "/data/compass/trueNorth":
        valeur_boussole = args[0]
        print(f"Valeur de la boussole : {valeur_boussole}")
        nouvelle_vitesse = boussole_vers_vitesse(valeur_boussole)
        print(f"Vitesse de la musique : {nouvelle_vitesse}")
        vitesse.value = nouvelle_vitesse

def boussole_vers_frequence(valeur):
    '''
    Entrée : valeur (float) représentant en degrés la valeur de la boussole
    Interpole la fréquence en fonction de la direction.
    0 -> 300 Hz, 90/270 -> 1000 Hz, 180 -> 5000 Hz
    '''
    if valeur <= 90:
        return 300 + (valeur / 90) * (1000 - 300)
    elif valeur <= 180:
        return 1000 + ((valeur - 90) / 90) * (5000 - 1000)
    elif valeur <= 270:
        return 5000 - ((valeur - 180) / 90) * (5000 - 1000)
    else:
        return 1000 - ((valeur - 270) / 90) * (1000 - 300)

def ajuster_frequence(adresse, *args):
    '''
    Entrées : adresse (string) désignant le chemin d'envoi des données de la boussole et args (float) représentant en degrés la valeur de la boussole
    Fonction appelée à chaque message OSC reçu et qui ajuste la fréquence de la musique.
    '''
    if adresse == "/data/compass/trueNorth":
        valeur_boussole = args[0]
        print(f"Valeur de la boussole : {valeur_boussole}")
        nouvelle_frequence = boussole_vers_frequence(valeur_boussole)
        print(f"Valeur de la frequence : {nouvelle_frequence} Hz")
        frequence.value = nouvelle_frequence

# ===== CODE =====
# Chemin relatif vers le fichier musical
chemin_fichier = os.path.join(os.path.dirname(__file__), "Musiques/Rick Astley - Never Gonna Give You Up.mp3")

# Initialisation du serveur audio
serveur = Server().boot().start()

# Variables de contrôle
vitesse = SigTo(value=1, time=0.1)  # Transition douce pour la vitesse
frequence = SigTo(value=1000, time=0.1)  # Transition douce pour la fréquence

# Chargement du fichier audio
source_audio = SfPlayer(chemin_fichier, speed=vitesse, loop=True)

# Application du filtre passe-bande
filtre_audio = ButBP(source_audio, freq=frequence, q=2, mul=1.0).out() # Connecte le signal filtré à la sortie

# Réception des messages OSC
osc_vitesse = OscDataReceive(port=8000, address="*", function=ajuster_vitesse)
osc_frequence = OscDataReceive(port=8001, address="*", function=ajuster_frequence)

# Interface graphique
serveur.gui(locals())