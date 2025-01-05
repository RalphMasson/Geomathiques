# Géomathiques : un outil géométrique transparent à déplacer 

<p align="center">
  <img src="https://github.com/RalphMasson/Rapporteur/blob/main/Geomathiques_Demo.gif" width="400" />
</p>


## Description

**Géomathiques** est une application interactive permettant de manipuler des outils géométriques numériques tels qu’un rapporteur, une équerre et une règle. Conçue pour être utilisée dans des contextes éducatifs ou personnels, cette application fournit des outils précis, transparents et personnalisables pour explorer la géométrie de manière visuelle.

## Fonctionnalités

### Outils disponibles
- **Rapporteur** : Rotation, zoom, déplacement.
- **Équerre** : Manipulation indépendante ou combinée avec une règle.
- **Règle** : Déplacement, zoom, et rotation. 
- **Mode combiné Équerre + Règle** : Affiche les deux outils en simultané avec ajustement dynamique.

### Fonctions principales
- **Zoom** : Agrandissez ou réduisez les outils avec les boutons ou les raccourcis clavier.
- **Rotation** : Effectuez des rotations précises (1°, 90°, 180°).
- **Dessin** : Activez un mode dessin pour tracer directement sur les outils affichés.
- **Transparence** : Rendre les zones blanches des outils semi-transparentes.
- **Déplacement** : Manipulez les outils individuellement dans la fenêtre.
- **Historique des dessins** : Annulez des actions avec `Ctrl+Z` ou réinitialisez le canevas.

### Raccourcis clavier
- **← / →** : Rotation (sens antihoraire / horaire).
- **+ / -** : Zoom avant / arrière.
- **Entrée** : Rotation de 180°.
- **R** : Rotation de 90°.
- **D** : Activer / désactiver le mode dessin.
- **Espace** : Activer le mode clic à travers.
- **Échap** : Quitter l'application.
- **Ctrl+Z** : Annuler la dernière action de dessin.

### Interfaces utilisateur
- **Popup d'informations** : Une fenêtre affiche les raccourcis clavier pour une prise en main rapide.
- **Boutons stylisés** : Accès rapide aux fonctions courantes.
- **Fenêtre flottante** : Permet de réinitialiser la transparence en mode clic à travers.

## Installation

1. Assurez-vous d’avoir Python 3.8+ installé sur votre système.
2. Installez les dépendances requises :

```bash
pip install PyQt5 Pillow
```

3. Clonez ce dépôt ou téléchargez les fichiers nécessaires.

```bash
git clone https://github.com/votre-repo/geomathiques.git
cd geomathiques
```

4. Placez les images des outils (rapporteur, équerre, règle) dans le même répertoire que le script ou modifiez les chemins dans le code.

## Utilisation

1. Lancez l'application :

```bash
python geomathiques.py
```

2. Utilisez les boutons ou les raccourcis pour interagir avec les outils.
3. Passez en mode dessin pour annoter directement sur l’écran.

## Structure du projet

```
geomathiques/
│
├── geomathiques.py       # Code principal de l'application.
├── rapporteur.png        # Image du rapporteur.
├── equerre.png           # Image de l'équerre.
├── regle.png             # Image de la règle.
└── README.md             # Documentation du projet.
```

## Contributions

Les contributions sont les bienvenues ! Si vous souhaitez ajouter de nouvelles fonctionnalités ou corriger des bugs, n’hésitez pas à :

1. **Forker** ce dépôt.
2. Créer une nouvelle branche :

```bash
git checkout -b nouvelle-fonctionnalite
```

3. Soumettre une pull request.

## Auteur

Créé par **Ralph Masson**.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus d’informations.

## Remerciements

Merci d’utiliser Géomathiques ! Si vous avez des suggestions ou des retours, contactez-moi ou ouvrez une issue sur le dépôt.

# Code #
Voici les différentes bibliothèques utilisées : 
- PyQt5 pour gérer l'interface
- PIL (pillow) pour gérer les images
- cryptography pour contourner la détection antivirus (SPOILER : il est quand-même détecté comme malveillant)

