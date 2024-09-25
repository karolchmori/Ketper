import json
import os

def createFile(filename, information):
    # Convert the selection list to JSON format for easy storage
    with open(filename, 'w') as file:
        json.dump(information, file)

def readFile(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    # Select the objects listed in the file
    return data

def getFileName(filename):
    nameBase = os.path.splitext(os.path.basename(filename))[0]
    return nameBase