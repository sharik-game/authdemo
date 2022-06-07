# FastAPI server
import base64
import hmac
import hashlib
import json

from typing import Optional
from fastapi import FastAPI, Form, Cookie, Body
from fastapi.responses import Response
app = FastAPI()
SECRET_KEY = "50ce6e9c88355a20620e208cc82c71ff33508be6b460c04290bb4460320d6b6b"
PASSWORD_SALT = "b130a864015e8dd4c23784a314e6e6f54720f8d1695f49a5ee044c565fdafa2d"
def sign_data(data: str) -> str:
    """Возвращаем подписанные данные"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()
def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sing = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sing):
        return username
def verify_password(username, password: str) -> bool:
    password_hash = hashlib.sha256( (password + PASSWORD_SALT).encode() )\
        .hexdigest().lower()
    stored_password_hash = users[username]["password"].lower()
        
    return password_hash == stored_password_hash

users = {
    "vova@user.com": {
        "name": "Вова",
        "password": "7f56f97d9c62bf7d7a33fa8391b833131615f07c9011124c335d4f268221c8f9",
        "balance": 900_000
    },
    "masha@user.com": {
        "name": "Маша",
        "password": "b78797e7318ffb88c4b999c394331de35ed6849bb1adb455945a8b5602f1447f",
        "balance": 1_0
    }
}
@app.get("/")
def index_page(username : Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as file_html:
        login_page = file_html.read()
    if not username:
        return Response(login_page, media_type="text/html")
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    return Response(
        f"Привет, {users[valid_username]['name']}!<br />"
        f"Баланс: {users[valid_username]['balance']}",
        media_type="text/html")
        
    
print("yes")
@app.post("/login")
def process_login_page(data: dict = Body(...)):
    print(data)
    username = data["username"]
    password = data["password"]
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response(
            json.dumps({
                "success": False,
                "message": "Я вас не знаю!"
            }),
            media_type="application/json") 
    response = Response(
        json.dumps({
            "success": True,
            "message": f"Привет, {user['name']}!<br />Баланс: {user['balance']}"
        }),
        media_type='application/json'
    )
    username_signed = base64.b64encode(username.encode()).decode() + "." + \
        sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response
