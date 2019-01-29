import json


def loadJsonFromFile(file_path):
    with open(file_path, "r") as f:
        content = json.load(f)
    return content