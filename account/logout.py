from flask import Response, Request, jsonify, make_response
from .checktoken import getTokens, setTokens


def logout(r: Request) -> Response:
    token = r.cookies.get("token")
    if not token:
        return jsonify({"code": 10007, "msg": "please login first"})
    tokens = getTokens()
    if token in tokens:
        del tokens[token]
        setTokens(tokens)
        resp = make_response(jsonify({"code": 0, "msg": "OK"}), 200, {"Content-Type": "application/json"})
        resp.set_cookie("token", "", max_age=0, path="/")
        return resp
    return jsonify({"code": 10010, "msg": "invalid token"})
