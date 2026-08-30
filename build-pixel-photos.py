# -*- coding: utf-8 -*-
"""픽셀 버전(version-pixel.html) 전용 사진 빌드.

일반 버전(index.html)이 쓰는 photos/ 와 완전히 분리해서 관리한다.
여기서 만든 것만 version-pixel.html 이 사용한다.

  photos-pixel/01.jpg ...  갤러리 사진 (모두 2:3, 1400px)
                           장수를 바꾸면 version-pixel.html 의 GAL_COUNT 도 맞출 것
  photos-pixel/og.jpg      카카오톡 링크 미리보기용 1200x630

일반 버전 사진을 바꿔도 이 폴더는 영향받지 않는다. 반대도 마찬가지.
"""
import os, re, shutil
from PIL import Image, ImageOps, ImageEnhance

SRC_FIELD = 'pictures/quest-scene-source.jpg'   # 들판 사진 (갤러리 첫 장)
SRC_ALL   = 'photos-all'                        # build-photos.py 가 만든 웹사이즈 보관본
OUT       = 'photos-pixel'

# 첫 장은 들판 사진, 그 뒤는 일반 버전 갤러리와 같은 순서로 이어붙인다.
# 픽셀 버전 갤러리 순서. 일반 버전(index.html)과 무관하게 여기서만 관리한다.
# photos-all/ 의 번호 기준이며, 첫 장은 위 SRC_FIELD(들판 사진)가 들어간다.
FOLLOWING = ['01', '17', '18', '07', '04', '20', '11', '14']

MAX_DIM = 1400
QUALITY = 84
OG_SIZE = (1200, 630)
OG_FACE_Y, OG_FACE_AT = 0.62, 0.55   # 들판 사진에서 두 사람이 있는 높이


def load(path):
    return ImageOps.exif_transpose(Image.open(path)).convert('RGB')


def fit(im, max_dim):
    ratio = min(1.0, max_dim / max(im.size))
    if ratio == 1.0:
        return im.copy()
    return im.resize((round(im.width * ratio), round(im.height * ratio)), Image.LANCZOS)


def make_og(im, path):
    w = im.width
    h = round(w * OG_SIZE[1] / OG_SIZE[0])
    top = max(0, min(im.height - h, round(im.height * OG_FACE_Y) - round(h * OG_FACE_AT)))
    crop = im.crop((0, top, w, top + h)).resize(OG_SIZE, Image.LANCZOS)
    ImageEnhance.Color(crop).enhance(1.12).save(path, quality=86, optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if re.fullmatch(r'(\d{2}|og)\.jpg', f):
            os.remove(os.path.join(OUT, f))

    field = load(SRC_FIELD)
    fit(field, MAX_DIM).save(os.path.join(OUT, '01.jpg'), quality=QUALITY, optimize=True)
    make_og(field, os.path.join(OUT, 'og.jpg'))
    print('01.jpg  <- 들판 사진')

    for i, num in enumerate(FOLLOWING, start=2):
        src = os.path.join(SRC_ALL, num + '.jpg')
        if not os.path.exists(src):
            print('!! %s 없음 — build-photos.py 를 먼저 실행하세요' % src)
            continue
        dst = os.path.join(OUT, '%02d.jpg' % i)
        shutil.copy2(src, dst)
        print('%s  <- %s/%s.jpg' % (os.path.basename(dst), SRC_ALL, num))

    shots = sorted(f for f in os.listdir(OUT) if re.fullmatch(r'\d{2}\.jpg', f))
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in shots)
    print('\n갤러리 %d장, 합계 %.1f MB' % (len(shots), total / 1024 ** 2))


if __name__ == '__main__':
    main()
