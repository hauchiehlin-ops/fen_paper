import sys, os, re, datetime, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from refs_extra import EXTRA
root, outdir, stamp = sys.argv[1], sys.argv[2], sys.argv[3]
writedir = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else outdir
plan = sys.argv[5] if len(sys.argv) > 5 else ''          # '' = plan-1 (content.py); 'plan2' = content_plan2.py
content = importlib.import_module('content_' + plan if plan else 'content')
extra = EXTRA + (importlib.import_module('refs_' + plan).EXTRA2 if plan else [])
pdfs = scan_pdfs(root)
refs = load_refs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orig_refs.json'), extra, pdfs)
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
if not plan: print('NOT cited:', [(r.auth[:30], r.year) for r in refs if not r.used])
else: print('NOT cited (plan additions):', [(r.auth[:30], r.year) for r in refs if not r.used and any(r.auth == e['auth'] for e in extra[len(EXTRA):])])
print('unresolved citations:', d.stats.get('bad'))
print('no pdf (cited):', [(r.auth[:30], r.year) for r in used if not r.path])
import json
json.dump([dict(auth=r.auth, year=r.year, title=r.title, journal=r.journal, doi=r.doi, path=r.path, preprint=r.preprint, stage=getattr(r, 'stage', ''),
                tier=getattr(r, 'tier', ''), chk=getattr(r, 'chk', '')) for r in used],
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'used_refs{"_" + plan if plan else ""}.json'), 'w'), ensure_ascii=False, indent=1)
