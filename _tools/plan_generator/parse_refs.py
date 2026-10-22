import re,html,json,sys,zipfile,os
src=sys.argv[1]; root=sys.argv[2]
z=zipfile.ZipFile(src); doc=z.read('word/document.xml').decode(); rels=z.read('word/_rels/document.xml.rels').decode()
relmap=dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"',rels))
paras=re.findall(r'<w:p>.*?</w:p>|<w:p [^>]*>.*?</w:p>',doc,re.S)
def ptext(p): return html.unescape(''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>',p,re.S)))
i=[k for k,p in enumerate(paras) if ptext(p)=='參考文獻'][0]
out=[]
for p in paras[i:]:
    if '<w:numPr>' not in p: continue
    runs=re.findall(r'(<w:hyperlink r:id="([^"]+)".*?</w:hyperlink>)|(<w:r>.*?</w:r>)',p,re.S)
    pre='';ital='';post='';doi=None;state=0
    for hl,rid,r in runs:
        if hl: doi=relmap[rid]; continue
        t=html.unescape(''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>',r,re.S)))
        if '<w:i/>' in r: ital+=t; state=1
        elif state==0: pre+=t
        else: post+=t
    m=re.match(r'^(.*?) \((\d{4})\)\. (.*)$',pre.strip())
    auth,year,title=m.groups()
    note=''
    nm=re.search(r'（(.*)）\s*$',post)
    if nm: note=nm.group(1); post=post[:nm.start()]
    post=post.strip()
    if post.endswith('doi'): post=post[:-3].strip()
    out.append(dict(auth=auth,year=year,title=title.strip().rstrip('.'),journal=ital.strip(),rest=post,doi=doi,note=note))
json.dump(out,open('orig_refs.json','w'),ensure_ascii=False,indent=1)
print(len(out))
for r in out[:5]+out[-4:]: print(r)
for r in out:
    if not r['journal']: print('NOJ',r)
