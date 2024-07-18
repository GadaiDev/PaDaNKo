from flask import Flask, session, request, redirect
from uuid import uuid4
from datetime import datetime

import KIT

import ipwhois
import glob
import json
import random
import re
import base64

import Feature.OSVAI as OSVAI

def aku_process(text, name, id_, thr):
    if not thr == "root":
        if len(re.findall(r"!aku[0-9]+", text)):
            try:
                for i in re.findall(r"!aku([0-9]+)", text):
                    thr["aku"].append(thr["dat"][int(i[0])-1]["id"])     
                    text += f"\n<span style='color:red'>アク禁　{thr['dat'][int(i[0])-1]['id']}:成功</span>"
            except:
                text += f"\n<span style='color:blue'>アク禁:失敗</span>"
        elif len(re.findall(r"!kaijo[0-9]+", text)):
            try:
                for i in re.findall(r"!kaijo([0-9]+)", text):
                    del thr["aku"][thr["aku"].index(thr["dat"][int(i[0])-1]["id"])]   
                    text += f"\n<span style='color:orange'>アク禁解除　{thr['dat'][int(i[0])-1]['id']}:成功</span>"
            except:
                text += f"\n<span style='color:blue'>アク禁解除:失敗</span>"
    return text, name, id_, thr

def text_replace(text:str):
    text = text.replace("\n","<br>")
    text = re.sub(r"!Img:\"(.+)\"",r"<img src='\1' class='k_img'>", text)
    text = re.sub(r"!Video:\"(.+)\"",r"<video controls src='\1' class='k_img'>", text)
    return text

def post_replace(text:str, name:str, id_, thr):
    for i in range(text.count("!Random")):
        text = text.replace("!Random",f"<b class='k_spc1'>{str(random.randint(0,100))}</b>", 1)

    for i in range(text.count("!Coin")):
        text = text.replace("!Coin",f"<b class='k_spc1'>{random.choice(['裏','表'])}</b>", 1)

    text = text.replace("!Reload", "<button onclick='location.reload()'>リロード</button>")

    if thr == "root":
        ich = text
    else:
        ich = thr["dat"][0]["text"]

    if "!無個性" in ich:
        name = "OSVの名無しさん"
        id_ = "0000"
    
    if "!IP開示" in ich:
        id_ = request.remote_addr
        
    if "!ワッチョイ" in ich:
        
        
        ua_ = request.headers.get("User-Agent")
        
        if "Ubuntu" in ua_:
            ua = "ｳﾌﾞ"
        elif "Mac" in ua_:
            ua = "ｱﾎﾟｰ"
        elif "Windows" in ua_:
            ua = "ﾏﾄﾞ"
        elif "Android" in ua_:
            ua = "ﾄﾞﾛ"
        else:
            ua = "ｲﾐﾌ"
        

        wachoi = json.loads(KIT.fopen("./File/BBSwachoi/wachoi.json"))
        if wachoi.get(request.remote_addr) is None:
            try:
                head = random.Random(ipwhois.IPWhois(request.remote_addr).lookup_rdap()["nir"]["nets"][0]["name"])
            except:
                head = random.Random(request.remote_addr)
            wachoi[request.remote_addr] = ("+"+"".join(head.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
                                            +" "+"".join(random.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
                                            +"-"+"".join(random.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4)))
            json.dump(wachoi, open("./File/BBSwachoi/wachoi.json", "w"), ensure_ascii=False, indent=4)

            id_ += f"[{ua} {wachoi[request.remote_addr]}]"
    if "!AI\n" in text:
        text += "\n\n"+"<b>"+OSVAI.ai_que(text.replace("!AI\n",""))+"</b>"
        
        

    text, name, id_, thr = aku_process(text,name,id_,thr)

    return text, name, id_, thr

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

        text, name, id_, _ = post_replace(text, name, id_, "root")
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
        thr = json.load(open(f"./File/BBS/{thrid}.json", "r"))

        if text != "" and (not session.get("ID","???") in thr.get("aku",[])):
            session["Name"] = name

            if name == "":
                name = "とくめいさん"

            id_ = session.get("ID","???")



            if "!射精" in text:
                thr["Syasei"] = "1"
            elif "!ティッシュ" in text:
                thr["Syasei"] = "0"
            
            if thr.get("aku") is None:
                thr["aku"] = []
            
                                
        
            text, name, id_, thr = post_replace(text, name, id_, thr)
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
        elif len(text) == 0:
            return "テキストの長さが0である場合:投稿は不可能です"
        elif session.get("ID","???") in thr["aku"]:
            return "アクセス禁止処置:投稿は不可能です"
        else:
            return "原因不明のエラー"
            

    @app.route("/bbs/thread/<thrid>")
    def page_bbs_thread(thrid):
        if session.get("ID") is None:
            session["ID"] = "".join(random.choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))

        thr = json.load(open(f"./File/BBS/"+thrid+".json", "r"))
        
        if not request.remote_addr == "2600:3c00::f03c:91ff:fe93:dcd4": #IPv6Proxy.NETのアドレス
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
        if session.get("ID","???") in thr.get("aku",[]):
            thr = json.load(open(f"./File/BBSFile/Aku.json","r"))
        out = []
        
        for i, d in enumerate(thr["dat"]):
            if thr.get("Syasei") == "1":
                out.append(f"<dl><dt style='color:white'><a onclick='addanker({i + 1})'>{i + 1}</a>:<b>{d['name']}</b>, {d['date']}, ID:{d['id']}</dt><dd style='color:white'>{text_replace(d['text'])}</dd></dl>")
            else:
                out.append(f"<dl><dt><a onclick='addanker({i + 1})'>{i + 1}</a>:<b class='k_name'>{d['name']}</b>, {d['date']}, ID:{d['id']}</dt><dd>{text_replace(d['text'])}</dd></dl>")
        
        return f"<h1 class='t_title'>{thr['title']}</h1>\n"+"\n".join(out)

    @app.route("/bbs/api/FUP", methods=["POST"])
    def ev_bbs_apiFUP():
        b64text = request.form.get("B64File", "")
        b64text = re.sub(r"data:[a-zA-Z]+/[a-zA-Z]+;base64,",r"",b64text)
        id_ = "".join(random.choices("0123456789abcdef", k=16))
        if not b64text == "":
            open(f"./File/BBSFile/{id_}","wb").write(base64.b64decode(b64text))
        return f"!Img:\"/File/BBSFile/{id_}\""
    
    @app.route("/robots.txt")
    def robotstxt():
        return """User-agent: *
Disallow: /
Allow: /bbs/"""