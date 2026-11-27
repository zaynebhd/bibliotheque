"""Mini lecteur de fichiers Access (Jet4/ACE) : tables + lignes. Lecture seule."""
import struct, datetime, sys

PS = 4096
T_NAMES = {1: 'bool', 2: 'byte', 3: 'int16', 4: 'int32', 5: 'money', 6: 'float', 7: 'double',
           8: 'datetime', 9: 'binary', 10: 'text', 11: 'ole', 12: 'memo', 15: 'guid', 16: 'numeric', 18: 'complex'}


def i16(b, o): return struct.unpack_from('<H', b, o)[0]
def i32(b, o): return struct.unpack_from('<I', b, o)[0]


def decode_text(raw):
    if raw[:2] == b'\xff\xfe':  # compression Unicode
        out, i, comp = [], 2, True
        buf = bytearray()
        while i < len(raw):
            if comp:
                if raw[i] == 0:
                    comp = not comp; i += 1; continue
                out.append(bytes([raw[i]]).decode('cp1252', 'replace')); i += 1
            else:
                if i + 1 < len(raw) and raw[i] == 0 and raw[i + 1] == 0:
                    comp = True; i += 2; continue
                out.append(raw[i:i + 2].decode('utf-16le', 'replace')); i += 2
        return ''.join(out)
    return raw.decode('utf-16le', 'replace')


class Db:
    def __init__(self, path):
        self.d = open(path, 'rb').read()
        self.n = len(self.d) // PS

    def page(self, i): return self.d[i * PS:(i + 1) * PS]

    def tdef(self, pg):
        data = bytearray(self.page(pg))
        nxt = i32(data, 4)
        while nxt:
            p = self.page(nxt)
            data += p[8:]
            nxt = i32(p, 4)
        b = bytes(data)
        ncols = i16(b, 45); nidx = i32(b, 47); nreal = i32(b, 51)
        nvar = i16(b, 43)
        pos = 63 + nreal * 12
        cols = []
        for k in range(ncols):
            o = pos + k * 25
            cols.append(dict(type=b[o], num=i16(b, o + 5), var_idx=i16(b, o + 7), flags=b[o + 15],
                             fixed=bool(b[o + 15] & 1), off_f=i16(b, o + 21), size=i16(b, o + 23)))
        pos += ncols * 25
        for c in cols:
            ln = i16(b, pos); pos += 2
            c['name'] = b[pos:pos + ln].decode('utf-16le'); pos += ln
        cols.sort(key=lambda c: c['num'])
        return cols

    def rows(self, tdef_pg, cols):
        out = []
        for p in range(self.n):
            pg = self.page(p)
            if pg[0] != 1 or i32(pg, 4) != tdef_pg:
                continue
            nrows = i16(pg, 12)
            for r in range(nrows):
                off = i16(pg, 14 + 2 * r)
                if off & 0x8000:  # supprimée
                    continue
                start = off & 0x1FFF
                end = PS if r == 0 else (i16(pg, 14 + 2 * (r - 1)) & 0x1FFF)
                if off & 0x4000:  # pointeur de débordement
                    ptr = i32(pg, start)
                    pp, rr = ptr >> 8, ptr & 0xFF
                    pg2 = self.page(pp)
                    o2 = i16(pg2, 14 + 2 * rr) & 0x1FFF
                    e2 = PS if rr == 0 else (i16(pg2, 14 + 2 * (rr - 1)) & 0x1FFF)
                    row = pg2[o2:e2]
                else:
                    row = pg[start:end]
                try:
                    out.append(self.parse_row(row, cols))
                except Exception as e:  # ligne illisible
                    out.append({'__erreur__': str(e)})
        return out

    def parse_row(self, row, cols):
        ncols = i16(row, 0)
        E = len(row)
        bm = (ncols + 7) // 8
        mask = row[E - bm:E]
        nvar = i16(row, E - bm - 2)
        offs = [i16(row, E - bm - 4 - 2 * j) for j in range(nvar + 1)]
        res = {}
        for c in cols:
            k = c['num']
            if k >= ncols:
                res[c['name']] = None; continue
            present = bool(mask[k // 8] >> (k % 8) & 1)
            t = c['type']
            if t == 1:
                res[c['name']] = present; continue
            if not present:
                res[c['name']] = None; continue
            if c['fixed']:
                o = 2 + c['off_f']
                raw = row[o:o + c['size']]
            else:
                vi = c['var_idx']
                raw = row[offs[vi]:offs[vi + 1]] if vi < nvar else b''
            res[c['name']] = self.conv(t, raw)
        return res

    def conv(self, t, raw):
        if t == 2: return raw[0]
        if t == 3: return struct.unpack('<h', raw)[0]
        if t == 4: return struct.unpack('<i', raw)[0]
        if t == 5: return struct.unpack('<q', raw)[0] / 10000
        if t == 6: return struct.unpack('<f', raw)[0]
        if t == 7: return struct.unpack('<d', raw)[0]
        if t == 8:
            d = struct.unpack('<d', raw)[0]
            return (datetime.datetime(1899, 12, 30) + datetime.timedelta(days=d)).isoformat(sep=' ')
        if t == 10: return decode_text(raw)
        if t == 12:
            ln = i32(raw, 0)
            flag = ln >> 24
            if flag & 0x80:
                return decode_text(raw[12:])
            if flag & 0x40:
                dp = i32(raw, 4); pg = self.page(dp >> 8); r = dp & 0xFF
                o = i16(pg, 14 + 2 * r) & 0x1FFF
                e = PS if r == 0 else (i16(pg, 14 + 2 * (r - 1)) & 0x1FFF)
                return decode_text(pg[o + 4:e])
            return '<memo long>'
        if t == 18: return struct.unpack('<i', raw)[0]
        return raw.hex()

    def tables(self):
        cols = self.tdef(2)
        objs = self.rows(2, cols)
        res = {}
        for o in objs:
            if o.get('Type') == 1 and o.get('Name') and not o['Name'].startswith('MSys'):
                res[o['Name']] = o['Id'] & 0xFFFFFF
        return res, objs

    def read_table(self, name):
        tabs, _ = self.tables()
        pg = tabs[name]
        cols = self.tdef(pg)
        return cols, self.rows(pg, cols)


if __name__ == '__main__':
    db = Db(sys.argv[1])
    tabs, objs = db.tables()
    print('TABLES:', tabs)
    print('AUTRES OBJETS:', [(o['Name'], o['Type']) for o in objs if o.get('Type') != 1 and o.get('Name') and not str(o['Name']).startswith('MSys')])
    for n in tabs:
        cols, rows = db.read_table(n)
        print('\n==', n, len(rows), 'lignes')
        print(' colonnes:', [(c['name'], T_NAMES.get(c['type'], c['type'])) for c in cols])
        for r in rows[:int(sys.argv[2]) if len(sys.argv) > 2 else 3]:
            print('  ', r)
