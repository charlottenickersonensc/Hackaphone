# ===== INSTALLATIONS =====
# pip install mutagen pillow pyo python-osc

# ===== IMPORTATIONS =====
import os
import io
import time
import threading
from pyo import *
import tkinter as tk
from ctypes import windll
from PIL import Image, ImageTk
from pythonosc import dispatcher, osc_server
from mutagen import File
from mutagen.id3 import ID3, APIC

# ===== FONCTIONS =====
def jouer_chanson(index):
    '''
    Entrée : index (entier) représentant le numéro de la chanson dans la file de lecture
    Joue une chanson et surveille sa progression pour enchaîner automatiquement.
    '''
    global source_audio, filtre_audio, selecteur_audio, index_chanson_actuelle, stop_event

    index_chanson_actuelle = index % len(musiques)
    chemin_fichier = musiques[index_chanson_actuelle]
    print(f"🎵 Lecture de : {os.path.splitext(os.path.basename(chemin_fichier))[0]}") # Afficher le nom de la chanson sans l'extension

    # Arrêter l’ancienne source
    try:
        source_audio.stop()
    except NameError:
        pass # Si c'est la première lecture, il n'y a pas encore de source définie

    if stop_event is not None:
        stop_event.set() # On signale l’arrêt du thread précédent

    stop_event = threading.Event() # (Re)création d’un nouvel Event pour le thread courant

    # Chargement de la chanson
    source_audio = SfPlayer(chemin_fichier, speed=vitesse, loop=False, mul=0.8)
    
    # Définition du filtre passe-bande
    filtre_audio = ButBP(source_audio, freq=frequence, q=2, mul=1.0)
    
    # Sélectionneur pour basculer entre changement de vitesse et son filtré
    selecteur_audio = Selector([source_audio, filtre_audio], voice=0).out()

    # Démarrage du thread de surveillance avec l’Event en paramètre
    threading.Thread(target=surveiller_fin_chanson, args=(stop_event,), daemon=True).start()

    # Mettre à jour les informations de la chanson
    afficher_info_chanson(chemin_fichier)

def surveiller_fin_chanson(stop_event):
    '''
    Entrée : stop_event (threading.Event) qui communique avec le thread de surveillance pour lui demander de s'arrêter proprement
    Boucle de surveillance qui s'arrête dès que stop_event.is_set() est True.
    Passe automatiquement à la piste suivante dès que le temps virtuel est supérieur à la durée originale.
    '''
    duree_originale = sndinfo(musiques[index_chanson_actuelle])[1]
    temps_virtuel = 0.0
    dernier_temps_reel = time.time()

    while not stop_event.is_set():
        maintenant = time.time()
        delta = maintenant - dernier_temps_reel
        dernier_temps_reel = maintenant

        temps_virtuel += delta * vitesse.value # Pondération par la vitesse actuelle

        # Si la piste est terminée, on déclenche la suivante
        if temps_virtuel >= duree_originale:
            # On signale l’arrêt de CE thread avant d’appeler jouer_chanson
            stop_event.set()
            jouer_chanson(index_chanson_actuelle + 1)
            return

        time.sleep(0.05)

