"""Relit le fichier Access (.accdb) et régénère donnees.sql.
Usage :  python outils/generer_donnees.py chemin/vers/Bibliotheque.accdb
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from accdb import Db

RENOMMER = {'num-adherent': 'num_adherent', 'typr_adherent': 'type_adherent', 'status': 'statut'}
ORDRE = ['CATEGORIE', 'EDITEUR', 'AUTEUR', 'LIVRE', 'ECRIRE', 'EXEMPLAIRE', 'ADHERENT', 'EMPRUNT', 'RESERVATION']


def sql(v, col):
    if v is None: return 'NULL'
    if isinstance(v, bool): return '1' if v else '0'
    if isinstance(v, (int, float)): return str(v) if col != 'telephone' else "'%s'" % v
    v = str(v).strip()
    if col.startswith('date_'): v = v[:10]
    return "'" + v.replace("'", "''") + "'"


def main(chemin, sortie):
    db = Db(chemin)
    out = ['-- Données importées depuis le fichier Access\n']
    for t in ORDRE:
        cols, rows = db.read_table(t)
        noms = [RENOMMER.get(c['name'], c['name']).lower() for c in cols]
        for r in rows:
            vals = [sql(r[c['name']], n) for c, n in zip(cols, noms)]
            out.append('INSERT INTO %s (%s) VALUES (%s);' % (t.lower(), ', '.join(noms), ', '.join(vals)))
        out.append('')
    pathlib.Path(sortie).write_text('\n'.join(out), encoding='utf-8')
    print('OK ->', sortie)


if __name__ == '__main__':
    main(sys.argv[1], pathlib.Path(__file__).parent.parent / 'donnees.sql')
