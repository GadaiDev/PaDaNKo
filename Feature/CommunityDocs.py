from flask import Flask, request
from queue import Queue

import KIT



def Register(app: Flask):
    queue = Queue()    
    @app.route("/CommunityDocs/")
    def page_ChatOSV_index():
        return KIT.html_render("CommunityDocs/index")