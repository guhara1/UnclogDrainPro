# -*- coding: utf-8 -*-
"""흐름터 — 정적 사이트를 굽는다.

★★OUT 기본값은 **배포 폴더**다. 리포 뿌리를 가리키면 build() 가 .git 만 빼고 싹 지운다
  ([[static-site-generator-out-path-wipes-repo]] — 나울에서 한 번 당했다).
★기준 사이트(drainit.co.kr)의 **구성과 기능**을 눈으로 보고 옮겼다
  ([[reference-site-means-copy-the-structure]]). 다만 세 가지는 일부러 다르게 했고 보고드린다.
  ① **후기를 짓지 않는다** — 기준 사이트에는 고객 후기가 있지만 없는 후기를 만들지 않는다
  ② **금액을 적지 않는다** — 정본 요금표를 못 받았다. 「현장 확정 견적」까지만 쓴다
  ③ **지역을 전국 3층으로 편다** — 기준 사이트는 수도권 목록 한 덩이로 끝난다
★사진 설명·시공점 소개에 길 주소·별점·건수를 넣지 않는다.
"""
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, '/root/heureum/gen')
import bank                                                           # noqa: E402
import cfg                                                            # noqa: E402
import photos                                                         # noqa: E402
import prose                                                          # noqa: E402
import seo                                                            # noqa: E402
import shops                                                          # noqa: E402
import svg                                                            # noqa: E402
import tpl                                                            # noqa: E402
from cfg import COL                                                   # noqa: E402

OUT = os.environ.get('HT_OUT', '/root/heureum/repo/public')
REG = json.load(open('/root/heureum/gen/regions.json', encoding='utf-8'))
INKEY = 'a7d2f9c41e6b48f0b35d9a27c8e14f63'
KST = timezone(timedelta(hours=9))
NOW = datetime.now(KST)
URLS = []


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def w(path, text, add=True):
    flat = path.endswith(('.xml', '.txt', '.css', '.svg', '.js', '.json', '.webmanifest'))
    p = OUT + path if flat else OUT + path + 'index.html'
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    if add and not flat:
        URLS.append(path)


def ld(*objs):
    return ''.join('<script type="application/ld+json">%s</script>'
                   % json.dumps(o, ensure_ascii=False, separators=(',', ':')) for o in objs)


def crumb(items):
    """★첫 칸에 「홈」을 넣지 않는다([[naver-structured-data-types]])."""
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n,
                                 'item': cfg.HOST + u} for i, (n, u) in enumerate(items)]}


def faq_ld(qa):
    return {'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': q,
                            'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}}
                           for q, a in qa]}


ORG = {'@context': 'https://schema.org', '@type': 'Organization', '@id': cfg.HOST + '/#org',
       'name': cfg.BRAND, 'url': cfg.HOST + '/', 'description': cfg.TAGLINE,
       'telephone': cfg.TEL, 'logo': cfg.HOST + '/favicon.svg',
       'areaServed': [{'@type': 'AdministrativeArea', 'name': s['nm']} for s in REG]}


# ══════════════ 공통 조각 ══════════════
def bc_html(items):
    return ('<div class="wrap bc">' + ' › '.join(
        ('<a href="%s">%s</a>' % (u, esc(n))) for n, u in items[:-1])
        + ' › ' + esc(items[-1][0]) + '</div>')


TRUST = [('clock', '24시간 접수', '밤·새벽·주말도 받습니다'),
         ('cam', '보고 나서 시작', '내시경으로 안쪽을 확인합니다'),
         ('check', '확정 견적', '현장에서 금액을 맞춘 뒤 작업합니다'),
         ('shield', '원인까지', '뚫고 끝내지 않고 왜 막혔는지 봅니다'),
         ('pin', '전국 출동', '가까운 기사가 움직입니다'),
         ('find', '열기 전에 탐지', '벽·바닥은 자리를 정한 다음 엽니다')]


def trust_row():
    return ('<section class="alt"><div class="wrap"><div class="grid g3">' + ''.join(
        '<div class="card"><div class="ibx">%s</div><h3>%s</h3><p>%s</p></div>'
        % (svg.ico(k, COL['acc2'], 22), t, d) for k, t, d in TRUST) + '</div></div></section>')


STEPS = [('전화 접수', '지금 상태를 말씀해 주시면 됩니다. 도착 전에 하실 수 있는 조치를 먼저 안내해 드립니다.'),
         ('현장 도착', '가장 가까운 기사가 움직입니다. 공용 공간은 양생하고 들어갑니다.'),
         ('진단과 확정 견적', '어디서 멈췄는지, 어디가 새는지 좁힙니다. 할 일과 금액을 맞춘 다음 시작합니다.'),
         ('작업과 확인', '물을 다시 흘려 직접 보시는 앞에서 확인하고, 작업한 자리를 정리하고 나옵니다.')]


def steps_block():
    return ('<section><div class="wrap"><span class="kick">HOW IT WORKS</span>'
            '<h2>전화 한 통이면 됩니다</h2>'
            '<p class="lead">접수에서 마무리까지 네 걸음입니다.</p>'
            '<div class="steps">' + ''.join(
                '<div class="step"><b>%d</b><div><strong>%s</strong><p>%s</p></div></div>'
                % (i + 1, t, d) for i, (t, d) in enumerate(STEPS))
            + '</div></div></section>')


def svc_grid(cur=None, n=10):
    out = []
    for slug, nm, one, ic in cfg.SERVICES[:n]:
        if slug == cur:
            continue
        out.append('<a class="card" href="/service/%s/"><div class="ibx">%s</div>'
                   '<h3>%s</h3><p>%s</p><span class="more">자세히 보기 →</span></a>'
                   % (slug, svg.ico(ic, COL['acc2'], 22), nm, one))
    return '<div class="grid g4">' + ''.join(out) + '</div>'


def reel(idxs):
    return '<div class="reel">' + ''.join(
        '<figure><img src="%s" srcset="%s 420w, %s 760w" sizes="230px" width="420" height="315" '
        'loading="lazy" alt="%s"><figcaption>%s</figcaption></figure>'
        % (photos.thumb(i), photos.thumb(i), photos.img(i), esc(cap), esc(cap))
        for i, k, cap in idxs) + '</div>'


