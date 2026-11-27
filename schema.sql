-- Schéma relationnel (3FN) de la bibliothèque - SQLite
PRAGMA foreign_keys = ON;

CREATE TABLE categorie (
    id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle      TEXT NOT NULL UNIQUE
);

CREATE TABLE editeur (
    id_editeur  INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_editeur TEXT NOT NULL UNIQUE
);

CREATE TABLE auteur (
    id_auteur INTEGER PRIMARY KEY AUTOINCREMENT,
    nom       TEXT NOT NULL,
    prenom    TEXT NOT NULL,
    UNIQUE (nom, prenom)
);

CREATE TABLE livre (
    isbn              TEXT PRIMARY KEY,
    titre             TEXT NOT NULL,
    annee_publication INTEGER CHECK (annee_publication BETWEEN 1000 AND 2100),
    id_categorie      INTEGER NOT NULL REFERENCES categorie (id_categorie) ON DELETE RESTRICT,
    id_editeur        INTEGER NOT NULL REFERENCES editeur (id_editeur) ON DELETE RESTRICT
);

-- Association plusieurs-à-plusieurs livre <-> auteur
CREATE TABLE ecrire (
    isbn      TEXT    NOT NULL REFERENCES livre (isbn) ON DELETE CASCADE,
    id_auteur INTEGER NOT NULL REFERENCES auteur (id_auteur) ON DELETE RESTRICT,
    PRIMARY KEY (isbn, id_auteur)
);

CREATE TABLE exemplaire (
    code_exemplaire  TEXT PRIMARY KEY,
    date_acquisition TEXT NOT NULL,
    etat_physique    TEXT NOT NULL CHECK (etat_physique IN ('bon', 'usé', 'endommagé')),
    indisponible     INTEGER NOT NULL DEFAULT 0 CHECK (indisponible IN (0, 1)),
    isbn             TEXT NOT NULL REFERENCES livre (isbn) ON DELETE RESTRICT
);

CREATE TABLE adherent (
    num_adherent     INTEGER PRIMARY KEY AUTOINCREMENT,
    nom              TEXT NOT NULL,
    prenom           TEXT NOT NULL,
    telephone        TEXT,
    email            TEXT UNIQUE,
    date_inscription TEXT NOT NULL,
    type_adherent    TEXT NOT NULL CHECK (type_adherent IN ('étudiant', 'enseignant', 'autre'))
);

CREATE TABLE emprunt (
    id_emprunt            INTEGER PRIMARY KEY AUTOINCREMENT,
    date_emprunt          TEXT NOT NULL,
    date_retour_prevue    TEXT NOT NULL,
    date_retour_effective TEXT,
    num_adherent          INTEGER NOT NULL REFERENCES adherent (num_adherent) ON DELETE RESTRICT,
    code_exemplaire       TEXT    NOT NULL REFERENCES exemplaire (code_exemplaire) ON DELETE RESTRICT,
    CHECK (date_retour_prevue >= date_emprunt),
    CHECK (date_retour_effective IS NULL OR date_retour_effective >= date_emprunt)
);

CREATE TABLE reservation (
    id_reservation INTEGER PRIMARY KEY AUTOINCREMENT,
    date_demande   TEXT NOT NULL,
    statut         TEXT NOT NULL DEFAULT 'en attente'
                   CHECK (statut IN ('en attente', 'satisfaite', 'annulée')),
    num_adherent   INTEGER NOT NULL REFERENCES adherent (num_adherent) ON DELETE RESTRICT,
    isbn           TEXT    NOT NULL REFERENCES livre (isbn) ON DELETE RESTRICT
);

-- Vues (équivalents des requêtes Access Q_EmpruntsActifs et Q0__ExemplairesDispo)
CREATE VIEW v_emprunts_actifs AS
    SELECT * FROM emprunt WHERE date_retour_effective IS NULL;

CREATE VIEW v_exemplaires_dispo AS
    SELECT e.* FROM exemplaire e
    WHERE e.indisponible = 0
      AND NOT EXISTS (SELECT 1 FROM v_emprunts_actifs m WHERE m.code_exemplaire = e.code_exemplaire);
