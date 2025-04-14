# ===== INSTALLATIONS =====
# pip install pyo wxpython matplotlib

# IMPORTATIONS
import tkinter as tk
from tkinter import ttk
from pyo import Server, OscDataReceive
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading

# Initialisation du serveur
serveur = Server().boot().start()

# Dictionnaire pour stocker les données reçues
data = {
    "/data/motion/gyroscope/x": [],
    "/data/motion/gyroscope/y": [],
    "/data/motion/gyroscope/z": [],
    "/data/motion/accelerometer/x": [],
    "/data/motion/accelerometer/y": [],
    "/data/motion/accelerometer/z": []
}

# Initialisation du temps
max_points = 100
time_data = np.linspace(-max_points, 0, max_points)

# Fonction appelée à chaque message OSC reçu
def recuperer_data(adresse, *args):
    '''
    Entrées : adresse (string) désignant le chemin d'envoi des données et args (float) représentant la valeur récupérée
    Fonction appelée à chaque message OSC reçu et qui affiche les valeurs obtenues pour chaque adresse.
    '''
    if adresse in data:
        if len(data[adresse]) >= max_points:
            data[adresse].pop(0)
        data[adresse].append(args[0])

# Réception des messages OSC
osc_reception = OscDataReceive(port=8000, address="*", function=recuperer_data)

# Création de la fenêtre Tkinter
root = tk.Tk()
root.title("Visualisation des données OSC")

# Création des graphiques avec Matplotlib
fig, axes = plt.subplots(2, 3, figsize=(12, 8))  # 2 lignes et 3 colonnes
fig.tight_layout(pad=3.0)
lines = {}

adresses = list(data.keys())
for i, adresse in enumerate(adresses):
    row = i // 3  # Calcul de la ligne
    col = i % 3   # Calcul de la colonne
    ax = axes[row, col]
    ax.set_title(adresse)
    ax.set_xlim(-max_points, 0)
    ax.set_ylim(-10, 10)
    lines[adresse], = ax.plot([], [], lw=2)

# Intégration de la figure dans Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Mise à jour des graphiques en temps réel
def update_graphs():
    while True:
        for adresse in adresses:
            if len(data[adresse]) > 0:
                y_data = data[adresse]
                lines[adresse].set_data(time_data[-len(y_data):], y_data)
        canvas.draw()
        root.update()

# Thread pour la mise à jour des graphiques
thread = threading.Thread(target=update_graphs, daemon=True)
thread.start()

# Lancement de la boucle principale Tkinter
root.mainloop()

# Fermeture du serveur audio
serveur.stop()