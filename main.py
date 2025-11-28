from data_manager import DataManager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



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






#if __name__ == "__main__":
 #   import uvicorn
  #  uvicorn.run("FastAPI:app", host="127.0.0.1", port=8000, reload=True)

#uvicorn main:app --reload #start