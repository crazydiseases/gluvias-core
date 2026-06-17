import os
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="GLUVIAS // SPATIAL CONSOLE")

@app.get("/")
async def serve_workspace():
    # Reach up out of the backend folder to target the root index.html file
    return FileResponse("index.html")
