# ===== INSTALLATIONS =====
# pip install pyo wxpython

from pyo import *

def osc_donnees(adresse, *args):
    '''
    Entrées : adresse (string) désignant le chemin d'envoi des données et args (float) représentant la valeur récupérée
    Fonction appelée à chaque message OSC reçu et qui affiche les valeurs obtenues pour chaque adresse.
    '''
    print(f"{adresse} : {args[0]}")

# Initialisation du serveur OSC
serveur = Server().boot().start()
osc_receiver = OscDataReceive(port=8000, address="*", function=osc_donnees)
serveur.gui(locals())