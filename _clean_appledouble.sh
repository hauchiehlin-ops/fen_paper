#!/bin/zsh
# 將資料夾內 macOS 產生的 AppleDouble 隱藏檔（._*）移到該磁碟的垃圾桶。
# 不直接刪除：清空垃圾桶前都還能救回。
#
# 用法：
#   ./_clean_appledouble.sh [資料夾] [-n]
#     資料夾  預設為本腳本所在的資料夾
#     -n      只列出會被移走的檔案，不實際移動

set -euo pipefail

target="${0:A:h}"
dry_run=0
for arg in "$@"; do
  case "$arg" in
    -n|--dry-run) dry_run=1 ;;
    *) target="${arg:A}" ;;
  esac
done
[[ -d "$target" ]] || { echo "找不到資料夾：$target" >&2; exit 1; }

# 外接磁碟用該磁碟的 .Trashes/<uid>，開機磁碟用 ~/.Trash，與 Finder 的「丟到垃圾桶」相同
volume=$(df -P "$target" | awk 'NR==2 {print $6}')
if [[ "$volume" == "/" || "$volume" == /System/Volumes/* ]]; then
  trash="$HOME/.Trash"
else
  trash="$volume/.Trashes/$(id -u)"
  mkdir -p "$trash"
fi

moved=0
skipped=0
while IFS= read -r -d '' f; do
  # 只處理真正的 AppleDouble 檔（開頭魔術碼 00 05 16 07），避免誤動到名稱剛好以 ._ 開頭的一般檔案
  if [[ "$(xxd -p -l 4 "$f")" != "00051607" ]]; then
    skipped=$((skipped + 1))
    continue
  fi
  if (( dry_run )); then
    echo "$f"
  else
    dest="$trash/${f:t}"
    [[ -e "$dest" ]] && dest="$trash/${f:t}.$(date +%Y%m%d%H%M%S).$RANDOM"
    mv "$f" "$dest"
  fi
  moved=$((moved + 1))
done < <(find "$target" -name '._*' -type f -not -path '*/.Trashes/*' -print0)

if (( dry_run )); then
  echo "共 $moved 個 ._ 檔會被移到 $trash（略過 $skipped 個非 AppleDouble 檔）"
else
  echo "已將 $moved 個 ._ 檔移到 $trash（略過 $skipped 個非 AppleDouble 檔）"
fi
