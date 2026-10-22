from lib import Fig

C1, C2, C3, CG, CT = 'FBE5D6', 'E2F0D9', 'DEEBF7', 'EDEDED', 'FFF2CC'   # stage colours, common, translation
BLUE = '1F4E79'

def fig1():
    f = Fig(480, 560)
    # ---- upper part: methodological level x time
    f.line(40, 238, 40, 8)                       # y axis
    f.line(40, 238, 470, 238)                    # x axis
    f.text(0, 0, 38, 40, '方法論\n層次', size=8.5, bold=True)
    f.text(14, 40, 24, 16, '高', size=9); f.text(14, 205, 24, 16, '低', size=9)
    f.text(420, 240, 60, 16, '時間構面', size=8.5)
    f.box(52, 14, 330, 218, kind='ellipse', lw=1)
    f.box(56, 82, 236, 148, kind='ellipse', lw=1)
    f.box(60, 146, 140, 82, kind='ellipse', lw=1)
    f.text(170, 24, 190, 44, '第三階段【推廣】\n以 SEM × SEM 決策樹／潛在類別\n驗證社群商務的異質路徑', size=8.5, bold1=True)
    f.text(118, 90, 160, 44, '第二階段【檢驗】\n以實驗 × 因果森林檢驗\n短影音視聽一致性的異質效果', size=8.5, bold1=True)
    f.text(66, 160, 128, 56, '第一階段【發現】\n以計算化階梯法探索\nAR 試穿的價值族群', size=8.5, bold1=True)
    f.box(388, 98, 84, 54, '消費者異質性\n感知的數位行銷\n研究方法論', kind='rect', fill='FFFFFF', bold=True, size=8.5, lw=1.2)
    f.line(382, 124, 388, 124)
    f.text(46, 242, 120, 26, '第一階段\n2027.08–2028.07', size=8)
    f.text(168, 242, 120, 26, '第二階段\n2027.11–2029.04', size=8)
    f.text(290, 242, 120, 26, '第三階段\n2028.02–2029.07', size=8)
    f.line(46, 274, 250, 274, arrow=False, dash=True); f.text(110, 268, 80, 14, '第一年', size=8, fill='FFFFFF')
    f.line(256, 274, 470, 274, arrow=False, dash=True); f.text(320, 268, 80, 14, '第二年', size=8, fill='FFFFFF')
    f.box(225, 284, 30, 22, kind='darrow', fill='D9D9D9', lc='7F7F7F')
    # ---- lower part: pipeline
    f.text(118, 310, 96, 26, '價值族群成為\n候選調節變數', size=8, color=BLUE)
    f.text(278, 310, 96, 26, '反應族群成為\n預先註冊假設', size=8, color=BLUE)
    t1 = '第一階段【發現】\n經典方法：MEC 軟式階梯訪談\n資料探勘：LLM 訪談與編碼、\n關聯規則、網絡分析、分群\n產出：跨品類價值族群'
    t2 = '第二階段【檢驗】\n經典方法：2×2×2 實驗設計\n資料探勘：影片特徵擷取、\n跨品類刺激抽樣、因果森林\n產出：異質處理效果地圖'
    t3 = '第三階段【推廣】\n經典方法：SEM\n資料探勘：SEM 決策樹與森林、\n潛在類別 SEM、樣本外預測\n產出：異質路徑模型'
    f.box(8, 340, 142, 86, t1, kind='round', fill=C1, size=8.5, bold1=True, align='left', anchor='t')
    f.box(169, 340, 142, 86, t2, kind='round', fill=C2, size=8.5, bold1=True, align='left', anchor='t')
    f.box(330, 340, 142, 86, t3, kind='round', fill=C3, size=8.5, bold1=True, align='left', anchor='t')
    f.line(150, 383, 169, 383); f.line(311, 383, 330, 383)
    for x in (79, 240, 401): f.line(x, 426, x, 446, arrow=False, dash=True)
    f.box(8, 446, 464, 52, '共同基礎（三階段共用）\n消費者側寫問卷｜品類庫：運動鞋（錨定）、美妝保養、居家家具，各含享樂型與實用型\n異質性發現與驗證程序：預先註冊、發現／確認樣本切分、偽陽性防護、可解釋演算法',
          kind='round', fill=CG, size=8.5, bold1=True, align='left')
    f.line(240, 498, 240, 514)
    f.box(8, 514, 464, 34, '實務轉譯（主題五）：開源工具包、中小企業分群與內容測試指南、個資與演算法公平指引',
          kind='round', fill=CT, size=9, bold=True, lc=BLUE, lw=1.3)
    return f

