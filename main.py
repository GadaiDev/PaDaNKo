from flask import Flask, send_file

import KIT

import sys
from Feature import OSV

app = Flask(__name__)
app.secret_key = "1919"

@app.route("/")
def page_index():
    return KIT.html_render("index")

@app.route("/File/<path:path>")
def page_path(path):
    return send_file(f"./File/{path}")

OSV.Register(app)

app.run(sys.argv[1], int(sys.argv[2]), True)