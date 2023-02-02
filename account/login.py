from flask import Response, Request, jsonify, make_response
from captcha import verify
from .checktoken import getTokens, setTokens, checkToken
from .register import getAccounts
import hashlib
import time


def login(r: Request) -> Response:
    username: str
    password: str
    captcha: str
    md5: str
    try:
        username = r.json["username"]
        password = r.json["password"]
        captcha = r.json["captcha"]
        md5 = r.json["md5"]
    except KeyError:
        return jsonify({"code": 10005, "msg": "missing parameter"})
    i = verify.verify(md5, captcha)
    if i == 10011:
        return jsonify({"code": i, "msg": "expired captcha"})
    elif i == 10012:
        return jsonify({"code": i, "msg": "wrong captcha"})
    code, msg = checkToken(r)
    if code <= 999:
        return jsonify({"code": 10008, "msg": "please logout first"})
    accounts = getAccounts()
    if username not in accounts:
        return jsonify({"code": 10004, "msg": "username not exist"})
    if password != accounts[username]["password"]:
        return jsonify({"code": 10003, "msg": "wrong password"})
    t = int(time.time())
    token = hashlib.md5(f"{t}{username}".encode()).hexdigest()
    tokens = getTokens()
    tokens[token] = {"username": username, "gen_time": t}
    setTokens(tokens)
    resp = make_response(jsonify({"code": 0, "msg": "OK"}), 200, {"Content-Type": "application/json"})
    resp.set_cookie("token", token, max_age=2419200, path="/")
    return resp