def fig2():
    f = Fig(480, 290)
    f.box(4, 26, 124, 196, kind='rect', dash='dash', lc='2E75B6')
    f.text(4, 8, 124, 16, '操弄變數（2×2×2，受試者間）', size=8, color='2E75B6', bold=True)
    f.box(14, 36, 104, 52, '音樂喚起\n快節奏高喚起／\n慢節奏低喚起', fill='FFFFFF', size=8.5, bold1=True)
    f.box(14, 98, 104, 46, '剪輯頻率\n高頻切換／慢速運鏡', fill='FFFFFF', size=8.5, bold1=True)
    f.box(14, 158, 104, 52, '產品類型\n享樂型／實用型\n（三品類各一組）', fill='FFFFFF', size=8.5, bold1=True)
    f.box(146, 78, 104, 52, '視聽一致性\n一致／不一致', kind='ellipse', fill=C2, size=8.5, bold1=True)
    f.line(118, 70, 152, 96); f.line(118, 121, 152, 110)
    f.box(282, 46, 86, 34, '認知負荷', kind='ellipse', size=9)
    f.box(282, 112, 86, 34, '處理流暢度', kind='ellipse', size=9)
    f.box(392, 92, 84, 44, '品牌記憶\n（立即／三天後）', kind='rect', size=8.5, bold1=True)
    f.box(392, 152, 84, 44, '觀看意願\n完播、停留秒數', kind='rect', size=8.5, bold1=True)
    f.line(244, 96, 284, 66); f.text(250, 66, 24, 14, 'H1', size=8.5, bold=True)
    f.line(246, 106, 282, 126)
    f.line(368, 125, 392, 116); f.line(368, 132, 392, 166); f.text(366, 140, 24, 14, 'H3', size=8.5, bold=True)
    f.line(198, 80, 198, 18, arrow=False); f.line(198, 18, 434, 18, arrow=False); f.line(434, 18, 434, 92)
    f.text(300, 4, 120, 14, 'H2：喚起 × 剪輯交互作用', size=8.5, bold=True)
    f.line(118, 184, 262, 118, dash=True); f.text(186, 150, 26, 14, 'H4', size=8.5, bold=True)
    f.box(150, 238, 250, 44, '消費者側寫變數＋第一階段價值傾向\n以因果森林估計每位受試者的條件效果（研究 2d）', kind='rect', dash='dash', lc='C55A11', size=8.5, bold1=True)
    f.line(300, 238, 320, 147, dash=True, lc='C55A11'); f.text(316, 196, 26, 14, 'H5', size=8.5, bold=True, color='C55A11')
    return f

def fig3():
    f = Fig(480, 330)
    f.box(4, 150, 108, 58, '推薦來源關係強度\n強連結（好友）／\n弱連結（網紅）', fill=C3, size=8.5, bold1=True)
    f.box(176, 92, 92, 40, '感知信任', kind='ellipse', size=9)
    f.box(176, 214, 92, 40, '資訊診斷性', kind='ellipse', size=9)
    f.box(306, 154, 84, 40, '產品態度', kind='ellipse', size=9)
    f.box(404, 150, 72, 48, '購買轉換\n（加入購物車）', size=8.5, bold1=True)
    f.line(112, 166, 177, 116); f.line(112, 192, 177, 230)
    f.text(150, 160, 26, 14, 'H1', size=8.5, bold=True)
    f.line(268, 116, 310, 165); f.line(268, 230, 310, 185); f.line(390, 174, 404, 174)
    f.text(282, 196, 30, 14, 'H3', size=8.5, bold=True)
    f.box(100, 34, 92, 36, '產品類型\n享樂型／實用型', fill='FFFFFF', size=8.5, bold1=True)
    f.line(146, 70, 145, 138); f.text(148, 82, 26, 14, 'H2', size=8.5, bold=True)
    f.box(4, 34, 86, 36, '賣家來源\n國內／跨境', fill='FFFFFF', size=8.5, bold1=True)
    f.line(47, 70, 140, 140); f.text(60, 70, 26, 14, 'H4', size=8.5, bold=True)
    f.box(4, 96, 62, 40, '跨國購物\n經驗（測量）', fill='FFFFFF', size=8, bold1=True)
    f.line(66, 108, 88, 105); f.text(40, 136, 26, 14, 'H5', size=8.5, bold=True)
    f.box(306, 34, 168, 54, '信任理論：Morgan & Hunt (1994)\n社會資本：Granovetter (1973)\n心理距離：Han & Lai (2025)', kind='rect', dash='dash', size=8, align='left', lc='7F7F7F')
    f.box(96, 278, 316, 46, '異質性探勘（研究 3d）：SEM 決策樹、SEM 森林、潛在類別 SEM\n候選變數：側寫變數、第一階段價值族群、第二階段反應族群', kind='rect', dash='dash', lc='C55A11', size=8.5, bold1=True)
    f.line(254, 278, 254, 196, dash=True, lc='C55A11'); f.text(258, 256, 44, 14, 'H6／H7', size=8.5, bold=True, color='C55A11')
    return f

