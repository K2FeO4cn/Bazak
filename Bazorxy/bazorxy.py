#TODO : USE C++ to rewrite this proxy!!!
import requests
from bottle import route, run, Bottle,response,request
import random
import time
import json
import os
import threading 

def save():
    global appdata
    with open("bazorxy.json","w+",encoding="UTF-8") as fp:
        d1 = appdata["strt"] 
        d2 = appdata["strp"]
        appdata["strt"] = "[placehoder]"
        appdata["strp"] = "[placehoder]"
        json.dump(appdata,fp)
        appdata["strt"] = d1
        appdata["strp"] = d2
        fp.close()

def gen(data,code):
    ret = {
        "code":code,
        "data":data
    }
    return json.dumps(ret)

def trefresh():
    randf = random.random()
    url_final = "https://api.hypixel.net/skyblock/bazaar" + "?r=" + str(randf)
    try:
        req = requests.get(url_final)
        if req.status_code == 200 or req.status_code == 304 :
            ret = req.json()
            print("Successfully Refresh Proxy Cache:",ret["lastUpdated"])
        else:
            print("Failed to get data from upstream server: " + str(url_final) +".")
            ret = {}
        req.close()
    except:
        print("Failed to get data from upstream server: " + str(url_final) +".")
        ret = {"success":False,"bazorxy":"Upstream Server Lost Response."}
    
    ret["proxy"] = "bazorxy"
    return ret

def thread_refresh():
    global appdata
    while True:
        appdata["session-lock"] = True
        appdata["strt"] = json.dumps(trefresh())
        appdata["session-lock"] = False
        appdata["strp"] = appdata["strt"]
        time.sleep(appdata["refresh-time"] / 1000)

if __name__ != "__main__":
    raise Exception("This program is only runs in console mode.")

app = Bottle()

appdata = {}

@app.route("/skyblock/bazaar")#Suits Old API
@app.route("/")
def readCache():
    global appdata
    response.content_type = "application/json; charset=UTF-8"
    if appdata['session-lock']:
        return appdata['strp']
    return appdata['strt']

@app.route("/admin/<password>/<action>/<argument>/")
def admin(password,action,argument):
    global appdata
    response.content_type = "application/json; charset=UTF-8"
    action = action.lower()
    if password == appdata["pwd"]:
        if action == "refresh":
            appdata["session-lock"] = True
            appdata["strt"] = json.dumps(trefresh())
            appdata["session-lock"] = False
            appdata["strp"] = appdata["strt"]
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
        elif action == "save":
            save()
            ret = {
                "msg":"Server Saved."
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
    response.content_type = "application/json; charset=UTF-8"
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


@app.hook('before_request')
def validate():
    REQUEST_METHOD = request.environ.get('REQUEST_METHOD')
 
    HTTP_ACCESS_CONTROL_REQUEST_METHOD = request.environ.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD')
    if REQUEST_METHOD == 'OPTIONS' and HTTP_ACCESS_CONTROL_REQUEST_METHOD:
        request.environ['REQUEST_METHOD'] = HTTP_ACCESS_CONTROL_REQUEST_METHOD
 
 
@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Server'] = 'bazorxy'

if not os.path.exists("bazorxy.json"):
    appdata = {
        "pwd":"",
        # "proxy-json":{},
        "strt":"",
        "strp":"",
        "refresh-time":2000,
        "session-lock":False
    }
    # refresh()
    appdata["session-lock"] = True
    appdata["strt"] = json.dumps(trefresh())
    appdata["session-lock"] = False
    appdata["strp"] = appdata["strt"]
    save()
else:
    with open("bazorxy.json","r",encoding="UTF-8") as fp:
        appdata = json.load(fp)
        appdata['session-lock'] = False
        appdata['strp'] = "{\"success\":false,\"bazorxy\":\"Requiring data.\",\"porxy\":\"Bazorxy\"}"
        appdata['strt'] = "{\"success\":false,\"bazorxy\":\"Requiring data.\",\"porxy\":\"Bazorxy\"}"
        fp.close()

t = threading.Thread(target=thread_refresh)
t.start()
run(app, host='0.0.0.0', port=8080)