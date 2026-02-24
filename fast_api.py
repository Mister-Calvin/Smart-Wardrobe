from data_manager import DataManager
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from db_filters import filter_db_dynamic, build_filter_kwargs_from_strings
from main import build_outfit
import json
from fastapi import HTTPException
from openai_model import NotEnoughItemsForOutfitError
from fastapi.responses import JSONResponse
from main import build_outfit, BuildOutfitError, HallucinationError
from json_manager import load_json, wirte_json
from agentic_ai import run_agent_from_payload




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


@app.post("/input")
def get_input_and_built_answer(
    request: Request,

    # LLM Input
    user_input: str = Form(...),
    event_input: str = Form(...),
    location_input: str = Form(...),
    season_input: str = Form(...),
    weather_input: str = Form(...),
    mood_input: str = Form(...),

    # Filter Inputs (NEU)
    colors_any: str = Form(""),
    colors_all: str = Form(""),
    score: str = Form(""),
    score_min: str = Form(""),
    score_max: str = Form(""),
    condition_any: str = Form(""),
    name_contains: str = Form(""),
    description_contains: str = Form(""),
    text_all: str = Form(""),
    text_any: str = Form(""),
    limit: str = Form(""),
):
    # 1) Filter kwargs bauen (NUR hier Strings -> kwargs)
    filter_kwargs = build_filter_kwargs_from_strings(
        colors_any=colors_any,
        colors_all=colors_all,
        score=score,
        score_min=score_min,
        score_max=score_max,
        condition_any=condition_any,
        name_contains=name_contains,
        description_contains=description_contains,
        text_all=text_all,
        text_any=text_any,
        limit=limit,
    )

    # 2) IDs filtern
    filtered_ids = filter_db_dynamic(**filter_kwargs)

    if not filtered_ids:
        return templates.TemplateResponse("error.html", {"request": request,
                                                         "message": "Filter liefern gar keine Items - Filter anpassen"})

    if len(filtered_ids) < 5:
        return templates.TemplateResponse("error.html", {"request": request, "message": "nich genügend Items zum Erstellen eines Outfits"})



    with open("fast_api_filter_ids.json", "w", encoding="utf-8") as f:
        json.dump(filtered_ids, f, ensure_ascii=False, indent=2)

        #liefert die tatsächlichen ids nach den Filtern - funktioniert also

    #hier würde nun die ausfürhung von agentic_ai kommen:
    payload_for_agentic = {
        "weather": "kalt",
        "event_type": "Büro",
        "mood": "minimalistisch",
    }
    state = run_agent_from_payload(weather_input=weather_input, event_input=event_input, mood_input=mood_input)


    # 3) Payload wie gehabt + filtered_ids ergänzen
    payload = {
        "user_input": user_input,
        "context": {
            "event_input": event_input,
            "location_input": location_input,
            "season_input": season_input,
            "weather_input": weather_input,
            "mood_input": mood_input,
            "styling_hints": state["style_hints"],
        }
    }
    wirte_json(data_to_wirte=payload, filename="fastapi_payload")
    # 4) Pipeline starten
    answer_text = build_outfit(payload, filtered_ids)

    return templates.TemplateResponse(
        "answer.html",
        {
            "request": request,
            "answer_text": answer_text,
        },
    )

@app.exception_handler(NotEnoughItemsForOutfitError)
async def handle_not_enough_items(request: Request, text: NotEnoughItemsForOutfitError):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": str(text)},
        status_code=422,
    )

@app.exception_handler(HallucinationError)
async def handle_hallucination(request: Request, exc: HallucinationError):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": str(exc)},
        status_code=422,
    )


@app.exception_handler(BuildOutfitError)
async def handle_build_outfit(request: Request, exc: BuildOutfitError):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": str(exc)},
        status_code=500,
    )



# dann einer der die daten sendet mit POST

#if __name__ == "__main__":
 #   import uvicorn
  #  uvicorn.run("FastAPI:app", host="127.0.0.1", port=8000, reload=True)

#uvicorn main:app --reload #start