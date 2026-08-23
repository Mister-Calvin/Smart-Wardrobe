import json


def wirte_json(filename, data_to_wirte):
    with open(f"{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data_to_wirte, f, ensure_ascii=False, indent=2)

def load_json(filename):
    with open(f"{filename}.json", "r", encoding="utf-8") as f:
        return json.load(f)







