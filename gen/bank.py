# -*- coding: utf-8 -*-
"""흐름터 — 문장은행과 스핀 엔진.

★같은 뼈대로 3천 쪽을 찍으면 서로 베낀 글이 된다. 그래서 세 가지를 같이 쓴다.
  ① `[[가|나|다]]` 슬롯 — 자리마다 다른 낱말을 집는다(슬러그로 고정 추첨: 늘 같은 결과)
  ② **문장마다 그 쪽의 지역 이름**을 넣는다([[xdup-rewrite-the-most-used-paragraph]])
  ③ 쪽마다 **축(물이 멈추는 자리 10갈래)**이 달라 이야기의 출발점 자체가 다르다
★자리표는 `{N}` 꼴. **조사 보정은 자리표 바로 뒤에서만**([[korean-particle-fix-only-at-placeholder]]).
★`spin()` 다음에 반드시 `fill()`([[spin-slots-leak-when-injected-raw]]).
★`**굵게**` 는 `bold()` 가 태그로 바꾼다([[generated-markdown-bold-never-converted]]).
★★문장은 **물길·틔움·다잡이에서 한 줄도 옮겨 오지 않았다**([[shell-port-carries-original-prose]]).
  어휘 갈래를 아예 달리해 새로 썼고, 빌드 뒤 18낱말 n-gram 으로 형제와 겹침을 센다.
"""
import hashlib
import re

SLOT = re.compile(r'\[\[(.+?)\]\]')
MARK = '\x00'
JOSA = re.compile(MARK + r'(으로|로|은|는|이(?![에었야란])|가|을|를|과|와|에서|부터)')


def _pick(opts, *seed):
    h = hashlib.md5('|'.join(map(str, seed)).encode('utf-8')).hexdigest()
    return opts[int(h, 16) % len(opts)]


def spin(t, *seed):
    n = [0]

    def one(m):
        n[0] += 1
        opts = m.group(1).split('|')
        return _pick(opts, *seed, n[0], m.group(1)[:12])
    return SLOT.sub(one, t)


def _jong(w):
    if not w:
        return False
    c = w[-1]
    if '가' <= c <= '힣':
        return (ord(c) - 0xAC00) % 28 != 0
    if c.isdigit():
        return c in '0136780'
    if c.isalpha():
        if w.lower().endswith('ng'):
            return True
        return c.lower() in 'lmnbp'
    return False


def fill(t, V):
    def put(m):
        k = m.group(1)
        return str(V.get(k, m.group(0))) + MARK
    t = re.sub(r'\{(\w+)\}', put, t)

    def jo(m):
        j, i = m.group(1), m.start()
        w = t[:i].rstrip(MARK)
        has = _jong(w)
        return {'으로': '으로' if has else '로', '로': '으로' if has else '로',
                '은': '은' if has else '는', '는': '은' if has else '는',
                '이': '이' if has else '가', '가': '이' if has else '가',
                '을': '을' if has else '를', '를': '을' if has else '를',
                '과': '과' if has else '와', '와': '과' if has else '와',
                '에서': '에서', '부터': '부터'}[j]
    return JOSA.sub(jo, t).replace(MARK, '')


def bold(t):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)


def para(tpl, V, *seed):
    return '<p>' + bold(fill(spin(tpl, *seed), V)) + '</p>'


def sec(head, tpls, V, *seed):
    h = bold(fill(spin(head, *seed), V))
    return ('<h3>' + h + '</h3>'
            + ''.join(para(t, V, *seed, i) for i, t in enumerate(tpls)))


def body(heads, bodies, V, *seed):
    return ''.join(sec(h, b, V, *seed, i) for i, (h, b) in enumerate(zip(heads, bodies)))
