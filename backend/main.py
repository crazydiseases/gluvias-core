import os
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="GLUVIAS // SPATIAL CONSOLE")

# Dynamically calculate the absolute path to the root directory
# This moves up one level from backend/main.py to find index.html at the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE_DIR, "index.html")

@app.get("/")
async def serve_workspace():
    # Defensive check: if the file somehow isn't there, display a clear error instead of a 404
    if not os.path.exists(HTML_PATH):
        return {"error": f"index.html not found at expected path: {HTML_PATH}"}
        
    return FileResponse(HTML_PATH)
