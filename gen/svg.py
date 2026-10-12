# -*- coding: utf-8 -*-
"""흐름터 — 화면에 쓰는 그림은 **전부 벡터로 직접 그린다**(2026-10-12 사장님
「업소 이미지, 히어로박스는 텍스트 SVG로」).

★히어로와 시공점 그림은 사진이 아니라 글자 + 선으로 만든 SVG 다. 그래서
  ① 무게가 거의 없고 ② 글자가 선명하고 ③ 지역마다 다른 그림이 공짜로 나온다.
★배색은 cfg.COL 한 곳에서 온다. 강조색 위 글자는 **검은 글자**로 대비를 지킨다.
"""
import hashlib
import sys

sys.path.insert(0, '/root/heureum/gen')
from cfg import COL, BRAND                                            # noqa: E402

ACC, ACC2, ACC3 = COL['acc'], COL['acc2'], COL['acc3']
INK, TX, MUT = COL['ink'], COL['tx'], COL['mut']


def h(seed, n):
    return int(hashlib.md5(str(seed).encode('utf-8')).hexdigest(), 16) % n


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


# ── 로고 ─────────────────────────────────────────────────────
def logo(w=132):
    """물방울이 관을 지나는 모양 + 글자."""
    return (
        '<svg class="lg" width="%d" height="30" viewBox="0 0 132 30" fill="none" '
        'aria-label="%s" role="img">'
        '<rect x="0" y="7" width="30" height="16" rx="8" fill="none" stroke="%s" stroke-width="2.4"/>'
        '<path d="M8 15h14" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>'
        '<path d="M24.5 11.5c2.6 2.4 2.6 4.6 0 7-2.6-2.4-2.6-4.6 0-7z" fill="%s"/>'
        '<text x="40" y="22" font-size="19" font-weight="800" fill="%s" '
        'letter-spacing="-.5">%s</text></svg>'
        % (w, BRAND, ACC2, ACC2, ACC, TX, BRAND))


def favicon():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<rect width="64" height="64" rx="15" fill="%s"/>'
            '<rect x="12" y="24" width="40" height="18" rx="9" fill="none" stroke="%s" stroke-width="4"/>'
            '<path d="M21 33h16" stroke="%s" stroke-width="4" stroke-linecap="round"/>'
            '<path d="M43 26c4.4 4.2 4.4 8.4 0 12.6-4.4-4.2-4.4-8.4 0-12.6z" fill="%s"/>'
            '</svg>' % (COL['bg'], ACC2, ACC2, ACC))


# ── 히어로(텍스트 SVG) ────────────────────────────────────────
def hero(kicker, line1, line2, seed='x'):
    """16:7 벡터 히어로. 지역마다 선 무늬가 달라진다."""
    k = h(seed, 4)
    curves = [
        'M-20 300 C 180 300 180 120 380 120 S 620 300 860 300 S 1100 150 1320 150',
        'M-20 140 C 220 140 220 300 460 300 S 760 120 1000 120 S 1180 260 1320 260',
        'M-20 230 C 160 230 220 90 420 90 S 700 320 940 320 S 1160 180 1320 180',
        'M-20 90 C 240 90 260 280 520 280 S 820 110 1060 110 S 1200 250 1320 250',
    ]
    dots = ''.join('<circle cx="%d" cy="%d" r="%s" fill="%s" opacity="%s"/>'
                   % (90 + i * 137 + h(str(seed) + str(i), 40),
                      60 + h(str(seed) + 'y' + str(i), 300),
                      [2, 2.6, 3.4][h(str(seed) + 'r' + str(i), 3)],
                      [ACC, ACC2, ACC3][h(str(seed) + 'c' + str(i), 3)], '.5')
                   for i in range(6))
    l2 = ('<text x="64" y="252" font-size="40" font-weight="800" fill="%s" '
          'letter-spacing="-1">%s</text>' % (ACC3, esc(line2))) if line2 else ''
    return (
        '<svg class="hv" viewBox="0 0 1280 380" preserveAspectRatio="xMinYMid slice" '
        'role="img" aria-label="%s %s">'
        '<defs><linearGradient id="hg%s" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="%s"/><stop offset=".55" stop-color="%s"/>'
        '<stop offset="1" stop-color="#0D2430"/></linearGradient></defs>'
        '<rect width="1280" height="380" fill="url(#hg%s)"/>'
        '<path d="%s" stroke="%s" stroke-width="26" fill="none" opacity=".14" stroke-linecap="round"/>'
        '<path d="%s" stroke="%s" stroke-width="2" fill="none" opacity=".55" stroke-dasharray="7 9"/>'
        '%s'
        '<rect x="64" y="56" width="%d" height="30" rx="15" fill="%s" opacity=".16"/>'
        '<circle cx="82" cy="71" r="4.5" fill="%s"/>'
        '<text x="96" y="76" font-size="15" font-weight="700" fill="%s">%s</text>'
        '<text x="64" y="176" font-size="54" font-weight="800" fill="%s" letter-spacing="-1.6">%s</text>'
        '%s</svg>'
        % (esc(line1), esc(line2 or ''), k, COL['bg2'], COL['bg'], k,
           curves[k], ACC2, curves[(k + 2) % 4], ACC,
           dots, 42 + len(kicker) * 15, ACC, ACC, ACC3, esc(kicker),
           TX, esc(line1), l2))


