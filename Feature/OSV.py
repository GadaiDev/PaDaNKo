from flask import Flask, session, request, redirect

from uuid import uuid4
from datetime import datetime


import KIT
import glob
import json
import random
import re



def text_replace(text:str):
    text = text.replace("\n","<br>")
    text = re.sub(r"!Img:\"(.+)\"",r"<img src='\1' class='k_img'>", text)
    return text

def post_replace(text:str, name:str, id_, thr):
    for i in range(text.count("!Random")):
        text = text.replace("!Random",f"<b class='k_spc1'>{str(random.randint(0,100))}</b>", 1)

    for i in range(text.count("!Coin")):
        text = text.replace("!Coin",f"<b class='k_spc1'>{random.choice(['裏','表'])}</b>", 1)

    if thr == "root":
        ich = text
    else:
        ich = thr["dat"][0]["text"]

    if "!無個性" in ich:
        name = "OSVの名無しさん"
        id_ = "0000"
    
    if "!IP開示" in ich:
        id_ = request.remote_addr
        
    if "!ワッチョイ" in ich or "!ワッチョイ" in text:
        
        ua_ = request.headers.get("User-Agent")
        
        if "Ubuntu" in ua_:
            ua = "ｳﾌﾞ"
        elif "Mac" in ua_:
            ua = "ｱﾎﾟｰ"
        elif "Windows" in ua_:
            ua = "ﾏﾄﾞ"
        
        
        
        wachoi = json.loads(KIT.fopen("./File/BBSwachoi/wachoi.json"))
        if wachoi.get(request.remote_addr) is None:
            wachoi[request.remote_addr] = ("+"+"".join(random.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
                                            +" "+"".join(random.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
                                            +"-"+"".join(random.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4)))

        id_ += f"[{ua} {wachoi[request.remote_addr]}]"
        json.dump(wachoi, open("./File/BBSwachoi/wachoi.json", "w"))

    return text, name, id_

def Register(app: Flask):
    
    @app.route("/bbs/")
    def page_BBS_index():
        if session.get("ID") is None:
            session["ID"] = "".join(random.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
        
        html = KIT.html_render("OSV/index")
        thrl = []
        
        for i in glob.glob("./File/BBS/*.json"):
            thr = json.load(open(i, "r"))
            tid = i.replace('./File/BBS/','').replace('.json','')
            thrl.append(f"        <a href='/bbs/thread/{tid}'>{thr['title']}({len(thr['dat'])})</a><a href='/bbs/thread/{tid}?Proxy'>[P]</a>")
        
        html = html.replace("{{ Name }}",session.get("Name",""))
        return html.replace("{{ thi }}", "<br>\n".join(thrl))
    
    @app.route("/bbs/thrMake", methods=["POST"])
    def ev_bbs_postthread():
        thrid = str(uuid4())
        name = request.form.get("name","名無しさん").replace(">","&gt;").replace("<","&lt;")
        session["Name"] = name
        text = request.form.get("text","NoneType").replace(">","&gt;").replace("<","&lt;")
        title = request.form.get("title","[私はタイトルを入れられない馬鹿です]").replace(">","&gt;").replace("<","&lt;")

        if name == "":
            name = "とくめいさん"

        if title == "":
            title = "[私はタイトルを入れられない馬鹿です]"


        id_ = session.get("ID","???")

        text, name, id_ = post_replace(text, name, id_, "root")
        now = datetime.now()
        thr = {}
        thr["title"] = title
        thr["dat"] = [
            {
                "name": name,
                "date": f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}",
                "id": id_,
                "text": text 
            }
        ]
        json.dump(thr, open(f"./File/BBS/{thrid}.json", "w"), indent=4, ensure_ascii=False)
        return redirect("/bbs/thread/"+thrid)

    @app.route("/bbs/api/post", methods=["POST"])
    def ev_bbs_apipost():
        thrid = request.form.get("thrID","").replace("/","").replace("..","")
        name = request.form.get("name","名無しさん").replace(">","&gt;").replace("<","&lt;")
        text = request.form.get("text","NoneType").replace(">","&gt;").replace("<","&lt;")

        if text != "":
            session["Name"] = name

            if name == "":
                name = "とくめいさん"

            id_ = session.get("ID","???")


            thr = json.load(open(f"./File/BBS/{thrid}.json", "r"))

            text, name, id_ = post_replace(text, name, id_, thr)
            now = datetime.now()
            thr["dat"].append(
                {
                    "name": name,
                    "date": f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}",
                    "id": id_,
                    "text": text 
                }
            )
            json.dump(thr, open(f"./File/BBS/{thrid}.json", "w"), indent=4, ensure_ascii=False)
        return "ok"

    @app.route("/bbs/thread/<thrid>")
    def page_bbs_thread(thrid):
        if session.get("ID") is None:
            session["ID"] = "".join(random.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))

        thr = json.load(open(f"./File/BBS/"+thrid+".json", "r"))
        
        if not request.remote_addr == "2600:3c00::f03c:91ff:fe93:dcd4":
            html = KIT.html_render("OSV/thread")
        else:
            html = KIT.html_render("OSV/threadP")
        html = html.replace("{{ ttl }}", thr["title"])

        html = html.replace("{{ thrid }}", thrid)
        html = html.replace("{{ Name }}",session.get("Name",""))
        return html
    
    @app.route("/bbs/api/get")
    def ev_bbs_apiget():
        thrid = request.args.get("thrID","").replace("/","").replace("..","")
        thr = json.load(open(f"./File/BBS/{thrid}.json", "r"))

        out = []
        
        for i, d in enumerate(thr["dat"]):
            if thr["dat"][0]["id"] == d["id"]:
                out.append(f"<dl><dt><a onclick='addanker({i + 1})'>{i + 1}</a>:<b class='k_name'>{d['name']}</b>, {d['date']}, <b class='t_title'>ID:{d['id']}</b></dt><dd>{text_replace(d['text'])}</dd></dl>")
            else:
                out.append(f"<dl><dt><a onclick='addanker({i + 1})'>{i + 1}</a>:<b class='k_name'>{d['name']}</b>, {d['date']}, ID:{d['id']}</dt><dd>{text_replace(d['text'])}</dd></dl>")
        
        return f"<h1 class='t_title'>{thr['title']}</h1>\n"+"\n".join(out)
