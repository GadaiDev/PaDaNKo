from flask import Flask, send_file
import KIT

from Feature import OSV

app = Flask(__name__)
app.secret_key = "Secret!"

@app.route("/")
def page_index():
    return KIT.html_render("index")

@app.route("/File/<path:path>")
def page_path(path):
    return send_file(f"./File/{path}")

OSV.Register(app)

app.run("::", 80, True)