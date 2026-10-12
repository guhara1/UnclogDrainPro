# -*- coding: utf-8 -*-
"""흐름터 — 화면 뼈대와 CSS.

★시인성 기준(사장님이 가장 신경 쓰시는 자리)
  ─ 본문 #E8F0F6 / 바탕 #0A1017 = 15.4:1, 보조 글자도 6.9:1 을 넘긴다
  ─ 강조색(주황)은 **배경으로만** 쓰고 그 위 글자는 검은색이다
    ([[accent-color-used-as-text-fails-wcag]])
  ─ 모든 단추는 높이 44px 이상, 손가락이 닿는 자리는 더 크게
  ─ 폭이 좁아지는 자리의 flex 항목에 min-width:0 ([[flex-min-width-auto-causes-mobile-overflow]])
★모바일 아래쪽 **24시 긴급전화 띠**는 전 쪽에 깔린다(사장님 지시). 본문이 가리지 않도록
  body 에 아래 여백을 준다.
"""
import sys

sys.path.insert(0, '/root/heureum/gen')
import cfg                                                            # noqa: E402
from cfg import COL                                                   # noqa: E402
import svg                                                            # noqa: E402

CSS = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%%}
body{margin:0;background:%(bg)s;color:%(tx)s;font-family:Pretendard,'Pretendard Variable',
 -apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR',sans-serif;
 font-size:16px;line-height:1.72;word-break:keep-all;overflow-wrap:break-word;
 padding-bottom:0}
img,svg{max-width:100%%;height:auto}
a{color:%(tx)s;text-decoration:none}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}

/* ── 머리 ── */
header{position:sticky;top:0;z-index:60;background:rgba(10,16,23,.92);
 backdrop-filter:blur(10px);border-bottom:1px solid %(line)s}
.hd{display:flex;align-items:center;gap:14px;height:62px}
.hd .lg{flex:0 0 auto}
nav.nav{display:flex;gap:4px;margin-left:auto;align-items:center;min-width:0}
nav.nav a{padding:8px 11px;border-radius:9px;font-size:14.5px;font-weight:600;color:%(mut)s}
nav.nav a:hover,nav.nav a[aria-current]{color:%(tx)s;background:%(card)s}
.tel-top{display:inline-flex;align-items:center;gap:7px;background:%(acc)s;color:%(ink)s;
 font-weight:800;padding:10px 15px;border-radius:999px;font-size:14.5px;white-space:nowrap}
.tel-top svg{stroke:%(ink)s}
.mbtn{display:none;margin-left:auto;background:%(card)s;border:1px solid %(line)s;color:%(tx)s;
 width:44px;height:40px;border-radius:10px;font-size:18px;line-height:1;cursor:pointer}
.mnav{display:none;border-top:1px solid %(line)s;background:%(bg2)s}
.mnav div{display:grid;grid-template-columns:1fr 1fr;gap:6px;padding:12px 20px 16px}
.mnav a{padding:11px 12px;border-radius:10px;background:%(card)s;font-size:15px;font-weight:600}
#mn:checked ~ .mnav{display:block}
#mn{display:none}

/* ── 히어로 ── */
.hero{position:relative}
.hero .hv{display:block;width:100%%;height:auto;aspect-ratio:1280/380}
.hero .hvm{display:none;width:100%%;height:auto}
.hero .cta{display:flex;gap:10px;flex-wrap:wrap;padding:16px 0 4px}
.btn{display:inline-flex;align-items:center;gap:8px;min-height:48px;padding:0 20px;
 border-radius:999px;font-weight:800;font-size:16px}
.btn-p{background:%(acc)s;color:%(ink)s}
.btn-p svg{stroke:%(ink)s}
.btn-s{background:%(card)s;color:%(tx)s;border:1px solid %(line)s}
.sub{color:%(mut)s;font-size:15px;margin:10px 0 0}

