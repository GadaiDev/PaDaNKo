def fopen(fname: str):
    return open(fname, "r").read()

def html_render(fname: str):
    return fopen(f"./HTML/{fname}.html")