#!/usr/bin/env python3

import time
from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from image_db import ImageDB

image_db_instance = ImageDB()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_image_db_singleton():
    return image_db_instance


@app.get("/")
def read_root():
    return FileResponse('static/index.html')


@app.get("/search")
async def search(request: Request, imagedb: ImageDB = Depends(get_image_db_singleton)):
    term = request.query_params.get('term', '')

    start_time = time.time()
    file_paths = imagedb.search_files(term)
    print(f"searched in {time.time() - start_time} seconds")

    return JSONResponse(content=file_paths)


@app.get("/image/{filename:path}")
async def serve_images(filename: str, imagedb: ImageDB = Depends(get_image_db_singleton)):
    if not imagedb.validate_image(filename):
        # fail
        print(f"Image not found: {filename}")
        return FileResponse('static/404.html')
    print(f"Getting image: {filename}")
    return FileResponse(f"/{filename}")


@app.get("/open_directory_dialog")
def open_directory_dialog(imagedb: ImageDB = Depends(get_image_db_singleton)):
    directory = imagedb.get_directory()

    print(f"Selected folder: {directory}")

    imagedb.index_directory(directory)

    return JSONResponse(content={"folder_selected": directory})


@app.get("/favicon.ico")
async def favicon():
    return FileResponse('static/assets/favicon.png')


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6841)
