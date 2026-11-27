"""Le Coin Lecture : site de gestion de bibliothèque (Flask + SQLite)."""
import sqlite3
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

BASE = Path(__file__).parent
DB = BASE / "bibliotheque.db"

app = Flask(__name__)
app.secret_key = "coin-lecture-secret"


# ---------------------------------------------------------------- utilitaires
def norm(s):
    """minuscules + sans accents (pour la recherche)."""
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def db():
    if "db" not in g:
        if not DB.exists():
            raise RuntimeError("Base introuvable : lancez d'abord  python init_db.py")
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.create_function("norm", 1, norm)
    return g.db


@app.teardown_appcontext
def fermer(_):
    c = g.pop("db", None)
    if c:
        c.close()


def q(sql, params=()):
    return db().execute(sql, params).fetchall()


def q1(sql, params=()):
    return db().execute(sql, params).fetchone()


def ecrire(sql, params=(), succes=None):
    """Exécute une écriture ; affiche un message clair si une règle est violée."""
    try:
        db().execute(sql, params)
        db().commit()
        if succes:
            flash(succes, "ok")
        return True
    except sqlite3.IntegrityError as e:
        db().rollback()
        m = str(e)
        if "UNIQUE" in m:
            m = "Cette valeur existe déjà (doublon interdit)."
        elif "FOREIGN KEY" in m:
            m = "Opération impossible : des données sont liées à cet élément (ou référence invalide)."
        elif "CHECK" in m:
            m = "Valeur invalide : vérifiez les dates et les champs saisis."
        elif "NOT NULL" in m:
            m = "Un champ obligatoire est vide."
        flash(m, "err")
        return False


def aujourdhui():
    return date.today().isoformat()


@app.template_filter("fr")
def fr_date(v):
    if not v:
        return "—"
    return datetime.strptime(v[:10], "%Y-%m-%d").strftime("%d/%m/%Y")


@app.context_processor
def globaux():
    return {"today": aujourdhui(), "nb_retards": q1(SQL_RETARD_COUNT, (aujourdhui(),))[0]}


SQL_RETARD_COUNT = "SELECT COUNT(*) FROM v_emprunts_actifs WHERE date_retour_prevue < ?"

SQL_CATALOGUE = """
SELECT l.isbn, l.titre, l.annee_publication, c.libelle, e.nom_editeur,
       (SELECT group_concat(a.prenom || ' ' || a.nom, ', ')
          FROM ecrire w JOIN auteur a ON a.id_auteur = w.id_auteur WHERE w.isbn = l.isbn) AS auteurs,
       (SELECT COUNT(*) FROM exemplaire x WHERE x.isbn = l.isbn) AS nb_ex,
       (SELECT COUNT(*) FROM v_exemplaires_dispo d WHERE d.isbn = l.isbn) AS nb_dispo
FROM livre l
JOIN categorie c ON c.id_categorie = l.id_categorie
JOIN editeur  e ON e.id_editeur  = l.id_editeur
"""


def val(nom):
    return (request.form.get(nom) or "").strip()


# ---------------------------------------------------------------- accueil
@app.route("/")
def accueil():
    t = aujourdhui()
    stats = {
        "livres": q1("SELECT COUNT(*) FROM livre")[0],
        "exemplaires": q1("SELECT COUNT(*) FROM exemplaire")[0],
        "dispo": q1("SELECT COUNT(*) FROM v_exemplaires_dispo")[0],
        "adherents": q1("SELECT COUNT(*) FROM adherent")[0],
        "cours": q1("SELECT COUNT(*) FROM v_emprunts_actifs")[0],
        "retards": q1(SQL_RETARD_COUNT, (t,))[0],
        "attente": q1("SELECT COUNT(*) FROM reservation WHERE statut='en attente'")[0],
    }
    retards = q(SQL_RETARDS + " LIMIT 5", (t, t))
    derniers = q("""SELECT m.*, a.prenom, a.nom, l.titre FROM emprunt m
                    JOIN adherent a ON a.num_adherent = m.num_adherent
                    JOIN exemplaire x ON x.code_exemplaire = m.code_exemplaire
                    JOIN livre l ON l.isbn = x.isbn
                    ORDER BY m.date_emprunt DESC, m.id_emprunt DESC LIMIT 5""")
    return render_template("accueil.html", s=stats, retards=retards, derniers=derniers)


