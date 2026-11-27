-- Règles de gestion appliquées par la base elle-même (déclencheurs)
-- Elles sont créées APRÈS l'import des données de test.

CREATE TRIGGER trg_emprunt_regles BEFORE INSERT ON emprunt
BEGIN
    SELECT RAISE(ABORT, 'Cet exemplaire est déclaré indisponible (endommagé) : il ne peut pas être emprunté.')
    WHERE (SELECT indisponible FROM exemplaire WHERE code_exemplaire = NEW.code_exemplaire) = 1;

    SELECT RAISE(ABORT, 'Cet exemplaire est déjà emprunté : un exemplaire ne peut avoir qu''un seul emprunt actif.')
    WHERE EXISTS (SELECT 1 FROM v_emprunts_actifs WHERE code_exemplaire = NEW.code_exemplaire);

    SELECT RAISE(ABORT, 'Limite atteinte : un adhérent ne peut pas avoir plus de 3 emprunts simultanés.')
    WHERE (SELECT COUNT(*) FROM v_emprunts_actifs WHERE num_adherent = NEW.num_adherent) >= 3;
END;

CREATE TRIGGER trg_reservation_regles BEFORE INSERT ON reservation
BEGIN
    SELECT RAISE(ABORT, 'Un exemplaire de ce livre est disponible : on réserve seulement quand aucun exemplaire n''est libre.')
    WHERE EXISTS (SELECT 1 FROM v_exemplaires_dispo WHERE isbn = NEW.isbn);

    SELECT RAISE(ABORT, 'Cet adhérent a déjà une réservation en attente sur ce livre.')
    WHERE NEW.statut = 'en attente'
      AND EXISTS (SELECT 1 FROM reservation
                  WHERE num_adherent = NEW.num_adherent AND isbn = NEW.isbn AND statut = 'en attente');
END;
