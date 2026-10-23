from lib import Fig
from figures import C1, C2, C3, CG, CT, BLUE

ORANGE = 'C55A11'

def fig_slr():
    f = Fig(480, 330)
    f.text(0, 4, 70, 30, '辨識', size=9, bold=True)
    f.text(0, 104, 70, 30, '篩選', size=9, bold=True)
    f.text(0, 200, 70, 30, '納入', size=9, bold=True)
    f.box(76, 4, 186, 52, '主題資料夾 2024–2026 年文獻\n（五個主題資料夾）\nn = 119', fill=CG, size=8.5, bold1=True)
    f.box(282, 4, 194, 52, '網路檢索補充：出版社頁面、\nRePEc／大學典藏、期刊新聞稿\nn = 48', fill=CG, size=8.5, bold1=True)
    f.line(169, 56, 169, 84); f.line(379, 56, 379, 84)
    f.box(76, 84, 186, 46, '題名與摘要篩選後\n與主題相關：n = 21', fill='FFFFFF', size=8.5, bold1=True)
    f.box(282, 84, 194, 46, '期刊等級與書目核對\n（A 級 FT50；B 級 SSCI、IF > 2）', fill='FFFFFF', size=8.5, bold1=True)
    f.box(76, 140, 186, 40, '排除 n = 10（分析式模型、\n非銷售情境、勘誤、期刊等級）', fill='F2F2F2', size=8, lc='7F7F7F')
    f.box(282, 140, 194, 40, '排除 n = 9；保留候選待全文篩選\nn = 16（列於待下載清單）', fill='F2F2F2', size=8, lc='7F7F7F')
    f.line(169, 130, 169, 140, arrow=False); f.line(379, 130, 379, 140, arrow=False)
    f.line(169, 180, 169, 200); f.line(379, 180, 379, 200)
    f.box(76, 200, 186, 34, '納入 n = 11', fill=C1, size=9, bold=True)
    f.box(282, 200, 194, 34, '納入 n = 23', fill=C1, size=9, bold=True)
    f.line(169, 234, 230, 256); f.line(379, 234, 320, 256)
    f.box(140, 256, 240, 40, '近五年核心文獻 n = 34（A 級 14 篇、B 級 20 篇）\n＋理論基礎文獻 n = 10（2021 年以前）', fill=CT, size=8.5, bold1=True, lc=BLUE, lw=1.3)
    f.text(76, 302, 400, 26, '正式回顧（計畫第 1 個月）：依表 3 之檢索式於 Web of Science 與 Scopus 重新執行，\n本圖數字屬計畫書撰寫階段之初步回顧。', size=8, color='7F7F7F', align='left')
    return f

def fig1():
    f = Fig(480, 560)
    f.line(40, 238, 40, 8); f.line(40, 238, 470, 238)
    f.text(0, 0, 38, 40, '研究\n層次', size=8.5, bold=True)
    f.text(14, 40, 24, 16, '高', size=9); f.text(14, 205, 24, 16, '低', size=9)
    f.text(420, 240, 60, 16, '時間構面', size=8.5)
    f.box(52, 14, 330, 218, kind='ellipse', lw=1)
    f.box(56, 82, 236, 148, kind='ellipse', lw=1)
    f.box(60, 146, 140, 82, kind='ellipse', lw=1)
    f.text(170, 24, 190, 44, '第三階段【推廣】\n以 SEM 與多群組 SEM 驗證\n直播購物的購後路徑', size=8.5, bold1=True)
    f.text(118, 90, 160, 44, '第二階段【檢驗】\n以實驗設計檢驗主播類型\n× 話術 × 產品類型', size=8.5, bold1=True)
    f.text(66, 160, 128, 56, '第一階段【發現】\n以 MEC 探索 AI 與\n真人主播的價值鏈', size=8.5, bold1=True)
    f.box(388, 92, 84, 66, 'AI 虛擬主播與\n真人主播的\n價值說服與\n購後後果', kind='rect', fill='FFFFFF', bold=True, size=8.5, lw=1.2)
    f.line(382, 124, 388, 124)
    f.text(46, 242, 120, 26, '第一階段\n2027.08–2028.01', size=8)
    f.text(168, 242, 120, 26, '第二階段\n2028.02–2028.10', size=8)
    f.text(290, 242, 120, 26, '第三階段\n2028.06–2029.04', size=8)
    f.line(46, 274, 250, 274, arrow=False, dash=True); f.text(110, 268, 80, 14, '第一年', size=8, fill='FFFFFF')
    f.line(256, 274, 470, 274, arrow=False, dash=True); f.text(320, 268, 80, 14, '第二年', size=8, fill='FFFFFF')
    f.box(225, 284, 30, 22, kind='darrow', fill='D9D9D9', lc='7F7F7F')
    f.text(118, 310, 96, 26, '價值鏈改寫為\n實驗話術', size=8, color=BLUE)
    f.text(278, 310, 96, 26, '價值傾向量表\n成為分組變數', size=8, color=BLUE)
    t1 = '第一階段【發現】\n方法：MEC 軟式階梯訪談\n對象：AI／真人主播購買者\n分析：人工編碼、HVM\n產出：價值鏈與價值訴求'
    t2 = '第二階段【檢驗】\n方法：2×2×2 實驗設計\n＋AI 身分揭露實驗\n結果：購買與購後預期\n產出：主播 × 話術對照表'
    t3 = '第三階段【推廣】\n方法：SEM、多群組 SEM\n對象：直播實際購買者\n結果：滿意、退貨、再購\n產出：購後路徑模型'
    f.box(8, 340, 142, 86, t1, kind='round', fill=C1, size=8.5, bold1=True, align='left', anchor='t')
    f.box(169, 340, 142, 86, t2, kind='round', fill=C2, size=8.5, bold1=True, align='left', anchor='t')
    f.box(330, 340, 142, 86, t3, kind='round', fill=C3, size=8.5, bold1=True, align='left', anchor='t')
    f.line(150, 383, 169, 383); f.line(311, 383, 330, 383)
    for x in (79, 240, 401): f.line(x, 426, x, 446, arrow=False, dash=True)
    f.box(8, 446, 464, 52, '共同基礎（三階段共用）\n品類庫：運動鞋（錨定）、美妝保養、居家家具，各含享樂型與實用型｜共同量表：價值傾向、主播知覺\n效度程序：預先註冊、操弄檢驗、刺激抽樣、共同方法變異檢查、測量恆等性',
          kind='round', fill=CG, size=8.5, bold1=True, align='left')
    f.line(240, 498, 240, 514)
    f.box(8, 514, 464, 34, '實務轉譯（主題五）：中小企業「主播類型 × 話術 × 品類」決策表、AI 主播揭露與退貨溝通指引',
          kind='round', fill=CT, size=9, bold=True, lc=BLUE, lw=1.3)
    return f

