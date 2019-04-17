import json
import string
import random


def loadJsonFromFile(file_path):
    with open(file_path, "r") as f:
        content = json.load(f)
    return content

def getRandomName(prefix="", suffix="", length=6):
    name = "".join([random.choice(string.ascii_lowercase) for i in range(length)])
    if prefix:
        name = "".join([prefix, name])
    if suffix:
        name = "".join([name, suffix])
    return name

def getRandomInt(min_int=0, max_int=100):
    return random.randint(min_int, max_int)

def fileObject(filePath):
    return open(filePath, "rb")

def getNone():
    return None