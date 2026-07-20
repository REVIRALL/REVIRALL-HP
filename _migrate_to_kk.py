"""合同会社リバイラル → 株式会社リバイラル へのサイト表記移行。

ビルド済みバンドル(assets/index-*.js)にReactのソースが存在しないため、
minified JS を文字列単位で直接置換する。
各置換は期待出現回数を assert し、想定外の当たり方をしたら止める。

新法人の確定情報(登記・国税庁法人番号公表サイトより):
  商号     株式会社リバイラル / 法人番号 7013301056505
  本店     〒171-0022 東京都豊島区南池袋一丁目3番9号2F
  設立     2026年7月6日 / 資本金 200万円 / 代表取締役 沼倉隆平
"""
import re
import sys
from pathlib import Path

JS = Path('assets/index-BTt0Ebvz.js')
RECRUIT = Path('recruit.html')

OLD_ADDR = '東京都渋谷区渋谷2-19-15 宮益坂ビルディング609'
NEW_ADDR = '東京都豊島区南池袋一丁目3番9号2F'

# (対象ファイル, 検索文字列, 置換文字列, 期待出現回数)
EDITS = [
    # --- 会社概要データ (Re) ---
    (JS, 'entity:"Revirall LLC. (合同会社リバイラル)"',
         'entity:"REVIRALL Inc. (株式会社リバイラル)"', 1),
    (JS, 'founded:"2023.03.20"', 'founded:"2026.07.06"', 1),
    (JS, 'capital:"8,000,000 JPY"', 'capital:"2,000,000 JPY"', 1),
    (JS, 'hq_coordinates:"Shibuya 2-19-15, Tokyo"',
         'hq_coordinates:"Minami-Ikebukuro 1-3-9, Tokyo"', 1),
    # 本社が池袋になったため「池袋オフィス」行は重複。データとラベル両方から除去
    (JS, ',base_2:"Ikebukuro 1-3-9, Tokyo"', '', 1),
    (JS, 'base_2:"池袋オフィス",', '', 1),

    # --- 特定商取引法に基づく表記 ---
    (JS, '{heading:"販売業者",text:"合同会社リバイラル"}',
         '{heading:"販売業者",text:"株式会社リバイラル"}', 1),
    (JS, '{heading:"代表責任者",text:"坂本 純一"}',
         '{heading:"代表責任者",text:"沼倉 隆平"}', 1),
    (JS, '{heading:"所在地",text:"〒150-0002 %s"}' % OLD_ADDR,
         '{heading:"所在地",text:"〒171-0022 %s"}' % NEW_ADDR, 1),

    # --- プライバシーポリシー お問い合わせ窓口 ---
    (JS, '住所：%s\n社名：合同会社リバイラル' % OLD_ADDR,
         '住所：%s\n社名：株式会社リバイラル' % NEW_ADDR, 1),

    # --- 個人情報の取り扱いについて 基本方針 ---
    (JS, '合同会社リバイラル（以下、「当社」といいます。）',
         '株式会社リバイラル（以下、「当社」といいます。）', 1),

    # --- 代表メッセージの署名（合同会社の「代表社員」→ 株式会社の「代表取締役」）---
    (JS, '代表社員 坂本 純一', '代表取締役 沼倉 隆平', 1),

    # --- recruit.html ---
    (RECRUIT, '<meta name="description" content="合同会社リバイラル 採用情報。',
              '<meta name="description" content="株式会社リバイラル 採用情報。', 1),
    (RECRUIT, '合同会社リバイラル / REVIRALL LLC',
              '株式会社リバイラル / REVIRALL Inc.', 1),
    # 沿革の実績は前身の合同会社のもの。法人が変わったことを明示しつつ実績は残す
    (RECRUIT, '合同会社リバイラルは <span class="text-viral-cyan font-bold">2023年3月</span> に設立。',
              '株式会社リバイラルは <span class="text-viral-cyan font-bold">2026年7月</span> に設立。'
              '前身の合同会社リバイラルは <span class="text-viral-cyan font-bold">2023年3月</span> 創業。', 1),
]


def main():
    cache, report, failed = {}, [], []
    for path, old, new, expect in EDITS:
        if path not in cache:
            cache[path] = path.read_text(encoding='utf-8')
        n = cache[path].count(old)
        if n != expect:
            failed.append((path.name, old[:60], n, expect))
            continue
        cache[path] = cache[path].replace(old, new)
        report.append((path.name, old[:52], new[:52]))

    if failed:
        print('ABORT — 期待と異なる出現回数:')
        for f, o, n, e in failed:
            print('  %s | %r | 実際%d回 / 期待%d回' % (f, o, n, e))
        return 1

    for path, text in cache.items():
        path.write_text(text, encoding='utf-8')

    print('applied %d edits' % len(report))
    for f, o, n in report:
        print('  [%s] %s' % (f, o))

    # 残存チェック
    print()
    for path in cache:
        s = path.read_text(encoding='utf-8')
        for term in ['合同会社リバイラル', '坂本', '渋谷区渋谷2-19-15', '150-0002',
                     'Revirall LLC', '8,000,000', '2023.03.20']:
            c = s.count(term)
            if c:
                print('  REMAINS: %s | %s x%d' % (path.name, term, c))
    return 0


if __name__ == '__main__':
    sys.exit(main())