def fig2():
    f = Fig(480, 300)
    f.box(4, 26, 124, 196, kind='rect', dash='dash', lc='2E75B6')
    f.text(4, 8, 124, 16, '操弄變數（2×2×2，受試者間）', size=8, color='2E75B6', bold=True)
    f.box(14, 36, 104, 52, '主播類型\nAI 虛擬主播／\n真人主播', fill='FFFFFF', size=8.5, bold1=True)
    f.box(14, 98, 104, 52, '價值訴求話術\n功能價值／\n情感社會價值', fill='FFFFFF', size=8.5, bold1=True)
    f.box(14, 160, 104, 52, '產品類型\n享樂型／實用型\n（三品類各一組）', fill='FFFFFF', size=8.5, bold1=True)
    f.box(170, 34, 96, 32, '溫暖感', kind='ellipse', size=9)
    f.box(170, 82, 96, 32, '能力感', kind='ellipse', size=9)
    f.box(170, 150, 96, 36, '說服意圖知覺', kind='ellipse', size=9)
    f.box(318, 50, 158, 44, '購買意圖\n加入購物車（行為）', kind='rect', size=8.5, bold1=True)
    f.box(318, 144, 158, 48, '一週後預期後悔\n退貨意圖', kind='rect', size=8.5, bold1=True)
    f.line(118, 62, 171, 52); f.line(118, 66, 171, 96); f.line(118, 70, 172, 164)
    f.text(140, 120, 24, 14, 'H4', size=8.5, bold=True)
    f.line(266, 50, 318, 66); f.line(266, 98, 318, 76); f.text(276, 40, 24, 14, 'H3', size=8.5, bold=True)
    f.line(266, 168, 318, 168); f.text(282, 172, 24, 14, 'H4', size=8.5, bold=True)
    f.line(118, 124, 150, 124, arrow=False); f.line(150, 124, 150, 20, arrow=False); f.line(150, 20, 396, 20, arrow=False); f.line(396, 20, 396, 50)
    f.text(230, 4, 160, 14, 'H1：主播類型 × 話術交互作用', size=8.5, bold=True)
    f.line(118, 186, 300, 120, dash=True); f.line(300, 120, 318, 82, dash=True); f.text(256, 128, 26, 14, 'H2', size=8.5, bold=True)
    f.box(96, 236, 330, 56, '研究 2c：AI 身分揭露（僅 AI 主播）\n不標示／平台標示「AI 生成」／主播自述「我是 AI 主播」\n→ 信任、購買意圖（H5、H6）', kind='rect', dash='dash', lc=ORANGE, size=8.5, bold1=True)
    f.line(330, 236, 360, 192, dash=True, lc=ORANGE)
    return f

