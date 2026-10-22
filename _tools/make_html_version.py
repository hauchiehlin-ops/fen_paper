"""Build a browser version of the plan whose in-text citations open the local PDFs (relative links, no Office prompts).
usage: python3 make_html_version.py <export.html> <raw.docx for images> <out.html> <paper_root>"""
import sys,os,re,html,base64,zipfile,urllib.parse,difflib
src,docx,dst,root=sys.argv[1:5]
h=open(src,encoding='utf-8').read()
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
pdfs=[]
for dp,dns,fns in os.walk(root):
    dns[:]=[d for d in dns if not d.startswith(('.','_')) and d!='External References']
    for f in fns:
        if f.endswith('.pdf') and not f.startswith('._'):
            b=f[:-4]; y=b[:4]; t=re.sub(r'^\d{4} - ','',b); suf=bool(re.search(r'\((arXiv|SSRN|abstract|\d{4} working)',t))
            t=re.sub(r' \((arXiv preprint|SSRN preprint|abstract only|\d{4} working paper)\)$','',t)
            pdfs.append((os.path.join(dp,f),y,norm(t),suf))
cut=h.find('>參考文獻<'); cut=h.rfind('<h2',0,cut)
body,refsec=h[:cut],h[cut:]
refs=[]
def addpdf(m):
    li=m.group(0); t=html.unescape(re.sub(r'<[^>]+>','',li))
    mm=re.match(r'^\s*(.*?) \((\d{4})\)\. (.*)$',t,re.S)
    if not mm: return li
    auth,year,rest=mm.groups(); title=re.sub(r'^Frontiers: ','',rest.split('. ')[0])
    doi=(re.findall(r'href="(https://doi[^"]+)"',li) or [None])[-1]
    etal='et al.' in auth
    surn=re.findall(r'(?:^|, |& )((?:[a-z]+ )?[A-ZÀ-Ž][^,&]*?), (?=(?:[A-Z][a-z]?\.|[A-Z]\.-))',auth)
    ini=re.match(r'^[^,]+, ([A-Z])',auth).group(1); n=3 if etal else len(surn)
    nt=norm(title); c=sorted([(suf,'Plan_fen' not in p,p) for p,y,k,suf in pdfs if y==year and (k.startswith(nt[:35]) or nt.startswith(k[:35]))]); c=[(a,x) for a,b,x in c]
    path=c[0][1] if c else None
    S1=surn[0]
    forms=[S1] if n==1 else [f'{S1} & {surn[1]}'] if n==2 else [f'{S1} et al.',f'{ini}. {S1} et al.']+([f'{S1}, {surn[1]} & {surn[2]}'] if n==3 and not etal else [])
    href=urllib.parse.quote(os.path.relpath(path,os.path.dirname(os.path.abspath(dst)))) if path else doi
    refs.append(dict(year=year,forms=forms,href=href,local=bool(path)))
    if path: li=li.replace('</li>',f' · <a href="{href}" target="_blank">PDF</a></li>')
    return li
refsec=re.sub(r'<li>.*?</li>',addpdf,refsec,flags=re.S)
lk={}
for r in refs:
    for f in r['forms']: lk.setdefault((f,r['year']),[]).append(r)
forms=sorted({f for f,y in lk},key=len,reverse=True)
pat=re.compile('('+'|'.join(re.escape(html.escape(f,quote=False)) for f in forms)+r')(, |（)(\d{4})((?:, \d{4})*)')
cnt=[0]
def link(name,y,text):
    rs=lk.get((html.unescape(name),y))
    if not rs or len(rs)>1: return text
    cnt[0]+=1; r=rs[0]
    return f'<a class="cite{"" if r["local"] else " doi"}" href="{r["href"]}" target="_blank">{text}</a>'
def sub(m):
    name,sep,y,more=m.groups()
    out=link(name,y,f'{name}{sep}{y}')
    for ym in re.finditer(r', (\d{4})',more): out+=', '+link(name,ym.group(1),ym.group(1))
    return out
parts=re.split(r'(<[^>]+>)',body); inA=False
for i,pt in enumerate(parts):
    if pt.startswith('<a '): inA=True
    elif pt.startswith('</a'): inA=False
    elif not pt.startswith('<') and not inA: parts[i]=pat.sub(sub,pt)
body=''.join(parts)
# images from the Word export (diagrams), in document order
z=zipfile.ZipFile(docx); imgs=sorted(n for n in z.namelist() if n.startswith('word/media/'))
it=iter(imgs)
def fig(m):
    try: n=next(it)
    except StopIteration: return m.group(0)
    b=base64.b64encode(z.read(n)).decode()
    return f'<figure><img alt="{m.group(1)}" src="data:image/png;base64,{b}"><figcaption>{m.group(1)}</figcaption></figure>'
body=re.sub(r'<figure data-embed="[^"]+"><figcaption>(.*?)</figcaption></figure>',fig,body)
body=re.sub(r'<span data-atom="mention"[^>]*>[^<]*</span>','Dr. Barret Lin',body)
title=html.unescape(re.sub(r'<[^>]+>','',re.search(r'<h1[^>]*>(.*?)</h1>',body,re.S).group(1)))
page=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>
:root{{--bg:#fff;--fg:#1f2328;--muted:#59636e;--line:#d1d9e0;--link:#0b5cad;--note:#f3f6fa}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16181d;--fg:#e6e8eb;--muted:#9aa3ad;--line:#3a3f47;--link:#7fb4ff;--note:#1f242c}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.75 "PingFang TC","Microsoft JhengHei","Noto Sans TC",sans-serif;max-width:900px;margin:0 auto;padding:24px 16px 80px}}
h1{{font-size:1.6em;line-height:1.35}} h2{{margin-top:2.2em;border-bottom:1px solid var(--line);padding-bottom:.3em}} h3{{margin-top:1.6em}}
table{{border-collapse:collapse;width:100%;margin:1em 0;font-size:.92em;display:block;overflow-x:auto}} th,td{{border:1px solid var(--line);padding:6px 8px;vertical-align:top}} th{{background:var(--note)}}
a{{color:var(--link)}} a.cite{{text-decoration:underline}} a.cite.doi{{text-decoration-style:dotted}}
figure{{margin:1.5em 0}} figure img{{max-width:100%;height:auto;background:#fff;border-radius:6px}} figcaption{{color:var(--muted);font-size:.9em}}
.note{{background:var(--note);border:1px solid var(--line);border-radius:8px;padding:12px 16px;font-size:.92em}}
</style></head><body>
<div class="note">網頁版與同時間戳的 Word 版內容相同。點擊內文的文獻引用，會在瀏覽器新分頁直接開啟主題資料夾中的 PDF（虛線底線者尚無本地檔案，開啟 DOI 頁面）。請將本檔與五個主題資料夾放在同一層；Windows、macOS、Linux 的 Chrome、Edge、Safari、Firefox 皆可使用，不需另行授權。</div>
{body}{refsec}</body></html>'''
open(dst,'w',encoding='utf-8').write(page)
miss=[r for r in refs if not r['local']]
print('refs',len(refs),'local',len(refs)-len(miss),'citation links',cnt[0])
