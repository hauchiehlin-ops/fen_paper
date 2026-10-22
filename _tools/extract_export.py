"""Extract the file saved by the Docs export tool (raw JSON or a JSON array of text blocks) -> binary/text file.
usage: python3 extract_export.py <tool-result.txt> <out>"""
import json,base64,sys
j=json.load(open(sys.argv[1]))
if isinstance(j,list):
    for blk in j:
        t=blk.get('text','').strip()
        if t.startswith('{'): j=json.loads(t); break
open(sys.argv[2],'wb').write(base64.b64decode(j['data']['bytes_b64'])); print('rev',j['rev'],j['data']['format'])
