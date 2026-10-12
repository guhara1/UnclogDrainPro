#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""흐름터 — 네이버 IndexNow 통보.

★이 사이트는 **네틸리파이**에 있어서 자사 공용 통보기(`own_indexnow`, nginx vhost 자동발견)가
  못 찾는다. 그래서 따로 둔다([[own-indexnow-22-sites-never-notified]]).
★주소당 23시간 쿨다운 · 회차 상한 1500 — 전량을 한 번에 밀면 막힌다.
★IndexNow 는 「바뀌었다」는 **알림**이지 수집 보장이 아니다. 서치어드바이저의 수동 수집요청
  (하루 50건)과 **같이** 쓴다([[kkuk-naver-only-home-indexed]]).
사용: indexnow.py [--all]
"""
import json, os, re, sys, time, urllib.request, urllib.error
sys.path.insert(0, '/root/heureum/gen')
from cfg import HOST, INDEXNOW_KEY

EP = 'https://searchadvisor.naver.com/indexnow'
UA = {'User-Agent': 'Mozilla/5.0 (compatible; heureum-indexnow/1.0)'}
SEEN = '/root/heureum/indexnow_seen.json'
LOG = '/root/heureum/indexnow.log'
CAP, CHUNK, COOL = 1500, 500, 23 * 3600


def log(m):
    line = time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + m
    print(line, flush=True)
    open(LOG, 'a', encoding='utf-8').write(line + '\n')


def get(u):
    r = urllib.request.Request(u, headers=UA)
    return urllib.request.urlopen(r, timeout=40).read().decode('utf-8', 'replace')


def urls():
    out = []
    try:
        idx = get(HOST + '/sitemap.xml')
    except Exception as e:
        log('사이트맵 못 읽음 %s' % str(e)[:60]); return out
    maps = re.findall(r'<loc>([^<]+)</loc>', idx)
    if '<sitemapindex' in idx:
        for m in maps:
            try:
                out += re.findall(r'<loc>([^<]+)</loc>', get(m))
            except Exception:
                pass
    else:
        out = maps
    return [u.strip() for u in dict.fromkeys(out) if u.startswith(HOST)]


def post(chunk):
    body = json.dumps({'host': HOST.split('//')[1], 'key': INDEXNOW_KEY,
                       'keyLocation': '%s/%s.txt' % (HOST, INDEXNOW_KEY),
                       'urlList': chunk}, ensure_ascii=False).encode()
    r = urllib.request.Request(EP, data=body,
                               headers={'Content-Type': 'application/json; charset=utf-8', **UA})
    try:
        with urllib.request.urlopen(r, timeout=120) as x:
            return x.status, ''
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:80].decode('utf8', 'replace')
    except Exception as e:
        return 0, str(e)[:80]


def main(allmode=False):
    try:
        seen = json.load(open(SEEN))
    except Exception:
        seen = {}
    U = urls()
    if not U:
        log('주소 0건'); return
    now = time.time()
    fresh = U if allmode else [u for u in U if now - seen.get(u, 0) > COOL]
    if not fresh:
        log('전체 %d건 중 새 주소 0 — 보내지 않음' % len(U)); return
    fresh = fresh[:CAP]
    ok = 0
    for i in range(0, len(fresh), CHUNK):
        c = fresh[i:i + CHUNK]
        code, note = post(c)
        log('%d~%d건 → HTTP %s %s' % (i + 1, i + len(c), code or '-', note))
        if code in (200, 202, 422):
            for u in c:
                seen[u] = now
            if code != 422:
                ok += len(c)
        if code == 429:
            log('429 — 이 회차 중단'); break
        time.sleep(3)
    json.dump(seen, open(SEEN, 'w'))
    log('제출 %d건 (전체 %d · 통보 누적 %d)' % (ok, len(U), len(seen)))


if __name__ == '__main__':
    main('--all' in sys.argv)
