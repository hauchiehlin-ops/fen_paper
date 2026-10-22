import sys,re,zipfile
from xml.sax.saxutils import escape
src,dst=sys.argv[1],sys.argv[2]
lines=open(src,encoding='utf-8').read().split('\n')
rels=[]
def run(t,sz=21,b=False,link=False):
    rpr=f'<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Microsoft JhengHei"/>{"<w:b/>" if b else ""}{"<w:color w:val=\"0563C1\"/><w:u w:val=\"single\"/>" if link else ""}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(t)}</w:t></w:r>'
def runs(t,sz=21,b=False):
    out=[]; pos=0
    for m in re.finditer(r'https?://[^\s）]+?(?=\s|$|）|\)(?:\s|$))',t):
        if m.start()>pos: out.append(run(t[pos:m.start()],sz,b))
        rid=f'rId{len(rels)+10}'; rels.append((rid,m.group(0)))
        out.append(f'<w:hyperlink r:id="{rid}">{run(m.group(0),sz,b,True)}</w:hyperlink>'); pos=m.end()
    if pos<len(t): out.append(run(t[pos:],sz,b))
    return ''.join(out)
def para(t,sz=21,b=False,after=120):
    return f'<w:p><w:pPr><w:spacing w:after="{after}"/></w:pPr>{runs(t,sz,b)}</w:p>'
body=[]; i=0
while i<len(lines):
    l=lines[i]
    if l.startswith('# '): body.append(para(l[2:],32,True,200))
    elif l.startswith('## '): body.append(para(l[3:],26,True,120))
    elif l.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            r=[c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(set(c)<=set('-: ') for c in r): rows.append(r)
            i+=1
        n=len(rows[0]); widths=[450,6000,3200,1000,4100] if n==5 else {6:[5400,1500,1500,1300,2200,2850],3:[5200,1300,8250],'pre':[2600,6400,1500,2200,2050]}.get(n,[14750//n]*n)
        if n==5 and rows[0][2]=='子計畫': widths=[450,5600,1000,5000,2700]
        if n==5 and rows[0][0]=='資料夾': widths=[2600,6400,1500,2200,2050]
        tbl=['<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>'+''.join(f'<w:{s} w:val="single" w:sz="4" w:color="999999"/>' for s in ['top','left','bottom','right','insideH','insideV'])+'</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>'+''.join(f'<w:gridCol w:w="{w}"/>' for w in widths)+'</w:tblGrid>']
        for k,r in enumerate(rows):
            tr='<w:tr>'+('<w:trPr><w:tblHeader/></w:trPr>' if k==0 else '')
            for c,w in zip(r,widths):
                shade='<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if k==0 else ''
                tr+=f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shade}</w:tcPr><w:p><w:pPr><w:spacing w:after="0"/></w:pPr>{runs(c,17,k==0)}</w:p></w:tc>'
            tbl.append(tr+'</w:tr>')
        tbl.append('</w:tbl>'); body.append(''.join(tbl)); body.append(para('',10,after=0)); continue
    elif l.strip(): body.append(para(l))
    i+=1
sect='<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000" w:header="500" w:footer="500" w:gutter="0"/></w:sectPr>'
doc=f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>{"".join(body)}{sect}</w:body></w:document>'
ct='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
r0='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
dr='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{a}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{escape(u)}" TargetMode="External"/>' for a,u in rels)+'</Relationships>'
with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml',ct); z.writestr('_rels/.rels',r0); z.writestr('word/document.xml',doc); z.writestr('word/_rels/document.xml.rels',dr)
print('links',len(rels))
