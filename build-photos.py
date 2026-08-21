# -*- coding: utf-8 -*-
"""pictures/ 원본 -> 웹용 이미지 생성.

같은 사진의 수정본이 여러 개 있으면 항상 최신 차수만 사용하므로,
새 수정본을 pictures/ 에 넣고 다시 실행해도 사진 번호가 밀리지 않는다.

  photos-all/NN.jpg  전체 사진 (gitignore, 갤러리 교체용 보관)
  photos/NN.jpg      index.html 이 실제로 쓰는 사진만
  photos/og.jpg      카카오톡 공유 미리보기용 1200x630
"""
import os, re, shutil, unicodedata
from PIL import Image, ImageOps

SRC        = 'pictures'
ALL_DIR    = 'photos-all'
WEB_DIR    = 'photos'
SELECTED   = ['01', '03', '07', '15', '11', '16', '17']   # index.html 갤러리 순서 (17=수정본2차)
MAX_DIM    = 1400
QUALITY    = 82
OG_SIZE    = (1200, 630)
OG_FACE_Y  = 0.23   # 세로 원본에서 얼굴이 오는 위치
OG_FACE_AT = 0.40   # 크롭 안에서 얼굴을 놓을 위치


def revision(name):
    """'수정본2차' -> 2, 차수 표기가 없으면 0."""
    m = re.search(r'수정본(\d+)차', unicodedata.normalize('NFC', name))
    return int(m.group(1)) if m else 0


def photo_code(name):
    """확장자와 수정본 표기를 뺀 사진 식별자."""
    return re.split(r'\s*수정본', unicodedata.normalize('NFC', name))[0]


def latest_originals():
    best = {}
    for f in os.listdir(SRC):
        if not f.lower().endswith('.jpg'):
            continue
        code = photo_code(f)
        if code not in best or revision(f) > revision(best[code]):
            best[code] = f
    # 액자메인(숫자로 시작하지 않는 이름)을 01번으로, 나머지는 이름순
    return sorted(best.values(), key=lambda f: (bool(re.match(r'^\d', f)), f))


def resize(im, max_dim):
    ratio = min(1.0, max_dim / max(im.size))
    if ratio == 1.0:
        return im.copy()
    return im.resize((round(im.width * ratio), round(im.height * ratio)), Image.LANCZOS)


def make_og(im, path):
    w = im.width
    h = round(w * OG_SIZE[1] / OG_SIZE[0])
    top = max(0, min(im.height - h, round(im.height * OG_FACE_Y) - round(h * OG_FACE_AT)))
    im.crop((0, top, w, top + h)).resize(OG_SIZE, Image.LANCZOS).save(path, quality=85, optimize=True)


def main():
    os.makedirs(ALL_DIR, exist_ok=True)
    os.makedirs(WEB_DIR, exist_ok=True)

    originals = latest_originals()
    mapping = []
    for i, name in enumerate(originals, 1):
        im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, name)))
        num = '%02d' % i
        resize(im, MAX_DIM).save(os.path.join(ALL_DIR, num + '.jpg'), quality=QUALITY, optimize=True)
        if i == 1:
            make_og(im, os.path.join(WEB_DIR, 'og.jpg'))
        mapping.append((num, revision(name), photo_code(name)))
        im.close()

    # index.html 이 쓰는 사진만 photos/ 로
    for f in os.listdir(WEB_DIR):
        if re.fullmatch(r'\d{2}\.jpg', f) and f[:2] not in SELECTED:
            os.remove(os.path.join(WEB_DIR, f))
    for num in SELECTED:
        shutil.copy2(os.path.join(ALL_DIR, num + '.jpg'), os.path.join(WEB_DIR, num + '.jpg'))

    print('%-4s %-5s %-14s %s' % ('NO', 'REV', 'PHOTO', 'IN GALLERY'))
    for num, rev, code in mapping:
        print('%-4s %-5s %-14s %s' % (num, 'rev%d' % rev if rev else '-',
                                      code.replace('액자메인', 'MAIN-'),
                                      'YES' if num in SELECTED else ''))
    print('\n전체 %d장 -> %s/, 사이트 사용 %d장 -> %s/'
          % (len(mapping), ALL_DIR, len(SELECTED), WEB_DIR))


if __name__ == '__main__':
    main()