def case_grid(idxs):
    return '<div class="grid g3">' + ''.join(
        '<figure class="card" style="padding:0;overflow:hidden">'
        '<img src="%s" srcset="%s 420w, %s 760w" sizes="(max-width:560px) 100vw, 350px" '
        'width="760" height="570" loading="lazy" alt="%s" style="display:block;width:100%%;'
        'aspect-ratio:4/3;object-fit:cover">'
        '<figcaption style="padding:13px 15px;color:%s;font-size:14.5px">%s</figcaption></figure>'
        % (photos.img(i), photos.thumb(i), photos.img(i), esc(cap), COL['mut'], esc(cap))
        for i, k, cap in idxs) + '</div>'


def pick_photos(seed, spot=None, n=3):
    kinds = photos.SPOT_KIND.get(spot, []) if spot else []
    pool = [c for c in photos.CASES if c[1] in kinds] or photos.CASES
    o = svg.h(seed, len(pool))
    out = [pool[(o + i * 3) % len(pool)] for i in range(n)]
    seen = []
    for c in out:
        if c not in seen:
            seen.append(c)
    while len(seen) < n:
        c = photos.CASES[(o + len(seen) * 7) % len(photos.CASES)]
        if c not in seen:
            seen.append(c)
    return seen


def price_block():
    rows = [('누수탐지', '벽·바닥을 열기 전에 새는 자리를 찾습니다'),
            ('누수공사', '찾은 구간만 열고 고친 뒤 되돌립니다'),
            ('하수구막힘', '집 안 배수구부터 바깥 맨홀까지'),
            ('배관막힘', '관 안쪽에 쌓인 것을 긁어냅니다'),
            ('수전·변기 교체', '부속만 갈아도 되는지 먼저 봅니다'),
            ('고압세척', '되풀이되는 자리는 관 벽까지 씻어 냅니다')]
    return ('<table class="tbl"><thead><tr><th>하는 일</th><th>금액</th><th>어떤 일인가</th></tr></thead>'
            '<tbody>' + ''.join('<tr><td>%s</td><td>현장 확정</td><td>%s</td></tr>' % r for r in rows)
            + '</tbody></table>'
            '<p class="lead" style="margin-top:14px">금액은 자리와 방법이 정해져야 나옵니다. '
            '전화로 못 박지 않고, 현장에서 범위를 정해 확정 견적을 말씀드린 다음 시작합니다.</p>')


def faq_block(qa):
    return ''.join('<details class="faq"><summary>%s</summary><div>%s</div></details>'
                   % (esc(q), a) for q, a in qa)


KWCHIPS = cfg.MAIN_KW + cfg.SUB_KW


def strip_bar(seed='s'):
    """쪽마다 12낱말씩 돌려 깐다 — 21개를 전 쪽에 다 깔면 1만 쪽에서 무게가 된다."""
    o = svg.h(seed, len(KWCHIPS))
    ks = cfg.MAIN_KW + [KWCHIPS[(o + i * 3) % len(KWCHIPS)] for i in range(8)]
    li = ''.join('<li>%s</li>' % k for k in ks)
    return '<div class="strip"><ul>%s%s</ul></div>' % (li, li)


def hero_block(kicker, l1, l2, seed, lead=''):
    return ('<div class="hero">%s<div class="wrap">'
            '<div class="cta"><a class="btn btn-p" href="tel:%s">%s%s %s</a>'
            '<a class="btn btn-s" href="/service/">하는 일 보기</a></div>'
            '%s</div></div>'
            % (svg.hero(kicker, l1, l2, seed) + svg.hero_m(kicker, l1, l2, seed), cfg.TEL_RAW,
               svg.ico('call', COL['ink'], 19), cfg.EMERGENCY, cfg.TEL,
               ('<p class="sub">%s</p>' % lead) if lead else ''))


def sub_kw(gu_slug):
    """★행정동마다 보조키워드를 돌려 넣되, **한 구 안에서 17개가 하나도 빠지지 않게** 한다.
       3동 × 3시공점 × 2낱말 = 18칸 ≥ 17낱말. 시작점은 구마다 다르다."""
    k = list(cfg.SUB_KW)
    o = svg.h(gu_slug, len(k))
    k = k[o:] + k[:o]
    return k + [k[0]]


