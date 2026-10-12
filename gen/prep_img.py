# -*- coding: utf-8 -*-
"""원본 작업 사진 → 웹용 두 벌(760px / 420px, 4:3). 사람 얼굴은 원본에 크게 잡힌 것이 없다.

★원본은 3~5MB 다. 그대로 올리면 사이트가 무거워진다([[site-build-lightweight]]).
"""
import os
import sys
from PIL import Image

SRC = '/tmp/claude-0/-data-wwwroot-therapyssem/f52ac394-ecc2-5190-aebc-b28e9255a444/scratchpad/dl'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/root/heureum/repo/public/img'
sys.path.insert(0, '/root/heureum/gen')
from photos import CASES                                              # noqa: E402


def crop43(im):
    w, h = im.size
    if w / h > 4 / 3:
        nw = int(h * 4 / 3); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w * 3 / 4); top = int((h - nh) * 0.38)
        im = im.crop((0, top, w, top + nh))
    return im


def run():
    os.makedirs(OUT, exist_ok=True)
    fs = sorted(os.listdir(SRC))
    n = 0
    for i, kind, cap in CASES:
        im = Image.open(os.path.join(SRC, fs[i])).convert('RGB')
        im = crop43(im)
        im.resize((760, 570), Image.LANCZOS).save('%s/w%02d.jpg' % (OUT, i),
                                                  quality=78, optimize=True, progressive=True)
        im.resize((420, 315), Image.LANCZOS).save('%s/t%02d.jpg' % (OUT, i),
                                                  quality=74, optimize=True, progressive=True)
        n += 1
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.endswith('.jpg'))
    print('작업 사진 %d장 · 모두 %.1fMB' % (n, tot / 1048576))


if __name__ == '__main__':
    run()
