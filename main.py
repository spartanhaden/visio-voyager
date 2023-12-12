#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse('static/index.html')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6841)