# ══════════════ 홈 ══════════════
def home():
    m = seo.home()
    qa = [('밤이나 새벽에도 출동되나요?',
           '시간을 끊지 않고 접수를 받습니다. 물이 넘치는 중이라면 먼저 전화 주십시오. '
           '도착 전에 잠가야 할 것부터 안내해 드립니다.'),
          ('금액은 언제 정해지나요?',
           '현장에서 범위를 보고 확정해 드립니다. 전화로 금액을 못 박지 않습니다. '
           '할 일과 금액을 맞춘 다음 시작합니다.'),
          ('누수탐지만 따로 받을 수 있나요?',
           '찾는 것까지만 하셔도 됩니다. 어디가 새는지 확인한 다음 공사를 언제 할지는 '
           '보시고 정하시면 됩니다.'),
          ('뚫었는데 또 막히면요?',
           '뚫는 것으로 끝내지 않고 왜 막혔는지를 함께 봅니다. 쌓인 것 때문인지, '
           '걸린 것 때문인지, 관 자체 문제인지에 따라 다음 할 일이 달라집니다.'),
          ('어느 지역까지 가나요?',
           '전국에서 접수를 받습니다. 시·도에서 시·군·구, 다시 행정동까지 좁혀 '
           '그 동네 안내를 보실 수 있습니다.')]
    sido_cards = ''.join(
        '<a class="card" href="/area/%s/"><h3>%s</h3><p>%s</p>'
        '<span class="more">지역 보기 →</span></a>' % (s['slug'], s['nm'],
            ' · '.join(g['nm'] for g in s['gus'][:4])) for s in REG)
    html = (
        tpl.head(m['title'], m['desc'], cfg.HOST + '/',
                 jsonld=ld(ORG,
                           {'@context': 'https://schema.org', '@type': 'WebSite',
                            'name': cfg.BRAND, 'url': cfg.HOST + '/'},
                           {'@context': 'https://schema.org', '@type': 'Service',
                            'serviceType': '누수탐지·누수공사·하수구막힘·배관막힘',
                            'provider': {'@id': cfg.HOST + '/#org'},
                            'areaServed': {'@type': 'Country', 'name': '대한민국'},
                            'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': '하는 일',
                                'itemListElement': [
                                    {'@type': 'Offer', 'itemOffered':
                                     {'@type': 'Service', 'name': nm, 'description': one}}
                                    for _, nm, one, _ in cfg.SERVICES]}},
                           faq_ld(qa)))
        + tpl.header('/')
        + '<h1 class="sr">%s</h1>' % esc(cfg.BRAND + ' — ' + cfg.TAGLINE)
        + hero_block('24시 긴급출동 · 전국', '물이 멈추면, 바로', '누수탐지 · 하수구막힘 · 배관막힘', 'home',
                     '벽과 바닥을 열기 전에 새는 자리부터 찾습니다. 현장 확인 후 확정 견적으로 진행합니다.')
        + strip_bar()
        + '<section><div class="wrap"><span class="kick">REAL WORK</span>'
          '<h2>실제 작업 현장</h2><p class="lead">사장님이 직접 다닌 현장 사진입니다.</p>'
        + reel(photos.CASES[:12]) + '</div></section>'
        + trust_row()
        + steps_block()
        + '<section class="alt"><div class="wrap ctr"><span class="kick">SERVICE</span>'
          '<h2>하는 일</h2><p class="lead">막힌 것을 여는 일과 새는 것을 찾는 일, '
          '두 가지가 중심입니다.</p></div><div class="wrap">' + svc_grid() + '</div></section>'
        + '<section><div class="wrap"><span class="kick">WHY</span><h2>이렇게 일합니다</h2>'
          '<p class="lead">다른 곳과 무엇이 다른지 적어 두었습니다.</p>'
          '<table class="tbl"><thead><tr><th>항목</th><th>%s</th><th>흔한 경우</th></tr></thead><tbody>'
          '<tr><td>금액</td><td>현장 확인 후 확정</td><td>전화로 먼저 못 박음</td></tr>'
          '<tr><td>벽·바닥</td><td>탐지로 자리를 정한 뒤 개방</td><td>짐작으로 먼저 개방</td></tr>'
          '<tr><td>막힘</td><td>원인까지 확인</td><td>뚫고 바로 마무리</td></tr>'
          '<tr><td>접수</td><td>시간을 끊지 않음</td><td>주간에만</td></tr>'
          '<tr><td>마무리</td><td>직접 보시는 앞에서 확인</td><td>말로만 설명</td></tr>'
          '</tbody></table></div></section>' % cfg.BRAND
        + '<section class="alt"><div class="wrap"><span class="kick">CASE</span>'
          '<h2>작업 사진</h2><p class="lead">같은 문제로 고민 중이시라면 사진부터 보십시오.</p>'
        + case_grid(photos.CASES[9:18]) + '<p class="lead" style="margin-top:18px">'
          '<a class="btn btn-s" href="/case/">사례 더 보기</a></p></div></section>'
        + '<section><div class="wrap"><span class="kick">PRICE</span><h2>요금 안내</h2>'
        + price_block() + '</div></section>'
        + '<section class="alt"><div class="wrap"><span class="kick">AREA</span>'
          '<h2>출동 지역</h2><p class="lead">시·도를 고르면 시·군·구와 행정동까지 들어갑니다.</p>'
          '<div class="grid g4">' + sido_cards + '</div></div></section>'
        + '<section><div class="wrap"><h2>자주 묻는 질문</h2>' + faq_block(qa) + '</div></section>'
        + tpl.footer())
    w('/', html)


# ══════════════ 지역 ══════════════
def area_index():
    t, d = seo.STATIC['area']
    cards = ''.join(
        '<a class="card" href="/area/%s/"><h3>%s</h3><p>%s</p>'
        '<span class="more">%s 지역 보기 →</span></a>'
        % (s['slug'], s['nm'], ' · '.join(g['nm'] for g in s['gus'][:5]), s['nm']) for s in REG)
    html = (tpl.head(t, d, cfg.HOST + '/area/',
                     jsonld=ld(crumb([('지역 안내', '/area/')])))
            + tpl.header('/area/') + bc_html([('지역 안내', '/area/')])
            + '<section><div class="wrap"><h1>전국 지역 안내</h1>'
              '<p class="lead">시·도를 고르시면 그 안의 시·군·구가 나옵니다. '
              '한 번 더 좁히면 행정동까지 들어갑니다.</p>'
              '<div class="grid g3">' + cards + '</div></div></section>'
            + '<section class="alt"><div class="wrap"><h2>하는 일</h2>' + svc_grid() + '</div></section>'
            + tpl.footer())
    w('/area/', html)


def sido_page(s):
    m = seo.sido(s)
    V = {'S': s['nm']}
    bodyhtml = bank.body(prose.S_HEAD, prose.S_BODY, V, s['slug'])
    cards = ''.join('<a class="card" href="/area/%s/"><h3>%s</h3><p>%s</p>'
                    '<span class="more">동네까지 보기 →</span></a>'
                    % (g['slug'], g['nm'], ' · '.join(x['nm'] for x in g['dongs'])) for g in s['gus'])
    cr = [('지역 안내', '/area/'), (s['nm'], '/area/%s/' % s['slug'])]
    html = (tpl.head(m['title'], m['desc'], cfg.HOST + '/area/%s/' % s['slug'],
                     jsonld=ld(crumb(cr),
                               {'@context': 'https://schema.org', '@type': 'Service',
                                'serviceType': '누수탐지·하수구막힘·배관막힘',
                                'provider': {'@id': cfg.HOST + '/#org'},
                                'areaServed': {'@type': 'AdministrativeArea', 'name': s['nm']}}))
            + tpl.header('/area/') + bc_html(cr)
            + hero_block('%s 전역 24시' % s['nm'], '%s 누수탐지·하수구막힘' % s['nm'],
                         '배관막힘까지 한 번에', s['slug'])
            + strip_bar()
            + '<section><div class="wrap"><h1>%s 누수탐지·누수공사·하수구막힘·배관막힘</h1>'
              '<div class="read">%s</div></div></section>' % (s['nm'], bodyhtml)
            + '<section class="alt"><div class="wrap"><h2>%s 시·군·구</h2>'
              '<p class="lead">지역을 고르시면 그 안의 동네로 더 좁힐 수 있습니다.</p>'
              '<div class="grid g3">%s</div></div></section>' % (s['nm'], cards)
            + '<section><div class="wrap"><h2>하는 일</h2>' + svc_grid(n=8) + '</div></section>'
            + tpl.footer())
    w('/area/%s/' % s['slug'], html)


