import sys, os, re, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from refs_extra import EXTRA
import content
root, outdir, stamp = sys.argv[1], sys.argv[2], sys.argv[3]
writedir = sys.argv[4] if len(sys.argv) > 4 else outdir
pdfs = scan_pdfs(root)
refs = load_refs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orig_refs.json'), EXTRA, pdfs)
lk, pat = build_lookup(refs)
amb = {k: v for k, v in lk.items() if len(v) > 1}
print('ambiguous forms:', list(amb))
d = Docx(lk, pat, outdir)
content.build(d, refs)
base = f'{stamp}_兩年期研究計畫書'
d.save(os.path.join(writedir, base + '.docx'), content.TITLE)
d.save_html(os.path.join(writedir, base + '.html'), content.TITLE)
used = [r for r in refs if r.used]
print('refs total', len(refs), 'cited', len(used), 'local pdf', sum(1 for r in used if r.path), 'preprint', [r.auth for r in used if r.preprint])
print('NOT cited:', [(r.auth[:30], r.year) for r in refs if not r.used])
print('unresolved citations:', d.stats.get('bad'))
print('no pdf (cited):', [(r.auth[:30], r.year) for r in used if not r.path])
import json
json.dump([dict(auth=r.auth, year=r.year, title=r.title, journal=r.journal, doi=r.doi, path=r.path, preprint=r.preprint, stage=getattr(r,'stage','')) for r in used],
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'used_refs.json'), 'w'), ensure_ascii=False, indent=1)