# ---------------------------------------------------------------- catalogue (Q1, Q2)
@app.route("/catalogue")
def catalogue():
    terme = norm(request.args.get("q", "").strip())
    cat = request.args.get("cat", "")
    dispo = request.args.get("dispo", "")
    sql = SQL_CATALOGUE + " WHERE 1=1 "
    p = []
    if terme:
        sql += """AND (norm(l.titre) LIKE ? OR l.isbn LIKE ? OR EXISTS (
                    SELECT 1 FROM ecrire w JOIN auteur a ON a.id_auteur = w.id_auteur
                    WHERE w.isbn = l.isbn AND (norm(a.nom) LIKE ? OR norm(a.prenom) LIKE ?)))"""
        p += ["%" + terme + "%"] * 4
    if cat:
        sql += "AND l.id_categorie = ? "
        p.append(cat)
    sql += "ORDER BY l.titre"
    livres = q(sql, p)
    if dispo == "1":
        livres = [l for l in livres if l["nb_dispo"] > 0]
    return render_template("catalogue.html", livres=livres, cats=q("SELECT * FROM categorie ORDER BY libelle"),
                           terme=request.args.get("q", ""), cat=cat, dispo=dispo)


# ---------------------------------------------------------------- livres & exemplaires
@app.route("/livres", methods=["GET", "POST"])
def livres():
    if request.method == "POST":
        if ecrire("INSERT INTO livre (isbn, titre, annee_publication, id_categorie, id_editeur) VALUES (?,?,?,?,?)",
                  (val("isbn"), val("titre"), val("annee") or None, val("id_categorie"), val("id_editeur")),
                  "Livre ajouté. Ajoutez maintenant ses auteurs et ses exemplaires."):
            return redirect(url_for("livre", isbn=val("isbn")))
    return render_template("livres.html", livres=q(SQL_CATALOGUE + " ORDER BY l.titre"),
                           cats=q("SELECT * FROM categorie ORDER BY libelle"),
                           eds=q("SELECT * FROM editeur ORDER BY nom_editeur"))


@app.route("/livres/<isbn>")
def livre(isbn):
    l = q1(SQL_CATALOGUE + " WHERE l.isbn = ?", (isbn,))
    if not l:
        abort(404)
    base = q1("SELECT * FROM livre WHERE isbn = ?", (isbn,))
    exemplaires = q("""SELECT x.*, (SELECT a.prenom || ' ' || a.nom FROM v_emprunts_actifs m
                          JOIN adherent a ON a.num_adherent = m.num_adherent
                          WHERE m.code_exemplaire = x.code_exemplaire) AS emprunte_par,
                          EXISTS (SELECT 1 FROM v_exemplaires_dispo d WHERE d.code_exemplaire = x.code_exemplaire) AS libre
                       FROM exemplaire x WHERE x.isbn = ? ORDER BY x.code_exemplaire""", (isbn,))
    return render_template("livre.html", l=l, b=base, exemplaires=exemplaires,
                           auteurs=q("""SELECT a.* FROM ecrire w JOIN auteur a ON a.id_auteur = w.id_auteur
                                        WHERE w.isbn = ? ORDER BY a.nom""", (isbn,)),
                           autres=q("""SELECT * FROM auteur WHERE id_auteur NOT IN
                                       (SELECT id_auteur FROM ecrire WHERE isbn = ?) ORDER BY nom""", (isbn,)),
                           attente=q("""SELECT r.*, a.prenom, a.nom FROM reservation r
                                        JOIN adherent a ON a.num_adherent = r.num_adherent
                                        WHERE r.isbn = ? AND r.statut = 'en attente' ORDER BY r.date_demande""", (isbn,)),
                           cats=q("SELECT * FROM categorie ORDER BY libelle"),
                           eds=q("SELECT * FROM editeur ORDER BY nom_editeur"))


@app.post("/livres/<isbn>/modifier")
def livre_modifier(isbn):
    ecrire("UPDATE livre SET titre=?, annee_publication=?, id_categorie=?, id_editeur=? WHERE isbn=?",
           (val("titre"), val("annee") or None, val("id_categorie"), val("id_editeur"), isbn), "Livre mis à jour.")
    return redirect(url_for("livre", isbn=isbn))