def n_shop(g):
    """★동이 한두 곳뿐인 구(동탄구·연제구·증평군 같은 곳)는 시공점을 늘린다.
       그래야 보조키워드 17개가 **그 구 안에서도 하나도 빠지지 않는다**(사장님 지시)."""
    import math
    return max(3, math.ceil(18.0 / (2 * len(g['dongs']))))


def dong_shops(g, d, di):
    """행정동 한 곳당 가상 시공점. 보조키워드는 구 안에서 하나도 빠지지 않게 돌린다."""
    ks = sub_kw(g['slug'])
    n = n_shop(g)
    out = []
    for j in range(n):
        p = (di * n + j) * 2
        k1, k2 = ks[p % 18], ks[(p + 1) % 18]
        nm = shops.pick(g['slug'] + d['slug'], j)
        if j and nm in [o['nm'] for o in out]:
            nm = shops.pick(g['slug'] + d['slug'] + 'x', j)
        out.append({'nm': nm, 'k1': k1, 'k2': k2,
                    'slug': '%s-%s-%d' % (g['slug'], d['slug'], j + 1)})
    return out


def shop_cards(s, g, d, sh_list):
    return '<div class="grid g3">' + ''.join(
        '<a class="card" href="/shop/%s/" style="padding:0;overflow:hidden">%s'
        '<div style="padding:15px 17px"><h3 style="margin:0 0 4px">%s</h3>'
        '<p>%s %s · %s·%s</p><span class="more">시공점 보기 →</span></div></a>'
        % (x['slug'], svg.shop_card(x['nm'], '%s %s' % (g['nm'], d['nm']), x['slug']),
           x['nm'], g['nm'], d['nm'], x['k1'], x['k2']) for x in sh_list) + '</div>'


def gu_page(s, g, gi):
    m = seo.gu(s, g)
    spot = cfg.SPOTS[svg.h(g['slug'], len(cfg.SPOTS))]
    ks = sub_kw(g['slug'])
    V = {'S': s['nm'], 'G': g['nm'], 'SP': spot[1], 'SPD': spot[2],
         'K1': ks[0], 'K2': ks[1], 'K3': ks[2]}
    bodyhtml = bank.body(prose.G_HEAD, prose.G_BODY, V, g['slug'])
    qa = [(bank.fill(bank.spin(q, g['slug'], i), V),
           bank.bold(bank.fill(bank.spin(a, g['slug'], i), V)))
          for i, (q, a) in enumerate(prose.FAQ_G)]
    dcards = ''.join(
        '<a class="card" href="/area/%s/%s/"><h3>%s %s</h3><p>%s</p>'
        '<span class="more">동네 안내 →</span></a>'
        % (g['slug'], x['slug'], g['nm'], x['nm'], x['nm'] + ' 하수구막힘·배관막힘·누수탐지 안내')
        for x in g['dongs'])
    sibs = [o for o in s['gus'] if o['slug'] != g['slug']]
    o = svg.h(g['slug'] + 'sib', max(1, len(sibs)))
    sib = [sibs[(o + i * 3) % len(sibs)] for i in range(min(6, len(sibs)))]
    sibhtml = ('<ul class="chips">' + ''.join(
        '<li><a href="/area/%s/">%s %s</a></li>' % (x['slug'], s['nm'], x['nm']) for x in sib)
        + '</ul>') if sib else ''
    ph = pick_photos(g['slug'], spot[0], 3)
    cr = [('지역 안내', '/area/'), (s['nm'], '/area/%s/' % s['slug']),
          (g['nm'], '/area/%s/' % g['slug'])]
    html = (tpl.head(m['title'], m['desc'], cfg.HOST + '/area/%s/' % g['slug'],
                     jsonld=ld(crumb(cr), faq_ld(qa),
                               {'@context': 'https://schema.org', '@type': 'Service',
                                'serviceType': '누수탐지·누수공사·하수구막힘·배관막힘',
                                'provider': {'@id': cfg.HOST + '/#org'},
                                'areaServed': {'@type': 'AdministrativeArea',
                                               'name': '%s %s' % (s['nm'], g['nm']),
                                               'geo': {'@type': 'GeoCoordinates',
                                                       'latitude': g['lat'], 'longitude': g['lng']}}}))
            + tpl.header('/area/') + bc_html(cr)
            + hero_block('%s %s 24시' % (s['nm'], g['nm']),
                         '%s 누수탐지·누수공사' % g['nm'], '하수구막힘·배관막힘', g['slug'])
            + strip_bar()
            + '<section><div class="wrap"><h1>%s %s 누수탐지·하수구막힘·배관막힘</h1>'
              '<div class="read">%s</div></div></section>' % (s['nm'], g['nm'], bodyhtml)
            + '<section class="alt"><div class="wrap"><h2>%s 작업 사진</h2>'
              '<p class="lead">%s 쪽에서 자주 손대는 자리입니다.</p>%s</div></section>'
              % (g['nm'], spot[1], case_grid(ph))
            + '<section><div class="wrap"><h2>%s 동네별 안내</h2>'
              '<p class="lead">동네를 고르시면 그 골목 이야기와 가까이 움직이는 시공점이 나옵니다.</p>'
              '<div class="grid g3">%s</div></div></section>' % (g['nm'], dcards)
            + '<section class="alt"><div class="wrap"><h2>자주 묻는 질문</h2>'
            + faq_block(qa) + '</div></section>'
            + '<section><div class="wrap"><h2>하는 일</h2>' + svc_grid(n=8)
            + ('<h2 style="margin-top:30px">%s 다른 지역</h2>%s' % (s['nm'], sibhtml) if sib else '')
            + '</div></section>'
            + tpl.footer())
    w('/area/%s/' % g['slug'], html)


