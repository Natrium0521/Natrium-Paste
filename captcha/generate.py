from PIL import Image, ImageDraw, ImageFont
from random import randint, seed, randrange
import hashlib
import json
import os
import time

font = ImageFont.truetype(os.path.dirname(__file__) + "/SmileySansCaptcha.ttf", 56)


def gen_str() -> list:
    opt = randint(1, 3)
    a = randrange(5) * 10 + randrange(10)
    b = randrange(5) * 10 + randrange(10)
    if a < b:
        a, b = b, a
    if opt == 1:
        return [f"{a}-{b}=", a - b]
    elif opt == 2 and a * b <= 400:
        return [f"{a}*{b}=", a * b]
    elif opt == 3 and b and a % b == 0:
        return [f"{a}÷{b}=", a // b]
    else:
        return [f"{a}+{b}=", a + b]


def generate() -> str:
    """
    return path of captcha
    """
    seed()
    img = Image.new(
        "RGB",
        (240, 100),
        (randint(220, 255), randint(220, 255), randint(220, 255)),
    )
    s, r = gen_str()
    left = 0
    for c in s:
        c_bk = Image.new("RGBA", (40, 60), (255, 255, 255, 0))
        c_dr = ImageDraw.Draw(c_bk)
        c_dr.text(
            (0, 2),
            c,
            (randrange(220), randrange(220), randrange(220)),
            font,
        )
        c_ro = c_bk.rotate(randint(-10, 20), expand=1)
        size = c_ro.size
        c_ro_f = Image.new("RGBA", size, (255, 255, 255, 0))
        p = c_ro.load()
        p_f = c_ro_f.load()
        offset = 0
        for x in range(size[0]):
            offset += randint(-3, 3)
            for y in range(size[1]):
                newy = y + offset // 3
                if newy >= size[1] or newy < 0:
                    continue
                p_f[x, newy] = p[x, y]
        img.paste(c_ro_f, (left + randint(-5, 10), randint(0, 20)), c_ro_f)
        left += 40
    draw = ImageDraw.Draw(img)
    for i in range(2400):
        draw.point(
            (randrange(240), randrange(100)),
            (randrange(255), randrange(255), randrange(255)),
        )
    for i in range(9):
        start = (randrange(240), randrange(100))
        end = (randrange(240), randrange(100))
        draw.line([start, end], (randrange(255), randrange(255), randrange(255)))
    path = os.path.dirname(__file__) + "/cache/tmp.jpg"
    img.save(path)
    f = open(path, "rb")
    md5obj = hashlib.md5()
    md5obj.update(f.read())
    f.close()
    md5 = md5obj.hexdigest()
    path_f = os.path.dirname(path) + f"/{md5}.jpg"
    os.rename(path, path_f)
    path = os.path.dirname(__file__) + "/captchas.json"
    j: json
    with open(path, "r") as f:
        j = json.load(f)
    j[md5] = {"val": r, "gen": int(time.time())}
    with open(path, "w") as f:
        json.dump(j, f)
    return path_f
