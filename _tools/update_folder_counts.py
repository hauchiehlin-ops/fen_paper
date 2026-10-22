"""Write Plan_fen/MMDD-HHMM_各主題資料夾文獻數量.docx: per-folder PDF counts, how many are cited by the latest plan,
and what was added/removed since the previous record. Previous record goes to the volume Trash.
usage: python3 update_folder_counts.py [paper_root]"""
import os,re,sys,json,zipfile,subprocess,datetime,shutil
root=sys.argv[1] if len(sys.argv)>1 else '/Volumes/Mobil/fen-data/paper'
plan=os.path.join(root,'Plan_fen'); tools=os.path.join(root,'_tools'); snapf=os.path.join(tools,'folder_snapshot.json')
trash=f'/Volumes/Mobil/.Trashes/{os.getuid()}'
folders=sorted(d for d in os.listdir(plan) if os.path.isdir(os.path.join(plan,d)) and re.match(r'\d\. ',d))
cur={d:sorted(f for f in os.listdir(os.path.join(plan,d)) if f.endswith('.pdf') and not f.startswith('._')) for d in folders}
# cited PDFs = relative link targets of the newest plan docx
plans=sorted(f for f in os.listdir(plan) if re.match(r'\d{4}-\d{4}_兩年期研究計畫書\.docx$',f))
cited=set(); planname=plans[-1] if plans else '（尚無計畫書）'
if plans:
    rels=zipfile.ZipFile(os.path.join(plan,plans[-1])).read('word/_rels/document.xml.rels').decode()
    for t in re.findall(r'Target="([^"]+)" TargetMode="External"',rels):
        if not t.startswith('http'):
            cited.add(os.path.normpath(t.replace('%20',' ').replace('%23','#').replace('%3F','?').replace('%25','%')))
prev=json.load(open(snapf)) if os.path.exists(snapf) else None
now=datetime.datetime.now(); ts=now.strftime('%m%d-%H%M')
L=[f'# 各主題資料夾文獻數量（{now:%Y-%m-%d %H:%M}）','',
   f'統計範圍：Plan_fen 內五個主題資料夾的 PDF。「計畫書引用」依 {planname} 的文獻連結計算。'+('' if prev else '本次為第一份紀錄，尚無前次可比較。'),'',
   '## 數量統計','','| 資料夾 | PDF 數量 | 計畫書引用 | 未引用 | 預印本／不完整版 | 與前次相比 |','|---|---|---|---|---|---|']
tot=[0,0,0,0]; changes=[]
for d in folders:
    fs=cur[d]; c=sum(1 for f in fs if os.path.join(d,f) in cited)
    pre=sum(1 for f in fs if re.search(r'\((arXiv preprint|SSRN preprint|abstract only|\d{4} working paper)\)\.pdf$',f))
    if prev is None: delta='—'
    else:
        old=set(prev['files'].get(d,[])); add=sorted(set(fs)-old); rem=sorted(old-set(fs))
        delta=('+%d'%len(add) if add else '')+(' −%d'%len(rem) if rem else '') or '無變動'
        changes+= [(d,'新增',f) for f in add]+[(d,'移除',f) for f in rem]
    L.append(f'| {d} | {len(fs)} | {c} | {len(fs)-c} | {pre} | {delta.strip()} |')
    tot=[tot[0]+len(fs),tot[1]+c,tot[2]+len(fs)-c,tot[3]+pre]
prevtot=sum(len(v) for v in prev['files'].values()) if prev else None
L.append(f'| 合計 | {tot[0]} | {tot[1]} | {tot[2]} | {tot[3]} | {"—" if prev is None else (("+%d" if tot[0]>prevtot else "−%d") % abs(tot[0]-prevtot) if tot[0]!=prevtot else "無變動")} |')
SUF=r' \((arXiv preprint|SSRN preprint|abstract only|\d{4} working paper)\)\.pdf$'
lab={'arXiv preprint':'arXiv 預印本','SSRN preprint':'SSRN 預印本','abstract only':'僅摘要','working paper':'工作論文'}
pre_rows=[]
for d in folders:
    for f in cur[d]:
        m=re.search(SUF,f)
        if not m: continue
        formal=re.sub(SUF,'.pdf',f); has_formal=formal in cur[d]
        here=os.path.join(d,f) in cited; via_formal=has_formal and os.path.join(d,formal) in cited
        if not (here or via_formal): continue
        kind=next(v for k,v in lab.items() if k in m.group(1))
        target='此檔（尚無正式版）' if here else '同資料夾的期刊正式版'
        advice='待下載期刊正式版後替換' if here else '已有正式版，此檔可保留或刪除'
        pre_rows.append(f'| {d.split(" (")[0]} | {re.sub(SUF,"",f)} | {kind} | {target} | {advice} |')
L+=['','## 計畫書有引用的預印本／不完整版','']
if pre_rows:
    L+=[f'上表「預印本／不完整版」中，共 {len(pre_rows)} 篇的論文在計畫書內有引用：','','| 資料夾 | 文獻 | 版本 | 計畫書連結指向 | 處理建議 |','|---|---|---|---|---|']+pre_rows
else: L.append('計畫書引用的文獻中沒有預印本或不完整版。')
L+=['','## 與前次紀錄的增刪明細','']
if prev is None: L.append('本次為第一份紀錄。')
else:
    L.append(f'前次紀錄時間：{prev["time"]}。')
    if changes:
        L+=['','| 資料夾 | 變動 | 檔名 |','|---|---|---|']+[f'| {d} | {k} | {f} |' for d,k,f in changes]
    else: L.append('各資料夾檔案無增刪。')
L+=['','## 各資料夾檔案清單','']
for d in folders:
    L+=['',f'## {d}（{len(cur[d])} 篇）','']+[('★ ' if os.path.join(d,f) in cited else '　 ')+f for f in cur[d]]
L+=['','★ 表示計畫書有引用。']
md=os.path.join(tools,'_counts.md'); open(md,'w',encoding='utf-8').write('\n'.join(L))
out=os.path.join(plan,f'{ts}_各主題資料夾文獻數量.docx')
for f in os.listdir(plan):
    if re.match(r'\d{4}-\d{4}_各主題資料夾文獻數量\.docx$',f) and os.path.join(plan,f)!=out:
        shutil.move(os.path.join(plan,f),os.path.join(trash,f))
        if os.path.exists(os.path.join(plan,'._'+f)): shutil.move(os.path.join(plan,'._'+f),os.path.join(trash,'._'+f+now.strftime('.%s')))
subprocess.run([sys.executable,os.path.join(tools,'make_download_list.py'),md,out],check=True,capture_output=True)
json.dump({'time':now.strftime('%Y-%m-%d %H:%M'),'files':cur},open(snapf,'w'),ensure_ascii=False,indent=1)
os.remove(md)
print(out); print('\n'.join(l for l in L if l.startswith('| ') and '---' not in l)[:1500])
