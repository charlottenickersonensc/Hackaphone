# ===== INSTALLATIONS =====
# pip install pyo wxpython

import os
from pyo import *

# Démarrer le serveur audio
s = Server().boot()
s.start()

# Récupération du fichier audio
base = os.path.dirname(__file__)
source_audio = os.path.join(base, "..", "Chansons", "ROSÉ, Bruno Mars - APT..mp3")
source_audio = os.path.abspath(source_audio)

# Lecture du fichier audio
sf = SfPlayer(source_audio, speed=1, loop=True, mul=1).out()

# Analyse spectrale
spec = Spectrum(sf, size=1024)

# Interface graphique
s.gui(locals())