def ajuster_parametres(address, *args):
    '''
    Entrées : address (string) désignant le chemin d'envoi des données OSC et args (float) représentant la valeur de l'adresse
    Gère les ajustements des paramètres de la chanson en fonction des données OSC reçues.
    '''
    global vitesse_fixe, frequence_fixe, effet_chorus, effet_distorsion, effet_echo, effet_reverberation

    if address == "/data/compass/trueNorth":
        if selecteur_audio.voice == 0: # Modification de la vitesse
            valeur_joystick = args[0] # Valeur entre 0 et 360
            # Conversion en échelle [0.25, 1.75]
            if valeur_joystick <= 90:
                nouvelle_vitesse = 0.25 + (valeur_joystick / 90) * (1 - 0.25)
            elif valeur_joystick <= 180:
                nouvelle_vitesse = 1 + ((valeur_joystick - 90) / 90) * (1.75 - 1)
            elif valeur_joystick <= 270:
                nouvelle_vitesse = 1.75 - ((valeur_joystick - 180) / 90) * (1.75 - 1)
            else:
                nouvelle_vitesse = 1 - ((valeur_joystick - 270) / 90) * (1 - 0.25)

            print(f"🔓 Vitesse de la musique : {nouvelle_vitesse:.2f}x")
            vitesse.value = nouvelle_vitesse
            afficher_parametres()

        elif selecteur_audio.voice == 1: # Modification de la fréquence
            valeur_joystick = args[0] # Valeur entre 0 et 360
            # Conversion en échelle [300, 5000]
            if valeur_joystick <= 90:
                nouvelle_frequence = 300 + (valeur_joystick / 90) * (2650 - 300)
            elif valeur_joystick <= 180:
                nouvelle_frequence = 2650 + ((valeur_joystick - 90) / 90) * (5000 - 2650)
            elif valeur_joystick <= 270:
                nouvelle_frequence = 5000 - ((valeur_joystick - 180) / 90) * (5000 - 2650)
            else:
                nouvelle_frequence = 2650 - ((valeur_joystick - 270) / 90) * (2650 - 300)

            print(f"🔓 Valeur de la fréquence : {nouvelle_frequence:.2f} Hz")
            frequence.value = nouvelle_frequence
            afficher_parametres()

    elif address == "/data/microphone/active" and args[0] == True: # Effet chorus
        if effet_chorus is None:
            effet_chorus = Chorus(source_audio, depth=0.8, feedback=0.4, bal=0.7, mul=0.5).out()
            print("🎤 Chorus activé.")
        else:
            effet_chorus = None
            print("🎤 Chorus désactivé.")
        afficher_parametres()

    elif address == "/data/motion/gyroscope/active" and args[0] == True: # Effet distorsion
        if effet_distorsion is None:
            effet_distorsion = Disto(source_audio, drive=0.8, slope=0.8, mul=0.5).out()
            print("🎸 Distorsion activée.")
        else:
            effet_distorsion = None
            print("🎸 Distorsion désactivée.")
        afficher_parametres()

    elif address == "/data/location/active" and args[0] == True: # Effet écho
        if effet_echo is None:
            effet_echo = Delay(source_audio, delay=0.3, feedback=0.6, mul=0.3).out()
            print("🔊 Écho activé.")
        else:
            effet_echo = None
            print("🔊 Écho désactivé.")
        afficher_parametres()

    elif address == "/data/gameController/active" and args[0] == True: # Effet réverbération
        if effet_reverberation is None:
            effet_reverberation = Freeverb(source_audio, size=0.9, damp=0.3, bal=0.8, mul=0.6).out()
            print("🌀 Réverbération activée.")
        else:
            effet_reverberation = None
            print("🌀 Réverbération désactivée.")
        afficher_parametres()

    elif address == "/data/compass/active" and args[0] == True: # Changer de mode
        selecteur_audio.voice = abs(selecteur_audio.voice - 1)
        if selecteur_audio.voice == 0:
            print("⏭  Mode actuel : Vitesse")
        elif selecteur_audio.voice == 1:
            print("⏭  Mode actuel : Fréquence")
        afficher_parametres()

    elif address == "/data/faceTracking/active" and args[0] == True: # Passer à la chanson suivante
        print("⏭  Changement de chanson")
        jouer_chanson(index_chanson_actuelle + 1)

def afficher_info_chanson(chemin_acces):
    global label_info_chanson

    fichier = File(chemin_acces)
    if fichier is not None and isinstance(fichier.tags, ID3):
        for tag in fichier.tags.values():
            if isinstance(tag, APIC):
                image_data = tag.data
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((150, 150), Image.LANCZOS) # Redimensionner pour une meilleure résolution
                image_tk = ImageTk.PhotoImage(image)
                label_info_chanson.config(image=image_tk)
                label_info_chanson.image = image_tk
                break

    nom_fichier = os.path.basename(chemin_acces)
    label_nom_chanson.config(text=nom_fichier.replace(".mp3", ""))

