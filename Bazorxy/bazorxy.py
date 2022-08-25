#TODO : USE C++ to rewrite this proxy!!!
import requests
from bottle import route, run, Bottle
import random
import time
import json
import os

def save():
    global appdata
    with open("bazorxy.json","w+",encoding="UTF-8") as fp:
        json.dump(appdata,fp)
        fp.close()

def gen(data,code):
    ret = {
        "code":code,
        "data":data
    }
    return json.dumps(ret)

def refresh():
    global appdata
    randf = random.random()
    url_final = "https://api.hypixel.net/skyblock/bazaar" + "?r=" + str(randf)
    req = requests.get(url_final)
    if req.status_code == 304 :
        # No changed
        if 'proxy-json' not in appdata:
            appdata['proxy-json'] = req.json()
        now = time.time()
        appdata['proxy-json']["lastUpdated"] = int(round(now * 1000))
        del now
    elif(req.status_code == 200):
        #data changed
        appdata['proxy-json'] = req.json()
        return
    else:
        assert "Failed to get data from upstream server: " + str(url_final) +" ."
    req.close()
    return

if __name__ != "__main__":
    raise Exception("This program is only runs in console mode.")

app = Bottle()

appdata = {}

@app.route("/")
def readCache():
    global appdata
    now = time.time()
    if 'proxy-json' not in appdata:
        refresh()
        appdata["proxy-str"] = json.dumps(appdata["proxy-json"])
    if int(round(now * 1000)) - int(appdata["proxy-json"]["lastUpdated"]) >= int(appdata["refresh-time"]):
        refresh()
        appdata["proxy-str"] = json.dumps(appdata["proxy-json"])
    if "proxy-str" not in appdata:
        refresh()
        appdata["proxy-str"] = json.dumps(appdata["proxy-json"])
    return appdata["proxy-str"]

@app.route("/admin/<password>/<action>/<argument>/")
def admin(password,action,argument):
    global appdata
    if password == appdata["pwd"]:
        if action == "refresh":
            refresh()
            ret = {
                "msg":"Refreshed."
            }
            return gen(ret,0)
        elif action == "change":
            appdata["pwd"] = argument
            save()
            ret = {
                "msg":"Changed."
            }
            return gen(ret,0)
        elif action == "refreshtime":
            appdata['refresh-time'] = int(argument)
            save()
            ret = {
                "msg":"Done."
            }
            return gen(ret,0)
        else:
            ret = {
                "msg":"Invaild Method."
            }
            return gen(ret,-1)
    else:
        ret = {
            "msg":"Your admin password isn't right."
        }
        return gen(ret,-1)

@app.route("/init/<password>")
def init(password):
    global appdata
    if appdata["pwd"] == "":
        appdata["pwd"] = password
        save()
        ret = {
            "msg":"Successfully Initialized Bazorxy.",
            "password":appdata["pwd"]
        }
        return gen(ret,0)
    else:
        print("Someone want to reinitialize bazorxy.")
        ret = {
            "msg":"You've Already Initialized Bazorxy.",
        }
        return gen(ret,-1)

if not os.path.exists("bazorxy.json"):
    appdata = {
        "pwd":"",
        "proxy-json":{},
        "proxy-str":"",
        "refresh-time":2000
    }
    refresh()
    save()
else:
    with open("bazorxy.json","r",encoding="UTF-8") as fp:
        appdata = json.load(fp)
        fp.close()
run(app, host='localhost', port=8080)