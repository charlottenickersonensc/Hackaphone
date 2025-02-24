import tkinter as tk
from PIL import Image, ImageTk
import os

# Définir le répertoire de travail au dossier contenant le fichier Python
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Fonction pour superposer les images
def superposer_calques(image_base_path, calques, variables):
    # Charger l'image de base
    image_base = Image.open(image_base_path).convert("RGBA")  # Convertir en RGBA si ce n'est pas déjà le cas

    # Ajouter les calques en fonction des variables
    for calque, actif in zip(calques, variables):
        if actif:
            image_calque = Image.open(calque).convert("RGBA")  # Convertir le calque en RGBA
            # Superposer les calques (la transparence sera correctement gérée)
            image_base.paste(image_calque, (0, 0), image_calque)  # Le troisième argument est le masque alpha pour la transparence

    return image_base

# Fonction pour afficher l'image résultante dans Tkinter
def afficher_image():
    # Liste des calques et des variables associées
    calques = ["Calques Manette Switch Pro/Manette.png"] + ["Calques Manette Switch Pro/" + calque for calque in calques_disponibles]  # Ajouter le chemin complet pour chaque calque
    variables = [True] + [var.get() for var in var_calques]  # True pour l'image de base et la valeur de chaque calque

    # Appliquer les calques
    image_resultat = superposer_calques("Calques Manette Switch Pro/Manette.png", calques, variables)

    # Convertir l'image pour l'afficher avec Tkinter
    image_resultat_tk = ImageTk.PhotoImage(image_resultat)

    # Mettre à jour l'image affichée dans le Label
    label_image.config(image=image_resultat_tk)
    label_image.image = image_resultat_tk

# Obtenir la liste des calques dans le dossier "Calques Manette Switch Pro"
def obtenir_calques():
    dossier_calques = "Calques Manette Switch Pro"
    calques = [f for f in os.listdir(dossier_calques) if f.endswith(".png") and f != "Manette.png"]
    return calques

# Créer la fenêtre principale Tkinter
root = tk.Tk()
root.title("Maquette pour superposer les calques")

# Récupérer les calques disponibles dans le dossier
calques_disponibles = obtenir_calques()

# Liste des variables pour les calques
var_calques = []

# Créer les boutons pour chaque calque
for calque in calques_disponibles:
    # Extraire le nom sans extension pour l'affichage du bouton
    nom_calque = os.path.splitext(calque)[0]
    var = tk.BooleanVar(value=False)  # Par défaut, le calque est désactivé
    var_calques.append(var)

    # Créer un bouton pour chaque calque
    bouton = tk.Checkbutton(root, text=f"Afficher {nom_calque}", variable=var)
    bouton.pack()

# Créer un bouton pour afficher l'image avec les calques sélectionnés
button_afficher = tk.Button(root, text="Afficher Manette avec Calques", command=afficher_image)
button_afficher.pack()

# Créer un label pour afficher l'image résultante
label_image = tk.Label(root)
label_image.pack()

# Afficher l'image de base "Manette.png" dès le lancement
image_de_base = Image.open("Calques Manette Switch Pro/Manette.png").convert("RGBA")
image_de_base_tk = ImageTk.PhotoImage(image_de_base)
label_image.config(image=image_de_base_tk)
label_image.image = image_de_base_tk

# Lancer la boucle Tkinter
root.mainloop()