import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="GLUVIAS // SPATIAL CONSOLE")

# 1. Mount the root folder to serve static files (like index.html) seamlessly
# This handles the asset pathing natively across Railway's architecture
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def serve_workspace():
    # Serve index.html straight from the root project directory
    return FileResponse("index.html")
