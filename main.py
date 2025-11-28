from data_manager import DataManager
from models import Base, Wardrobe, session
from flask import Flask, jsonify

app = Flask(__name__)



@app.route('/')
def index():
    items = session.query(Wardrobe).all()
    return jsonify([item.to_dict() for item in items])


if __name__ == '__main__':
    app.run(debug=True, port=5001)

