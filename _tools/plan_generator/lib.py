"""Shared builders: references, citation linking, DOCX (with editable DrawingML figures) and HTML output."""
import re, os, html, json, zipfile, urllib.parse, datetime
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- references
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())

def scan_pdfs(root):
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if not d.startswith(('.', '_')) and d != 'External References']
        for f in fns:
            if f.endswith('.pdf') and not f.startswith('._'):
                b = f[:-4]; y = b[:4]; t = re.sub(r'^\d{4} - ', '', b)
                pre = bool(re.search(r'\((arXiv|SSRN|abstract|\d{4} working)', t))
                t = re.sub(r' \((arXiv preprint|SSRN preprint|abstract only|\d{4} working paper)\)$', '', t)
                out.append(dict(path=os.path.join(dp, f), year=y, key=norm(t), title=t, pre=pre))
    return out

def surnames(auth):
    return re.findall(r'(?:^|, |& )((?:[a-z]+ )?[A-ZÀ-Ž][^,&]*?), (?=(?:[A-Z][a-z]?\.|[A-Z]\.-))', auth)

class Ref:
    def __init__(self, d, pdfs):
        self.__dict__.update(d)
        self.year = str(self.year)
        t = re.sub(r'^Frontiers: ', '', self.title); nt = norm(t)
        c = sorted([(p['pre'], p['path']) for p in pdfs if p['year'] == self.year and
                    (p['key'].startswith(nt[:35]) or nt.startswith(p['key'][:35]))])
        self.path = c[0][1] if c else None
        self.preprint = bool(c and c[0][0])
        if self.path:  # restore full title from the archived file name when the list carried a shortened one
            ft = [p for p in pdfs if p['path'] == self.path][0]['title']
            full = re.sub(r' - ', ': ', ft)
            if norm(full).startswith(nt) and len(norm(full)) > len(nt) + 5:
                full = re.sub(r': (\w)', lambda m: ': ' + m.group(1).upper(), full)
                self.title = re.sub(r'^(\w)', lambda m: m.group(1).upper(), full)
        sn = surnames(self.auth)
        etal = 'et al.' in self.auth
        n = 3 if etal else len(sn)
        ini = re.match(r'^[^,]+, ([A-Z])', self.auth).group(1)
        S = sn[0]
        if n == 1: self.forms = [S]
        elif n == 2: self.forms = [f'{S} & {sn[1]}']
        else: self.forms = [f'{S} et al.', f'{ini}. {S} et al.']
        self.used = 0

    def sortkey(self):
        return (norm(self.auth.split(',')[0]), self.auth.lower(), self.year)

def load_refs(orig_json, extra, pdfs):
    refs = [Ref(d, pdfs) for d in json.load(open(orig_json, encoding='utf-8'))]
    refs += [Ref(d, pdfs) for d in extra]
    return refs

def build_lookup(refs):
    lk = {}
    for r in refs:
        for f in r.forms: lk.setdefault((f, r.year), []).append(r)
    forms = sorted({f for f, y in lk}, key=len, reverse=True)
    pat = re.compile('(' + '|'.join(re.escape(f) for f in forms) + r')(, | \()(\d{4})((?:, \d{4})*)')
    return lk, pat

# ---------------------------------------------------------------- inline markup
def segments(text, lk, pat, stats):
    """text with **bold** -> list of (str, bold, ref-or-None)."""
    out = []
    for i, part in enumerate(re.split(r'\*\*', text)):
        bold = i % 2 == 1
        pos = 0
        for m in pat.finditer(part):
            name, sep, y, more = m.groups()
            pieces = [(m.start(), m.end() - len(more), (name, y))]
            p0 = m.end() - len(more)
            for ym in re.finditer(r', (\d{4})', more):
                pieces.append((p0 + ym.start() + 2, p0 + ym.end(), (name, ym.group(1))))
            if sep == ' (' and part[m.end():m.end() + 1] == ')':
                s_, e_, k_ = pieces[-1]; pieces[-1] = (s_, e_ + 1, k_)
            for s, e, key in pieces:
                rs = lk.get(key)
                if not rs or len(rs) > 1:
                    stats.setdefault('bad', []).append(key); continue
                if s > pos: out.append((part[pos:s], bold, None))
                if e <= pos: continue
                out.append((part[s:e], bold, rs[0])); rs[0].used += 1; pos = e
        if pos < len(part): out.append((part[pos:], bold, None))
    return out

