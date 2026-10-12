# -*- coding: utf-8 -*-
"""흐름터 — 마감 점검. 빌드 뒤 한 번에 다 본다."""
import collections
import os
import re
import sys

ROOT = '/root/heureum/repo/public'
sys.path.insert(0, '/root/heureum/gen')
import cfg                                                            # noqa: E402

pages = []
for r, _, fs in os.walk(ROOT):
    for f in fs:
        if f == 'index.html':
            pages.append(os.path.join(r, f))
print('쪽 %d장' % len(pages))

leak = 0; titles = collections.Counter(); descs = collections.Counter()
hrefs = collections.Counter(); imgs = set(); num = []; rank = []
bodies = {}
for p in pages:
    s = open(p, encoding='utf-8').read()
    u = '/' + os.path.relpath(p, ROOT)[:-10].replace('index.html', '')
    if '[[' in s or re.search(r'\{[A-Z]\w*\}', s):
        leak += 1
    m = re.search(r'<title>(.*?)</title>', s); titles[m.group(1)] += 1
    m = re.search(r'name="description" content="(.*?)"', s); descs[m.group(1)] += 1
    for h in re.findall(r'href="(/[^"#]*)"', s):
        hrefs[h] += 1
    for i in re.findall(r'src="(/img/[^"]+)"', s):
        imgs.add(i)
    if re.search(r'(1위|최고의 업체|순위 보장)', s):
        rank.append(u)
    body = ' '.join(re.sub('<[^>]+>', ' ', x) for x in re.findall(r'<div class="read">(.*?)</div>', s, re.S))
    if body.strip():
        bodies[u] = ' '.join(body.split())
    if re.search(r'(지역|동네|구)\s*(총\s*)?\d+\s*(곳|개)', s):
        num.append(u)
print('슬롯/자리표 샘 %d쪽' % leak)
print('제목 %d종 (겹침 %d) · 디스크립션 %d종 (겹침 %d)'
      % (len(titles), sum(v - 1 for v in titles.values() if v > 1),
         len(descs), sum(v - 1 for v in descs.values() if v > 1)))
print('개수 숫자 의심 %d · 순위 표현 %d' % (len(num), len(rank)))

# 내부 링크
bad = []
for h in hrefs:
    if h.endswith(('.xml', '.txt', '.css', '.svg', '.json', '.webmanifest')) or h.startswith('/img/'):
        t = ROOT + h
    else:
        t = ROOT + h + 'index.html'
    if not os.path.exists(t):
        bad.append(h)
print('내부 링크 %d종 · 끊김 %d' % (len(hrefs), len(bad)), bad[:6])
print('그림 %d종 · 없는 파일 %d' % (len(imgs), len([i for i in imgs if not os.path.exists(ROOT + i)])))

# 본문 교차중복(18낱말)
def grams(t, n=18):
    ws = t.split()
    return set(' '.join(ws[i:i + n]) for i in range(max(0, len(ws) - n + 1)))

keys = sorted(bodies)
samp = keys[::max(1, len(keys) // 300)][:300]
cnt = collections.Counter()
G = {}
for k in samp:
    G[k] = grams(bodies[k])
    for g in G[k]:
        cnt[g] += 1
dup = 0; tot = 0
for k in samp:
    tot += len(G[k]); dup += sum(1 for g in G[k] if cnt[g] > 1)
print('본문 교차중복(18낱말, 표본 %d쪽) %.2f%%' % (len(samp), 100.0 * dup / max(1, tot)))
