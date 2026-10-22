import sys, json, re, zipfile
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xml.sax.saxutils import escape
refs = json.load(open(sys.argv[1], encoding='utf-8')); dst = sys.argv[2]; planfile = sys.argv[3]
from refs_extra import EXTRA
newkeys = {(d['auth'], str(d['year'])) for d in EXTRA}
stage_of = {(d['auth'], str(d['year'])): d['stage'] for d in EXTRA}
orig_stage = {'Cacioppo': '共同', 'Lang, A.': '二', 'Granovetter': '三', 'Brown, J. J.': '三', 'Li, P.': '一'}
def stg(r):
    s = stage_of.get((r['auth'], r['year']))
    if s: return s
    for k, v in orig_stage.items():
        if r['auth'].startswith(k): return v
    return ''
def short(r):
    sn = re.findall(r'(?:^|, |& )((?:[a-z]+ )?[A-ZÀ-Ž][^,&]*?), (?=(?:[A-Z][a-z]?\.|[A-Z]\.-))', r['auth'])
    a = sn[0] if len(sn) == 1 else (' & '.join(sn) if len(sn) == 2 else ', '.join(sn[:-1]) + ' & ' + sn[-1])
    return f"{a} ({r['year']}). {r['title']}"
new = [r for r in refs if not r['path'] and (r['auth'], r['year']) in newkeys]
old = [r for r in refs if not r['path'] and (r['auth'], r['year']) not in newkeys]
pre = [r for r in refs if r['preprint']]
rels = []
def run(t, sz=21, b=False, link=False):
    rpr = f'<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Microsoft JhengHei"/>{"<w:b/>" if b else ""}{"<w:color w:val=\"0563C1\"/>" if link else ""}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>{"<w:u w:val=\"single\"/>" if link else ""}</w:rPr>'
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(t)}</w:t></w:r>'
def link(u, sz=17):
    rid = f'rId{len(rels) + 10}'; rels.append((rid, u))
    return f'<w:hyperlink r:id="{rid}">{run(u, sz, link=True)}</w:hyperlink>'
def para(t, sz=21, b=False, after=120): return f'<w:p><w:pPr><w:spacing w:after="{after}"/></w:pPr>{run(t, sz, b)}</w:p>'
W = [450, 7000, 3200, 900, 3200]
def table(rows):
    x = ['<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>' + ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="999999"/>' for s in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']) +
         '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in W) + '</w:tblGrid>']
    hdr = ['#', '文獻', '期刊', '階段', 'DOI']
    for k, r in enumerate([hdr] + rows):
        x.append('<w:tr>' + ('<w:trPr><w:tblHeader/></w:trPr>' if k == 0 else ''))
        for c, w in zip(r, W):
            sh = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if k == 0 else ''
            body = link(c) if (k and c.startswith('https://')) else run(c, 17, k == 0)
            x.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{sh}</w:tcPr><w:p><w:pPr><w:spacing w:after="0"/></w:pPr>{body}</w:p></w:tc>')
        x.append('</w:tr>')
    x.append('</w:tbl>'); return ''.join(x) + para('', 10, after=0)
def rows(lst, note=''):
    return [[str(i + 1), short(r) + note, re.sub(r', \d+$', '', r['journal']).strip(), stg(r), r['doi']] for i, r in enumerate(lst)]
n = len(new) + len(old) + len(pre)
body = [para(f'外部補充文獻：待下載清單（{n} 篇）', 32, True, 200),
        para(f'計畫書「{planfile}」參考文獻共 {len(refs)} 篇，其中 {sum(1 for r in refs if r["path"])} 篇已存放於主題資料夾。以下 {n} 篇尚未取得或需要換成期刊正式版。'
             '本次新增的外部文獻已以網路檢索比對出版者或索引資料（本次工作環境無法連線 Crossref API），下載後請再核對卷期頁碼。下載後放進 External References 資料夾即可，之後重新產出計畫書時，引用超連結會改連到本地 PDF。'),
        para(f'一、本次改寫新增的外部文獻（{len(new)} 篇）', 26, True), para('在校園網路或學校 VPN 下開啟 DOI 連結，通常可以直接下載。'), table(rows(new)),
        para(f'二、原計畫書已列、尚未取得的外部文獻（{len(old)} 篇）', 26, True), table(rows(old)),
        para(f'三、需換成期刊正式版（{len(pre)} 篇）', 26, True), table(rows(pre, '（目前為 SSRN 預印本，請下載期刊版）'))]
sect = '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000" w:header="500" w:footer="500" w:gutter="0"/></w:sectPr>'
doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>{"".join(body)}{sect}</w:body></w:document>'
ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
r0 = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
dr = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(f'<Relationship Id="{a}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{escape(u)}" TargetMode="External"/>' for a, u in rels) + '</Relationships>'
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', r0); z.writestr('word/document.xml', doc); z.writestr('word/_rels/document.xml.rels', dr)
print('new', len(new), 'old', len(old), 'pre', len(pre), 'links', len(rels))
