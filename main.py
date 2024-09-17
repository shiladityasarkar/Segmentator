import shutil
from fastapi import FastAPI, File, UploadFile, Form, Request, Response
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from mongo import Database
import os

app = FastAPI()
templates = Jinja2Templates(directory='temps')
dbs = Database()

@app.get("/")
def startup(request: Request):
    return templates.TemplateResponse('auth.html', {"request": request})

@app.post("/auth")
def login(request: Request, uname: str = Form(...), pasw: str = Form(...), action: str = Form(...)):
    user = dbs.get_user(uname, pasw)
    if user is not None:
        if action == 'login':
            return templates.TemplateResponse('form.html', {"request": request})
        elif action == 'signup':
            return templates.TemplateResponse('error.html', {"request": request, "error_message": "User already exists!"})
    elif action == 'signup':
        dbs.put_user(uname, pasw)
        return templates.TemplateResponse('sucsin.html', {"request": request})
    return templates.TemplateResponse('error.html', {"request": request, "error_message": "Invalid username or password!!!"}, status_code=401)

@app.post("/imauth")
def imauth(file: UploadFile = File(...), imchoice: str = Form(...)):
    if imchoice == "new":
        try:
            contents = file.file.read()
            with open(file.filename, 'wb') as f:
                f.write(contents)
        except (Exception,):
            return {"message": "There was an error uploading the file"}
        finally:
            resp = dbs.write(file.filename)
            if resp == -1:
                resp = "Reload Session!"
            file.file.close()
            try:
                os.remove(file.filename)
                shutil.rmtree('./temp')
            except FileNotFoundError:
                pass
            return HTMLResponse(resp)
    else:
        img = dbs.read()
        if img is None:
            return HTMLResponse('No previous image!')
        elif img == -1:
            return HTMLResponse('Reload Session!')
        return Response(content=img, media_type="image/jpeg")
