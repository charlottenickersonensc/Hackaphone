#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
import importlib.util
import subprocess
import signal
import threading
import time
import json

# Ajout du répertoire parent au chemin système pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialisation de l'application Flask
app = Flask(__name__, 
            static_folder='./frontend/build/static',
            template_folder='./frontend/build')
CORS(app)  # Activation de CORS pour permettre les requêtes cross-origin

# Dictionnaire pour stocker les processus de visualisation en cours
active_visualizers = {}
visualizer_lock = threading.Lock()

# Liste des visualisations disponibles
visualizations = [
    {
        "id": "frequency_bands",
        "name": "Bandes de Fréquence",
        "module": "../Visualiseurs/instruments.py",
        "class": "FrequencyBandsVisualizer",
        "description": "Visualisation des bandes de fréquence audio avec des vagues colorées"
    },
    {
        "id": "waveform",
        "name": "Forme d'onde",
        "module": "../Visualiseurs/Forme d'onde.py",
        "class": "WaveformVisualizer",
        "description": "Affichage de la forme d'onde du signal audio en temps réel"
    },
    {
        "id": "shape",
        "name": "Forme",
        "module": "../Visualiseurs/Forme.py",
        "class": "ShapeVisualizer",
        "description": "Visualisation géométrique réagissant au son"
    },
    {
        "id": "hallucination",
        "name": "Hallucination",
        "module": "../Visualiseurs/Hallucination.pyw",
        "class": "HallucinationVisualizer",
        "description": "Effets visuels psychédéliques réagissant à la musique"
    },
    {
        "id": "white_pad",
        "name": "Pavé Blanc",
        "module": "../Visualiseurs/Pavé blanc.py",
        "class": "WhitePadVisualizer",
        "description": "Surface interactive réagissant aux fréquences audio"
    },
    {
        "id": "spectrum",
        "name": "Spectre",
        "module": "../Visualiseurs/Spectre.py",
        "class": "SpectrumVisualizer",
        "description": "Analyse spectrale du son avec affichage coloré des fréquences"
    },
    {
        "id": "sphere",
        "name": "Sphère",
        "module": "../Visualiseurs/Sphère.py",
        "class": "SphereVisualizer",
        "description": "Sphère 3D qui pulse et change de forme avec la musique"
    },
    {
        "id": "terrain",
        "name": "Terrain",
        "module": "../Visualiseurs/Terrain.py",
        "class": "TerrainVisualizer",
        "description": "Paysage 3D généré et animé en fonction du son"
    },
    {
        "id": "cool_sphere",
        "name": "Sphère Cool",
        "module": "../Visualiseurs/coolsphere.py",
        "class": "CoolSphereVisualizer",
        "description": "Sphère animée avec effets de couleur réagissant à la musique"
    },
    {
        "id": "osc_visualize",
        "name": "Visualisation OSC",
        "module": "../Visualiseurs/oscvisualize.py",
        "class": "OSCVisualizer",
        "description": "Visualisation basée sur les messages OSC avec effets dynamiques"
    },
    {
        "id": "psychadelic",
        "name": "Psychédélique",
        "module": "../Visualiseurs/psychadelic.py",
        "class": "PsychedelicVisualizer",
        "description": "Effets visuels colorés de type psychédélique synchronisés avec la musique"
    },
    {
        "id": "terrain_mesh",
        "name": "Maillage de Terrain",
        "module": "../Visualiseurs/terrainmesh.py",
        "class": "TerrainMeshVisualizer", 
        "description": "Maillage 3D déformé par les fréquences audio"
    }
]

@app.route('/')
def index():
    """
    Route principale qui sert l'application React
    """
    return render_template('index.html')

@app.route('/api/visualizations', methods=['GET'])
def get_visualizations():
    """
    Renvoie la liste de toutes les visualisations disponibles
    """
    return jsonify(visualizations)

@app.route('/api/start/<visualization_id>', methods=['POST'])
def start_visualization(visualization_id):
    """
    Démarre une visualisation spécifique dans un processus séparé
    """
    with visualizer_lock:
        # Vérifier si cette visualisation est déjà en cours d'exécution
        if visualization_id in active_visualizers and active_visualizers[visualization_id].poll() is None:
            return jsonify({"status": "already_running", "message": "Cette visualisation est déjà en cours d'exécution"})
        
        # Trouver la visualisation demandée
        visualization = next((v for v in visualizations if v["id"] == visualization_id), None)
        if not visualization:
            return jsonify({"status": "error", "message": "Visualisation non trouvée"}), 404
        
        try:
            # Chemin complet vers le module de visualisation
            module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                       visualization["module"].lstrip("../"))
            
            # Préparer l'environnement pour le processus de visualisation
            env = os.environ.copy()
            env['KEEP_RUNNING'] = 'true'  # Signaler que la visualisation doit rester active
            
            # Lancer le processus Python pour exécuter la visualisation
            process = subprocess.Popen([sys.executable, module_path], 
                                       stdin=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       env=env,
                                       start_new_session=True)  # Détacher le processus pour qu'il soit plus indépendant
            
            active_visualizers[visualization_id] = process
            
            return jsonify({
                "status": "started", 
                "message": f"Visualisation {visualization['name']} démarrée avec succès"
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"Erreur lors du démarrage: {str(e)}"}), 500

@app.route('/api/stop/<visualization_id>', methods=['POST'])
def stop_visualization(visualization_id):
    """
    Arrête une visualisation en cours d'exécution
    """
    with visualizer_lock:
        if visualization_id in active_visualizers:
            process = active_visualizers[visualization_id]
            try:
                # Essayer d'arrêter proprement le processus
                if process.poll() is None:  # Si le processus est toujours en cours d'exécution
                    process.terminate()
                    time.sleep(0.5)
                    if process.poll() is None:
                        process.kill()
                
                del active_visualizers[visualization_id]
                return jsonify({"status": "stopped", "message": "Visualisation arrêtée avec succès"})
            except Exception as e:
                return jsonify({"status": "error", "message": f"Erreur lors de l'arrêt: {str(e)}"}), 500
        else:
            return jsonify({"status": "not_running", "message": "Cette visualisation n'est pas en cours d'exécution"}), 404

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Renvoie le statut de toutes les visualisations
    """
    status = {}
    with visualizer_lock:
        for viz_id in active_visualizers:
            process = active_visualizers[viz_id]
            status[viz_id] = "running" if process.poll() is None else "stopped"
    
    return jsonify(status)

# Route pour servir les fichiers statiques React
@app.route('/<path:path>')
def serve_react(path):
    """
    Sert les fichiers statiques de l'application React
    """
    if path != "" and os.path.exists(os.path.join(app.template_folder, path)):
        return send_from_directory(app.template_folder, path)
    else:
        return render_template('index.html')

def cleanup():
    """
    Nettoyage des processus à la fermeture de l'application
    """
    with visualizer_lock:
        for process in active_visualizers.values():
            if process.poll() is None:
                try:
                    process.terminate()
                    time.sleep(0.5)
                    if process.poll() is None:
                        process.kill()
                except:
                    pass

# Fonction principale pour démarrer le serveur
if __name__ == "__main__":
    try:
        # S'assurer que les processus sont nettoyés à la sortie
        import atexit
        atexit.register(cleanup)
        
        # Démarrer le serveur Flask
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        cleanup()