# ── 시공점 카드(텍스트 SVG) ───────────────────────────────────
def shop_card(nm, where, seed=''):
    s = seed or nm
    hue = h(s + 'h', 360)
    k = h(s + 'k', 5)
    pats = [
        '<circle cx="330" cy="92" r="40" fill="none" stroke="%s" stroke-width="1.6" opacity=".3"/>'
        '<circle cx="330" cy="92" r="66" fill="none" stroke="%s" stroke-width="1.6" opacity=".22"/>' % (ACC2, ACC2),
        '<rect x="266" y="36" width="52" height="52" rx="12" fill="none" stroke="%s" stroke-width="1.6" '
        'opacity=".3"/><rect x="330" y="90" width="52" height="52" rx="12" fill="none" stroke="%s" '
        'stroke-width="1.6" opacity=".22"/>' % (ACC2, ACC2),
        '<path d="M212 168 C 262 168 262 58 322 58 S 392 168 452 168" stroke="%s" stroke-width="11" '
        'fill="none" opacity=".26" stroke-linecap="round"/>' % ACC2,
        '<path d="M250 26 L278 174 M290 26 L318 174 M330 26 L358 174 M370 26 L398 174" stroke="%s" '
        'stroke-width="1.6" opacity=".26"/>' % ACC2,
        '<circle cx="330" cy="92" r="56" fill="none" stroke="%s" stroke-width="13" opacity=".2"/>'
        '<path d="M330 36 a56 56 0 0 1 56 56" stroke="%s" stroke-width="13" fill="none" '
        'stroke-linecap="round" opacity=".65"/>' % (ACC2, ACC),
    ]
    return (
        '<svg class="sc" viewBox="0 0 440 200" role="img" aria-label="%s">'
        '<defs><linearGradient id="sg%s" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="hsl(%d 26%% 13%%)"/>'
        '<stop offset="1" stop-color="hsl(%d 30%% 9%%)"/></linearGradient></defs>'
        '<rect width="440" height="200" fill="url(#sg%s)"/>%s'
        '<rect x="24" y="24" width="7" height="34" rx="3.5" fill="%s"/>'
        '<text x="42" y="50" font-size="27" font-weight="800" fill="%s" letter-spacing="-.8">%s</text>'
        '<text x="25" y="92" font-size="15" font-weight="600" fill="%s">%s</text>'
        '<rect x="24" y="118" width="128" height="30" rx="15" fill="%s" opacity=".9"/>'
        '<text x="42" y="138" font-size="14" font-weight="800" fill="%s">24시 접수</text>'
        '</svg>'
        % (esc(nm), s[:6].replace('-', ''), hue, (hue + 40) % 360, s[:6].replace('-', ''),
           pats[k], ACC, TX, esc(nm[:12]), MUT, esc(where), ACC, INK))


