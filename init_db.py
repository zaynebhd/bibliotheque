"""Crée (ou recrée) la base SQLite bibliotheque.db avec les données de test."""
import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
DB = BASE / "bibliotheque.db"

if DB.exists():
    DB.unlink()

con = sqlite3.connect(DB)
con.execute("PRAGMA foreign_keys = ON")
con.executescript((BASE / "schema.sql").read_text(encoding="utf-8"))
con.executescript((BASE / "donnees.sql").read_text(encoding="utf-8"))
con.executescript((BASE / "regles.sql").read_text(encoding="utf-8"))
con.commit()

for t in ["categorie", "editeur", "auteur", "livre", "exemplaire", "adherent", "emprunt", "reservation"]:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t:<12} {n} ligne(s)")
con.close()
print("Base créée :", DB)
