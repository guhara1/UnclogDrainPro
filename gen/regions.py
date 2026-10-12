# -*- coding: utf-8 -*-
"""흐름터 — 전국 3층 지역(시도 / 시군구 / 대표 행정동 3곳)을 굽는다.

★사장님 지시(2026-10-12): "행정동 1동, 2동, 3동 이런건 **대표 1곳만**".
  → 숫자 행정동을 대표동으로 합친다. **구마다 전체 행정동을 다 싣는다.**
  ★처음에 「각 3개씩」을 '구마다 동 3곳'으로 잘못 읽어 강남구에 동이 3곳만 나왔다.
    사장님이 바로 잡아 주셨다 — 「각 3개씩」은 **행정동마다 시공점 3곳**이다.
  지명은 **지어내지 않는다** — 실제 목록에서만 뽑는다. 차례는 행정코드 순.
★★원본(hjd.geojson)은 광주와 전남을 '전남광주통합특별시' 한 덩어리로 준다
  → 광주 5개 자치구를 떼어 돌려놓는다([[region-loader-truncates-compound-numbered-dong]] 형제).
★좌표는 **경계 폴리곤의 무게중심**을 직접 계산한다. GEO 스키마에 쓸 진짜 좌표다.
★슬러그에 하이픈을 쓰지 않는다 — 시도와 구를 '-' 로 잇기 때문이다
  ([[sido-slug-hyphen-breaks-sgg-url]]).
"""
import json
import re
import sys

GEO = '/root/jigeusi/hjd.geojson'
OUT = '/root/heureum/gen/regions.json'
GWANGJU_GU = {'동구', '서구', '남구', '북구', '광산구'}
SIDO = {
    '서울특별시': ('서울', 'seoul'), '부산광역시': ('부산', 'busan'),
    '대구광역시': ('대구', 'daegu'), '인천광역시': ('인천', 'incheon'),
    '광주광역시': ('광주', 'gwangju'), '대전광역시': ('대전', 'daejeon'),
    '울산광역시': ('울산', 'ulsan'), '세종특별자치시': ('세종', 'sejong'),
    '경기도': ('경기', 'gyeonggi'), '강원특별자치도': ('강원', 'gangwon'),
    '충청북도': ('충북', 'chungbuk'), '충청남도': ('충남', 'chungnam'),
    '전북특별자치도': ('전북', 'jeonbuk'), '전라남도': ('전남', 'jeonnam'),
    '경상북도': ('경북', 'gyeongbuk'), '경상남도': ('경남', 'gyeongnam'),
    '제주특별자치도': ('제주', 'jeju'),
}
ORDER = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산', '세종',
         '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
NO_SUFFIX = {'종로'}

sys.path.insert(0, '/root/dajabi/gen')
from rom import rom                                                   # noqa: E402


def slug(nm):
    """'고양시덕양구' → goyangsidukyanggu 꼴. 하이픈을 만들지 않는다."""
    return re.sub(r'[^a-z0-9]', '', rom(nm).lower())


def base_dong(nm):
    """'역삼1동'·'종로1·2·3·4가동' → 대표 하나로. 읍·면·출장소는 그대로 둔다."""
    if nm[-1] in '읍면':
        return nm
    n = re.sub(r'[0-9]+(?:[·.][0-9]+)*가[0-9]*동$', '', nm)
    if n != nm:
        return n if n in NO_SUFFIX else n + '동'
    return re.sub(r'[0-9]+(?:[·.][0-9]+)*동$', '동', nm)


def gu_disp(nm):
    m = re.match(r'^(.+?시)(.+?구)$', nm)
    return (m.group(1) + ' ' + m.group(2)) if m else nm


def centroid(geom):
    """폴리곤 무게중심. 멀티폴리곤이면 가장 넓은 조각을 쓴다."""
    rings = []
    if geom['type'] == 'Polygon':
        rings = [geom['coordinates'][0]]
    else:
        rings = [p[0] for p in geom['coordinates']]
    best, ba = None, -1
    for r in rings:
        a = 0.0; cx = 0.0; cy = 0.0
        for i in range(len(r) - 1):
            x0, y0 = r[i][0], r[i][1]; x1, y1 = r[i + 1][0], r[i + 1][1]
            f = x0 * y1 - x1 * y0
            a += f; cx += (x0 + x1) * f; cy += (y0 + y1) * f
        if abs(a) < 1e-12:
            continue
        a *= 0.5
        if abs(a) > ba:
            ba = abs(a); best = (cx / (6 * a), cy / (6 * a))
    return (round(best[1], 5), round(best[0], 5)) if best else (None, None)


def build():
    d = json.load(open(GEO, encoding='utf-8'))
    tree = {}
    for f in d['features']:
        p = f['properties']
        sidonm = p['sidonm']
        if sidonm == '전남광주통합특별시':
            sidonm = '광주광역시' if p['sggnm'] in GWANGJU_GU else '전라남도'
        if sidonm not in SIDO:
            continue
        s_nm, s_slug = SIDO[sidonm]
        gu_raw = p['sggnm']
        dong_raw = p['adm_nm'].split()[-1]
        bd = base_dong(dong_raw)
        g = tree.setdefault((s_nm, s_slug), {}).setdefault(gu_raw, {})
        e = g.setdefault(bd, {'n': 0, 'cd': p['adm_cd2'], 'pts': []})
        e['n'] += 1
        e['cd'] = min(e['cd'], p['adm_cd2'])
        lat, lng = centroid(f['geometry'])
        if lat:
            e['pts'].append((lat, lng))
    out = []
    for s_nm in ORDER:
        s_slug = dict((k[0], k[1]) for k in tree)[s_nm]
        gus = []
        for gu_raw in sorted(tree[(s_nm, s_slug)]):
            dongs = tree[(s_nm, s_slug)][gu_raw]
            dl = []
            for nm, e in sorted(dongs.items(), key=lambda kv: kv[1]['cd']):
                lat = round(sum(p[0] for p in e['pts']) / len(e['pts']), 5) if e['pts'] else None
                lng = round(sum(p[1] for p in e['pts']) / len(e['pts']), 5) if e['pts'] else None
                dl.append({'nm': nm, 'slug': slug(nm), 'lat': lat, 'lng': lng})
            if not dl:
                continue
            gus.append({'nm': gu_disp(gu_raw), 'raw': gu_raw,
                        'slug': s_slug + '-' + slug(gu_raw), 'dongs': dl,
                        'lat': round(sum(x['lat'] for x in dl if x['lat']) / max(1, len([x for x in dl if x['lat']])), 5),
                        'lng': round(sum(x['lng'] for x in dl if x['lng']) / max(1, len([x for x in dl if x['lng']])), 5)})
        out.append({'nm': s_nm, 'slug': s_slug, 'gus': gus})
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    ng = sum(len(s['gus']) for s in out)
    nd = sum(len(g['dongs']) for s in out for g in s['gus'])
    print('시도 %d · 시군구 %d · 행정동 %d' % (len(out), ng, nd))
    for s in out:
        print('  %-3s %3d구 %4d동  예) %s' % (s['nm'], len(s['gus']),
              sum(len(g['dongs']) for g in s['gus']),
              ' / '.join(x['nm'] for x in s['gus'][0]['dongs']) if s['gus'] else ''))


if __name__ == '__main__':
    build()
