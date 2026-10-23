import sys, json, re, zipfile
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xml.sax.saxutils import escape
refs = json.load(open(sys.argv[1], encoding='utf-8')); dst = sys.argv[2]; planfile = sys.argv[3]
plan = sys.argv[4] if len(sys.argv) > 4 else ''   # 'plan2' lists plan-2 additions and the review's screening record
from refs_extra import EXTRA
if plan:
    import importlib; P = importlib.import_module('refs_' + plan); EXTRA = P.EXTRA2
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
    chk = f"（待核對：{r['chk']}）" if r.get('chk') else ''
    return f"{a} ({r['year']}). {r['title']}{chk}"
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
    TIER = {'A': '（A 級，FT50）', 'B': '（B 級）', 'F': '（理論基礎）'}
    return [[str(i + 1), short(r) + note, re.sub(r', \d+$', '', r['journal']).strip() + TIER.get(r.get('tier', ''), ''), stg(r), r['doi']] for i, r in enumerate(lst)]
n = len(new) + len(old) + len(pre)
body = [para(f'外部補充文獻：待下載清單（{n} 篇）', 32, True, 200),
        para(f'計畫書「{planfile}」參考文獻共 {len(refs)} 篇，其中 {sum(1 for r in refs if r["path"])} 篇已存放於主題資料夾。以下 {n} 篇尚未取得或需要換成期刊正式版。'
             '本次新增的外部文獻已以網路檢索比對出版者或索引資料（本次工作環境無法連線 Crossref API），下載後請再核對卷期頁碼。下載後放進 External References 資料夾即可，之後重新產出計畫書時，引用超連結會改連到本地 PDF。'),
        para(f'一、本次改寫新增的外部文獻（{len(new)} 篇）', 26, True), para('在校園網路或學校 VPN 下開啟 DOI 連結，通常可以直接下載。'), table(rows(new)),
        para(f'二、原計畫書已列、尚未取得的外部文獻（{len(old)} 篇）', 26, True), table(rows(old)),
        para(f'三、需換成期刊正式版（{len(pre)} 篇）', 26, True), table(rows(pre, '（目前為 SSRN 預印本，請下載期刊版）'))]
