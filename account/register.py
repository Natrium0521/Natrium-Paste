from flask import Response, jsonify, make_response
from captcha import verify
from .checktoken import getTokens, setTokens, checkToken
import json
import os
import hashlib
import time


path = os.path.dirname(__file__) + "/accounts.json"


def getAccounts() -> json:
    j: json
    with open(path, "r") as f:
        j = json.load(f)
    return j


def setAccounts(j: json) -> None:
    with open(path, "w") as f:
        json.dump(j, f)


def register(j: json) -> Response:
    username: str
    password: str
    captcha: str
    md5: str
    try:
        username = j["username"]
        password = j["password"]
        captcha = j["captcha"]
        md5 = j["md5"]
    except KeyError:
        return jsonify({"code": 10005, "msg": "missing parameter"})
    i = verify.verify(md5, captcha)
    if i == 10011:
        return jsonify({"code": i, "msg": "expired captcha"})
    elif i == 10012:
        return jsonify({"code": i, "msg": "wrong captcha"})
    if len(username) < 6:
        return jsonify({"code": 10001, "msg": "username too short"})
    j = getAccounts()
    if username in j:
        return jsonify({"code": 10002, "msg": "have same username"})
    j[username] = {
        "password": password,
        "register_time": int(time.time()),
        "permission": 0,
    }
    setAccounts(j)
    t = int(time.time())
    token = hashlib.md5(f"{t}{username}".encode()).hexdigest()
    tokens = getTokens()
    tokens[token] = {"username": username, "gen_time": t}
    setTokens(tokens)
    resp = make_response(jsonify({"code": 0, "msg": "OK"}), 200, {"Content-Type": "application/json"})
    resp.set_cookie("token", token, max_age=2419200, path="/")
    return resp
