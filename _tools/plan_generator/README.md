# 計畫書產生程式（plan_generator）

由同一份內容產出兩年期研究計畫書的 Word 版與網頁版，以及待下載文獻清單。

| 檔案 | 內容 |
|---|---|
| `content.py` | 計畫書全文（章節、段落、表格、假說）。修改內文改這裡。`**粗體**` 以兩個星號標示。 |
| `figures.py` | 圖 1–4 的形狀與座標（單位：點）。Word 版輸出為可編輯的繪圖物件，網頁版輸出為 SVG。 |
| `refs_extra.py` | 本次新增文獻的書目資料。新增文獻時在此加一筆。 |
| `orig_refs.json` | 由 1022-1111 版計畫書解析出的原有文獻（`parse_refs.py` 產生）。 |
| `lib.py` | 引用自動加超連結、DOCX／HTML 寫出、參考文獻格式。 |
| `build.py` | 產出計畫書 .docx 與 .html。 |
| `dl.py` | 產出待下載文獻清單 .docx。 |

## 使用方式（於 paper/ 資料夾執行）

```
python3 _tools/plan_generator/build.py Plan_fen Plan_fen MMDD-HHMM
python3 _tools/plan_generator/dl.py _tools/plan_generator/used_refs.json Plan_fen/MMDD-HHMM_待下載文獻清單.docx MMDD-HHMM_兩年期研究計畫書.docx
```

- `build.py <主題資料夾根目錄> <超連結基準目錄> <時間戳> [輸出目錄]`；輸出目錄省略時與超連結基準目錄相同。
- 內文引用寫成 `(Gutman, 1982)`、`(Reynolds & Gutman, 1988)`、`(Ter Hofstede et al., 1998, 1999)` 或 `Gutman (1982)` 即會自動加上超連結；同年同姓者以 `Z. Li et al., 2025` 區分。
- 有本地 PDF 的文獻連到主題資料夾（相對路徑），否則連到 DOI。PDF 放進主題資料夾後重新執行即會改連本地檔案。
- 執行結果會列出「未被引用的文獻」與「無法對應的引用」，兩者都應為空。
