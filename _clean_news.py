"""ニュース(沿革)から、旧法人時代のオフィス移転履歴を削除する。

残す:   メディア掲載2件（スポニチ / 市井紗耶香さん対談）— 広報資産のため
消す:   オフィス移転・出張所の履歴3件
        新本店が豊島区南池袋になったため「本社を渋谷に移転」は現状と矛盾する
"""
import sys
from pathlib import Path

JS = Path('assets/index-BTt0Ebvz.js')

REMOVE = (
    ',{date:"2024.10.01",title:"オフィスを池袋に移転"}'
    ',{date:"2024.06.27",title:"本社を渋谷に移転"}'
    ',{date:"2023.07.01",title:"新橋出張所追加"}'
)


def main():
    s = JS.read_text(encoding='utf-8')
    n = s.count(REMOVE)
    if n != 1:
        print('ABORT: 対象が %d 件（期待1件）' % n)
        return 1
    JS.write_text(s.replace(REMOVE, ''), encoding='utf-8')

    after = JS.read_text(encoding='utf-8')
    print('removed 3 news items')
    for t in ['オフィスを池袋に移転', '本社を渋谷に移転', '新橋出張所追加',
              'スポーツニッポン', '市井紗耶香']:
        print('  %-16s x%d' % (t, after.count(t)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
