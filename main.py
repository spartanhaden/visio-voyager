#!/usr/bin/env python3

from typing import Optional
import tkinter as tk
from tkinter import filedialog
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

    # randomize the order of the files
    import random
    random.shuffle(file_paths)

    return file_paths


@app.get("/test_images/{filename}")
async def serve_images(filename: str):
    return FileResponse(f"test_images/{filename}")


@app.get("/open_directory_dialog")
def open_directory_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory()  # Open the folder dialog
    root.destroy()  # Destroy the main window

    print(f"Selected folder: {folder_selected}")

    return JSONResponse(content={"folder_selected": folder_selected})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6841)
