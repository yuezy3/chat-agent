from fastapi import FastAPI
from pydantic import BaseModel
from tinydb import TinyDB, Query

from datetime import datetime
from datetime import timezone
from datetime import timedelta
import os
import openai
from dotenv import load_dotenv
load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")
db = TinyDB('chat-db.json')
Chat = Query() # {chatid:str, msgs:[], lastmodify:date, isnew: True}

class Chatreq(BaseModel):
    chatid: str
    msg: str

app = FastAPI()

def createChatMsg(chatreq: Chatreq):
    utcfmtstr = "%Y-%m-%d %H:%M:%S.%f%z"
    usermsg = {"role": "user", "content":f"{chatreq.msg}"}
    msgs = []
    isnew = True
    if db.contains(Chat.chatid == chatreq.chatid):
        lastmodify = datetime.strptime((db.get(Chat.chatid == chatreq.chatid))["lastmodify"], utcfmtstr)
        if datetime.now(timezone.utc) - lastmodify > timedelta(minutes=30) : # 30 minutes ago
            msgs = [{"role": "system", "content": "You are a helpful assistant."}, usermsg]
            isnew = False
        else:
            msgs = (db.get(Chat.chatid == chatreq.chatid))["msgs"] + [usermsg]
            isnew = True
    else:
        msgs = [{"role": "system", "content": "You are a helpful assistant."}, usermsg]
        isnew = True
    db.upsert({"chatid":chatreq.chatid, "msgs":msgs, "isnew":isnew, "lastmodify":datetime.now(timezone.utc).strftime(utcfmtstr)}, Chat.chatid == chatreq.chatid)
    return msgs
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/chat")
async def make_chat(chatreq: Chatreq):
    print(f"get {chatreq}")
    msgs = createChatMsg(chatreq)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msgs,
        temperature=0.8
    )
    return {"chatid":chatreq.chatid, "msg":response['choices'][0]['message']['content']}
