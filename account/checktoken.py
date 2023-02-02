from flask import Request
import json
import os
import time


def getAccounts() -> json:
    j: json
    with open(os.path.dirname(__file__) + "/accounts.json", "r") as f:
        j = json.load(f)
    return j


def getTokens() -> json:
    j: json
    with open(os.path.dirname(__file__) + "/tokens.json", "r") as f:
        j = json.load(f)
    return j


def setTokens(j: json) -> None:
    with open(os.path.dirname(__file__) + "/tokens.json", "w") as f:
        json.dump(j, f)


def checkToken(r: Request) -> list:
    """
    return value:\n
        0-999 permission\n
        10009 expired\n
        10010 invalid\n
        10007 no token\n
    """
    token = r.cookies.get("token")
    if not token:
        return 10007, "please login first"
    tokens = getTokens()
    if token not in tokens:
        return 10010, "invalid token"
    if int(time.time()) - tokens[token]["gen_time"] >= 2419200:
        del tokens[token]
        setTokens(tokens)
        return 10009, "expired token"
    return (
        getAccounts()[tokens[token]["username"]]["permission"],
        tokens[token]["username"],
    )
