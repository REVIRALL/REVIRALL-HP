"""旧法人（合同会社リバイラル）由来の過去情報を全て除去する。

方針:
- 実績・沿革・売上は旧法人のもの。新法人（2026-07-06設立・資本金200万・1期目）の
  ものとして掲示すると事実と異なるため削除する。
- 実数が分からない項目（従業員数）は、誤った数字を残すより行ごと削除する。
- コピーライト表記の LLC → Inc. も揃える。
"""
import re
import sys
from pathlib import Path

JS = Path('assets/index-BTt0Ebvz.js')
INDEX = Path('index.html')
RECRUIT = Path('recruit.html')

# (file, 検索, 置換, 期待回数)
EDITS = [
    # ---- JS: ニュース(旧法人時代のメディア掲載)を全削除 ----
    (JS, 'vp=[{date:"2025.12.23",title:"第27491号 スポーツニッポン新聞に掲載されました",'
         'imageUrl:"assets/sponichi.jpg"},{date:"2024.12.01",'
         'title:"元モー娘。市井紗耶香さんと対談しました",'
         'imageUrl:"assets/masters-magazine.jpg"}]', 'vp=[]', 1),

    # ---- JS: 従業員数は新法人の実数が不明なため行ごと削除 ----
    (JS, 'crew:"14 Units (Inc. Contractors)",', '', 1),
    (JS, 'crew:"従業員数",', '', 1),

    # ---- JS: コピーライト LLC → Inc. ----
    (JS, '"REVIRALL LLC. // TOKYO"', '"REVIRALL Inc. // TOKYO"', 1),
    (JS, ' REVIRALL LLC. All Rights Reserved.', ' REVIRALL Inc. All Rights Reserved.', 1),
    (JS, 'COPYRIGHT © 2025 REVIRALL LLC.', 'COPYRIGHT © 2026 REVIRALL Inc.', 1),

    # ---- index.html: タイトルの年号 ----
    (INDEX, '<title>REVIRALL | REBOOT 2025</title>',
            '<title>REVIRALL | 株式会社リバイラル</title>', 1),

    # ---- recruit.html ----
    (RECRUIT, '2023年の設立以来、急成長を続ける弊社で、組織の内製化を支える重要なポジションをお任せします。',
              '組織の内製化を支える重要なポジションをお任せします。', 1),
    (RECRUIT, '<dd>2023年3月</dd>', '<dd>2026年7月</dd>', 1),
    (RECRUIT, '<dt class="text-stark-white/60">事業期</dt><dd>4期目</dd>',
              '<dt class="text-stark-white/60">事業期</dt><dd>1期目</dd>', 1),
    (RECRUIT, '// 事業4期目', '// 事業1期目', 2),
    (RECRUIT, '© 2026 REVIRALL LLC. ALL RIGHTS RESERVED.',
              '© 2026 REVIRALL Inc. ALL RIGHTS RESERVED.', 1),
]

# 正規表現で消すもの（空白揺れがあるため）
REGEX_EDITS = [
    # 沿革の文章（前身の合同会社への言及と「4期目」を落とす）
    (RECRUIT,
     r'株式会社リバイラルは <span class="text-viral-cyan font-bold">2026年7月</span> に設立。'
     r'前身の合同会社リバイラルは <span class="text-viral-cyan font-bold">2023年3月</span> 創業。<br/>\s*'
     r'少数精鋭の体制ながら、着実に実績を積み上げ、現在は事業 '
     r'<span class="text-viral-cyan">4期目</span> を迎えています。',
     '株式会社リバイラルは <span class="text-viral-cyan font-bold">2026年7月</span> に設立。<br/>\n'
     '              少数精鋭の体制で、組織の内製化を推進しています。', 1),

    # 売上推移セクションごと削除（旧法人の実績のため）
    (RECRUIT, r'\s*<!-- 売上推移 -->.*?</table>\s*</div>', '', 1),
]


def main():
    cache, applied, failed = {}, [], []

    for path, old, new, expect in EDITS:
        cache.setdefault(path, path.read_text(encoding='utf-8'))
        n = cache[path].count(old)
        if n != expect:
            failed.append((path.name, old[:55], n, expect))
            continue
        cache[path] = cache[path].replace(old, new)
        applied.append((path.name, old[:55]))

    for path, pat, new, expect in REGEX_EDITS:
        cache.setdefault(path, path.read_text(encoding='utf-8'))
        n = len(re.findall(pat, cache[path], flags=re.DOTALL))
        if n != expect:
            failed.append((path.name, 'RE:' + pat[:50], n, expect))
            continue
        cache[path] = re.sub(pat, new, cache[path], flags=re.DOTALL)
        applied.append((path.name, 'RE:' + pat[:50]))

    if failed:
        print('ABORT — 出現回数が期待と不一致:')
        for f, o, n, e in failed:
            print('  %s | %s | 実際%d / 期待%d' % (f, o, n, e))
        return 1

    for path, text in cache.items():
        path.write_text(text, encoding='utf-8')

    print('applied %d edits' % len(applied))
    for f, o in applied:
        print('  [%s] %s' % (f, o))

    print('\n--- 残存チェック ---')
    terms = ['合同会社', 'REVIRALL LLC', '坂本', '渋谷', '新橋', '4期目',
             '2023年', '2024年度', '2025年度', 'スポーツニッポン', '市井',
             'REBOOT 2025', '14 Units', '売上推移']
    clean = True
    for path in [JS, INDEX, RECRUIT]:
        s = path.read_text(encoding='utf-8')
        for t in terms:
            c = s.count(t)
            if c:
                print('  REMAINS %s | %s x%d' % (path.name, t, c))
                clean = False
    if clean:
        print('  旧法人由来の記述は残っていません')
    return 0


if __name__ == '__main__':
    sys.exit(main())
