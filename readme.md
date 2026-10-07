# Gestion de stock pharmaceutique

Logiciel de gestion des stocks pour une usine de produits pharmaceutiques, développé en Python. L'application permet de gérer les entrées et sorties de lots, avec une logique de sortie FEFO (First Expired, First Out) et une traçabilité complète par numéro de lot.

**Application en ligne :** https://gestion-stock-pharma-hrprud35ma29mnuw6g4gpb.streamlit.app/


## Fonctionnalités

- **Tableau de bord** : vue d'ensemble du stock par produit, avec alertes en temps réel (stock bas, péremption proche, lots périmés)
- **Gestion des nouveaux produits** : création de nouveaux produits avec leur premier lot
- **Réception de lots** : entrée de nouveaux lots pour les produits existants
- **Sortie de stock** : décrémentation automatique selon la logique FEFO (le lot qui périme le plus tôt est utilisé en premier), avec blocage des lots périmés
- **Traçabilité** : recherche de l'historique complet d'un lot par sa référence
- **Historique** : consultation de toutes les entrées et de l'état courant des lots
- **Réinitialisation** : remise à zéro des données de démonstration en un clic

## Technologies utilisées

- **Python 3**
- **Streamlit** — interface utilisateur
- **SQLite** — base de données

## Structure du projet

```
├── app.py          # Interface Streamlit (pages et navigation)
├── DATABASE.py     # Logique métier et accès à la base de données
├── seed.py         # Génération du jeu de données de démonstration
└── requirements.txt
```

## Lancer le projet en local

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/polemik44/GESTION-STOCK-PHARMA.git
   cd GESTION-STOCK-PHARMA
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancer l'application :
   ```bash
   streamlit run app.py
   ```

La base de données se crée et se peuple automatiquement avec des données de démonstration au premier lancement (aucune étape manuelle nécessaire).

## Scénario de test suggéré

- Consulter le **tableau de bord** pour voir les alertes de stock bas, de péremption proche et les lots périmés
- Effectuer une **sortie de stock** sur un produit ayant plusieurs lots, pour observer la logique (First Expired First out) FEFO
- Rechercher une **référence de lot** (visible dans l'onglet Historique) dans la page Traçabilité
- Utiliser le bouton de **réinitialisation** pour revenir à l'état initial des données