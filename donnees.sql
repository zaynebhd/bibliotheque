-- Données importées depuis le fichier Access

INSERT INTO categorie (id_categorie, libelle) VALUES (1, 'Informatique');
INSERT INTO categorie (id_categorie, libelle) VALUES (2, 'Mathématiques');
INSERT INTO categorie (id_categorie, libelle) VALUES (3, 'Littérature');
INSERT INTO categorie (id_categorie, libelle) VALUES (4, 'Sciences');

INSERT INTO editeur (id_editeur, nom_editeur) VALUES (1, 'Eyrolles');
INSERT INTO editeur (id_editeur, nom_editeur) VALUES (2, 'Dunod');
INSERT INTO editeur (id_editeur, nom_editeur) VALUES (3, 'Gallimard');
INSERT INTO editeur (id_editeur, nom_editeur) VALUES (4, 'Pearson');
INSERT INTO editeur (id_editeur, nom_editeur) VALUES (5, 'Springer');

INSERT INTO auteur (id_auteur, nom, prenom) VALUES (1, 'Date', 'Chris');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (2, 'Silberschatz', 'Abraham');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (3, 'Korth', 'Henry');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (4, 'Sudarshan', 'S.');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (5, 'Knuth', 'Donald');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (6, 'Camus', 'Albert');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (7, 'Hugo', 'Victor');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (8, 'Hawking', 'Stephen');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (9, 'Rudin', 'Walter');
INSERT INTO auteur (id_auteur, nom, prenom) VALUES (10, 'Tanenbaum', 'Andrew');

INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES ('978000011', 'Systèmes de bases de données', 2019, 2, 4);
INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES ('978000028', 'Introduction aux bases de données', 2004, 1, 2);
INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES ('978000042', 'Réseaux informatiques', 2011, 1, 4);
INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES ('978000059', 'Principes d''analyse mathématique', 1976, 2, 4);
INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES ('978000066', 'L''Étranger', 1942, 3, 3);
INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES ('978000073', 'Les Misérables', 1862, 3, 3);
INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES ('978000080', 'Une brève histoire du temps', 1988, 4, 1);
INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES ('978000035', 'The Art of Computer Programming', 1997, 1, 1);

INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000011', 2);
INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000011', 3);
INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000011', 4);
INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000028', 1);
INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000042', 10);
INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000059', 9);
INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000066', 6);
INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000073', 7);
INSERT INTO ecrire (isbn, id_auteur) VALUES ('978000080', 8);

INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E001', '2022-09-01', 'bon', 0, '978000011');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E002', '2022-09-01', 'usé', 0, '978000011');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E003', '2021-03-15', 'bon', 0, '978000028');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E004', '2023-02-20', 'bon', 0, '978000042');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E005', '2019-05-05', 'usé', 0, '978000059');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E006', '2019-05-05', 'bon', 0, '978000066');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E007', '2018-10-01', 'endommagé', 1, '978000066');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E008', '2020-11-30', 'bon', 0, '978000073');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E009', '2022-04-12', 'bon', 0, '978000080');
INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn) VALUES ('E010', '2020-01-10', 'bon', 0, '978000035');

INSERT INTO adherent (num_adherent, nom, prenom, telephone, email, date_inscription, type_adherent) VALUES (1, 'Ben Salah', 'Mohamed', '52147855', 'bensalahmed@gmail.com', '2025-09-15', 'étudiant');
INSERT INTO adherent (num_adherent, nom, prenom, telephone, email, date_inscription, type_adherent) VALUES (2, 'Trabelsi', 'Amira', '98251478', 'TrabelsiAmira11@gmail.com', '2025-09-16', 'étudiant');
INSERT INTO adherent (num_adherent, nom, prenom, telephone, email, date_inscription, type_adherent) VALUES (3, 'Jlassi', 'Karim', '22587412', 'karimjlassi2005@gmail.com', '2024-02-01', 'enseignant');
INSERT INTO adherent (num_adherent, nom, prenom, telephone, email, date_inscription, type_adherent) VALUES (4, 'Gharbi', 'Sarra', '50147852', 'sarragharbi@gmail.com', '2026-01-10', 'étudiant');
INSERT INTO adherent (num_adherent, nom, prenom, telephone, email, date_inscription, type_adherent) VALUES (5, 'Mejri', 'Yassine', '97412036', 'mejriyassine14@gmail.com', '2026-02-20', 'étudiant');
INSERT INTO adherent (num_adherent, nom, prenom, telephone, email, date_inscription, type_adherent) VALUES (6, 'Bouzid', 'Lina', '50639854', 'LinaBouzid7@gmail.com', '2026-03-05', 'autre');

INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (1, '2026-10-01', '2026-10-15', '2026-11-25', 1, 'E001');
INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (2, '2026-10-05', '2026-10-19', '2026-10-18', 2, 'E003');
INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (3, '2026-10-20', '2026-11-03', NULL, 3, 'E010');
INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (4, '2026-10-25', '2026-11-08', NULL, 3, 'E006');
INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (5, '2026-11-10', '2026-11-24', NULL, 3, 'E006');
INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (6, '2026-11-12', '2026-11-26', NULL, 1, 'E008');
INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (7, '2026-11-15', '2026-11-29', '2026-11-24', 1, 'E001');
INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (8, '2026-09-01', '2026-09-15', '2026-09-14', 5, 'E004');
INSERT INTO emprunt (id_emprunt, date_emprunt, date_retour_prevue, date_retour_effective, num_adherent, code_exemplaire) VALUES (9, '2026-11-10', '2026-11-24', NULL, 6, 'E002');

INSERT INTO reservation (id_reservation, date_demande, statut, num_adherent, isbn) VALUES (1, '2026-11-13', 'en attente', 2, '978000035');
INSERT INTO reservation (id_reservation, date_demande, statut, num_adherent, isbn) VALUES (2, '2026-11-15', 'en attente', 5, '978000035');
INSERT INTO reservation (id_reservation, date_demande, statut, num_adherent, isbn) VALUES (3, '2026-11-16', 'en attente', 6, '978000059');
INSERT INTO reservation (id_reservation, date_demande, statut, num_adherent, isbn) VALUES (4, '2026-10-18', 'satisfaite', 4, '978000073');
INSERT INTO reservation (id_reservation, date_demande, statut, num_adherent, isbn) VALUES (5, '2026-11-06', 'annulée', 2, '978000080');