/* ── 띠 ── */
.strip{background:%(acc3)s;color:#120E04;overflow:hidden;white-space:nowrap}
.strip ul{display:flex;gap:26px;margin:0;padding:9px 0;list-style:none;
 animation:mv 42s linear infinite;width:max-content}
.strip li{font-size:13.5px;font-weight:800}
@keyframes mv{from{transform:translateX(0)}to{transform:translateX(-50%%)}}
@media(prefers-reduced-motion:reduce){.strip ul{animation:none}}

/* ── 사진 띠 ── */
.reel{display:grid;grid-auto-flow:column;grid-auto-columns:230px;gap:10px;overflow-x:auto;
 padding:4px 0 10px;scroll-snap-type:x mandatory}
.reel figure{margin:0;scroll-snap-align:start;border-radius:13px;overflow:hidden;
 background:%(card)s;border:1px solid %(line)s}
.reel img{width:100%%;aspect-ratio:4/3;object-fit:cover;display:block}
.reel figcaption{padding:9px 11px;font-size:13px;color:%(mut)s}

/* ── 구역 ── */
section{padding:52px 0}
section.alt{background:%(bg2)s}
.kick{display:inline-block;background:rgba(47,212,192,.14);color:%(acc2)s;font-size:12.5px;
 font-weight:800;letter-spacing:.06em;padding:5px 11px;border-radius:999px}
h1{font-size:clamp(26px,5.4vw,40px);line-height:1.26;letter-spacing:-.03em;margin:14px 0 10px}
h2{font-size:clamp(21px,3.6vw,30px);line-height:1.34;letter-spacing:-.025em;margin:12px 0 8px}
h3{font-size:18.5px;line-height:1.45;letter-spacing:-.02em;margin:26px 0 8px}
.lead{color:%(mut)s;font-size:16px;margin:0 0 22px}
.ctr{text-align:center}
.ctr .lead{max-width:620px;margin:0 auto 26px}

/* ── 카드 ── */
.grid{display:grid;gap:14px}
.g2{grid-template-columns:repeat(2,minmax(0,1fr))}
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
.card{background:%(card)s;border:1px solid %(line)s;border-radius:15px;padding:18px;min-width:0}
.card h3{margin:12px 0 5px;font-size:17.5px}
.card p{margin:0;color:%(mut)s;font-size:14.5px;line-height:1.62}
.card .more{display:inline-block;margin-top:10px;color:%(acc2)s;font-weight:700;font-size:14px}
a.card:hover{border-color:%(acc2)s}
.ibx{width:44px;height:44px;border-radius:12px;background:rgba(47,212,192,.12);
 display:flex;align-items:center;justify-content:center}

/* ── 단계 ── */
.steps{display:grid;gap:12px}
.step{display:flex;gap:14px;align-items:flex-start;background:%(card)s;border:1px solid %(line)s;
 border-radius:14px;padding:16px 18px;min-width:0}
.step b{flex:0 0 34px;height:34px;border-radius:50%%;background:%(acc)s;color:%(ink)s;
 display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800}
.step div{min-width:0}
.step p{margin:3px 0 0;color:%(mut)s;font-size:14.5px}

/* ── 표 ── */
.tbl{width:100%%;border-collapse:collapse;font-size:15px;background:%(card)s;
 border:1px solid %(line)s;border-radius:14px;overflow:hidden}
.tbl th,.tbl td{padding:13px 14px;border-bottom:1px solid %(line)s;text-align:left}
.tbl thead th{background:%(bg2)s;font-size:14px;color:%(mut)s}
.tbl thead th:nth-child(2){color:%(acc3)s}
.tbl tr:last-child td{border-bottom:0}
.tbl td:nth-child(2){font-weight:800}
.tbl td:nth-child(3){color:%(mut)s}

/* ── 지역 ── */
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.chips a{display:inline-block;padding:9px 14px;border-radius:999px;background:%(card)s;
 border:1px solid %(line)s;font-size:14.5px;font-weight:600}
.chips a:hover{border-color:%(acc2)s;color:%(acc2)s}
.sido{background:%(card)s;border:1px solid %(line)s;border-radius:15px;padding:18px}
.sido h3{margin:0 0 12px;color:%(acc2)s;font-size:17px}

/* ── 본문 글 ── */
.read h3{color:%(tx)s;border-left:3px solid %(acc)s;padding-left:11px}
.read p{margin:0 0 14px;color:#CFDCE6;font-size:15.6px;line-height:1.82}
.read strong{color:%(acc3)s;font-weight:700}

/* ── 문답 ── */
details.faq{background:%(card)s;border:1px solid %(line)s;border-radius:13px;margin-bottom:10px}
details.faq summary{padding:15px 17px;font-weight:700;cursor:pointer;list-style:none;
 display:flex;justify-content:space-between;gap:12px;font-size:15.5px}
details.faq summary::-webkit-details-marker{display:none}
details.faq summary::after{content:'+';color:%(acc2)s;font-weight:800}
details.faq[open] summary::after{content:'−'}
details.faq div{padding:0 17px 16px;color:%(mut)s;font-size:15px;line-height:1.75}

/* ── 마무리 띠 ── */
.band{background:linear-gradient(118deg,%(acc3)s,%(acc)s 62%%);color:%(ink)s;text-align:center;
 padding:46px 0}
.band h2{color:%(ink)s;margin:0 0 6px}
.band p{margin:0 0 18px;font-weight:700;opacity:.82}
.band .btn-p{background:%(ink)s;color:%(acc3)s}
.band .btn-p svg{stroke:%(acc3)s}

/* ── 발 ── */
footer{background:%(deep)s;border-top:1px solid %(line)s;padding:34px 0 96px;color:%(mut)s;
 font-size:14px}
footer a{color:%(mut)s}
footer a:hover{color:%(tx)s}
.fnav{display:flex;flex-wrap:wrap;gap:8px 18px;margin:16px 0}
.ai{font-size:12.6px;opacity:.72;margin-top:14px;line-height:1.6}

/* ── 모바일 긴급전화 띠 ── */
.callbar{position:fixed;left:0;right:0;bottom:0;z-index:70;display:none;
 background:%(acc)s;color:%(ink)s;align-items:center;justify-content:center;gap:9px;
 height:62px;font-weight:800;font-size:17px;box-shadow:0 -6px 20px rgba(0,0,0,.42)}
.callbar svg{stroke:%(ink)s}
.callbar b{font-size:15px;background:rgba(0,0,0,.14);padding:3px 9px;border-radius:999px}

/* ── 빵부스러기 ── */
.bc{font-size:13.5px;color:%(mut)s;padding:14px 0 0}
.bc a{color:%(mut)s}
.bc a:hover{color:%(acc2)s}

@media(max-width:900px){
 nav.nav{display:none}
 .mbtn{display:block}
 .tel-top{display:none}
 .g4{grid-template-columns:repeat(2,minmax(0,1fr))}
 .g3{grid-template-columns:repeat(2,minmax(0,1fr))}
 section{padding:38px 0}
 body{padding-bottom:62px}
 .callbar{display:flex}
}
@media(max-width:560px){
 .wrap{padding:0 16px}
 .g2,.g3,.g4{grid-template-columns:1fr}
 .reel{grid-auto-columns:200px}
 .hero .hv{display:none}
 .hero .hvm{display:block}
 .btn{width:100%%;justify-content:center}
}
""" % COL


def head(title, desc, canon, extra='', jsonld=''):
    v = ('<meta name="naver-site-verification" content="%s">' % cfg.VERIFY_NAVER) if cfg.VERIFY_NAVER else ''
    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>%s</title><meta name="description" content="%s">'
        '<link rel="canonical" href="%s">'
        '<meta property="og:type" content="website"><meta property="og:title" content="%s">'
        '<meta property="og:description" content="%s"><meta property="og:url" content="%s">'
        '<meta property="og:site_name" content="%s"><meta name="theme-color" content="%s">'
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
        '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/'
        'dist/web/variable/pretendardvariable-dynamic-subset.min.css">'
        '<link rel="stylesheet" href="/s.css">%s%s%s</head><body>'
        % (title, desc, canon, title, desc, canon, cfg.BRAND, COL['bg'], v, extra, jsonld))


NAV = [('/', '홈'), ('/service/', '서비스'), ('/area/', '지역'), ('/price/', '요금'),
       ('/case/', '시공사례'), ('/guide/', '이용안내'), ('/faq/', '자주 묻는 질문')]


def header(cur=''):
    nv = ''.join('<a href="%s"%s>%s</a>' % (u, ' aria-current="page"' if u == cur else '', t)
                 for u, t in NAV)
    mv = ''.join('<a href="%s">%s</a>' % (u, t) for u, t in NAV)
    return (
        '<header><div class="wrap hd"><a href="/" aria-label="%s 홈">%s</a>'
        '<nav class="nav">%s</nav>'
        '<a class="tel-top" href="tel:%s">%s%s 바로 연결</a>'
        '<input type="checkbox" id="mn"><label class="mbtn" for="mn" '
        'aria-label="메뉴 열기">☰</label>'
        '<div class="mnav"><div>%s</div></div></div></header>'
        % (cfg.BRAND, svg.logo(), nv, cfg.TEL_RAW, svg.ico('call', COL['ink'], 17), cfg.TEL, mv))


def callbar():
    """모바일 아래쪽 24시 긴급전화 띠 — 사장님 지시, 전 쪽 공통."""
    return ('<a class="callbar" href="tel:%s">%s%s<b>%s</b></a>'
            % (cfg.TEL_RAW, svg.ico('call', COL['ink'], 21), cfg.EMERGENCY, cfg.TEL))


def band(h2='지금 바로 연결하세요', p=None):
    return ('<div class="band"><div class="wrap"><h2>%s</h2><p>%s</p>'
            '<a class="btn btn-p" href="tel:%s">%s%s %s</a></div></div>'
            % (h2, p or '24시간 접수 · 현장 확인 후 확정 견적',
               cfg.TEL_RAW, svg.ico('call', COL['acc3'], 19), cfg.EMERGENCY, cfg.TEL))


def footer(links=''):
    fn = ''.join('<a href="%s">%s</a>' % (u, t) for u, t in NAV)
    return (
        '%s<footer><div class="wrap">%s'
        '<div class="fnav">%s</div>'
        '<p>%s · %s<br>전화 <a href="tel:%s">%s</a> · 접수는 시간을 끊지 않고 받습니다</p>'
        '%s'
        '<p class="ai">%s<br>시공점 소개는 지역별 안내를 위해 구성한 예시이며, '
        '실제 접수와 배정은 대표 전화로 이루어집니다.</p>'
        '<p style="opacity:.6;margin-top:14px">© 2026 %s</p>'
        '</div></footer>%s</body></html>'
        % (band(), svg.logo(118), fn, cfg.BRAND, cfg.TAGLINE, cfg.TEL_RAW, cfg.TEL,
           links, cfg.AI_NOTE, cfg.BRAND, callbar()))