def dong_page(s, g, d, di):
    ks = sub_kw(g['slug'])
    p0 = di * n_shop(g) * 2
    k1, k2, k3 = ks[p0 % 18], ks[(p0 + 1) % 18], ks[(p0 + 2) % 18]
    m = seo.dong(s, g, d, k1, k2)
    spot = cfg.SPOTS[svg.h(g['slug'] + d['slug'], len(cfg.SPOTS))]
    sh = dong_shops(g, d, di)
    V = {'S': s['nm'], 'G': g['nm'], 'N': d['nm'], 'SP': spot[1], 'SPD': spot[2],
         'K1': k1, 'K2': k2, 'K3': k3, 'M': sh[0]['nm']}
    bodyhtml = bank.body(prose.D_HEAD, prose.D_BODY, V, g['slug'], d['slug'])
    qa = [(bank.fill(bank.spin(q, g['slug'], d['slug'], i), V),
           bank.bold(bank.fill(bank.spin(a, g['slug'], d['slug'], i), V)))
          for i, (q, a) in enumerate(prose.FAQ_D)]
    sibs = [x for x in g['dongs'] if x['slug'] != d['slug']]
    if len(sibs) > 20:
        o = svg.h(d['slug'], len(sibs))
        sibs = [sibs[(o + i) % len(sibs)] for i in range(20)]
    sibhtml = ('<ul class="chips">' + ''.join(
        '<li><a href="/area/%s/%s/">%s %s</a></li>' % (g['slug'], x['slug'], g['nm'], x['nm'])
        for x in sibs) + '</ul>')
    ph = pick_photos(g['slug'] + d['slug'], spot[0], 3)
    url = '/area/%s/%s/' % (g['slug'], d['slug'])
    cr = [('지역 안내', '/area/'), (s['nm'], '/area/%s/' % s['slug']),
          (g['nm'], '/area/%s/' % g['slug']), (d['nm'], url)]
    geo = ({'@type': 'GeoCoordinates', 'latitude': d['lat'], 'longitude': d['lng']}
           if d['lat'] else None)
    area = {'@type': 'AdministrativeArea', 'name': '%s %s %s' % (s['nm'], g['nm'], d['nm'])}
    if geo:
        area['geo'] = geo
    html = (tpl.head(m['title'], m['desc'], cfg.HOST + url,
                     jsonld=ld(crumb(cr), faq_ld(qa),
                               {'@context': 'https://schema.org', '@type': 'Service',
                                'serviceType': '하수구막힘·배관막힘·누수탐지',
                                'provider': {'@id': cfg.HOST + '/#org'}, 'areaServed': area,
                                'description': m['desc']}))
            + tpl.header('/area/') + bc_html(cr)
            + hero_block('%s %s' % (g['nm'], d['nm']), '%s 하수구막힘·배관막힘' % d['nm'],
                         '누수탐지는 열기 전에', g['slug'] + d['slug'])
            + strip_bar()
            + '<section><div class="wrap"><h1>%s %s %s 하수구막힘·배관막힘·누수탐지</h1>'
              '<p class="lead">%s</p><div class="read">%s</div></div></section>'
              % (s['nm'], g['nm'], d['nm'], esc(m['desc']), bodyhtml)
            + '<section class="alt"><div class="wrap"><h2>%s 작업 사진</h2>'
              '<p class="lead">%s — %s</p>%s</div></section>'
              % (d['nm'], spot[1], spot[2], case_grid(ph))
            + '<section><div class="wrap"><h2>%s 시공점</h2>'
              '<p class="lead">%s 둘레를 맡는 곳입니다. 접수는 대표 전화 한 곳으로 받습니다.</p>'
              '%s</div></section>' % (d['nm'], d['nm'], shop_cards(s, g, d, sh))
            + '<section class="alt"><div class="wrap"><h2>자주 묻는 질문</h2>'
            + faq_block(qa) + '</div></section>'
            + '<section><div class="wrap"><h2>%s 다른 동네</h2>%s'
              '<h2 style="margin-top:30px">하는 일</h2>%s</div></section>'
              % (g['nm'], sibhtml, svc_grid(n=6))
            + tpl.footer())
    w(url, html)
    for j, x in enumerate(sh):
        shop_page(s, g, d, x, sh, spot)


def shop_page(s, g, d, x, sh, spot):
    m = seo.shop(x['nm'], g, d, x['k1'], x['k2'])
    V = {'S': s['nm'], 'G': g['nm'], 'N': d['nm'], 'M': x['nm'],
         'K1': x['k1'], 'K2': x['k2'], 'SP': spot[1]}
    d1 = bank.para(prose.SHOP_DESC[svg.h(x['slug'], len(prose.SHOP_DESC))], V, x['slug'])
    d2 = bank.para(prose.SHOP_DESC[(svg.h(x['slug'], len(prose.SHOP_DESC)) + 3)
                                   % len(prose.SHOP_DESC)], V, x['slug'] + 'b')
    others = [o for o in sh if o['slug'] != x['slug']]
    oh = '<ul class="chips">' + ''.join(
        '<li><a href="/shop/%s/">%s</a></li>' % (o['slug'], o['nm']) for o in others) + '</ul>'
    ph = pick_photos(x['slug'], spot[0], 2)
    url = '/shop/%s/' % x['slug']
    cr = [('지역 안내', '/area/'), (s['nm'], '/area/%s/' % s['slug']),
          (g['nm'], '/area/%s/' % g['slug']),
          (d['nm'], '/area/%s/%s/' % (g['slug'], d['slug'])), (x['nm'], url)]
    biz = {'@context': 'https://schema.org', '@type': 'Plumber', 'name': x['nm'],
           'url': cfg.HOST + url, 'telephone': cfg.TEL, 'image': cfg.HOST + photos.img(ph[0][0]),
           'description': m['desc'], 'parentOrganization': {'@id': cfg.HOST + '/#org'},
           'areaServed': {'@type': 'AdministrativeArea',
                          'name': '%s %s %s' % (s['nm'], g['nm'], d['nm'])},
           'openingHoursSpecification': {'@type': 'OpeningHoursSpecification',
                                         'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                                       'Friday', 'Saturday', 'Sunday'],
                                         'opens': '00:00', 'closes': '23:59'},
           'knowsAbout': [x['k1'], x['k2']] + cfg.MAIN_KW}
    if d['lat']:
        biz['geo'] = {'@type': 'GeoCoordinates', 'latitude': d['lat'], 'longitude': d['lng']}
    html = (tpl.head(m['title'], m['desc'], cfg.HOST + url, jsonld=ld(crumb(cr), biz))
            + tpl.header('/area/') + bc_html(cr)
            + '<section><div class="wrap"><div class="grid g2" style="align-items:center">'
              '<div>%s</div><div><h1>%s</h1><p class="lead">%s %s %s · %s·%s</p>'
              '<div class="cta"><a class="btn btn-p" href="tel:%s">%s%s %s</a>'
              '<a class="btn btn-s" href="/area/%s/%s/">%s 안내 보기</a></div></div>'
              '</div></div></section>'
              % (svg.shop_card(x['nm'], '%s %s' % (g['nm'], d['nm']), x['slug']),
                 x['nm'], s['nm'], g['nm'], d['nm'], x['k1'], x['k2'],
                 cfg.TEL_RAW, svg.ico('call', COL['ink'], 19), cfg.EMERGENCY, cfg.TEL,
                 g['slug'], d['slug'], d['nm'])
            + '<section><div class="wrap"><h2>%s 소개</h2><div class="read">%s%s</div>'
              '<ul class="chips" style="margin-top:14px">%s</ul></div></section>'
              % (x['nm'], d1, d2,
                 ''.join('<li><a href="/service/%s/">%s</a></li>' % (sl, nm)
                         for sl, nm, _, _ in cfg.SERVICES[:6]))
            + '<section class="alt"><div class="wrap"><h2>작업 사진</h2>%s</div></section>'
              % case_grid(ph)
            + '<section><div class="wrap"><h2>%s 다른 시공점</h2>%s'
              '<p class="lead" style="margin-top:22px">금액은 현장에서 범위를 보고 '
              '확정해 드립니다. <a class="more" href="/price/">요금 안내 보기 →</a></p>'
              '</div></section>' % (d['nm'], oh)
            + tpl.footer())
    w(url, html)


