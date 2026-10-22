import sys,os,re,zipfile,html,urllib.parse
from xml.sax.saxutils import escape
src,dst,root=sys.argv[1],sys.argv[2],sys.argv[3]
z=zipfile.ZipFile(src); files={n:z.read(n) for n in z.namelist()}
doc=files['word/document.xml'].decode(); rels=files['word/_rels/document.xml.rels'].decode()
relmap=dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"',rels))
def ptext(p): return html.unescape(''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>',p,re.S)))
paras=list(re.finditer(r'<w:p>.*?</w:p>|<w:p [^>]*>.*?</w:p>',doc,re.S))
# reference section start
refstart=next(m.start() for m in paras if ptext(m.group())=='參考文獻')
refparas=[m for m in paras if m.start()>refstart and '<w:numPr>' in m.group()]
numids=[re.search(r'<w:numId w:val="(\d+)"',m.group()).group(1) for m in refparas]
# PDFs
pdfs=[]
for dp,dns,fns in os.walk(root):
    dns[:]=[d for d in dns if not d.startswith(('.','_')) and d!='External References']
    for f in fns:
        if f.endswith('.pdf') and not f.startswith('._'): pdfs.append(os.path.join(dp,f))
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
def pdfkey(path):
    f=os.path.basename(path)[:-4]; y=f[:4]; t=re.sub(r'^\d{4} - ','',f); suffix=bool(re.search(r'\((arXiv|SSRN|abstract|\d{4} working)',t))
    t=re.sub(r' \((arXiv preprint|SSRN preprint|abstract only|\d{4} working paper)\)$','',t)
    return y,norm(t),suffix
pk=[(p,)+pdfkey(p) for p in pdfs]
refs=[]
for m in refparas:
    t=ptext(m.group())
    mm=re.match(r'^(.*?) \((\d{4})\)\. (.*)$',t)
    if not mm: print('PARSEFAIL',t[:80]); continue
    auth,year,rest=mm.groups()
    title=rest.split('. ')[0] if not rest.startswith('Frontiers') else rest
    doi=None
    hl=re.findall(r'<w:hyperlink r:id="([^"]+)"',m.group())
    if hl: doi=relmap.get(hl[-1])
    etal='et al.' in auth
    surn=re.findall(r'(?:^|, |& )((?:[a-z]+ )?[A-ZÀ-Ž][^,&]*?), (?=(?:[A-Z][a-z]?\.|[A-Z]\.-))',auth)
    first_init=re.match(r'^[^,]+, ([A-Z])',auth).group(1)
    n=3 if etal else len(surn)
    # file match
    nt=norm(re.sub(r'^Frontiers: ','',title))
    cands=[(p,suf) for p,y,k,suf in pk if y==year and (k.startswith(nt[:35]) or nt.startswith(k[:35]))]
    cands.sort(key=lambda c:(c[1],'Plan_fen' not in c[0]))
    path=cands[0][0] if cands else None
    S1=surn[0]
    forms=[]
    if n==1: forms=[S1]
    elif n==2: forms=[f'{S1} & {surn[1]}']
    else:
        forms=[f'{S1} et al.',f'{first_init}. {S1} et al.']
        if n==3 and not etal: forms.append(f'{S1}, {surn[1]} & {surn[2]}')
    refs.append(dict(auth=auth,year=year,title=title,doi=doi,path=path,forms=forms))
print('refs',len(refs),'with pdf',sum(1 for r in refs if r['path']))
for r in refs:
    if not r['path']: print('  no pdf:',r['auth'][:40],r['year'])
# lookup
lk={}
for r in refs:
    for f in r['forms']: lk.setdefault((f,r['year']),[]).append(r)
formset=sorted({f for (f,y) in lk},key=len,reverse=True)
pat=re.compile('('+'|'.join(re.escape(f) for f in formset)+r')(, |（)(\d{4})((?:, \d{4})*)')
newrels=[]; relid=[1000]
def target(r):
    if r['path']:
        rel=os.path.relpath(r['path'], os.path.dirname(os.path.abspath(dst)))
        # keep non-ASCII (Chinese folder names) raw; Word for Mac does not decode %XX for them
        return ''.join({'%':'%25',' ':'%20','#':'%23','?':'%3F'}.get(c,c) for c in rel)
    return r['doi']
def rid_for(r):
    t=target(r)
    for a,b in newrels:
        if b==t: return a
    relid[0]+=1; a=f'rIdC{relid[0]}'; newrels.append((a,t)); return a
stats=dict(links=0,ambig=[],miss=[])
def process(p):
    # tokens: runs at top level of paragraph vs other
    parts=re.split(r'(<w:hyperlink.*?</w:hyperlink>|<w:r>.*?</w:r>|<w:r [^>]*>.*?</w:r>)',p,flags=re.S)
    runs=[]  # (index in parts, rPr, text)
    full=''; offs=[]
    for i,pt in enumerate(parts):
        if pt.startswith('<w:r>') or pt.startswith('<w:r '):
            ts=re.findall(r'<w:t[^>]*>(.*?)</w:t>',pt,re.S)
            if len(ts)!=1 or '<w:tab' in pt or '<w:br' in pt: full+='\x00'; continue
            rpr=re.search(r'<w:rPr>.*?</w:rPr>',pt,re.S); rpr=rpr.group() if rpr else ''
            t=html.unescape(ts[0]); runs.append((i,rpr,len(full),t)); full+=t
        elif pt.startswith('<w:hyperlink'): full+='\x00'
    matches=[]
    for m in pat.finditer(full):
        name,sep,y,more=m.groups()
        segs=[(m.start(),m.end()-len(more),(name,y))]
        pos=m.end()-len(more)
        for ym in re.finditer(r', (\d{4})',more):
            segs.append((pos+ym.start()+2,pos+ym.end(),(name,ym.group(1))))
        for s,e,key in segs:
            rs=lk.get(key)
            if not rs: stats['miss'].append(key); continue
            if len({id(x) for x in rs})>1: stats['ambig'].append(key); continue
            matches.append((s,e,rs[0]))
    if not matches: return p
    # rebuild runs
    out=list(parts)
    for (i,rpr,st,t) in runs:
        en=st+len(t); cuts={st,en}
        for s,e,r in matches:
            if s<en and e>st: cuts.add(max(s,st)); cuts.add(min(e,en))
        cuts=sorted(cuts); xml=''
        for a,b in zip(cuts,cuts[1:]):
            seg=t[a-st:b-st]
            if not seg: continue
            hit=next((r for s,e,r in matches if s<=a and b<=e),None)
            if hit:
                r2=rpr.replace('<w:rPr>','<w:rPr><w:rStyle w:val="Hyperlink"/>') if rpr else '<w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr>'
                xml+=f'<w:hyperlink r:id="{rid_for(hit)}" w:history="1"><w:r>{r2}<w:t xml:space="preserve">{escape(seg)}</w:t></w:r></w:hyperlink>'
                stats['links']+=1
            else:
                xml+=f'<w:r>{rpr}<w:t xml:space="preserve">{escape(seg)}</w:t></w:r>'
        out[i]=xml
    return ''.join(out)
newdoc=[];last=0
for m in paras:
    newdoc.append(doc[last:m.start()])
    p=m.group()
    if m.start()<refstart: p=process(p)
    newdoc.append(p); last=m.end()
newdoc.append(doc[last:]); doc2=''.join(newdoc)
# continuous numbering: external list uses local list numId
if len(set(numids))==2:
    a,b=numids[0],numids[-1]
    doc2=doc2.replace(f'<w:numId w:val="{b}"/>',f'<w:numId w:val="{a}"/>')
rels2=rels.replace('</Relationships>',''.join(f'<Relationship Id="{a}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{escape(t)}" TargetMode="External"/>' for a,t in newrels)+'</Relationships>')
files['word/document.xml']=doc2.encode(); files['word/_rels/document.xml.rels']=rels2.encode()
with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as zo:
    for n,v in files.items(): zo.writestr(n,v)
print('citation links',stats['links'],'distinct targets',len(newrels))
from collections import Counter
print('ambiguous',Counter(stats['ambig'])); print('missing',Counter(stats['miss']))
used={t for a,t in newrels}
print('refs never cited:',[ (r['auth'][:25],r['year']) for r in refs if target(r) not in used])
