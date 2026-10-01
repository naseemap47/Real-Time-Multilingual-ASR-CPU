import os
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import router as api_router
from src.api.call_leg_manager import CallLegManager
from src.api.websocket_handler import handle_asr_websocket

app = FastAPI(
    title="Real-Time Multilingual ASR on CPU API",
    description="Decoupled streaming speech recognition service for Qwen3-ASR, Parakeet TDT, Moonshine, and Whisper Turbo.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = CallLegManager()
app.include_router(api_router)


@app.websocket("/ws/asr")
async def websocket_asr_endpoint(websocket: WebSocket):
    await handle_asr_websocket(websocket, session_manager)


# Serve static web UI files if present
web_ui_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web_ui")
if os.path.exists(web_ui_path):
    app.mount("/ui", StaticFiles(directory=web_ui_path, html=True), name="web_ui")


if __name__ == "__main__":
    import uvicorn
    print("ASR UI: http://localhost:8000/ui")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)