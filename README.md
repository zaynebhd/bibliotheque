# 📚 Le Coin Lecture : site de gestion de bibliothèque

Mini-projet « Gestion d'une bibliothèque » (ISSAT Sousse). Le site est branché sur **les données de votre fichier Access** (`Bibliothèque.accdb`) : livres, auteurs, exemplaires, adhérents, emprunts, réservations.

## Lancer le site dans VS Code

Prérequis : Python 3.10 ou plus récent (https://www.python.org).

1. Ouvrez le dossier `bibliotheque` dans VS Code (Fichier → Ouvrir un dossier).
2. Ouvrez un terminal (Ctrl + `) et tapez :

```bash
python -m venv .venv
# Windows :
.venv\Scripts\activate
# Mac / Linux :
source .venv/bin/activate

pip install -r requirements.txt
python init_db.py      # crée bibliotheque.db avec vos données
python app.py          # lance le site
```

3. Ouvrez http://127.0.0.1:5000 dans votre navigateur.

Astuce : le bouton ▶ « Run and Debug » de VS Code propose « Lancer le site » et « Recréer la base de données » (touche F5).

`python init_db.py` remet la base à zéro (données de test d'origine). À ne relancer que pour repartir de zéro.

## Les pages

| Page | Correspond dans Access à |
|---|---|
| Accueil | F_Accueil |
| Catalogue | F_Catalogue, Q1_Catalogue, Q2_ExemplairesDispoLivre, Q0b_DispoTitre |
| Livres (fiche + auteurs + exemplaires) | F_Livres, F_Auteurs_sf, F_Exemplaires_sf |
| Adhérents (fiche + emprunts en cours) | F_Adherents, Q3_EmpruntsEnCours |
| Emprunts | F_Emprunts, Q_EmpruntsActifs |
| Réservations | F_Reservations, Q5_ReservationsAttente, Q7_livresSansDispo |
| Retards | Q4_EmpruntsEnretard |
| Statistiques | Q6_NbEmpruntsParLivre |

## Règles de gestion (appliquées par la base, fichier `regles.sql`)

- 3 emprunts simultanés maximum par adhérent ;
- un exemplaire n'a jamais deux emprunts actifs en même temps ;
- un exemplaire déclaré indisponible (endommagé) ne peut pas être emprunté ;
- on ne réserve un livre que si aucun exemplaire n'est libre ;
- une seule réservation « en attente » par adhérent et par livre ;
- intégrité référentielle (clés étrangères) et contraintes CHECK (états, statuts, dates).

## Les fichiers

```
app.py            le site (Flask) : routes et requêtes SQL
init_db.py        crée la base à partir des 3 fichiers .sql
schema.sql        tables, clés, contraintes, vues (modèle relationnel en 3FN)
donnees.sql       vos données de test, extraites du fichier Access
regles.sql        règles de gestion (déclencheurs)
templates/        les pages HTML (en français)
static/style.css  le thème « cosy » (crème, terracotta, vert sauge)
outils/           lecteur de .accdb : régénère donnees.sql si vous modifiez le fichier Access
```

Pour réimporter un fichier Access modifié :
`python outils/generer_donnees.py MonFichier.accdb` puis `python init_db.py`.

## Différences avec le fichier Access (volontaires)

- `typr_adherent` devient `type_adherent`, `num-adherent` devient `num_adherent` (pas de tiret) et `status` devient `statut`.
- Les tabulations parasites au début de quelques titres et noms ont été retirées.
- La requête `Q1_Catalogue` d'Access relie la catégorie à `id_editeur` ; ici la jointure utilise bien `id_categorie`.

## Mettre le projet sur GitHub

1. Créez un dépôt vide sur https://github.com/new (sans README ni .gitignore).
2. Dans le terminal de VS Code, depuis le dossier du projet :

```bash
git remote add origin https://github.com/VOTRE-NOM/NOM-DU-DEPOT.git
git branch -M main
git push -u origin main
```

Le dépôt Git est déjà initialisé avec un premier commit. Le fichier `.gitignore` exclut `.venv/`, `__pycache__/` et `bibliotheque.db` : la base se recrée avec `python init_db.py`.