@app.post("/livres/<isbn>/supprimer")
def livre_supprimer(isbn):
    if ecrire("DELETE FROM livre WHERE isbn=?", (isbn,), "Livre supprimé."):
        return redirect(url_for("livres"))
    return redirect(url_for("livre", isbn=isbn))


@app.post("/livres/<isbn>/auteurs")
def livre_auteur_ajouter(isbn):
    if val("id_auteur"):
        ecrire("INSERT INTO ecrire (isbn, id_auteur) VALUES (?,?)", (isbn, val("id_auteur")), "Auteur ajouté au livre.")
    return redirect(url_for("livre", isbn=isbn))


@app.post("/livres/<isbn>/auteurs/<int:id_auteur>/retirer")
def livre_auteur_retirer(isbn, id_auteur):
    ecrire("DELETE FROM ecrire WHERE isbn=? AND id_auteur=?", (isbn, id_auteur), "Auteur retiré du livre.")
    return redirect(url_for("livre", isbn=isbn))


@app.post("/livres/<isbn>/exemplaires")
def exemplaire_ajouter(isbn):
    ecrire("""INSERT INTO exemplaire (code_exemplaire, date_acquisition, etat_physique, indisponible, isbn)
              VALUES (?,?,?,?,?)""",
           (val("code"), val("date_acquisition") or aujourdhui(), val("etat"),
            1 if request.form.get("indisponible") else 0, isbn), "Exemplaire ajouté.")
    return redirect(url_for("livre", isbn=isbn))


@app.post("/exemplaires/<code>/modifier")
def exemplaire_modifier(code):
    x = q1("SELECT isbn FROM exemplaire WHERE code_exemplaire=?", (code,))
    if not x:
        abort(404)
    ecrire("UPDATE exemplaire SET etat_physique=?, indisponible=? WHERE code_exemplaire=?",
           (val("etat"), 1 if request.form.get("indisponible") else 0, code), "Exemplaire %s mis à jour." % code)
    return redirect(url_for("livre", isbn=x["isbn"]))


@app.post("/exemplaires/<code>/supprimer")
def exemplaire_supprimer(code):
    x = q1("SELECT isbn FROM exemplaire WHERE code_exemplaire=?", (code,))
    if not x:
        abort(404)
    ecrire("DELETE FROM exemplaire WHERE code_exemplaire=?", (code,), "Exemplaire supprimé.")
    return redirect(url_for("livre", isbn=x["isbn"]))


# ---------------------------------------------------------------- adhérents (Q3)
@app.route("/adherents", methods=["GET", "POST"])
def adherents():
    if request.method == "POST":
        if ecrire("""INSERT INTO adherent (nom, prenom, telephone, email, date_inscription, type_adherent)
                     VALUES (?,?,?,?,?,?)""",
                  (val("nom"), val("prenom"), val("telephone") or None, val("email") or None,
                   val("date_inscription") or aujourdhui(), val("type_adherent")), "Adhérent inscrit. Bienvenue !"):
            return redirect(url_for("adherents"))
    terme = norm(request.args.get("q", "").strip())
    rows = q("""SELECT a.*, (SELECT COUNT(*) FROM v_emprunts_actifs m WHERE m.num_adherent = a.num_adherent) AS nb_cours
                FROM adherent a
                WHERE ? = '' OR norm(a.nom) LIKE ? OR norm(a.prenom) LIKE ? OR norm(a.email) LIKE ?
                ORDER BY a.nom, a.prenom""", (terme, *["%" + terme + "%"] * 3))
    return render_template("adherents.html", adherents=rows, terme=request.args.get("q", ""))


@app.route("/adherents/<int:num>")
def adherent(num):
    a = q1("SELECT * FROM adherent WHERE num_adherent=?", (num,))
    if not a:
        abort(404)
    base = """SELECT m.*, l.titre, l.isbn FROM emprunt m
              JOIN exemplaire x ON x.code_exemplaire = m.code_exemplaire
              JOIN livre l ON l.isbn = x.isbn WHERE m.num_adherent = ? """
    return render_template("adherent.html", a=a,
                           cours=q(base + "AND m.date_retour_effective IS NULL ORDER BY m.date_retour_prevue", (num,)),
                           histo=q(base + "AND m.date_retour_effective IS NOT NULL ORDER BY m.date_emprunt DESC", (num,)),
                           resa=q("""SELECT r.*, l.titre FROM reservation r JOIN livre l ON l.isbn = r.isbn
                                     WHERE r.num_adherent = ? ORDER BY r.date_demande DESC""", (num,)))


