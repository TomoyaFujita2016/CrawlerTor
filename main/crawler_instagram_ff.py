import requests
import os
from datetime import datetime
import time
import re
import functools
import json
from bs4 import BeautifulSoup
import threading
from logging import (getLogger, StreamHandler, INFO, Formatter)

# log config
handler = StreamHandler()
handler.setLevel(INFO)
handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
logger = getLogger()
logger.addHandler(handler)
logger.setLevel(INFO)

# const
SAVE_FREQ = 10
SLEEP_SEC = 100
USER_FILE = "../res/userid/users"
USERDATA_FILE = "../res/userff/"
PORTS_DIR = "../tools/ports"
INSTA_URL = "https://www.instagram.com/"
JSON_STRING = 'window\._sharedData = '
JSON_END = "};"
TAG_FOLLOW = "edge_follow"
TAG_FOLLOWER = "edge_followed_by"
TAG_TIMELINE = "edge_owner_to_timeline_media"
TAG_COUNT = "count"
TAGS_PARENT = ["graphql", "user"]

# values
THREAD_COUNT = 10 #tmp init
SAVER_ACTIVE = False
users = []
users_d = []
threads = []
ports = []
sessions = []
user_data = {}

def getUserIds():
    global users
    with open(USER_FILE, "r") as f:
        for row in f:
            users.append(row.replace("\n", ""))
    print("Reading the user file was Successfully!")

def getHTML(url, thread_num):
    global sleep_thread_num
    global SLEEP_CHECK
    FLAG_GO = False
    while not FLAG_GO:
        try:
            time.sleep(1)
            result = sessions[thread_num].get(url)
            # TODO Also support other status codes
            # TODO Restart tor when a request gets 429
            
            if result.status_code == 429:
                logger.info("sleep for 429")
                time.sleep(60)
            elif result.status_code == 404:
                logger.info("NOT FOUND!")
            else:
                FLAG_GO = True
            
        except:
            logger.info("\033[31mAn Error occured!\033[0m"+ url + "\n")
            return ""
    return result.text

def getPorts():
    global ports, THREAD_COUNT
    with open(PORTS_DIR, "r") as f:
        lines = f.readlines()
    for line in lines:
        ports.append(line.split(" ")[0])
    THREAD_COUNT = len(ports)

def initSessions():
    global sessions
    for i in range(THREAD_COUNT):
        session = requests.session()
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:' + ports[i]
        session.proxies['https'] = 'socks5h://localhost:' + ports[i]
        sessions.append(session)

def initEvent():
    global event
    event = threading.Event()

def divideUsers():
    global users_d
    q = len(users) // THREAD_COUNT
    m = len(users) % THREAD_COUNT

    users_d = functools.reduce(
        lambda acc, i:
            (lambda fr = sum([ len(x) for x in acc ]):
                acc + [ users[fr:(fr + q + (1 if i < m else 0))] ]
            )()
        ,
        range(THREAD_COUNT),
        []
    )


def filteringFF(text):
    data = re.search(JSON_STRING, text)
    jsonData = json.loads(text[data.span()[1]:text.find(JSON_END)+1])
    try:
        user = jsonData["entry_data"]["ProfilePage"][0][TAGS_PARENT[0]][TAGS_PARENT[1]]
    except:
        logger.info(jsonData["entry_data"])
        return {TAG_TIMELINE: -1, TAG_FOLLOW: -1, TAG_FOLLOWER: -1}
    return {TAG_TIMELINE: int(user[TAG_TIMELINE][TAG_COUNT]), TAG_FOLLOW: int(user[TAG_FOLLOW][TAG_COUNT]), TAG_FOLLOWER: int(user[TAG_FOLLOWER][TAG_COUNT])}

def saveHandler(userDict, num):
    global SAVER_ACTIVE
    global user_data
    while SAVER_ACTIVE:
        pass
    SAVER_ACTIVE = True
    user_data.update(userDict)
    saveUserData()
    logger.info("SAVED!")
    SAVER_ACTIVE = False 

def getIp(thread_num):
    result = sessions[thread_num].get("http://httpbin.org/ip")
    jsonData = json.loads(result.text)
    logger.info("ip: " + str(jsonData["origin"]))

def work(users_dt, thread_num):
    userData = {}
    getIp(thread_num)
    for i, user in enumerate(users_dt):
        if getHTML(INSTA_URL + user + "/", thread_num) == "":
            userData[user] = {TAG_TIMELINE: -1, TAG_FOLLOW: -1, TAG_FOLLOWER:-1}
        else:
            userData[user] = filteringFF(getHTML(INSTA_URL + user + "/", thread_num))
        # log
        # This if is for avoiding to divide by zero
        if len(users_dt) < 100:
            logger.info(str(100*i/len(users_dt)) + "% " + str(user) + " post:" + str(userData[user][TAG_TIMELINE]) + " follow:" + str(userData[user][TAG_FOLLOW]) + " follower:" + str(userData[user][TAG_FOLLOWER]))
            pass
        else:
            if i % (len(users_dt)//100) == 0:
                logger.info(str(100*i/len(users_dt)) + "% " + str(user) + " post:" + str(userData[user][TAG_TIMELINE]) + " follow:" + str(userData[user][TAG_FOLLOW]) + " follower:" + str(userData[user][TAG_FOLLOWER]))

        if i != 0 and i % SAVE_FREQ == 0:
            saveHandler(userData, thread_num)
            # initialize to append new dict
            userData = {}

    saveHandler(userData, thread_num)
    logger.info("SAVED!")

def generateWorkers():
    for i in range(THREAD_COUNT):
        t = threading.Thread(target=work, args=(users_d[i], i))
        threads.append(t)
        t.start()

def saveUserData():
    with open(USERDATA_FILE, "w") as f:
        for username in user_data.keys():
            f.write(username  + "," + str(user_data[username][TAG_TIMELINE]) + "," + str(user_data[username][TAG_FOLLOW]) + "," + str(user_data[username][TAG_FOLLOWER]) + "\n")

def setupDir():
    global USERDATA_FILE
    USERDATA_FILE += "{0:%Y%m%d_%H%M.csv}".format(datetime.now())
    filePath = os.path.dirname(USERDATA_FILE)
    if not os.path.exists(filePath):
        os.makedirs(filePath)

if __name__=="__main__":
    setupDir()
    getPorts()
    initSessions()
    getUserIds()
    divideUsers()
    generateWorkers()
