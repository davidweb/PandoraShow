# Pandora Show

**Pandora Show** est une application web interactive conçue pour organiser des jeux de quiz en direct. Grâce à une interface utilisateur dynamique et un panneau d'administration complet, l'application permet de gérer en temps réel la répartition des joueurs en équipes, le suivi des scores, un compte à rebours interactif, ainsi que diverses animations ludiques (roulette thématique, lancer de dé, etc.).

## Fonctionnalités

- **Interface de Quiz Interactive**  
  Affichage dynamique des questions et des réponses avec des animations engageantes.
- **Gestion des Scores en Temps Réel**  
  Mise à jour automatique et synchronisée des scores via Flask-SocketIO.
- **Répartition Automatique des Joueurs**  
  Affectation aléatoire et équilibrée des joueurs aux équipes.
- **Compte à Rebours Global**  
  Timer interactif pour rythmer le déroulement des épreuves.
- **Roulette Thématique et Lancer de Dé**  
  Sélection aléatoire d'un thème et simulation d'un lancer de dé animé.
- **Panneau d’Administration Sécurisé**  
  Interface dédiée pour gérer équipes, scores, quiz et autres paramètres (protégée par mot de passe).

## Prérequis Techniques

- **Python** : Version 3.6 ou supérieure
- **pip** : Gestionnaire de paquets Python
- **Modules Python** :
  - Flask
  - Flask-SocketIO
  - python-socketio
  - eventlet

> **Astuce** : Utilisez un environnement virtuel pour isoler les dépendances du projet.

## Installation

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/votre-utilisateur/pandora-show.git
   cd pandora-show

2. **Créer et activer un environnement virtuel (optionnel mais recommandé) :**
   ```bash
   python -m venv env
   source env/bin/activate      # Sur Windows : env\Scripts\activate

3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt


## Structure du Projet
La structure du projet est organisée comme suit :

   ```bash
   pandora-show/
├── main.py                  # Point d'entrée de l'application Flask
├── questions.json           # Fichier JSON contenant les questions et réponses du quiz
├── requirements.txt         # Liste des dépendances Python
├── README.md                # Documentation du projet (ce fichier)
├── templates/               # Fichiers HTML pour les vues (layout, index, admin, login)
│   ├── layout.html
│   ├── index.html
│   ├── admin.html
│   └── login.html
└── static/                  # Fichiers statiques (CSS, JavaScript)
    ├── style.css
    └── script.js
```
## Utilisation

1. **Lancer l'application en local :**
   ```bash
   python main.py

L'application démarre par défaut sur le port 5000.
Accédez via : http://0.0.0.0:5000 ou http://localhost:5000.

2. **Accès aux Interfaces :**
   **Interface Joueur :**
  - Rendez-vous sur la page d'accueil, entrez votre pseudo et participez au quiz interactif.
   **Interface Administrateur :**
  - Accédez à /admin (ex. : http://localhost:5000/admin) et connectez-vous avec le mot de passe par défaut 123456 pour gérer le jeu.

## Déploiement
Pandora Show peut être déployé sur plusieurs plateformes compatibles avec Flask, telles que :

  - Heroku
  - AWS (Elastic Beanstalk, EC2)
  - CodeSandbox
  - Docker

**Pour déployer :**
  - Configurez les variables d'environnement nécessaires (ex. : SECRET_KEY).
  - Exposez le port utilisé (par défaut 5000).
  - Assurez-vous que la structure du projet est respectée (dossiers templates et static).

## Déploiement
   **Débogage :**
  - Lancez l'application en mode debug (python main.py) et consultez les logs pour suivre les erreurs éventuelles.
    
   **Tests Unitaires :**
  - Vous pouvez ajouter des tests unitaires à l'aide de frameworks comme pytest pour valider la logique de l'application et ses fonctions utilitaires.

## Contribution
Les contributions sont les bienvenues !
Pour contribuer :

   **Forkez le dépôt.**
  - Créez une branche dédiée à votre fonctionnalité ou correction :
Créez une branche dédiée à votre fonctionnalité ou correction :
   ```bash
   git checkout -b feature/nom-de-la-feature
   ```

  - Commitez vos modifications.
  - Soumettez une Pull Request avec une description détaillée de vos changements.

## Licence
Ce projet est distribué sous licence MIT.

## Auteur
Neorak


Pandora Show offre une solution complète pour organiser des sessions de quiz ludiques et interactives. Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur GitHub.



