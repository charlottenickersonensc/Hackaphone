# ===== INSTALLATIONS =====
# pip install pyo wxpython

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

def changer_mode(gyroscope_x, gyroscope_z):
    '''
    Entrées : gyroscope_x et gyzoscope_z (float) représentant respectivement la valeur du gyroscope sur l'axe x et sur l'axe z
    Met à jour le mode d'utilisation de la musique en fonction des valeurs des gyroscopes sur les axes x et z.
    '''
    global mode_actuel, echo_actif, derniere_valeur_gyroscope_z

    # Mettre l'écho si gyzoscope_z > 8
    if derniere_valeur_gyroscope_z < 8 <= gyroscope_z:
        echo_actif = not echo_actif
        if echo_actif:
            print("Écho activé")
            selecteur_echo.voice = 1
        else:
            print("Écho désactivé")
            selecteur_echo.voice = 0

    derniere_valeur_gyroscope_z = gyroscope_z

    # Changer le mode si gyroscope_x > 8
    if gyroscope_x > 8:
        if mode_actuel == "ChangerVitesse":
            mode_actuel = "ChangerFrequence"
        elif mode_actuel == "ChangerFrequence":
            mode_actuel = "ChangerVitesse"

def ajuster_parametres(adresse, *args):
    '''
    Entrées : adresse (string) désignant le chemin d'envoi des données OSC et args (float) représentant la valeur de l'adresse
    Gère les ajustements des paramètres en fonction du mode et des données OSC.
    '''
    global mode_actuel

    if adresse == "/data/motion/gyroscope/x":
        gyroscope_x = args[0]
        changer_mode(gyroscope_x, derniere_valeur_gyroscope_z)

    elif adresse == "/data/motion/gyroscope/z":
        gyroscope_z = args[0]
        changer_mode(derniere_valeur_gyroscope_x, gyroscope_z)

    elif adresse == "/data/compass/trueNorth":
        valeur_boussole = args[0]
        print(f"Valeur de la boussole : {valeur_boussole}")

        if mode_actuel == "ChangerVitesse":
            nouvelle_vitesse = boussole_vers_vitesse(valeur_boussole)
            print(f"Vitesse de la musique : {nouvelle_vitesse}")
            vitesse.value = nouvelle_vitesse
            selecteur_audio.voice = 0  # Son initial (pas de filtre)

        elif mode_actuel == "ChangerFrequence":
            nouvelle_frequence = boussole_vers_frequence(valeur_boussole)
            print(f"Valeur de la fréquence : {nouvelle_frequence} Hz")
            frequence.value = nouvelle_frequence
            selecteur_audio.voice = 1  # Son filtré

# ===== CODE =====
# Initialisation
chemin_fichier = os.path.join(os.path.dirname(__file__), "Chansons/Philippe Katerine - Louxor j'adore.mp3")
serveur = Server().boot().start()

# Variables de contrôle
vitesse = SigTo(value=1, time=0.1)  # Transition douce pour la vitesse
frequence = SigTo(value=1000, time=0.1)  # Transition douce pour la fréquence
mode_actuel = "ChangerVitesse"  # Mode initial
echo_actif = False  # État initial de l'écho
derniere_valeur_gyroscope_x = 0  # Dernière valeur du gyroscope x
derniere_valeur_gyroscope_z = 0  # Dernière valeur du gyroscope z

# Chargement du fichier audio
source_audio = SfPlayer(chemin_fichier, speed=vitesse, loop=True)

# Application du filtre passe-bande
filtre_audio = ButBP(source_audio, freq=frequence, q=2, mul=1.0)

# Application de l'écho
echo_audio = Delay(source_audio, delay=[0.3, 0.6], feedback=0.5, mul=0.7)

# Sélectionneur pour basculer entre son initial/filtré et écho
selecteur_audio = Selector([source_audio, filtre_audio], voice=0)
selecteur_echo = Selector([selecteur_audio, echo_audio], voice=0).out()

# Réception des messages OSC
osc = OscDataReceive(port=8000, address="*", function=ajuster_parametres)

# Interface graphique
serveur.gui(locals())