if plan:
    W[:] = [450, 5900, 2700, 800, 3950]
    def table2(rows, hdr):
        x = ['<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>' + ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="999999"/>' for s in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']) +
             '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in W) + '</w:tblGrid>']
        for k, r in enumerate([hdr] + rows):
            x.append('<w:tr>' + ('<w:trPr><w:tblHeader/></w:trPr>' if k == 0 else ''))
            for c, w in zip(r, W):
                sh = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if k == 0 else ''
                bd = link(c) if (k and c.startswith('https://')) else run(c, 17, k == 0)
                x.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{sh}</w:tcPr><w:p><w:pPr><w:spacing w:after="0"/></w:pPr>{bd}</w:p></w:tc>')
            x.append('</w:tr>')
        x.append('</w:tbl>'); return ''.join(x) + para('', 10, after=0)
    keep = [c for c in P.CANDIDATES if c['status'] == '保留' and not c.get('got')]; drop = [c for c in P.CANDIDATES if c['status'] == '排除']
    got = [c for c in P.CANDIDATES if c.get('got')]
    import glob
    def where(c):
        t = re.sub(r'[^a-z0-9]', '', re.sub(r'（.*$', '', c['ref'].split(' — ')[-1]).lower())[:40]
        for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(dst)), '..', '[1-5]. *', '*.pdf')):
            if re.sub(r'[^a-z0-9]', '', os.path.basename(f)[7:].lower()).startswith(t): return os.path.basename(os.path.dirname(f)).split(' (')[0]
        return '（未找到檔案）'
    body = [para(f'plan-2 待下載文獻清單與系統性文獻回顧篩選紀錄', 32, True, 200),
            para(f'計畫書「{planfile}」參考文獻共 {len(refs)} 篇，其中 {sum(1 for r in refs if r["path"])} 篇已存放於主題資料夾，{len(new) + len(old)} 篇尚未取得。'
                 '書目資料已以網路檢索比對出版社頁面、RePEc／大學典藏或期刊新聞稿（本工作環境無法連線 Crossref 與 doi.org）；標示「待核對」者，請於下載時以出版社頁面確認後告知，以便更新計畫書。'
                 '下載後放進 External References 資料夾即可，之後重新產出計畫書時，引用超連結會改連到本地 PDF。'),
            para(f'一、plan-2 引用、尚未取得的文獻（{len(new) + len(old)} 篇）', 26, True), para('期刊欄標示 A 級（FT50）、B 級（SSCI、影響係數 > 2）或理論基礎（2021 年以前）。在校園網路或學校 VPN 下開啟 DOI 連結，通常可以直接下載。'),
            table(rows(new + old))]
    if pre: body += [para(f'另有 {len(pre)} 篇已存放於主題資料夾，但目前為預印本，需換成期刊正式版：'), table(rows(pre, '（目前為 SSRN 預印本，請下載期刊版）'))]
    W[:] = [450, 6300, 2600, 4450]
    body += ([para(f'二、系統性文獻回顧：保留候選、尚未下載（{len(keep)} 篇）', 26, True),
             para(f'以下文獻與主題相關，計畫書未引用，建議下載以供正式回顧時全文篩選。另有 {len(got)} 篇保留候選已下載並完成全文篩選（見第四節）。'),
             table2([[str(i + 1), c['ref'], c['why'], c['url']] for i, c in enumerate(keep)], ['#', '文獻', '保留理由', '連結'])] if keep else
             [para('二、系統性文獻回顧：保留候選（0 篇尚未下載）', 26, True), para(f'保留候選 {len(got)} 篇均已下載並完成全文篩選，結果見第四節。')]) + [
             para(f'三、系統性文獻回顧：排除紀錄（網路檢索 {len(drop)} 篇、主題資料夾 {len(P.FOLDER_EXCLUDED)} 篇）', 26, True)]
    W[:] = [450, 8600, 4750]
    def table3(rows, hdr=['#', '文獻', '排除理由']):
        x = ['<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>' + ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="999999"/>' for s in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']) +
             '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in W) + '</w:tblGrid>']
        for k, r in enumerate([hdr] + rows):
            x.append('<w:tr>')
            for c, w in zip(r, W):
                sh = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if k == 0 else ''
                x.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{sh}</w:tcPr><w:p><w:pPr><w:spacing w:after="0"/></w:pPr>{run(c, 17, k == 0)}</w:p></w:tc>')
            x.append('</w:tr>')
        x.append('</w:tbl>'); return ''.join(x) + para('', 10, after=0)
    W[:] = [450, 9600, 3750]
    ok = sum(c['status'] == '納入' for c in got)
    gotsec = [para(f'四、系統性文獻回顧：保留候選之全文篩選結果（{len(got)} 篇；納入 {ok}、排除 {len(got) - ok}）', 26, True),
              para('以下文獻已由 External References 更名並歸檔，書目資料依 PDF 更新。納入者已列入計畫書參考文獻與缺口矩陣；排除者亦列於第三節。'),
              table3([[str(i + 1), c['ref'], c['status'] + '｜' + where(c)] for i, c in enumerate(got)], ['#', '文獻', '篩選結果｜所在資料夾'])]
    W[:] = [450, 8600, 4750]
    body += [table3([[str(i + 1), c['ref'], c['why']] for i, c in enumerate(drop)] +
                    [[str(len(drop) + i + 1), t + '（主題資料夾）', w] for i, (t, w) in enumerate(P.FOLDER_EXCLUDED)])] + gotsec
    n = len(new) + len(old)
sect = '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000" w:header="500" w:footer="500" w:gutter="0"/></w:sectPr>'
doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>{"".join(body)}{sect}</w:body></w:document>'
ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
r0 = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
dr = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(f'<Relationship Id="{a}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{escape(u)}" TargetMode="External"/>' for a, u in rels) + '</Relationships>'
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', r0); z.writestr('word/document.xml', doc); z.writestr('word/_rels/document.xml.rels', dr)
print('plan', plan or 'plan-1', 'new', len(new), 'old', len(old), 'pre', len(pre), 'links', len(rels))
