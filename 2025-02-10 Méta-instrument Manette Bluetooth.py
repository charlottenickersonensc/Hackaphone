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
    Vérifie en continu si la chanson en cours de lecture est terminée en fonction de la vitesse et passe à la suivante si c'est le cas.
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
    global verrouillage, vitesse_fixe, effet_chorus, effet_distorsion, effet_echo, effet_reverberation, effet_harmonizer, effet_tremolo, effet_phaser, effet_bitcrusher

    if address == "/data/gameController/stick/left/y":
        if selecteur_audio.voice == 0: # Modification de la vitesse
            valeur_joystick = args[0] # Valeur entre -1 et 1
            nouvelle_vitesse = (valeur_joystick * 0.75 + 1) # Conversion en échelle [0.25, 1.75]

            if not verrouillage: # Mise à jour de la vitesse seulement si verrouillage = False
                print(f"Vitesse de la musique : {nouvelle_vitesse}")
                vitesse.value = nouvelle_vitesse
            else:
                print(f"🔒 Vitesse verrouillée à {vitesse_fixe}")

        elif selecteur_audio.voice == 1: # Modification de la fréquence
            valeur_joystick = args[0] # Valeur entre -1 et 1
            nouvelle_frequence = (valeur_joystick * 2350 + 2650) # Conversion en échelle [300, 5000]

            print(f"Valeur de la fréquence : {nouvelle_frequence}")
            frequence.value = nouvelle_frequence

    elif address == "/data/gameController/shoulder/left" and args[0] == True: # Verrouillage de la vitesse
        # Interrupteur : chaque appui inverse l'état du verrouillage
        verrouillage = not verrouillage

        if verrouillage:
            vitesse_fixe = vitesse.value  # On stocke la vitesse actuelle
            print(f"🔒 Vitesse verrouillée à {vitesse_fixe}")
        else:
            print("🔓 Vitesse déverrouillée")
    
    elif address == "/data/gameController/action/left" and args[0] == True: # Effet chorus
        if effet_chorus is None:
            effet_chorus = Chorus(source_audio, depth=0.8, feedback=0.4, bal=0.7, mul=0.5).out()
            print("🎤 Chorus activé.")
        else:
            effet_chorus = None
            print("🎤 Chorus désactivé.")

    elif address == "/data/gameController/action/right" and args[0] == True: # Effet distorsion
        if effet_distorsion is None:
            effet_distorsion = Disto(source_audio, drive=0.8, slope=0.8, mul=0.5).out()
            print("🎸 Distorsion activée.")
        else:
            effet_distorsion = None
            print("🎸 Distorsion désactivée.")

    elif address == "/data/gameController/action/down" and args[0] == True: # Effet écho
        if effet_echo is None:
            effet_echo = Delay(source_audio, delay=0.3, feedback=0.6, mul=0.3).out()
            print("🔊 Écho activé.")
        else:
            effet_echo = None
            print("🔊 Écho désactivé.")

    elif address == "/data/gameController/action/up" and args[0] == True: # Effet réverbération
        if effet_reverberation is None:
            effet_reverberation = Freeverb(source_audio, size=0.9, damp=0.3, bal=0.8, mul=0.6).out()
            print("🏛️ Réverbération activée.")
        else:
            effet_reverberation = None
            print("🏛️ Réverbération désactivée.")

    elif address == "/data/gameController/dpad/left" and args[0] == True: # Effet harmonizer
        if effet_harmonizer is None:
            env = WinTable(8)
            wsize = 0.1
            trans = -7
            ratio = pow(2.0, trans / 12.0)
            rate = -(ratio - 1) / wsize
            ind = Phasor(freq=rate, phase=[0, 0.5])
            win = Pointer(table=env, index=ind, mul=0.7)
            effet_harmonizer = Delay(source_audio, delay=ind * wsize, mul=win).mix(1).out()
            print("🚀 Harmonizer activé.")
        else:
            effet_harmonizer = None
            print("🚀 Harmonizer désactivé.")

    elif address == "/data/gameController/dpad/right" and args[0] == True: # Effet tremolo
        if effet_tremolo is None:
            effet_tremolo = source_audio * (1 - Sine(freq=4, mul=0.5))
            print("🎛️ Tremolo activé.")
        else:
            effet_tremolo = None
            print("🎛️ Tremolo désactivé.")

    elif address == "/data/gameController/dpad/down" and args[0] == True: # Effet phaser
        if effet_phaser is None:
            effet_phaser = Phaser(source_audio, freq=0.3, spread=0.7, feedback=0.3, num=8, mul=0.5).out()
            print("🌌 Phaser activé.")
        else:
            effet_phaser = None
            print("🌌 Phaser désactivé.")

    elif address == "/data/gameController/dpad/up" and args[0] == True: # Effet bitcrusher
        if effet_bitcrusher is None:
            effet_bitcrusher = Degrade(source_audio, bitdepth=5, srscale=0.5, mul=0.5).out()
            print("🎮 Bitcrusher activé.")
        else:
            effet_bitcrusher = None
            print("🎮 Bitcrusher désactivé.")

    elif address == "/data/gameController/menu" and args[0] == True: # Changer de mode
        selecteur_audio.voice = abs(selecteur_audio.voice - 1)
        if selecteur_audio.voice == 0:
            print("⏭  Mode actuel : Vitesse")
        elif selecteur_audio.voice == 1:
            print("⏭  Mode actuel : Fréquence")

    elif address == "/data/gameController/options" and args[0] == True: # Passer à la chanson suivante
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
vitesse_fixe = 1 # Définition d'une vitesse figée pour le verrouillage
frequence = SigTo(value=1000, time=0.1) # Variable pour ajuster le filtre passe-bande
verrouillage = False # Si le verrouillage vaut False, on peut modifier la vitesse ; sinon, on la fige
effet_chorus = None # Effet chorus
effet_distorsion = None # Effet distorsion
effet_echo = None # Effet écho
effet_reverberation = None # Effet réverbération
effet_harmonizer = None # Effet harmonizer
effet_tremolo = None # Effet tremolo
effet_phaser = None # Effet phaser
effet_bitcrusher = None # Effet bitcrusher

# Réception des messages OSC
osc_vitesse = OscDataReceive(port=8000, address="*", function=ajuster_parametres)

# Jouer la première chanson
jouer_chanson(index_chanson_actuelle)

# Lancement de l'interface graphique
serveur.gui(locals())