# ── 서비스 선 아이콘 ──────────────────────────────────────────
ICON = {
 'find': 'M7 17c3-6 7-6 10 0M12 4v3M5.5 7.5l2 2M18.5 7.5l-2 2',
 'fix':  'M4 18l6-6M9 7a4 4 0 105 5l5 5-3 3-5-5a4 4 0 00-2-8z',
 'drain': 'M4 8h16M6 8l1.5 11h9L18 8M9 12v4M15 12v4',
 'pipe': 'M3 9h7a3 3 0 013 3v3h8M10 6v6M17 12v9',
 'toilet': 'M6 4h8v7H6zM5 11h14l-2 6H7zM10 17v3h6',
 'kitchen': 'M4 7h16v3H4zM8 10v10M16 10v10M12 10v4',
 'bath': 'M5 11h14v3a4 4 0 01-4 4H9a4 4 0 01-4-4zM9 11V6a2 2 0 014 0',
 'faucet': 'M5 13h6V8a3 3 0 016 0v2h3M11 13v7M8 20h6',
 'plumb': 'M4 6h5v12H4zM9 9h11M9 15h11M20 6v12',
 'jet':  'M3 12h7M5 8h5M5 16h5M13 7l7 5-7 5z',
 'call': 'M5 4h4l2 5-3 2a12 12 0 005 5l2-3 5 2v4a2 2 0 01-2 2A17 17 0 013 6a2 2 0 012-2z',
 'clock': 'M12 3a9 9 0 100 18 9 9 0 000-18zM12 7v5l3 2',
 'check': 'M4 12l5 5L20 6',
 'shield': 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z',
 'pin': 'M12 3a6 6 0 016 6c0 4.5-6 12-6 12S6 13.5 6 9a6 6 0 016-6zM12 9h.01',
 'cam': 'M3 8h4l2-2h6l2 2h4v11H3zM12 17a4 4 0 100-8 4 4 0 000 8z',
}


def ico(k, c=None, size=24, cls='ic'):
    return ('<svg class="%s" width="%d" height="%d" viewBox="0 0 24 24" fill="none" '
            'stroke="%s" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" '
            'aria-hidden="true"><path d="%s"/></svg>'
            % (cls, size, size, c or ACC2, ICON.get(k, ICON['check'])))


def _wrap(t, n):
    """글자 수로 줄을 나눈다. '·' 과 빈칸을 끊는 자리로 본다."""
    words = t.replace(' · ', ' ·\u0000').split('\u0000') if ' · ' in t else t.split(' ')
    out, cur = [], ''
    for w in words:
        c = (cur + ' ' + w).strip() if cur else w
        if len(c) > n and cur:
            out.append(cur); cur = w.strip()
        else:
            cur = c
    if cur:
        out.append(cur)
    return out[:3]


def hero_m(kicker, line1, line2, seed='x'):
    """모바일 전용 히어로 — 세로로 세워 **글자를 크게** 보여 준다.
       ★가로 그림을 모바일에서 잘라 쓰면 글자가 반 토막 나거나 깨알이 된다(실측으로 보고 나눴다)."""
    k = h(seed, 4)
    L = _wrap(line1, 13)
    L2 = _wrap(line2, 15) if line2 else []
    y = 150
    body = ''
    for t in L:
        body += ('<text x="26" y="%d" font-size="34" font-weight="800" fill="%s" '
                 'letter-spacing="-1">%s</text>' % (y, TX, esc(t)))
        y += 44
    y += 6
    for t in L2:
        body += ('<text x="26" y="%d" font-size="25" font-weight="800" fill="%s" '
                 'letter-spacing="-.6">%s</text>' % (y, ACC3, esc(t)))
        y += 33
    curves = ['M-10 330 C 90 330 110 250 220 250 S 330 340 440 340',
              'M-10 300 C 120 300 120 230 240 230 S 340 320 440 320',
              'M-10 345 C 110 345 100 245 230 245 S 350 330 440 330',
              'M-10 315 C 100 315 130 240 250 240 S 360 325 440 325']
    return (
        '<svg class="hvm" viewBox="0 0 420 %d" preserveAspectRatio="xMinYMid meet" '
        'role="img" aria-label="%s">'
        '<defs><linearGradient id="hm%s" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="%s"/><stop offset=".6" stop-color="%s"/>'
        '<stop offset="1" stop-color="#0D2430"/></linearGradient></defs>'
        '<rect width="420" height="%d" fill="url(#hm%s)"/>'
        '<path d="%s" stroke="%s" stroke-width="20" fill="none" opacity=".14" stroke-linecap="round"/>'
        '<path d="%s" stroke="%s" stroke-width="2" fill="none" opacity=".5" stroke-dasharray="6 8"/>'
        '<rect x="26" y="44" width="%d" height="30" rx="15" fill="%s" opacity=".18"/>'
        '<circle cx="44" cy="59" r="4.5" fill="%s"/>'
        '<text x="58" y="64" font-size="15" font-weight="700" fill="%s">%s</text>'
        '%s</svg>'
        % (y + 26, esc(line1), k, COL['bg2'], COL['bg'], y + 26, k,
           curves[k], ACC2, curves[(k + 1) % 4], ACC,
           42 + len(kicker) * 15, ACC, ACC, ACC3, esc(kicker), body))
