"""各主題資料夾文獻數量 .docx: PDF counts per topic folder, which plans cite each file, and changes since a git baseline.
usage: counts.py <Plan_fen> <out.docx> <baseline git rev> <label:plan.docx> [<label:plan.docx> ...]"""
import sys, os, re, zipfile, subprocess, urllib.parse, datetime
from xml.sax.saxutils import escape
root, dst, base = sys.argv[1], sys.argv[2], sys.argv[3]
plans = [a.split(':', 1) for a in sys.argv[4:]]
folders = sorted(d for d in os.listdir(root) if re.match(r'[1-5]\. ', d))
pdfs = {d: sorted(f for f in os.listdir(os.path.join(root, d)) if f.endswith('.pdf') and not f.startswith('._')) for d in folders}

def cited(docx):  # topic-folder PDFs a plan links to, as (folder, file)
    rels = zipfile.ZipFile(docx).read('word/_rels/document.xml.rels').decode()
    out = set()
    for t in re.findall(r'Target="([^"]+\.pdf)"', rels):
        p = os.path.normpath(os.path.join(os.path.dirname(docx), urllib.parse.unquote(t.replace('&amp;', '&'))))
        out.add((os.path.basename(os.path.dirname(p)), os.path.basename(p)))
    return out
C = [(lab, cited(p), os.path.basename(p)) for lab, p in plans]
prev = subprocess.run(['git', 'ls-tree', '-r', '-z', '--name-only', base, '--', root], capture_output=True, text=True, check=True).stdout.split('\0')
old = {d: {os.path.basename(f) for f in prev if f.split('/')[-2:-1] == [d] and f.endswith('.pdf')} for d in folders}
when = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=format-local:%Y-%m-%d %H:%M', base], capture_output=True, text=True,
                      env=dict(os.environ, TZ='Asia/Taipei')).stdout.strip()
pre = lambda f: bool(re.search(r'\((arXiv|SSRN|abstract|\d{4} working)', f))

def run(t, sz=21, b=False):
    return f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Microsoft JhengHei"/>{"<w:b/>" if b else ""}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr><w:t xml:space="preserve">{escape(t)}</w:t></w:r>'
def para(t, sz=21, b=False, after=120): return f'<w:p><w:pPr><w:spacing w:after="{after}"/></w:pPr>{run(t, sz, b)}</w:p>'
def table(W, rows):
    x = ['<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>' + ''.join(f'<w:{s} w:val="single" w:sz="4" w:color="999999"/>' for s in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']) +
         '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in W) + '</w:tblGrid>']
    for k, r in enumerate(rows):
        x.append('<w:tr>' + ('<w:trPr><w:tblHeader/></w:trPr>' if k == 0 else ''))
        for c, w in zip(r, W):
            sh = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if k == 0 else ''
            x.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{sh}</w:tcPr><w:p><w:pPr><w:spacing w:after="0"/></w:pPr>{run(str(c), 17, k == 0)}</w:p></w:tc>')
        x.append('</w:tr>')
    return ''.join(x) + '</w:tbl>' + para('', 10, after=0)

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
labs = [lab for lab, _, _ in C]
body = [para(f'各主題資料夾文獻數量（{now}）', 32, True, 200),
        para('統計範圍：Plan_fen 內五個主題資料夾的 PDF。「引用」依各計畫書 .docx 的文獻連結計算：' + '；'.join(f'{lab} 為 {fn}' for lab, _, fn in C) + '。'),
        para('數量統計', 26, True)]
hdr = ['資料夾', 'PDF 數量'] + [f'{lab} 引用' for lab in labs] + ['任一計畫引用', '均未引用', '預印本／不完整版', '與前次相比']
rows, tot = [hdr], [0] * (len(hdr) - 1)
for d in folders:
    fs = pdfs[d]
    per = [sum((d, f) in c for f in fs) for _, c, _ in C]
    anyc = sum(any((d, f) in c for _, c, _ in C) for f in fs)
    delta = len(fs) - len(old[d])
    vals = [len(fs)] + per + [anyc, len(fs) - anyc, sum(map(pre, fs)), delta]
    tot = [a + b for a, b in zip(tot, vals)]
    rows.append([d] + vals[:-1] + [f'{delta:+d}' if delta else '無變動'])
rows.append(['合計'] + tot[:-1] + [f'{tot[-1]:+d}' if tot[-1] else '無變動'])
body.append(table([4300, 1100] + [1200] * len(labs) + [1300, 1100, 1500, 1400], rows))

pr = [(d, f) for d in folders for f in pdfs[d] if pre(f) and any((d, f) in c for _, c, _ in C)]
body += [para('計畫書有引用的預印本／不完整版', 26, True), para(f'共 {len(pr)} 篇預印本在計畫書內有引用，下載期刊正式版後請替換：')]
body.append(table([3200, 7200, 2200, 2000], [['資料夾', '文獻', '版本', '引用的計畫']] +
                  [[d.split(' (')[0], f[:-4], re.search(r'\(([^)]*)\)\.pdf$', f).group(1).replace('preprint', '預印本'), '、'.join(l for l, c, _ in C if (d, f) in c)] for d, f in pr]))
chg = [(d, '新增', f) for d in folders for f in pdfs[d] if f not in old[d]] + [(d, '移除', f) for d in folders for f in sorted(old[d]) if f not in pdfs[d]]
body += [para('與前次紀錄的增刪明細', 26, True), para(f'比較基準：GitHub 版本 {base[:7]}（{when}），即本次歸檔前的資料夾內容。共 {len(chg)} 筆。')]
body.append(table([4300, 900, 9400], [['資料夾', '變動', '檔名']] + [list(r) for r in chg]))
body += [para('各資料夾檔案清單', 26, True), para('標記：' + '、'.join(f'{m} 為 {lab} 引用' for m, lab in zip('①②③', labs)) + '；無標記者為兩份計畫書均未引用。')]
for d in folders:
    body.append(para(f'{d}（{len(pdfs[d])} 篇）', 22, True))
    for f in pdfs[d]:
        mk = ''.join(m if (d, f) in c else '　' for m, (_, c, _) in zip('①②③', C))
        body.append(para(f'{mk} {f}', 18, after=0))
sect = '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000" w:header="500" w:footer="500" w:gutter="0"/></w:sectPr>'
doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>{"".join(body)}{sect}</w:body></w:document>'
ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
r0 = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
dr = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>'
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', r0); z.writestr('word/document.xml', doc); z.writestr('word/_rels/document.xml.rels', dr)
for r in rows: print(r)
print('preprints cited', len(pr), 'changes', len(chg))