def afficher_parametres():
    '''
    Affiche sur l'interface graphique les différents paramètres de la musique.
    '''
    global label_parametres, effet_chorus, effet_distorsion, effet_echo, effet_reverberation

    # Création de la chaîne de texte avec les paramètres
    if selecteur_audio.voice == 0: # Modification de la vitesse
        texte_parametres = "📳 MODE ACTUEL : VITESSE\n"
        texte_parametres += f"🔓 Vitesse actuelle : {vitesse.value:.2f}x\n"
    else:
        texte_parametres = "📳 MODE ACTUEL : FRÉQUENCE\n"
        texte_parametres += f"🔓 Fréquence actuelle : {frequence.value:.2f} Hz\n"

    # Vérification des effets activés
    texte_parametres += f"🎤 Chorus (Microphone) {'🔴' if effet_chorus else '⭕'}\n"
    texte_parametres += f"🎸 Distorsion (Motion) {'🔴' if effet_distorsion else '⭕'}\n"
    texte_parametres += f"🔊 Écho (Location) {'🔴' if effet_echo else '⭕'}\n"
    texte_parametres += f"🌀 Réverbération (Controller) {'🔴' if effet_reverberation else '⭕'}\n"
    texte_parametres += f"🎵 Changer la musique (Face Tracking)"

    # Mise à jour du label avec les nouveaux paramètres
    label_parametres.config(text=texte_parametres)

# ===== CODE =====
# Initialisation
dossier_chansons = os.path.join(os.path.dirname(__file__), "..\Chansons") # Chemin du dossier contenant les chansons
musiques = [os.path.join(dossier_chansons, f) for f in os.listdir(dossier_chansons) if f.endswith(".mp3")] # Récupération des chansons
serveur = Server().boot().start() # Initialisation du serveur audio

# Variables de contrôle
stop_event = None
index_chanson_actuelle = 0 # Indice de la première chanson
vitesse = SigTo(value=1, time=0.1) # Variable pour ajuster la vitesse de la musique
vitesse_fixe = 1 # Définition d'une vitesse figée pour le verrouillage
frequence = SigTo(value=1000, time=0.1) # Variable pour ajuster le filtre passe-bande
frequence_fixe = 300 # Définition d'une fréquence figée pour le verrouillage
effet_chorus = None # Effet chorus
effet_distorsion = None # Effet distorsion
effet_echo = None # Effet écho
effet_reverberation = None # Effet réverbération

# Création de la fenêtre principale Tkinter
windll.shcore.SetProcessDpiAwareness(1) # Règle la qualité de l'interface en fonction de la résolution de l'écran

root = tk.Tk()
root.title("Hackaphone")
root.geometry("1000x204")

# Création du label pour afficher l'image
label_image = tk.Label(root)
label_image.pack()

# Initialisation du label pour afficher l'image de la chanson
label_info_chanson = tk.Label(root, font=("Arial", 14), anchor="n", padx=10, pady=10)
label_info_chanson.place(relx=1.0, y=50, anchor="ne")

# Initialisation du label pour afficher le nom de la chanson
label_nom_chanson = tk.Label(root, font=("Arial", 14), anchor="n", padx=10, pady=10)
label_nom_chanson.place(relx=1.0, y=0, anchor="ne")

# Initialisation du label pour afficher les paramètres
label_parametres = tk.Label(root, font=("Arial", 12), anchor="nw", padx=10, pady=10, bd=2, relief="ridge", bg="lightgray")
label_parametres.place(relx=0.01, rely=0.02, anchor="nw")

# Jouer la première chanson
jouer_chanson(index_chanson_actuelle)

# Réception des messages OSC avec dispatcher
disp = dispatcher.Dispatcher()
disp.map("/data/compass/trueNorth", ajuster_parametres)
disp.map("/data/microphone/active", ajuster_parametres)
disp.map("/data/motion/gyroscope/active", ajuster_parametres)
disp.map("/data/location/active", ajuster_parametres)
disp.map("/data/gameController/active", ajuster_parametres)
disp.map("/data/compass/active", ajuster_parametres)
disp.map("/data/faceTracking/active", ajuster_parametres)

# Initialisation du serveur OSC
osc = osc_server.ThreadingOSCUDPServer(('0.0.0.0', 8000), disp)

# Lancer le serveur OSC dans un thread séparé
server_thread = threading.Thread(target=osc.serve_forever)
server_thread.daemon = True
server_thread.start()

# Afficher les paramètres dans l'interface graphique
afficher_parametres()

# Lancer la boucle principale Tkinter
root.mainloop()