def fig3():
    f = Fig(480, 330)
    f.box(4, 40, 96, 34, '主播溫暖感', kind='ellipse', size=9)
    f.box(4, 96, 96, 34, '主播能力感', kind='ellipse', size=9)
    f.box(4, 176, 96, 40, '感知互動強度\n（熱烈氣氛）', kind='ellipse', size=8.5)
    f.box(136, 66, 84, 36, '信任', kind='ellipse', size=9)
    f.box(136, 176, 84, 40, '購前期望', kind='ellipse', size=9)
    f.box(254, 118, 86, 40, '期望確認', kind='ellipse', size=9)
    f.box(372, 60, 104, 36, '購後滿意', kind='ellipse', size=9)
    f.box(392, 128, 84, 40, '退貨行為／\n退貨意圖', size=8.5, bold1=True)
    f.box(392, 196, 84, 34, '再購意圖', size=8.5, bold1=True)
    f.line(100, 57, 137, 78); f.line(100, 113, 137, 90); f.text(108, 46, 24, 14, 'H1', size=8.5, bold=True)
    f.line(100, 196, 136, 196); f.text(108, 200, 24, 14, 'H2', size=8.5, bold=True)
    f.line(220, 84, 262, 124); f.line(220, 196, 262, 152); f.text(224, 166, 30, 14, 'H2(−)', size=8.5, bold=True)
    f.line(340, 132, 378, 88); f.text(344, 92, 24, 14, 'H3', size=8.5, bold=True)
    f.line(434, 96, 434, 128); f.line(380, 96, 380, 213, arrow=False); f.line(380, 213, 392, 213)
    f.text(438, 104, 30, 14, 'H3', size=8.5, bold=True)
    f.box(4, 248, 230, 70, '多群組 SEM（H4、H5）\n① 主播類型：AI 虛擬主播／真人主播\n② 價值傾向：功能型／情感社會型（第一階段量表）', kind='rect', dash='dash', lc=ORANGE, size=8.5, bold1=True, align='left')
    f.line(118, 248, 118, 98, dash=True, lc=ORANGE)
    f.box(250, 254, 226, 64, '理論基礎\n溫暖與能力：Fiske et al. (2007)\n期望確認：Oliver (1980)\n直播信任：Wongkitrungrueng & Assarut (2020)', kind='rect', dash='dash', size=8, align='left', lc='7F7F7F')
    return f

def fig4():
    f = Fig(480, 470)
    f.box(36, 4, 440, 40, '系統性文獻回顧與研究共同基礎\n正式資料庫檢索・倫理審查（IRB）・品類庫・共同量表・預先註冊（2027.08–2027.10）', kind='round', fill=CG, size=8.5, bold1=True)
    f.box(4, 52, 26, 320, '\n'.join('預先註冊｜操弄檢驗｜測量恆等性｜開放資料'), kind='rect', fill='F2F2F2', size=8.5, bold=True)
    cols = [(36, C1, '第一階段【發現】', [('1a 訪談大綱與前導訪談', 'N = 6｜2027.08–2027.09'), ('1b 軟式階梯訪談', 'N = 48｜2027.09–2027.12'),
                                        ('1c 人工編碼與信度', '2027.11–2028.01'), ('1d 涵意矩陣與 HVM', '2027.12–2028.01'), ('1e 價值傾向量表發展', 'N ≈ 300｜2028.01–2028.03')]),
            (186, C2, '第二階段【檢驗】', [('刺激物製作與前測', '三品類｜2028.02–2028.04'), ('2a 錨定實驗：運動鞋', 'N = 480｜2028.05–2028.06'),
                                        ('2b 跨品類複製', 'N = 960｜2028.07–2028.09'), ('2c AI 身分揭露實驗', 'N = 360｜2028.07–2028.09'), ('一週後追蹤與分析', '2028.06–2028.10')]),
            (336, C3, '第三階段【推廣】', [('量表與問卷設計', '2028.06–2028.08'), ('前測與修訂', 'N ≈ 80｜2028.09'),
                                        ('3a 直播購買者調查', 'N ≈ 800｜2028.10–2028.12'), ('3b 三個月退貨追蹤', '2029.01–2029.03'), ('3c 多群組 SEM', '2029.02–2029.04')])]
    for x, col, head, items in cols:
        f.box(x, 52, 140, 22, head, fill=col, size=9, bold=True)
        for i, (a, b) in enumerate(items):
            y = 84 + i * 56
            f.box(x, y, 140, 38, a + '\n' + b, kind='round', fill='FFFFFF', lc='7F7F7F', size=8.5, bold1=True)
            if i < 4: f.line(x + 70, y + 38, x + 70, y + 56)
        f.line(x + 70, 84 + 4 * 56 + 38, x + 70, 372)
    f.line(176, 84 + 4 * 56 + 19, 186, 84 + 0 * 56 + 30, dash=True, lc=ORANGE)
    f.box(36, 372, 440, 42, '研究總結（2029.04–2029.07）：三階段結果的比較、整合及詮釋\n中小企業決策表・AI 主播揭露與退貨溝通指引・三篇期刊投稿', kind='round', fill=CT, size=8.5, bold1=True, lc=BLUE, lw=1.3)
    f.box(36, 422, 440, 40, '虛線箭頭：第一階段價值鏈改寫為第二階段話術；價值傾向量表用於第二階段操弄檢驗與第三階段分組\n滾動式檢討：期中報告（2028.07）更新文獻回顧與市場資料；各階段結果討論後，修正下一階段設計', kind='rect', dash='dash', size=8.5, lc='7F7F7F')
    f.line(256, 414, 256, 422, arrow=False)
    return f
