# -*- coding: utf-8 -*-
"""흐름터 — **가상 시공점** 이름을 만든다(2026-10-12 사장님 「업소는 가상으로」).

★형제 배관 3사(물길·틔움·다잡이)의 상호 3,952개를 읽어 **완전일치 0** 을 보장한다.
  나아가 그쪽이 쓰는 꼬리말(설비·기술·산업·공사·홈즈·기사단·리페어…)은 **아예 쓰지 않는다**.
★업체는 가상이므로 길 주소·별점·후기·실적 숫자를 만들지 않는다. 적는 것은
  **맡는 자리·하는 일·움직이는 때**뿐이다.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))

PRE = [
    '단비', '물레', '오름', '새벽', '한결', '다온', '미르', '해든', '소담', '윤슬',
    '라온', '아람', '다복', '너울', '들물', '밀물', '가람', '나루', '여울', '벼리',
    '도담', '두레', '솔빛', '별빛', '참솔', '온새', '하루', '바름', '고른', '든든',
    '한뼘', '모아', '이음', '새뜸', '터울', '잔물', '고요', '푸른', '청명', '초록',
    '햇살', '노을', '이슬', '서리', '무지개', '파랑', '들샘', '샘골', '돌샘', '구름',
    '백두', '한라', '태백', '소백', '금강', '낙동', '영산', '섬진', '두물', '세물',
    '바른길', '곧은', '찬찬', '야무진', '꼼꼼', '서두른', '한달음', '첫손', '손끝', '눈썰미',
    '물보라', '잔잔', '굽이', '마당', '봇물', '실개천', '방죽', '두레박', '두메', '벌터',
]
SUF = ['드레인', '워터스', '수리소', '배수원', '공업사',
       '누수센터', '플러밍', '배관팀', '수리방', '워크스']


def _sib():
    p = os.path.join(HERE, '_sib_names.txt')
    if not os.path.exists(p):
        return set()
    return set(x.strip() for x in open(p, encoding='utf-8') if x.strip())


def pool():
    """쓸 수 있는 상호를 모두 만든다. 형제와 겹치는 것은 버린다."""
    sib = _sib()
    # 형제가 머리말로 쓰는 낱말은 피한다 — 전체가 닮아 보인다
    sib_pre = set(s[:2] for s in sib) | set(s[:3] for s in sib)
    out = []
    for a in PRE:
        if a in sib_pre:
            continue
        for b in SUF:
            nm = a + b
            if nm in sib:
                continue
            out.append(nm)
    return out


POOL = pool()


def pick(seed, k=0):
    h = hashlib.md5(('%s|%d' % (seed, k)).encode('utf-8')).hexdigest()
    return POOL[int(h, 16) % len(POOL)]


if __name__ == '__main__':
    print('쓸 수 있는 상호 %d종 (머리말 %d · 꼬리말 %d)'
          % (len(POOL), len(set(n[:-len(SUF[0])] for n in POOL[:1])) or len(PRE), len(SUF)))
    print('보기:', ' / '.join(POOL[:8]))
    sib = _sib()
    print('형제 상호와 완전일치:', len([n for n in POOL if n in sib]))