@app.post("/adherents/<int:num>/modifier")
def adherent_modifier(num):
    ecrire("""UPDATE adherent SET nom=?, prenom=?, telephone=?, email=?, date_inscription=?, type_adherent=?
              WHERE num_adherent=?""",
           (val("nom"), val("prenom"), val("telephone") or None, val("email") or None,
            val("date_inscription"), val("type_adherent"), num), "Fiche mise à jour.")
    return redirect(url_for("adherent", num=num))


@app.post("/adherents/<int:num>/supprimer")
def adherent_supprimer(num):
    if ecrire("DELETE FROM adherent WHERE num_adherent=?", (num,), "Adhérent supprimé."):
        return redirect(url_for("adherents"))
    return redirect(url_for("adherent", num=num))


# ---------------------------------------------------------------- emprunts & retours
@app.route("/emprunts", methods=["GET", "POST"])
def emprunts():
    if request.method == "POST":
        ecrire("""INSERT INTO emprunt (date_emprunt, date_retour_prevue, num_adherent, code_exemplaire)
                  VALUES (?,?,?,?)""",
               (val("date_emprunt"), val("date_retour_prevue"), val("num_adherent"), val("code_exemplaire")),
               "Emprunt enregistré. Bonne lecture !")
        return redirect(url_for("emprunts"))
    f = request.args.get("f", "cours")
    t = aujourdhui()
    sql = """SELECT m.*, a.prenom, a.nom, l.titre, l.isbn FROM emprunt m
             JOIN adherent a ON a.num_adherent = m.num_adherent
             JOIN exemplaire x ON x.code_exemplaire = m.code_exemplaire
             JOIN livre l ON l.isbn = x.isbn """
    p = ()
    if f == "cours":
        sql += "WHERE m.date_retour_effective IS NULL "
    elif f == "retard":
        sql += "WHERE m.date_retour_effective IS NULL AND m.date_retour_prevue < ? "
        p = (t,)
    elif f == "rendus":
        sql += "WHERE m.date_retour_effective IS NOT NULL "
    sql += "ORDER BY m.date_emprunt DESC, m.id_emprunt DESC"
    return render_template("emprunts.html", rows=q(sql, p), f=f,
                           adherents=q("SELECT num_adherent, prenom, nom FROM adherent ORDER BY nom"),
                           dispo=q("""SELECT d.code_exemplaire, d.etat_physique, l.titre FROM v_exemplaires_dispo d
                                      JOIN livre l ON l.isbn = d.isbn ORDER BY l.titre, d.code_exemplaire"""),
                           retour_defaut=(date.today() + timedelta(days=14)).isoformat())


@app.post("/emprunts/<int:id_emprunt>/retour")
def emprunt_retour(id_emprunt):
    t = aujourdhui()
    m = q1("""SELECT x.isbn FROM emprunt m JOIN exemplaire x ON x.code_exemplaire = m.code_exemplaire
              WHERE m.id_emprunt = ?""", (id_emprunt,))
    if ecrire("UPDATE emprunt SET date_retour_effective=? WHERE id_emprunt=? AND date_retour_effective IS NULL",
              (t, id_emprunt), "Retour enregistré. Merci !") and m:
        n = q1("SELECT COUNT(*) FROM reservation WHERE isbn=? AND statut='en attente'", (m["isbn"],))[0]
        if n:
            flash("Ce livre a %d réservation(s) en attente : pensez à prévenir le premier adhérent." % n, "info")
    return redirect(request.referrer or url_for("emprunts"))