def fig4():
    f = Fig(480, 470)
    f.box(36, 4, 440, 40, '確立研究主題與方法論共同基礎\n倫理審查（IRB）・消費者側寫問卷・品類庫・預先註冊（2027.08–2028.01）', kind='round', fill=CG, size=8.5, bold1=True)
    f.box(4, 52, 26, 320, '\n'.join('共同驗證程序｜發現樣本探勘｜偽陽性防護｜確認樣本驗證'), kind='rect', fill='F2F2F2', size=8.5, bold=True)
    cols = [(36, C1, '第一階段【發現】', [('1a 人工軟式階梯訪談', 'N = 48｜2027.08–2028.01'), ('1b LLM 對話式階梯訪談', 'N ≈ 600｜2027.11–2028.04'),
                                        ('1c LLM 輔助編碼與一致性', '2028.02–2028.04'), ('1d 關聯規則階梯價值圖與分群', '2028.05–2028.07'), ('1e 三個月追蹤：預測效度', '2028.08–2029.01')]),
            (186, C2, '第二階段【檢驗】', [('2a 短影音語料庫與特徵擷取', '約 1,500 支｜2027.11–2028.07'), ('刺激物製作與前測', '三品類｜2028.02–2028.07'),
                                        ('2b 錨定實驗：運動鞋', 'N = 480｜2028.08–2028.10'), ('2c 跨品類複製：美妝、家具', 'N ≈ 960｜2028.08–2029.01'), ('2d 因果森林：反應族群', '2028.11–2029.04')]),
            (336, C3, '第三階段【推廣】', [('量表與問卷設計', '2028.02–2028.07'), ('介面建置與前測', 'N ≈ 80｜2028.05–2028.10'),
                                        ('3a–3c 情境實驗與回憶調查', 'N ≈ 2,600｜2028.11–2029.01'), ('3d 基準 SEM 與異質性探勘', '2029.02–2029.04'), ('樣本外預測與跨品類重現', '2029.02–2029.04')])]
    for x, col, head, items in cols:
        f.box(x, 52, 140, 22, head, fill=col, size=9, bold=True)
        for i, (a, b) in enumerate(items):
            y = 84 + i * 56
            f.box(x, y, 140, 38, a + '\n' + b, kind='round', fill='FFFFFF', lc='7F7F7F', size=8.5, bold1=True)
            if i < 4: f.line(x + 70, y + 38, x + 70, y + 56)
        f.line(x + 70, 84 + 4 * 56 + 38, x + 70, 372)
    f.line(176, 84 + 3 * 56 + 19, 186, 84 + 2 * 56 + 30, dash=True, lc='C55A11')
    f.line(326, 84 + 4 * 56 + 19, 336, 84 + 3 * 56 + 30, dash=True, lc='C55A11')
    f.box(36, 372, 440, 42, '研究總結（2029.02–2029.07）：三階段結果與模型的比較、分析、整合及詮釋\n開源工具包與中小企業使用指南・個資與演算法公平指引・三篇頂級期刊投稿', kind='round', fill=CT, size=8.5, bold1=True, lc=BLUE, lw=1.3)
    f.box(36, 422, 440, 40, '虛線箭頭：第一階段價值族群寫入第二、三階段側寫問卷；第二階段反應族群成為第三階段預先註冊假設\n滾動式檢討：期中報告（2028.07）更新文獻與市場資料；各階段結果討論後，修正或延伸下一階段設計', kind='rect', dash='dash', size=8.5, lc='7F7F7F')
    f.line(256, 414, 256, 422, arrow=False)
    return f
