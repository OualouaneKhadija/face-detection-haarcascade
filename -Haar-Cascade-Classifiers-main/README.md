# Système de Détection de Visage (Haar Cascade)

Ce projet implémente un système de détection de visage en temps réel utilisant l'algorithme de Viola-Jones (Haar Cascade). Il offre à la fois une interface en ligne de commande (CLI) polyvalente et une application web moderne pour détecter des visages via webcam, images ou vidéos.

## 🚀 Fonctionnalités

- **Détection en Temps Réel** : Utilisation de la webcam pour détecter les visages instantanément.
- **Traitement d'Images** : Téléchargement et détection de visages sur des fichiers images (JPG, PNG).
- **Traitement de Vidéos** : Analyse de fichiers vidéo avec suivi des visages image par image.
- **Interface Web** : Une interface utilisateur intuitive construite avec FastAPI.
- **Paramètres Configurables** : Ajustement facile du facteur d'échelle et du nombre de voisins minimes pour optimiser la détection.

## 🛠️ Technologies Utilisées

Ce projet a été réalisé avec les technologies suivantes :

- **Python** : Langage de programmation principal.
- **OpenCV (cv2)** : Bibliothèque puissante pour le traitement d'images et la vision par ordinateur.
- **FastAPI** : Framework web moderne et rapide pour la création de l'API et de l'interface web.
- **NumPy** : Calcul scientifique et manipulation de matrices pour le traitement des images.
- **Haar Cascade Classifiers** : Modèles pré-entraînés pour la détection d'objets (visages).
- **JavaScript/HTML/CSS** : Pour la partie frontend de l'interface web.

## 🎓 Ce que j'ai appris

En réalisant ce projet, j'ai acquis et renforcé mes compétences en :

- **Vision par Ordinateur** : Compréhension de l'algorithme de Viola-Jones et manipulation de flux vidéo et d'images avec OpenCV.
- **Développement Backend** : Création d'API RESTful et de WebSockets avec FastAPI pour la communication temps réel.
- **Intégration** : Connexion entre le traitement d'images backend et une interface utilisateur frontend.
- **Gestion de Projet** : Organisation du code en modules réutilisables (`face_detector.py`, `app.py`).

## 💻 Comment lancer le projet

### Prérequis

Assurez-vous d'avoir Python installé. Installez ensuite les dépendances nécessaires :

```bash
pip install opencv-python-headless numpy fastapi uvicorn python-multipart
# Note: Si vous utilisez la webcam en local, utilisez `opencv-python` au lieu de `headless`
pip install opencv-python numpy fastapi uvicorn python-multipart
```

### Méthode 1 : Interface Web (Recommandé)

1.  Lancez le serveur web :
    ```bash
    python app.py
    ```
2.  Ouvrez votre navigateur à l'adresse indiquée (généralement `http://localhost:8000`).

### Méthode 2 : Ligne de Commande (CLI)

Vous pouvez utiliser le script `face_detector.py` directement :

**Pour la webcam :**
```bash
python face_detector.py --source webcam
```

**Pour une image :**
```bash
python face_detector.py --source image --path chemin/vers/image.jpg --save
```

**Pour une vidéo :**
```bash
python face_detector.py --source video --path chemin/vers/video.mp4 --save
```

**Options supplémentaires :**
- `--save` : Sauvegarde le résultat (image ou vidéo) dans le dossier `output`.
- `--scale-factor 1.2` : Ajuste la sensibilité (1.1 par défaut).
- `--min-neighbors 6` : Ajuste la précision (5 par défaut).

## 👤 Auteur

**Khadija Oualouane**
[GitHub Profile](https://github.com/OualouaneKhadija)
