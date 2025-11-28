from data_manager import DataManager
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.responses import RedirectResponse



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
def create_item(name: str = Form(...), category: str = Form(...)):
    manager = DataManager()
    manager.create_item(name=name, category=category)
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
def edit_item(item_id: int, name: str = Form(...), category: str = Form(...)):
    manager = DataManager()
    manager.update_item(item_id, name=name, category=category)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)





#if __name__ == "__main__":
 #   import uvicorn
  #  uvicorn.run("FastAPI:app", host="127.0.0.1", port=8000, reload=True)

#uvicorn main:app --reload #start