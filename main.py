from data_manager import DataManager
from models import Wardrobe, session
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get('/json')
def index():
    items = session.query(Wardrobe).all()
    return [item.to_dict() for item in items]

@app.get("/")
def landingpage(request: Request):
    items = session.query(Wardrobe).all()
    return templates.TemplateResponse("wardrobe.html", {
        "request": request,
        "items": items
    })






#if __name__ == "__main__":
 #   import uvicorn
  #  uvicorn.run("FastAPI:app", host="127.0.0.1", port=8000, reload=True)

#uvicorn main:app --reload #start