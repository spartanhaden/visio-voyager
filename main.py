#!/usr/bin/env python3

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse('static/index.html')


@app.get("/search")
async def search(request: Request):
    term = request.query_params.get('term', '')
    file_paths = search_files(term)  # Replace this with your actual function
    return JSONResponse(content=file_paths)


def search_files(term):
    print(f"Searching for {term}")

    # Get a list of all files in the test_images directory
    file_paths = os.listdir("test_images")

    # Prepend the directory name to the file names
    file_paths = [os.path.join("test_images", f) for f in file_paths]

    return file_paths


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6841)
