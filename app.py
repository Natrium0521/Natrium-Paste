from flask import Flask, send_file, request, render_template, redirect, jsonify
from flask_cors import CORS
from account import register, login, checktoken, logout
from captcha import generate, verify
import datetime
import hashlib
import json
import os
import random
import time

app = Flask(__name__)
CORS(app)
APP_PATH = os.path.dirname(__file__)


@app.route("/")
def home():
    p, m = checktoken.checkToken(request)
    if p <= 999:
        return render_template("homepage.html", is_login=True, username=m)
    else:
        return render_template("homepage.html", is_login=False)


@app.route("/new", methods=["GET"])
def home_new():
    p, m = checktoken.checkToken(request)
    if p <= 999:
        return render_template("new_paste.html", username=m)
    else:
        return redirect("/")


@app.route("/api/captcha", methods=["GET"])
def home_api_captcha():
    return send_file(generate.generate(), mimetype="image/gif")


@app.route("/api/register", methods=["POST"])
def home_api_register():
    return register.register(request.json)


@app.route("/api/login", methods=["POST"])
def home_api_login():
    return login.login(request)


@app.route("/api/check_account/<username>", methods=["GET"])
def home_api_checkaccount_(username):
    j = register.getAccounts()
    if username in j:
        return jsonify({"op": "login"})
    return jsonify({"op": "register"})


@app.route("/api/logout", methods=["GET"])
def home_api_logout():
    return logout.logout(request)


@app.route("/api/save_paste", methods=["POST"])
def home_api_savepaste():
    p, m = checktoken.checkToken(request)
    if p > 999:
        return jsonify({"code": 10007, "msg": "please login first"})
    pj = request.json
    if len(pj["content"].encode()) > 10485760:
        return jsonify({"code": 10016, "msg": "too much content"})
    i = verify.verify(pj["md5"], pj["captcha"])
    if i == 10011:
        return jsonify({"code": i, "msg": "expired captcha"})
    elif i == 10012:
        return jsonify({"code": i, "msg": "wrong captcha"})
    j: json
    if pj["pid"] != "":
        if not os.path.isfile(f'{APP_PATH}/data/{pj["pid"]}.json'):
            return jsonify({"code": 10013, "msg": "no such paste"})
        with open(f'{APP_PATH}/data/{pj["pid"]}.json', "r") as f:
            j = json.load(f)
        if m != j["author"]:
            return jsonify({"code": 10014, "msg": "no permission"})
        try:
            if pj["expire_time"] != "":
                j["expire_time"] = max(int(pj["expire_time"]), -1)
        except:
            return jsonify({"code": 10006, "msg": "illegal parameter"})
        if pj["psw"] != "no" and pj["content"] != "":
            j["psw"] = hashlib.md5(pj["content"].encode(encoding="utf-8")).hexdigest()
        else:
            j["psw"] = "no"
        j["content"] = pj["content"]
        j["edit_time"] = int(time.time())
        with open(f'{APP_PATH}/data/{pj["pid"]}.json', "w") as f:
            json.dump(j, f, ensure_ascii=False)
        return jsonify({"code": 0, "msg": "OK", "pid": pj["pid"], "psw": j["psw"]})
    else:
        if pj["content"] == "":
            return jsonify({"code": 10015, "msg": "missing content"})
        random.seed(int(time.time()))
        pid = ""
        while len(pid) < 6:
            pid += "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[random.randint(0, 61)]
            if len(pid) == 6:
                if os.path.isfile(f"{APP_PATH}/data/{pid}.json"):
                    pid = pid[1:]
        try:
            j = json.loads(f'{{"author":"{m}","create_time":{int(time.time())},"edit_time":-1,"expire_time":{max(int(pj["expire_time"]), -1)},"psw":"no"}}')
            j["content"] = pj["content"]
            if pj["psw"] == "":
                j["psw"] = hashlib.md5(pj["content"].encode(encoding="utf-8")).hexdigest()
        except:
            return jsonify({"code": 10006, "msg": "illegal parameter"})
        with open(f"{APP_PATH}/data/{pid}.json", "w") as f:
            json.dump(j, f, ensure_ascii=False)
        return jsonify({"code": 0, "msg": "OK", "pid": pid, "psw": j["psw"]})


@app.route("/pid/<pid>", methods=["GET"])
def home_pid_(pid):
    time_now = int(time.time())
    if time_now % 10 == 0:
        for f in os.listdir(APP_PATH + "/data/"):
            fp = open(APP_PATH + "/data/" + f, "r")
            j = json.load(fp)
            fp.close()
            if j["expire_time"] >= 0 and time_now > j["expire_time"]:
                os.remove(APP_PATH + "/data/" + f)
    p, m = checktoken.checkToken(request)
    is_login = True if p <= 999 else False
    if not os.path.isfile(f"{APP_PATH}/data/{pid}.json"):
        return render_template("no_paste.html", is_login=is_login, username=m)
    paste: json
    with open(f"{APP_PATH}/data/{pid}.json", "r") as f:
        paste = json.load(f)
    if paste["expire_time"] >= 0 and paste["expire_time"] < time_now:
        os.remove(f"{APP_PATH}/data/{pid}.json")
        return render_template("no_paste.html", is_login=is_login, username=m)
    if not (paste["psw"] == "no" or paste["psw"] == request.args.get("psw") or paste["author"] == m):
        return render_template("wrong_password.html", is_login=is_login, username=m)
    CREATE_TIME = datetime.datetime.fromtimestamp(paste["create_time"]).strftime("%Y/%m/%d %H:%M:%S")
    EDIT_TIME = datetime.datetime.fromtimestamp(paste["edit_time"]).strftime("%Y/%m/%d %H:%M:%S") if paste["edit_time"] >= 0 else ""
    EXPIRE_TIME = datetime.datetime.fromtimestamp(paste["expire_time"]).strftime("%Y/%m/%d %H:%M:%S") if paste["expire_time"] >= 0 else ""
    return render_template(
        "view_paste.html",
        author=paste["author"],
        create_time=CREATE_TIME,
        edit_time=EDIT_TIME,
        expire_time=EXPIRE_TIME,
        is_login=is_login,
        is_author=paste["author"] == m,
        username=m,
        content=paste["content"],
        is_pswneed=False if paste["psw"] == "no" else True,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8765)
