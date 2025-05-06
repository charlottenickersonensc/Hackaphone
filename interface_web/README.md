# Interface Web Hackaphone

Cette application web permet de gérer et de contrôler les différentes visualisations du projet Hackaphone.

## Structure du Projet

- `app.py` : Backend Flask servant l'API et l'interface web
- `frontend/` : Application React pour l'interface utilisateur

## Prérequis

- Python 3.8+
- Node.js 14+ et npm

## Installation

### Backend (Flask)

1. Installez les dépendances Python nécessaires :

```bash
pip install flask flask-cors
```

### Frontend (React)

1. Naviguez vers le dossier frontend :

```bash
cd frontend
```

2. Installez les dépendances Node.js :

```bash
npm install
```

3. Construisez l'application React pour la production :

```bash
npm run build
```

## Démarrage de l'Application

1. Pour démarrer le serveur Flask, exécutez :

```bash
python app.py
```

2. Accédez à l'application dans votre navigateur à l'adresse :

```
http://localhost:5000
```

## Développement

Pour développer l'interface React :

1. Dans un terminal, démarrez le serveur Flask :

```bash
python app.py
```

2. Dans un autre terminal, lancez le serveur de développement React :

```bash
cd frontend
npm start
```

3. Accédez à l'application de développement React à l'adresse :

```
http://localhost:3000
```

## Fonctionnalités

- Visualisation de la liste des visualisations disponibles
- Démarrage et arrêt des visualisations à distance
- Surveillance de l'état des visualisations en temps réel
- Interface utilisateur intuitive avec thème sombre