# ---------------------------------------------------------------- réservations (Q5, Q7)
@app.route("/reservations", methods=["GET", "POST"])
def reservations():
    if request.method == "POST":
        ecrire("INSERT INTO reservation (date_demande, statut, num_adherent, isbn) VALUES (?, 'en attente', ?, ?)",
               (aujourdhui(), val("num_adherent"), val("isbn")), "Réservation enregistrée.")
        return redirect(url_for("reservations"))
    f = request.args.get("f", "en attente")
    isbn = request.args.get("isbn", "")
    sql = """SELECT r.*, a.prenom, a.nom, l.titre FROM reservation r
             JOIN adherent a ON a.num_adherent = r.num_adherent JOIN livre l ON l.isbn = r.isbn WHERE 1=1 """
    p = []
    if f != "toutes":
        sql += "AND r.statut = ? "
        p.append(f)
    if isbn:
        sql += "AND r.isbn = ? "
        p.append(isbn)
    sql += "ORDER BY r.date_demande"
    return render_template("reservations.html", rows=q(sql, p), f=f, isbn=isbn,
                           livres_tous=q("SELECT isbn, titre FROM livre ORDER BY titre"),
                           sans_dispo=q("""SELECT isbn, titre FROM livre
                                           WHERE isbn NOT IN (SELECT isbn FROM v_exemplaires_dispo) ORDER BY titre"""),
                           adherents=q("SELECT num_adherent, prenom, nom FROM adherent ORDER BY nom"))


@app.post("/reservations/<int:rid>/<action>")
def reservation_statut(rid, action):
    nouveau = {"satisfaire": "satisfaite", "annuler": "annulée"}.get(action)
    if not nouveau:
        abort(404)
    ecrire("UPDATE reservation SET statut=? WHERE id_reservation=?", (nouveau, rid), "Réservation %s." % nouveau)
    return redirect(request.referrer or url_for("reservations"))


# ---------------------------------------------------------------- retards (Q4) & statistiques (Q6)
SQL_RETARDS = """SELECT a.num_adherent, a.nom, a.prenom, a.telephone, a.email, l.titre, m.code_exemplaire,
                        m.date_retour_prevue, CAST(julianday(?) - julianday(m.date_retour_prevue) AS INTEGER) AS jours
                 FROM v_emprunts_actifs m
                 JOIN adherent a ON a.num_adherent = m.num_adherent
                 JOIN exemplaire x ON x.code_exemplaire = m.code_exemplaire
                 JOIN livre l ON l.isbn = x.isbn
                 WHERE m.date_retour_prevue < ?
                 ORDER BY jours DESC"""


@app.route("/retards")
def retards():
    t = aujourdhui()
    return render_template("retards.html", rows=q(SQL_RETARDS, (t, t)))


@app.route("/statistiques")
def statistiques():
    rows = q("""SELECT l.isbn, l.titre, COUNT(m.id_emprunt) AS nb
                FROM livre l LEFT JOIN exemplaire x ON x.isbn = l.isbn
                LEFT JOIN emprunt m ON m.code_exemplaire = x.code_exemplaire
                GROUP BY l.isbn, l.titre ORDER BY nb DESC, l.titre""")
    sans = q("""SELECT isbn, titre FROM livre WHERE isbn NOT IN (SELECT isbn FROM v_exemplaires_dispo) ORDER BY titre""")
    return render_template("stats.html", rows=rows, maxi=max([r["nb"] for r in rows] + [1]), sans=sans)


# ---------------------------------------------------------------- référentiels (auteurs, éditeurs, catégories)
@app.route("/referentiels", methods=["GET", "POST"])
def referentiels():
    if request.method == "POST":
        quoi = request.form.get("quoi")
        if quoi == "auteur":
            ecrire("INSERT INTO auteur (nom, prenom) VALUES (?,?)", (val("nom"), val("prenom")), "Auteur ajouté.")
        elif quoi == "editeur":
            ecrire("INSERT INTO editeur (nom_editeur) VALUES (?)", (val("nom"),), "Éditeur ajouté.")
        elif quoi == "categorie":
            ecrire("INSERT INTO categorie (libelle) VALUES (?)", (val("nom"),), "Catégorie ajoutée.")
        return redirect(url_for("referentiels"))
    return render_template("referentiels.html",
                           auteurs=q("""SELECT a.*, (SELECT COUNT(*) FROM ecrire w WHERE w.id_auteur=a.id_auteur) AS nb
                                        FROM auteur a ORDER BY a.nom"""),
                           editeurs=q("""SELECT e.*, (SELECT COUNT(*) FROM livre l WHERE l.id_editeur=e.id_editeur) AS nb
                                         FROM editeur e ORDER BY e.nom_editeur"""),
                           cats=q("""SELECT c.*, (SELECT COUNT(*) FROM livre l WHERE l.id_categorie=c.id_categorie) AS nb
                                     FROM categorie c ORDER BY c.libelle"""))


@app.errorhandler(404)
def introuvable(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
