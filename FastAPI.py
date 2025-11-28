from fastapi import FastAPI
from models import Wardrobe, session

app = FastAPI()

@app.get('/')
def index():
    items = session.query(Wardrobe).all()
    return [item.to_dict() for item in items]

#if __name__ == "__main__":
 #   import uvicorn
  #  uvicorn.run("FastAPI:app", host="127.0.0.1", port=8000, reload=True)

#uvicorn FastAPI:app --reload #start