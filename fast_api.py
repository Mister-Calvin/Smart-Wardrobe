from data_manager import DataManager
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.responses import RedirectResponse
import json
import openai_model1
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/json')
def index():
    manager = DataManager()
    items = manager.get_all_items()
    return [item.to_dict() for item in items]

@app.get("/")
def landingpage(request: Request):
    manager = DataManager()
    items = manager.get_all_items()
    return templates.TemplateResponse("wardrobe.html", {
        "request": request,
        "items": items
    })

@app.get("/items/create")
def show_create_form(request: Request):
    return templates.TemplateResponse("create_item.html", {"request": request})

@app.post("/items/create")
def create_item(name: str = Form(...),
                description: str = Form(...),
                color: str = Form(...),
                condition: str = Form(...),
                type: str = Form(...),
                score: int = Form(...),):
    manager = DataManager()
    manager.create_item(name=name, description=description, color=color, condition=condition, type=type, score=score)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


@app.post("/items/{item_id}/delete")
def delete_item(item_id: int):
    manager = DataManager()
    manager.delete_item(item_id)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@app.get("/items/{item_id}/edit")
def show_edit_formular(request: Request, item_id: int):
    manager = DataManager()
    item = manager.get_item_by_id(item_id)
    return templates.TemplateResponse("update_item.html", {
        "request": request,
        "item": item
    })

@app.post("/items/{item_id}/edit")
def edit_item(item_id: int, name: str = Form(...),
              description: str = Form(...),
              color: str = Form(...),
              condition: str = Form(...),
              type: str = Form(...),
              score: int = Form(...),):
    manager = DataManager()
    manager.update_item(item_id, name=name, description=description, color=color, condition=condition, type=type, score=score)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)



#endpoint der input_for_llm.html wiedergibt mit GET
@app.get("/input")
def show_input_bar(request: Request):
    return templates.TemplateResponse("input_for_llm.html", {"request": request})

from this_is_main import build_outfit
@app.post("/input")
def write_json_from_input(
    request: Request,
    user_input: str = Form(...),
    event_input: str = Form(...),
    location_input: str = Form(...),
    season_input: str = Form(...),
    weather_input: str = Form(...),
    mood_input: str = Form(...),
):
    payload = {
        "user_input": user_input,
        "context": {
            "event_input": event_input,
            "location_input": location_input,
            "season_input": season_input,
            "weather_input": weather_input,
            "mood_input": mood_input,
        },
    }

    build_outfit(payload)

    return RedirectResponse(url="/answer", status_code=HTTP_303_SEE_OTHER)

from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

ANSWER_TXT_PATH = Path("extend_llm_answer.txt")

@app.get("/answer")
def show_answer_page(request: Request):
    answer_text = None
    if ANSWER_TXT_PATH.exists() and ANSWER_TXT_PATH.stat().st_size > 0:
        answer_text = ANSWER_TXT_PATH.read_text(encoding="utf-8")

    return templates.TemplateResponse(
        "answer.html",
        {"request": request, "answer_text": answer_text},
    )







# dann einer der die daten sendet mit POST

#if __name__ == "__main__":
 #   import uvicorn
  #  uvicorn.run("FastAPI:app", host="127.0.0.1", port=8000, reload=True)

#uvicorn main:app --reload #start