# ══════════════ 서비스 ══════════════
import prose_svc                                                      # noqa: E402


def service_index():
    t, d = seo.STATIC['service']
    html = (tpl.head(t, d, cfg.HOST + '/service/', jsonld=ld(crumb([('하는 일', '/service/')])))
            + tpl.header('/service/') + bc_html([('하는 일', '/service/')])
            + hero_block('SERVICE', '막힌 것을 열고', '새는 것을 찾습니다', 'svc')
            + strip_bar()
            + '<section><div class="wrap"><h1>하는 일</h1>'
              '<p class="lead">누수탐지와 누수공사, 하수구막힘과 배관막힘이 중심입니다. '
              '수전·변기 교체와 고압세척처럼 함께 나오는 일도 같은 걸음에 봅니다.</p>'
            + svc_grid() + '</div></section>'
            + '<section class="alt"><div class="wrap"><h2>이런 낱말로 찾아오십니다</h2>'
              '<ul class="chips">' + ''.join('<li><a href="/service/%s/">%s</a></li>'
                                             % (cfg.SERVICES[i % 10][0], k)
                                             for i, k in enumerate(cfg.SUB_KW))
            + '</ul></div></section>'
            + steps_block()
            + '<section class="alt"><div class="wrap"><h2>요금</h2>' + price_block() + '</div></section>'
            + tpl.footer())
    w('/service/', html)


def service_page(sv, i):
    slug, nm, one, ic = sv
    m = seo.service(sv)
    secs = prose_svc.SVC[slug]
    qa = prose_svc.SVC_FAQ[slug]
    body = ''.join('<h3>%s</h3><p>%s</p>' % (h, p) for h, p in secs)
    ph = pick_photos('svc' + slug, None, 6)
    kw = [cfg.SUB_KW[(i * 2 + j) % len(cfg.SUB_KW)] for j in range(5)]
    sido_chips = '<ul class="chips">' + ''.join(
        '<li><a href="/area/%s/">%s</a></li>' % (s['slug'], s['nm']) for s in REG) + '</ul>'
    cr = [('하는 일', '/service/'), (nm, '/service/%s/' % slug)]
    html = (tpl.head(m['title'], m['desc'], cfg.HOST + '/service/%s/' % slug,
                     jsonld=ld(crumb(cr), faq_ld(qa),
                               {'@context': 'https://schema.org', '@type': 'Service',
                                'name': nm, 'serviceType': nm, 'description': one,
                                'provider': {'@id': cfg.HOST + '/#org'},
                                'areaServed': {'@type': 'Country', 'name': '대한민국'}}))
            + tpl.header('/service/') + bc_html(cr)
            + hero_block(nm, '%s' % nm, one, 'svc' + slug)
            + strip_bar()
            + '<section><div class="wrap"><h1>%s — 전국 24시 접수</h1>'
              '<p class="lead">%s</p><div class="read">%s</div>'
              '<ul class="chips" style="margin-top:16px">%s</ul></div></section>'
              % (nm, one, body,
                 ''.join('<li><a href="/service/%s/">%s</a></li>'
                         % (cfg.SERVICES[(i + j + 1) % 10][0], k) for j, k in enumerate(kw)))
            + '<section class="alt"><div class="wrap"><h2>작업 사진</h2>%s</div></section>'
              % case_grid(ph)
            + steps_block()
            + '<section class="alt"><div class="wrap"><h2>자주 묻는 질문</h2>'
            + faq_block(qa) + '</div></section>'
            + '<section><div class="wrap"><h2>지역</h2>'
              '<p class="lead">시·도를 고르시면 시·군·구와 행정동까지 들어갑니다.</p>%s'
              '<h2 style="margin-top:30px">다른 작업</h2>%s</div></section>'
              % (sido_chips, svc_grid(cur=slug, n=10))
            + tpl.footer())
    w('/service/%s/' % slug, html)


