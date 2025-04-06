from sanic import Sanic, response, json
from sanic.response import json
from sanic_ext import Extend
from db import *
import db as database
from datetime import datetime
import os, uuid
import string
from auth import create_token, decode_token
from telegram_bot import run_bot, bot
from multiprocessing import Process
from sendemail import *
import asyncio
from sanic_cors import CORS
import base64
import random

app = Sanic("CommunicationHub")
Extend(app)
CORS(app, supports_credentials=True)
tokens = {}


@app.middleware("response")
async def add_cors_headers(request, response):
    response.headers["Access-Control-Allow-Origin"] = "http://192.168.0.105:5173"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def authorized(request):
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    token = auth.replace("Bearer ", "")
    return decode_token(token)

@app.post("/files/upload")
async def upload_file(request):
    if "file" not in request.files:
        return response.json({"error": "No file provided"}, status=400)
    file = request.files.get("file")
    original_name = file.name
    unique_filename = f"{uuid.uuid4().hex}_{original_name}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    with open(file_path, "wb") as f:
        f.write(file.body)
    uploader_id = request.json.get("uploader_id", 0)
    add_file_metadata(original_name, unique_filename, file.type, len(file.body), uploader_id)
    return response.json({"message": "File uploaded", "stored_name": unique_filename})

@app.get("/files/<file_id:int>")
async def download_file(request, file_id):
    file_meta = get_file_metadata(file_id)
    if not file_meta:
        return response.json({"error": "File not found"}, status=404)
    stored_name = file_meta[2]  # Поле stored_name
    file_path = os.path.join(UPLOAD_FOLDER, stored_name)
    if not os.path.exists(file_path):
        return response.json({"error": "File not found on server"}, status=404)
    return await response.file(file_path) 


def generatetoken():
    token = base64.b64encode(datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('utf-8')).decode('utf-8')
    return token