# ---------------------------------------------------------------- DOCX
PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'widowControl', 'numPr', 'pBdr', 'shd', 'tabs', 'spacing', 'ind', 'jc', 'outlineLvl', 'rPr']
def order_ppr(inner):
    els = re.findall(r'(<w:(\w+)[^>]*/>|<w:(\w+)[^>]*>.*?</w:\3>)', inner)
    assert ''.join(e[0] for e in els) == inner, inner
    return ''.join(e[0] for e in sorted(els, key=lambda e: PPR_ORDER.index(e[1] or e[2])))

FONT_E = 'Times New Roman'; FONT_C = '標楷體'
W_NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
        'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" mc:Ignorable="w14"')
EMU = 12700  # per point

class Docx:
    GITHUB_BLOB_BASE = 'https://github.com/hauchiehlin-ops/fen_paper/blob/main'

    def __init__(self, lk, pat, outdir, link_mode='cloud'):
        self.lk, self.pat, self.outdir = lk, pat, outdir
        self.link_mode = link_mode
        self.body = []; self.rels = []; self.stats = {}; self.shape_id = 100
        self.html = []

    def cloud_url(self, path):
        if not path:
            return None
        norm_p = path.replace('\\', '/')
        if 'Plan_fen/' in norm_p:
            rel = norm_p[norm_p.index('Plan_fen/'):]
        else:
            rel = norm_p
        parts = rel.split('/')
        encoded = '/'.join(urllib.parse.quote(p) for p in parts)
        return f'{self.GITHUB_BLOB_BASE}/{encoded}'

    # links ---------------------------------------------------------
    def target(self, r):
        if r.path:
            if self.link_mode == 'cloud':
                return self.cloud_url(r.path)
            rel = os.path.relpath(r.path, self.outdir)
            # keep non-ASCII raw (Word for Mac does not decode %XX in Chinese folder names)
            return ''.join({'%': '%25', ' ': '%20', '#': '%23', '?': '%3F'}.get(c, c) for c in rel)
        return r.doi

    def html_target(self, r):
        if r.path:
            if self.link_mode == 'cloud':
                return self.cloud_url(r.path)
            return urllib.parse.quote(os.path.relpath(r.path, self.outdir))
        return r.doi

    def rid(self, url):
        for a, b in self.rels:
            if b == url: return a
        a = f'rIdL{len(self.rels) + 1}'; self.rels.append((a, url)); return a

    # runs ------------------------------------------------------------
    @staticmethod
    def rpr(bold=False, italic=False, size=None, link=False, extra=''):
        s = f'<w:rFonts w:ascii="{FONT_E}" w:hAnsi="{FONT_E}" w:eastAsia="{FONT_C}" w:cs="{FONT_E}"/>'
        if link: s = '<w:rStyle w:val="Hyperlink"/>' + s
        if bold: s += '<w:b/><w:bCs/>'
        if italic: s += '<w:i/><w:iCs/>'
        if extra.startswith('<w:color'): s += extra; extra = ''
        if size: s += f'<w:sz w:val="{int(size*2)}"/><w:szCs w:val="{int(size*2)}"/>'
        s += extra
        return f'<w:rPr>{s}</w:rPr>'

    def run(self, t, **k):
        return f'<w:r>{self.rpr(**k)}<w:t xml:space="preserve">{escape(t)}</w:t></w:r>'

    def runs(self, text, size=None, bold=False, extra=''):
        x = ''; h = ''
        for t, b, ref in segments(text, self.lk, self.pat, self.stats):
            bb = b or bold
            if ref:
                x += f'<w:hyperlink r:id="{self.rid(self.target(ref))}" w:history="1">{self.run(t, bold=bb, size=size, link=True, extra=extra)}</w:hyperlink>'
                cls = 'cite' if ref.path else 'cite doi'
                seg = f'<a class="{cls}" href="{html.escape(self.html_target(ref))}" target="_blank">{html.escape(t)}</a>'
            else:
                x += self.run(t, bold=bb, size=size, extra=extra); seg = html.escape(t)
            h += f'<b>{seg}</b>' if b else seg
        return x, h

    def para(self, text, ppr='', size=None, bold=False, extra='', tag='p', cls=''):
        x, h = self.runs(text, size, bold, extra)
        self.body.append(f'<w:p><w:pPr>{ppr}</w:pPr>{x}</w:p>')
        c = f' class="{cls}"' if cls else ''
        self.html.append(f'<{tag}{c}>{h}</{tag}>')

    # block helpers ---------------------------------------------------------
    SP = '<w:spacing w:before="0" w:after="0" w:line="440" w:lineRule="exact"/>'
    def p(self, t): self.para(t, '<w:jc w:val="both"/>' + self.SP + '<w:ind w:firstLineChars="200" w:firstLine="480"/>')
    def plain(self, t, ind=0): self.para(t, '<w:jc w:val="both"/>' + self.SP + (f'<w:ind w:left="{ind}"/>' if ind else ''), cls='plain')
    def item(self, t, ind=480): self.para(t, '<w:jc w:val="both"/>' + self.SP + f'<w:ind w:left="{ind}" w:hanging="480"/>', cls='item')
    def hyp(self, t): self.para(t, '<w:jc w:val="both"/>' + self.SP + '<w:ind w:left="960" w:hanging="480"/>', bold=True, cls='hyp')
    def q(self, t): self.para(t, '<w:jc w:val="both"/>' + self.SP + '<w:ind w:firstLineChars="200" w:firstLine="480"/>', bold=True, cls='q')
    def title(self, t):
        self.para(t, '<w:pStyle w:val="Title"/><w:jc w:val="center"/><w:spacing w:before="0" w:after="240" w:line="480" w:lineRule="exact"/>', size=16, bold=True, tag='h1')
    def h1(self, t): self.para(t, '<w:pStyle w:val="Heading1"/><w:keepNext/><w:spacing w:before="240" w:after="120" w:line="440" w:lineRule="exact"/>', size=14, bold=True, tag='h2')
    def h2(self, t):
        self.para(t, '<w:pStyle w:val="Heading2"/><w:keepNext/><w:spacing w:before="160" w:after="80" w:line="440" w:lineRule="exact"/>', bold=True,
                  extra='<w:bdr w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>', tag='h3')
    def h3(self, t): self.para(t, '<w:pStyle w:val="Heading3"/><w:keepNext/><w:spacing w:before="120" w:after="40" w:line="440" w:lineRule="exact"/><w:ind w:left="480" w:hanging="480"/>', bold=True, tag='h4')
    def h4(self, t): self.para(t, '<w:keepNext/><w:spacing w:before="120" w:after="40" w:line="440" w:lineRule="exact"/>', bold=True, extra='<w:u w:val="single"/>', tag='h5', cls='u')
    def h5(self, t): self.para(t, '<w:keepNext/>' + self.SP, bold=True, tag='h6')
    def caption(self, t, keep=True):
        self.para(t, ('<w:keepNext/>' if keep else '') + '<w:jc w:val="center"/><w:spacing w:before="120" w:after="80" w:line="360" w:lineRule="exact"/>', tag='p', cls='cap')
    def pagebreak(self):
        self.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    # tables ---------------------------------------------------------------
    def table(self, caption, widths, rows, header=1, size=10.5, fills=None, center_cols=(), cont=None, keep=False):
        """rows: list of list of cells; a cell is str or dict(t=, span=, vm='r'|'c', fill=, c=bool, b=bool)."""
        if caption: self.caption(caption)
        tw = sum(widths)
        x = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>' % tw +
             ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="000000"/>' for s in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']) +
             '</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="57" w:type="dxa"/><w:right w:w="57" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>' +
             ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>']
        h = ['<div class="tw"><table>' + '<colgroup>' + ''.join(f'<col style="width:{w*100/tw:.1f}%">' for w in widths) + '</colgroup>']
        for ri, row in enumerate(rows):
            hdr = ri < header
            x.append('<w:tr>' + ('<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' if hdr else '<w:trPr><w:cantSplit/></w:trPr>'))
            h.append('<tr>')
            ci = 0
            for cell in row:
                if isinstance(cell, str): cell = dict(t=cell)
                span = cell.get('span', 1); w = sum(widths[ci:ci + span]); ci += span
                fill = cell.get('fill') or ('DDEBF7' if hdr else None)
                tcpr = f'<w:tcW w:w="{w}" w:type="dxa"/>'
                if span > 1: tcpr += f'<w:gridSpan w:val="{span}"/>'
                if cell.get('vm') == 'r': tcpr += '<w:vMerge w:val="restart"/>'
                if cell.get('vm') == 'c': tcpr += '<w:vMerge/>'
                if fill: tcpr += f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
                tcpr += '<w:vAlign w:val="center"/>'
                center = hdr or cell.get('c') or (ci - span) in center_cols
                paras = []; hp = []
                for line in (cell.get('t', '') or '').split('\n'):
                    rx, rh = self.runs(line, size, bold=hdr or cell.get('b', False))
                    paras.append(f'<w:p><w:pPr>{"<w:keepNext/>" if keep and ri < len(rows) - 1 else ""}<w:spacing w:before="20" w:after="20" w:line="300" w:lineRule="exact"/><w:jc w:val="{"center" if center else "left"}"/></w:pPr>{rx}</w:p>')
                    hp.append(rh)
                x.append(f'<w:tc><w:tcPr>{tcpr}</w:tcPr>{"".join(paras)}</w:tc>')
                if cell.get('vm') != 'c':
                    tag = 'th' if hdr else 'td'
                    st = f' style="background:#{fill}"' if fill and not hdr else ''
                    cl = ' class="c"' if center else ''
                    rs = f' rowspan="{cell["rs"]}"' if cell.get('rs') else ''
                    h.append(f'<{tag}{cl}{st} colspan="{span}"{rs}>{"<br>".join(hp)}</{tag}>')
            x.append('</w:tr>'); h.append('</tr>')
        x.append('</w:tbl>'); h.append('</table></div>')
        self.body.append(''.join(x)); self.html.append(''.join(h))
        self.body.append('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="200" w:lineRule="exact"/></w:pPr></w:p>')

    # figures --------------------------------------------------------------
    def figure(self, fig, caption):
        W, H = fig.W, fig.H
        self.shape_id += 1
        kids = ''.join(self._shape(s) for s in fig.shapes)
        g = (f'<wpg:wgp><wpg:cNvGrpSpPr/><wpg:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{W*EMU}" cy="{H*EMU}"/>'
             f'<a:chOff x="0" y="0"/><a:chExt cx="{W*EMU}" cy="{H*EMU}"/></a:xfrm></wpg:grpSpPr>{kids}</wpg:wgp>')
        inline = (f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{W*EMU}" cy="{H*EMU}"/>'
                  f'<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{self.shape_id}" name="{escape(caption)}"/><wp:cNvGraphicFramePr/>'
                  f'<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup">{g}</a:graphicData></a:graphic></wp:inline>')
        dr = f'<mc:AlternateContent><mc:Choice Requires="wpg"><w:drawing>{inline}</w:drawing></mc:Choice></mc:AlternateContent>'
        self.body.append(f'<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/><w:spacing w:before="120" w:after="0"/></w:pPr><w:r>{dr}</w:r></w:p>')
        self.html.append(f'<figure>{fig.svg()}')
        self.caption(caption, keep=False)
        self.html[-1] = self.html[-1].replace('<p class="cap">', '<figcaption>').replace('</p>', '</figcaption>') + '</figure>'

    def _txbx(self, s):
        ps = ''
        for i, line in enumerate(s['text'].split('\n')):
            b = s.get('bold') or (s.get('bold1') and i == 0)
            col = s.get('color')
            ex = f'<w:color w:val="{col}"/>' if col else ''
            ps += (f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="{int(s.get("size",9.5)*24*1.18)}" w:lineRule="exact"/>'
                   f'<w:jc w:val="{s.get("align","center")}"/></w:pPr>{self.run(line, bold=b, size=s.get("size",9.5), extra=ex)}</w:p>')
        return f'<wps:txbx><w:txbxContent>{ps}</w:txbxContent></wps:txbx>'

    def _shape(self, s):
        self.shape_id += 1; sid = self.shape_id
        if s['kind'] == 'line':
            x1, y1, x2, y2 = s['x1'], s['y1'], s['x2'], s['y2']
            fh = ' flipH="1"' if x2 < x1 else ''; fv = ' flipV="1"' if y2 < y1 else ''
            ox, oy = min(x1, x2), min(y1, y2); cx, cy = abs(x2 - x1), abs(y2 - y1)
            dash = '<a:prstDash val="dash"/>' if s.get('dash') else ''
            head = '<a:tailEnd type="triangle" w="med" len="med"/>' if s.get('arrow', True) else ''
            if s.get('both'): head = '<a:headEnd type="triangle" w="med" len="med"/>' + head
            return (f'<wps:wsp><wps:cNvPr id="{sid}" name="Line {sid}"/><wps:cNvCnPr/><wps:spPr><a:xfrm{fh}{fv}><a:off x="{int(ox*EMU)}" y="{int(oy*EMU)}"/>'
                    f'<a:ext cx="{int(cx*EMU)}" cy="{int(cy*EMU)}"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
                    f'<a:ln w="{int(s.get("w",1)*EMU)}"><a:solidFill><a:srgbClr val="{s.get("lc","404040")}"/></a:solidFill>{dash}{head}</a:ln></wps:spPr><wps:bodyPr/></wps:wsp>')
        geom = {'rect': 'rect', 'round': 'roundRect', 'ellipse': 'ellipse', 'text': 'rect', 'rarrow': 'rightArrow', 'darrow': 'downArrow'}[s['kind']]
        fill = f'<a:solidFill><a:srgbClr val="{s["fill"]}"/></a:solidFill>' if s.get('fill') else '<a:noFill/>'
        if s['kind'] == 'text' or s.get('noline'):
            ln = '<a:ln><a:noFill/></a:ln>'
        else:
            dash = f'<a:prstDash val="{s["dash"]}"/>' if s.get('dash') else ''
            ln = f'<a:ln w="{int(s.get("lw",1)*EMU)}"><a:solidFill><a:srgbClr val="{s.get("lc","404040")}"/></a:solidFill>{dash}</a:ln>'
        av = '<a:avLst><a:gd name="adj" fmla="val 12000"/></a:avLst>' if geom == 'roundRect' else '<a:avLst/>'
        tx = self._txbx(s) if s.get('text') else ''
        anchor = s.get('anchor', 'ctr')
        vert = 'eaVert' if s.get('vert') else 'horz'
        return (f'<wps:wsp><wps:cNvPr id="{sid}" name="Shape {sid}"/><wps:cNvSpPr/><wps:spPr><a:xfrm><a:off x="{int(s["x"]*EMU)}" y="{int(s["y"]*EMU)}"/>'
                f'<a:ext cx="{int(s["w"]*EMU)}" cy="{int(s["h"]*EMU)}"/></a:xfrm><a:prstGeom prst="{geom}">{av}</a:prstGeom>{fill}{ln}</wps:spPr>{tx}'
                f'<wps:bodyPr rot="0" vert="{vert}" wrap="square" lIns="25400" tIns="12700" rIns="25400" bIns="12700" anchor="{anchor}" anchorCtr="0"><a:noAutofit/></wps:bodyPr></wps:wsp>')

    # references -----------------------------------------------------------
    def references(self, refs):
        for r in sorted(refs, key=lambda r: r.sortkey()):
            url = self.target(r)
            jx = r.journal
            x = self.run(f'{r.auth} ({r.year}). ')
            x += f'<w:hyperlink r:id="{self.rid(url)}" w:history="1">{self.run(r.title + ".", link=True)}</w:hyperlink>'
            x += self.run(' ') + self.run(jx, italic=True) + self.run(r.rest)
            self.body.append(f'<w:p><w:pPr><w:jc w:val="both"/><w:spacing w:before="0" w:after="0" w:line="400" w:lineRule="exact"/><w:ind w:left="480" w:hanging="480"/></w:pPr>{x}</w:p>')
            hu = html.escape(self.html_target(r))
            cls = 'cite' if r.path else 'cite doi'
            self.html.append(f'<p class="ref">{html.escape(r.auth)} ({r.year}). <a class="{cls}" href="{hu}" target="_blank">{html.escape(r.title)}.</a> '
                             f'<i>{html.escape(jx)}</i>{html.escape(r.rest)}</p>')

    # save ------------------------------------------------------------------
    def save(self, path, title):
        sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdF1"/><w:pgSz w:w="11906" w:h="16838"/>'
                '<w:pgMar w:top="1247" w:right="1134" w:bottom="1247" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/>'
                '<w:docGrid w:type="lines" w:linePitch="360"/></w:sectPr>')
        doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {W_NS}><w:body>{"".join(self.body)}{sect}</w:body></w:document>'
        doc = re.sub(r'<w:pPr>(.*?)</w:pPr>', lambda m: '<w:pPr>' + order_ppr(m.group(1)) + '</w:pPr>', doc)
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rIdS1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                '<Relationship Id="rIdS2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
                '<Relationship Id="rIdF1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>' +
                ''.join(f'<Relationship Id="{a}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{escape(u)}" TargetMode="External"/>' for a, u in self.rels) +
                '</Relationships>')
        rpr = f'<w:rFonts w:ascii="{FONT_E}" w:hAnsi="{FONT_E}" w:eastAsia="{FONT_C}" w:cs="{FONT_E}"/><w:kern w:val="2"/><w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="en-US" w:eastAsia="zh-TW"/>'
        def hst(i, name, lvl):
            return (f'<w:style w:type="paragraph" w:styleId="{i}"><w:name w:val="{name}"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>'
                    f'<w:pPr><w:keepNext/><w:outlineLvl w:val="{lvl}"/></w:pPr><w:rPr><w:b/></w:rPr></w:style>')
        styles = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                  f'<w:docDefaults><w:rPrDefault><w:rPr>{rpr}</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:widowControl/><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
                  '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
                  + hst('Title', 'Title', 0).replace('<w:outlineLvl w:val="0"/>', '') + hst('Heading1', 'heading 1', 0) + hst('Heading2', 'heading 2', 1) + hst('Heading3', 'heading 3', 2) +
                  '<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont"><w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>'
                  '<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/><w:basedOn w:val="DefaultParagraphFont"/><w:rPr><w:color w:val="0563C1"/><w:u w:val="single"/></w:rPr></w:style>'
                  '<w:style w:type="paragraph" w:styleId="Footer"><w:name w:val="footer"/><w:basedOn w:val="Normal"/></w:style>'
                  '</w:styles>')
        settings = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    '<w:defaultTabStop w:val="480"/><w:characterSpacingControl w:val="compressPunctuation"/><w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat></w:settings>')
        footer = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr {W_NS}><w:p><w:pPr><w:pStyle w:val="Footer"/><w:jc w:val="center"/></w:pPr>'
                  '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>'
                  '<w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
        ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
              '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
              '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
              '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
              '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
              '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
              '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>')
        r0 = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
              '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
              '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
              '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>')
        now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                f'<dc:title>{escape(title)}</dc:title><dc:creator>Dr. Barret Lin</dc:creator>'
                f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>')
        app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
               '<Application>Microsoft Office Word</Application></Properties>')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', r0)
            z.writestr('word/document.xml', doc); z.writestr('word/_rels/document.xml.rels', rels)
            z.writestr('word/styles.xml', styles); z.writestr('word/settings.xml', settings); z.writestr('word/footer1.xml', footer)
            z.writestr('docProps/core.xml', core); z.writestr('docProps/app.xml', app)

    def save_html(self, path, title):
        css = '''
:root{--bg:#fff;--fg:#1f2328;--muted:#59636e;--line:#c9d1d9;--link:#0b5cad;--note:#f3f6fa;--th:#ddebf7}
@media (prefers-color-scheme:dark){:root{--bg:#16181d;--fg:#e6e8eb;--muted:#9aa3ad;--line:#3a3f47;--link:#7fb4ff;--note:#1f242c;--th:#22324a}}
body{background:var(--bg);color:var(--fg);font:16px/1.85 "BiauKai","DFKai-SB","標楷體","Noto Serif TC",serif;max-width:900px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:1.5em;text-align:center;line-height:1.4} h2{font-size:1.3em;margin-top:2em} h3{font-size:1.1em;display:inline-block;border:1px solid var(--fg);padding:0 4px;margin:1.4em 0 .4em}
h4,h5,h6{font-size:1em;margin:1.1em 0 .3em} h5.u{text-decoration:underline}
p{margin:.2em 0;text-align:justify;text-indent:2em} p.plain,p.item,p.hyp,p.ref,p.cap{text-indent:0} p.item{padding-left:2em;text-indent:-2em}
p.hyp{font-weight:bold;padding-left:4em;text-indent:-2em} p.q{font-weight:bold} p.cap,figcaption{text-align:center;color:var(--muted);margin:1em 0 .4em}
p.ref{padding-left:2em;text-indent:-2em}
.tw{overflow-x:auto} table{border-collapse:collapse;width:100%;margin:.3em 0 1.2em;font-size:.88em;line-height:1.5} th,td{border:1px solid var(--line);padding:4px 6px;vertical-align:middle} th{background:var(--th)} .c{text-align:center}
a{color:var(--link)} a.cite.doi{text-decoration-style:dotted}
figure{margin:1.5em 0} figure svg{width:100%;height:auto;background:#fff;border-radius:6px}
.note{background:var(--note);border:1px solid var(--line);border-radius:8px;padding:12px 16px;font-size:.9em;text-indent:0;font-family:sans-serif}
@media (prefers-color-scheme:dark){td[style]{color:#111}}
'''
        note = ('<div class="note">網頁版與同時間戳的 Word 版內容相同。點擊內文的文獻引用或參考文獻標題，會在新分頁線上開啟論文全文 PDF（未取得 PDF 的文獻則開啟官方 DOI 頁面），無需額外下載資料夾，任何裝置皆可直接點擊閱讀。Word 版的圖為可編輯的繪圖物件。</div>')
        page = (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{html.escape(title)}</title><style>{css}</style></head><body>{note}{"".join(self.html)}</body></html>')
        open(path, 'w', encoding='utf-8').write(page)


# ---------------------------------------------------------------- figure spec (shared by DOCX shapes and SVG)
class Fig:
    def __init__(self, W, H): self.W, self.H, self.shapes = W, H, []
    def box(self, x, y, w, h, text='', kind='rect', **k):
        self.shapes.append(dict(kind=kind, x=x, y=y, w=w, h=h, text=text, **k)); return self
    def text(self, x, y, w, h, text, **k): return self.box(x, y, w, h, text, kind='text', **k)
    def line(self, x1, y1, x2, y2, **k):
        self.shapes.append(dict(kind='line', x1=x1, y1=y1, x2=x2, y2=y2, **k)); return self

    def svg(self):
        out = [f'<svg viewBox="0 0 {self.W} {self.H}" xmlns="http://www.w3.org/2000/svg" font-family="BiauKai,DFKai-SB,標楷體,Noto Serif TC,serif">'
               '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#404040"/></marker></defs>']
        for s in self.shapes:
            if s['kind'] == 'line':
                d = ' stroke-dasharray="5,3"' if s.get('dash') else ''
                m = ' marker-end="url(#ah)"' if s.get('arrow', True) else ''
                if s.get('both'): m += ' marker-start="url(#ah)"'
                out.append(f'<line x1="{s["x1"]}" y1="{s["y1"]}" x2="{s["x2"]}" y2="{s["y2"]}" stroke="#{s.get("lc","404040")}" stroke-width="{s.get("w",1)}"{d}{m}/>')
                continue
            x, y, w, h = s['x'], s['y'], s['w'], s['h']
            fill = '#' + s['fill'] if s.get('fill') else 'none'
            stroke = 'none' if s['kind'] == 'text' or s.get('noline') else '#' + s.get('lc', '404040')
            dash = ' stroke-dasharray="4,3"' if s.get('dash') else ''
            sw = s.get('lw', 1)
            if s['kind'] == 'ellipse':
                out.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
            elif s['kind'] == 'rarrow':
                hh = h / 4; tip = min(h * .6, w * .4)
                pts = f'{x},{y+hh} {x+w-tip},{y+hh} {x+w-tip},{y} {x+w},{y+h/2} {x+w-tip},{y+h} {x+w-tip},{y+h-hh} {x},{y+h-hh}'
                out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
            elif s['kind'] == 'darrow':
                ww = w / 4; tip = min(w * .6, h * .4)
                pts = f'{x+ww},{y} {x+w-ww},{y} {x+w-ww},{y+h-tip} {x+w},{y+h-tip} {x+w/2},{y+h} {x},{y+h-tip} {x+ww},{y+h-tip}'
                out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
            else:
                rx = min(w, h) * 0.12 if s['kind'] == 'round' else 0
                out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
            if s.get('text') and s.get('vert'):
                size = s.get('size', 9.5)
                out.append(f'<text x="{x+w/2}" y="{y+h/2}" font-size="{size}" text-anchor="middle" dominant-baseline="middle" style="writing-mode:vertical-rl;glyph-orientation-vertical:0" fill="#000"{" font-weight=\"bold\"" if s.get("bold") else ""}>{html.escape(s["text"])}</text>')
            elif s.get('text'):
                lines = s['text'].split('\n'); size = s.get('size', 9.5); lh = size * 1.18
                al = s.get('align', 'center')
                tx = x + w / 2 if al == 'center' else x + 3
                anchor = 'middle' if al == 'center' else 'start'
                va = s.get('anchor', 'ctr')
                y0 = (y + h / 2 - lh * len(lines) / 2 if va == 'ctr' else y + 2) + size * 0.95
                col = '#' + s['color'] if s.get('color') else '#000'
                for i, l in enumerate(lines):
                    b = s.get('bold') or (s.get('bold1') and i == 0)
                    out.append(f'<text x="{tx}" y="{y0+i*lh:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{col}"{" font-weight=\"bold\"" if b else ""}>{html.escape(l)}</text>')
        out.append('</svg>')
        return ''.join(out)