# ══════════════ 고정 쪽 ══════════════
def static_pages():
    # 요금
    t, d = seo.STATIC['price']
    w('/price/', tpl.head(t, d, cfg.HOST + '/price/', jsonld=ld(crumb([('요금 안내', '/price/')])))
      + tpl.header('/price/') + bc_html([('요금 안내', '/price/')])
      + '<section><div class="wrap"><h1>요금 안내</h1>'
        '<p class="lead">전화로 금액을 못 박지 않습니다. 보지 않고 정한 금액은 '
        '현장에서 반드시 달라지기 때문입니다.</p>' + price_block()
      + '<h2 style="margin-top:34px">금액이 갈리는 지점</h2>'
        '<div class="grid g2">'
        '<div class="card"><h3>어디가 문제인가</h3><p>같은 증상이라도 세대 안쪽인지 '
        '공용 쪽인지, 눈에 보이는 자리인지 벽 안쪽인지에 따라 달라집니다.</p></div>'
        '<div class="card"><h3>어떻게 여는가</h3><p>부속만 갈면 되는지, 구간을 잘라 '
        '내야 하는지, 마감을 걷어 내고 되돌려야 하는지에 따라 달라집니다.</p></div>'
        '<div class="card"><h3>얼마나 걸리는가</h3><p>한 자리에서 끝나는 일과 '
        '여러 구간을 따라가며 봐야 하는 일은 품이 다릅니다.</p></div>'
        '<div class="card"><h3>자재가 들어가는가</h3><p>변기·수전·배관처럼 제품이 '
        '들어가면 그 값이 따로 들어갑니다. 직접 준비하셔도 됩니다.</p></div>'
        '</div>'
        '<h2 style="margin-top:34px">이렇게 정합니다</h2>' + ''.join(
            '<div class="step"><b>%d</b><div><strong>%s</strong><p>%s</p></div></div>'
            % (i + 1, a, b) for i, (a, b) in enumerate([
                ('전화로 상태 확인', '어느 자리가 멈췄는지, 언제부터인지만 말씀해 주십시오.'),
                ('현장에서 범위 확정', '어디를 어디까지 손대는지 눈으로 보고 정합니다.'),
                ('확정 금액 안내', '시작 전에 금액을 말씀드립니다. 작업 중에 올리지 않습니다.'),
                ('작업 후 함께 확인', '물을 다시 흘려 보시는 앞에서 확인하고 마칩니다.')]))
      + '</div></section>' + tpl.footer())
    # 시공사례
    t, d = seo.STATIC['case']
    w('/case/', tpl.head(t, d, cfg.HOST + '/case/', jsonld=ld(crumb([('시공 사례', '/case/')])))
      + tpl.header('/case/') + bc_html([('시공 사례', '/case/')])
      + hero_block('REAL WORK', '실제 작업 현장', '사진 그대로', 'case')
      + '<section><div class="wrap"><h1>시공 사례</h1>'
        '<p class="lead">사장님이 직접 다닌 현장 사진입니다. 날짜와 장소는 적지 않습니다.</p>'
      + case_grid(photos.CASES) + '</div></section>' + tpl.footer())
    # 이용안내
    t, d = seo.STATIC['guide']
    w('/guide/', tpl.head(t, d, cfg.HOST + '/guide/', jsonld=ld(crumb([('이용 안내', '/guide/')])))
      + tpl.header('/guide/') + bc_html([('이용 안내', '/guide/')])
      + '<section><div class="wrap"><h1>이용 안내</h1>'
        '<p class="lead">접수에서 마무리까지 어떤 차례로 움직이는지 적어 두었습니다.</p>'
        '</div></section>' + steps_block()
      + '<section class="alt"><div class="wrap"><h2>전화 주시기 전에</h2>'
        '<div class="grid g3">'
        '<div class="card"><h3>어느 자리인가</h3><p>변기인지 주방인지 욕실인지, '
        '한 곳인지 집 안 전체인지 알려 주십시오.</p></div>'
        '<div class="card"><h3>언제부터인가</h3><p>갑자기 멈춘 것과 오래 느려진 것은 '
        '원인이 다릅니다.</p></div>'
        '<div class="card"><h3>번지고 있는가</h3><p>물이 넘치는 중이라면 먼저 말씀해 '
        '주십시오. 잠가야 할 것부터 안내해 드립니다.</p></div></div></div></section>'
      + '<section><div class="wrap"><h2>이런 것은 하지 않습니다</h2>'
        '<div class="grid g2">'
        '<div class="card"><h3>보지 않고 금액 정하기</h3><p>전화로 금액을 못 박지 않습니다. '
        '현장에서 범위를 보고 확정합니다.</p></div>'
        '<div class="card"><h3>짐작으로 벽 열기</h3><p>새는 자리를 좁힌 다음 엽니다. '
        '넓게 걷어 내고 찾지 않습니다.</p></div>'
        '<div class="card"><h3>작업 중 금액 올리기</h3><p>처음 말씀드린 범위를 벗어나면 '
        '손을 멈추고 먼저 말씀드립니다.</p></div>'
        '<div class="card"><h3>뚫고 바로 마무리</h3><p>왜 막혔는지 함께 봅니다. '
        '같은 자리가 되풀이되지 않게 다음 할 일을 말씀드립니다.</p></div>'
        '</div></div></section>' + tpl.footer())
    # 자주 묻는 질문
    t, d = seo.STATIC['faq']
    qa = [('밤이나 새벽에도 출동되나요?',
           '시간을 끊지 않고 접수를 받습니다. 물이 넘치는 중이라면 먼저 전화 주십시오.'),
          ('금액은 언제 정해지나요?',
           '현장에서 범위를 보고 확정해 드립니다. 전화로 금액을 못 박지 않습니다.'),
          ('누수탐지만 따로 받을 수 있나요?',
           '찾는 것까지만 하셔도 됩니다. 공사를 언제 할지는 보시고 정하시면 됩니다.'),
          ('뚫었는데 또 막히면요?',
           '왜 막혔는지를 함께 봅니다. 쌓인 것인지 걸린 것인지 관 자체 문제인지에 따라 '
           '다음 할 일이 달라집니다.'),
          ('공용 배관 문제면 누가 부담하나요?',
           '건물마다 다릅니다. 세대 안쪽 일인지 공용 쪽 일인지부터 확인해 드립니다.'),
          ('제품을 직접 준비해도 되나요?',
           '사 두신 제품으로 달아 드립니다. 규격이 맞는지 미리 여쭤보시면 헛걸음이 줍니다.'),
          ('어느 지역까지 가나요?',
           '전국에서 접수를 받습니다. 지역 안내에서 시·도부터 행정동까지 좁혀 보실 수 있습니다.'),
          ('작업 시간은 얼마나 걸리나요?',
           '한 자리에서 끝나는 일은 대개 그날 끝납니다. 마감을 되돌려야 하면 더 걸립니다.')]
    w('/faq/', tpl.head(t, d, cfg.HOST + '/faq/',
                        jsonld=ld(crumb([('자주 묻는 질문', '/faq/')]), faq_ld(qa)))
      + tpl.header('/faq/') + bc_html([('자주 묻는 질문', '/faq/')])
      + '<section><div class="wrap"><h1>자주 묻는 질문</h1>' + faq_block(qa)
      + '</div></section>' + tpl.footer())
    # 소개
    t, d = seo.STATIC['about']
    w('/about/', tpl.head(t, d, cfg.HOST + '/about/', jsonld=ld(crumb([('소개', '/about/')]), ORG))
      + tpl.header('') + bc_html([('소개', '/about/')])
      + '<section><div class="wrap"><h1>%s 소개</h1>'
        '<p class="lead">%s</p>'
        '<div class="read">'
        '<h3>하는 일</h3><p>누수탐지와 누수공사, 하수구막힘과 배관막힘이 중심입니다. '
        '수전·변기 교체, 고압세척처럼 같은 걸음에 끝나는 일도 함께 봅니다.</p>'
        '<h3>일하는 방식</h3><p>벽과 바닥은 자리를 정한 다음 엽니다. 금액은 현장에서 '
        '범위를 보고 확정한 뒤 시작합니다. 막힘은 뚫는 것으로 끝내지 않고 왜 막혔는지 '
        '함께 봅니다.</p>'
        '<h3>접수</h3><p>접수는 대표 전화 한 곳으로 받습니다. 시간을 끊지 않습니다. '
        '지역 안내에서 시·도부터 행정동까지 좁혀 그 동네 안내를 보실 수 있습니다.</p>'
        '</div></div></section>' % (cfg.BRAND, cfg.TAGLINE) + tpl.footer())


