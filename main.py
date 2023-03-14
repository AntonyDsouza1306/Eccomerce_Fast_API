# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 10:36:35 2023

@author: desou
"""
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"Data": "Test"}

if __name__ == "__main__":
    uvicorn.run(app,host='127.0.0.1',port = 8000)

