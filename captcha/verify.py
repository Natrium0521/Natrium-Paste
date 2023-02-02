import copy
import json
import os
import time

path = os.path.dirname(__file__) + "/captchas.json"


def getCaptchas() -> json:
    j: json
    with open(path, "r") as f:
        j = json.load(f)
    return j


def setCaptchas(j: json) -> None:
    with open(path, "w") as f:
        json.dump(j, f)


def verify(md5: str, val: str) -> int:
    """
    md5: md5 of captcha
    val: value submitted by user

    return: 0 or other error code
    """
    now = int(time.time())
    j = getCaptchas()
    jj = copy.copy(j)
    for i in jj:
        if now - j[i]["gen"] >= 86400:
            del j[i]
            os.remove(os.path.dirname(__file__) + f"/cache/{i}.jpg")
            if i == md5:
                setCaptchas(j)
                return 10011
        else:
            break
    if md5 in j:
        os.remove(os.path.dirname(__file__) + f"/cache/{md5}.jpg")
        if str(j[md5]["val"]) == val:
            del j[md5]
            setCaptchas(j)
            return 0
        del j[md5]
    setCaptchas(j)
    return 10012