# ══════════════ 자산·색인 ══════════════
def assets():
    w('/s.css', tpl.CSS)
    w('/favicon.svg', svg.favicon())
    w('/%s.txt' % INKEY, INKEY)
    w('/site.webmanifest', json.dumps(
        {'name': cfg.BRAND, 'short_name': cfg.BRAND, 'start_url': '/',
         'display': 'standalone', 'background_color': COL['bg'], 'theme_color': COL['acc'],
         'icons': [{'src': '/favicon.svg', 'sizes': 'any', 'type': 'image/svg+xml'}]},
        ensure_ascii=False))


def sitemaps():
    today = NOW.strftime('%Y-%m-%d')
    groups = {'main': [], 'area': [], 'shop': []}
    for u in URLS:
        groups['shop' if u.startswith('/shop/') else
               ('area' if u.startswith('/area/') else 'main')].append(u)
    names = []
    for g, us in groups.items():
        for n in range(0, len(us), 4000):
            chunk = us[n:n + 4000]
            fn = '/sitemap-%s%s.xml' % (g, '' if n == 0 else str(n // 4000 + 1))
            w(fn, '<?xml version="1.0" encoding="UTF-8"?>'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(
                  '<url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq>'
                  '<priority>%s</priority></url>'
                  % (cfg.HOST, u, today,
                     'daily' if u == '/' else 'weekly',
                     '1.0' if u == '/' else ('0.8' if u.count('/') <= 3 else '0.6'))
                  for u in chunk) + '</urlset>')
            names.append(fn)
    w('/sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>'
      '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(
          '<sitemap><loc>%s%s</loc><lastmod>%s</lastmod></sitemap>' % (cfg.HOST, n, today)
          for n in names) + '</sitemapindex>')
    return names


def rss():
    """네이버에 넣을 RSS. 최근 올린 쪽을 앞에 둔다."""
    items = ['/'] + ['/service/%s/' % s[0] for s in cfg.SERVICES] + \
            ['/price/', '/case/', '/guide/', '/faq/', '/area/'] + \
            [u for u in URLS if u.startswith('/area/') and u.count('/') == 4][:30]
    body = []
    for i, u in enumerate(items[:50]):
        ttl = TITLES.get(u, cfg.BRAND)
        dsc = DESCS.get(u, cfg.TAGLINE)
        pub = (NOW - timedelta(hours=i)).strftime('%a, %d %b %Y %H:%M:%S +0900')
        body.append('<item><title><![CDATA[%s]]></title><link>%s%s</link>'
                    '<guid isPermaLink="true">%s%s</guid>'
                    '<description><![CDATA[%s]]></description><pubDate>%s</pubDate></item>'
                    % (ttl, cfg.HOST, u, cfg.HOST, u, dsc, pub))
    w('/rss.xml', '<?xml version="1.0" encoding="UTF-8"?>'
      '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
      '<title><![CDATA[%s — %s]]></title><link>%s/</link>'
      '<atom:link href="%s/rss.xml" rel="self" type="application/rss+xml"/>'
      '<description><![CDATA[%s]]></description><language>ko</language>'
      '<lastBuildDate>%s</lastBuildDate>%s</channel></rss>'
      % (cfg.BRAND, cfg.TAGLINE, cfg.HOST, cfg.HOST, cfg.TAGLINE,
         NOW.strftime('%a, %d %b %Y %H:%M:%S +0900'), ''.join(body)))


def robots(maps):
    """★네이버·구글 **전면 허용**. Crawl-delay 를 넣지 않는다
       ([[static-host-naver-index-always-allow]] — Yeti 는 스스로 속도를 줄인다)."""
    ua = ''.join('User-agent: %s\nAllow: /\n\n' % a for a in
                 ['Yeti', 'NaverBot', 'Googlebot', 'Googlebot-Image', 'bingbot', 'Daumoa', '*'])
    w('/robots.txt', ua + ''.join('Sitemap: %s%s\n' % (cfg.HOST, m) for m in ['/sitemap.xml'] + maps)
      + 'Sitemap: %s/rss.xml\n' % cfg.HOST)


TITLES, DESCS = {}, {}
_w = w


def w(path, text, add=True):                                          # noqa: F811
    m = re.search(r'<title>(.*?)</title>', text)
    if m:
        TITLES[path] = m.group(1)
    m = re.search(r'<meta name="description" content="(.*?)"', text)
    if m:
        DESCS[path] = m.group(1)
    _w(path, text, add)


# ══════════════ 전체 ══════════════
def build():
    if os.path.isdir(OUT):
        for f in os.listdir(OUT):
            if f in ('.git', 'img'):
                continue
            p = os.path.join(OUT, f)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    home()
    service_index()
    for i, sv in enumerate(cfg.SERVICES):
        service_page(sv, i)
    static_pages()
    area_index()
    for s in REG:
        sido_page(s)
        for gi, g in enumerate(s['gus']):
            gu_page(s, g, gi)
            for di, d in enumerate(g['dongs']):
                dong_page(s, g, d, di)
    assets()
    maps = sitemaps()
    rss()
    robots(maps)
    n_area = len([u for u in URLS if u.startswith('/area/')])
    n_shop = len([u for u in URLS if u.startswith('/shop/')])
    tot = 0
    for r, _, fs in os.walk(OUT):
        tot += sum(os.path.getsize(os.path.join(r, f)) for f in fs)
    print('쪽 %d장 (지역 %d · 시공점 %d · 그 밖 %d) · %.1fMB'
          % (len(URLS), n_area, n_shop, len(URLS) - n_area - n_shop, tot / 1048576))


if __name__ == '__main__':
    build()
