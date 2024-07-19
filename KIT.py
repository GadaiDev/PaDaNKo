import datetime
from cryptography.fernet import Fernet

def fopen(fname: str):
    return open(fname, "r").read()

def html_render(fname: str):
    return fopen(f"./HTML/{fname}.html")

def zkk():
    b = datetime.datetime.now()
    return [b.year,b.month,b.day,b.hour,b.minute,b.second]

def time_datetime(t):
    return datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])

def datetime_time(b: datetime.datetime):
    return [b.year,b.month,b.day,b.hour,b.minute,b.second]

def create_key():
    return Fernet.generate_key().decode("utf-8")

def encrypt(key: str, data: str):
    fernet = Fernet(bytes(key, 'utf-8'))
    encrypted_pass = fernet.encrypt(bytes(data, 'utf-8'))
    return encrypted_pass.decode('utf-8')


def decrypt(key: str, data: str):
    fernet = Fernet(bytes(key, 'utf-8'))
    decrypted_pass = fernet.decrypt(bytes(data, 'utf-8'))
    return decrypted_pass.decode('utf-8')