def verify_token(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return False
    if authorization_header.startswith('Bearer '):
            bearer_token = authorization_header.split(' ')[1]
    else: return False
    global tokens
    try:
        return tokens[bearer_token]
    except:
        return False
def get_token(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return False
    if authorization_header.startswith('Bearer '):
            bearer_token = authorization_header.split(' ')[1]
    else: return False
    
    return bearer_token

@app.post("/authorization")
async def authorization(request):
    global tokens
    if not request.json:
        return json({"success": False,
                    "message": "Login failed"}, status=401)
    email = request.json.get('email')
    password = request.json.get('password')
    dbresp = database.loginUser(email, password)
    if dbresp:
        token = generatetoken()
        tokens[token]={'email':email,'password':password,"first_name":dbresp[2],"last_name":dbresp[3]}
        return json({"success": True,
                    "message": "Success",
                    "token": token}, status=200)
    else:
        return json({"success": False,
                    "message": "Login failed"}, status=401)

@app.post("/registration")
async def registration(request):
    global tokens
    if not request.json:
        return json({"success": False,
                    "message": "Registration failed"}, status=401)
    email = request.json.get('email')
    password = request.json.get('password')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    message = {}
    if not email:
        message['email'] = 'email cannot be blank'
    if not password:
        message['password'] = 'password cannot be blank'
    if not first_name:
        message['first_name'] = 'first_name cannot be blank'
    if not last_name:
        message['last_name'] = 'last_name cannot be blank'
    if len(message.keys()) > 0:
        return json({"success": False,
                    "message": message}, status=422)
    if not database.createUser(email, password, first_name, last_name):
        return json({"success": False,
                    "message": "Registration failed, email already exists"}, status=500)
    token = generatetoken()
    tokens[token]={'email':email,'password':password,"first_name":first_name, "last_name":last_name}
    return json({"success": True, 'message':'Success', "token": token}, status=200)

@app.get('/login')
async def inventoryPage(request):
    return response.json({"success": True, 'message':'Success'}, status=200)

@app.get("/registration")
async def registrationPage(request):
    return response.json({"success": True, 'message':'Success'}, status=200)

@app.get("/authorization")
async def authorizationPage(request):
    return response.json({"success": True, 'message':'Success'}, status=200)

@app.get('/logout')
async def logout(request):
    if verify_token(request):
        del tokens[get_token(request)]
        return json({"success": True, 'message':'Success'}, status=200)
    else:
        return json({"success": False, 'message':'Unauthorised'}, status=401)

def getrandomstring(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

@app.get("/me")
async def me(request):
    user_id = authorized(request)
    if not user_id:
        return response.json({"error": "Unauthorized"}, status=401)
    return response.json({"user_id": user_id})

@app.post("/users/rename")
async def rename(request):
    data = request.json
    rename_user(data["email"], data["first_name"], data["last_name"])
    return response.json({"message": "User renamed"})

@app.post("/users/telegram")
async def bind_telegram(request):
    data = request.json
    set_telegram(data["email"], data["telegram_id"])
    return response.json({"message": "Telegram ID linked"})

# --------- PROJECTS ---------
#Заглушка
@app.get("/projects/list") # Посылается заброс на сбор проектов с базы
async def getprojs(request):
    result = {
        'id' : {
            1 : {
                "name" : "coolproj"
            }
        }
    }
    return response.json({"response": result}, status=200)

#Конец заглушки
@app.post("/projects")
async def create_proj(request):
    user_id = authorized(request)
    if not user_id:
        return response.json({"error": "Unauthorized"}, status=401)
    data = request.json
    create_project(data["title"], data["description"], data["type"], data["status"], user_id)
    return response.json({"message": "Project created"})

@app.put("/projects/<project_id:int>/status")
async def update_status(request, project_id):
    data = request.json
    update_project_status(project_id, data["status"])
    return response.json({"message": "Project status updated"})

@app.get("/projects/search")
async def search_projects(request):
    query = request.args.get("q", "")
    results = search_projects_by_title(query)
    return response.json({"results": results})

# --------- CHATS ---------

@app.post("/chats")
async def create_chat_api(request):
    data = request.json
    create_chat(data["project_id"], data["title"], data["chat_type"], data["status"])
    return response.json({"message": "Chat created"})

@app.post("/chats/<chat_id:int>/participants")
async def add_participant(request, chat_id):
    data = request.json
    add_user_to_chat(chat_id, data["user_id"], data.get("role", "member"))
    return response.json({"message": "Participant added"})

@app.get("/chats/<project_id:int>")
async def get_chats(request, project_id):
    chat_type = request.args.get("type", "text")
    chats = filter_chats(project_id, chat_type)
    return response.json({"chats": chats})

@app.post("/chats/<chat_id:int>/archive")
async def archive_chat_api(request, chat_id):
    archive_chat(chat_id)
    return response.json({"message": "Chat archived"})

@app.post("/chats/<chat_id:int>/tags")
async def add_tag(request, chat_id):
    data = request.json
    add_tag_to_chat(chat_id, data["tag"])
    return response.json({"message": "Tag added"})

# --------- MESSAGES ---------

@app.post("/messages")
async def send_msg(request):
    data = request.json
    send_message(data["chat_id"], data["sender_id"], data["content"],
                 markdown=data.get("markdown_enabled", False),
                 voice_url=data.get("voice_note_url"),
                 file_url=data.get("file_url"),
                 message_type=data.get("message_type", "text"))
    return response.json({"message": "Message sent"})

@app.get("/messages/<chat_id:int>")
async def get_chat_messages(request, chat_id):
    msgs = get_chat_history(chat_id)
    return response.json({"messages": msgs})

@app.delete("/messages/<message_id:int>")
async def delete_msg(request, message_id):
    data = request.json
    delete_message(message_id, data["sender_id"])
    return response.json({"message": "Message deleted"})

# --------- NOTIFICATIONS ---------

@app.get("/notifications")
async def get_notifications(request):
    user_id = authorized(request)
    if not user_id:
        return response.json({"error": "Unauthorized"}, status=401)
    notes = get_unread_notifications(user_id)
    return response.json({"notifications": notes})

@app.post("/notifications/<notif_id:int>/read")
async def mark_note_read(request, notif_id):
    mark_notification_read(notif_id)
    return response.json({"message": "Notification marked as read"})

@app.post("/notifications")
async def create_note(request):
    data = request.json
    create_notification(data["user_id"], data["content"], data["type"],
                        data["related_type"], data["related_id"])
    return response.json({"message": "Notification created"})

# --------- INTEGRATIONS ---------

@app.post("/integrations")
async def add_integration_api(request):
    user_id = authorized(request)
    if not user_id:
        return response.json({"error": "Unauthorized"}, status=401)
    data = request.json
    add_integration(user_id, data["service"], data["config"])
    return response.json({"message": "Integration saved"})

@app.get("/integrations/<service>")
async def get_integration_api(request, service):
    user_id = authorized(request)
    if not user_id:
        return response.json({"error": "Unauthorized"}, status=401)
    token = get_user_integration(user_id, service)
    return response.json({"config": token})

# --------- TELEGRAM NOTIFICATION ---------
@app.post("/send_telegram_notification")
async def send_telegram_notification(request):
    data = request.json
    email = data.get("email")
    chat_id = get_telegram_chat_id_from_email(email)
    message_text = data.get("message")
    if not chat_id or not message_text:
        return response.json({"error": "Missing chat_id or message"}, status=400)
    try:
        await bot.send_message(chat_id, message_text)
        return response.json({"message": "Telegram notification sent"})
    except Exception as e:
        return response.json({"error": str(e)}, status=500)
    

# --------- EMAIL NOTIFICATION ---------
@app.post("/send_email_notification")
async def send_email_notification(request):
    data = request.json
    email = data.get("email")
    message = data.get("message")
    title_email = data.get("title_email")
    if not email or not message or not title_email:
        return response.json({"error": "Missing email, subject, or body"}, status=400)
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, send_email, title_email, message, email)
        return response.json({"message": "Email notification sent"})
    except Exception as e:
        return response.json({"error": str(e)}, status=500)
    

# --------- CALENDAR NOTIFICATION ---------
@app.post("/send_calendar_event")
async def send_calendar_event(request):
    data = request.json
    user_email = data.get("email")
    summary = data.get("title_event")
    description = data.get("description")
    start_datetime = data.get("start_datetime")
    end_datetime = data.get("end_datetime")
    if not user_email or not summary or not description or not start_datetime or not end_datetime:
        return response.json({"error": "Missing email, title, description, start or end datetime"}, status=400)
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, send_calendar_event, user_email, summary, description, start_datetime, end_datetime)
        return response.json({"message": "Calendar event notification sent"})
    except Exception as e:
        return response.json({"error": str(e)}, status=500)
    

# --------- LAUNCH ---------

@app.listener('after_server_start')
async def start_telegram_bot(app, loop):
    app.add_task(run_bot())

if __name__ == "__main__":
    app.run(host="192.168.0.105", port=8000)


