from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import asyncio
from process_manager import ProcessManager

app = FastAPI(title="Card Sort Control")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    """Serve the frontend application"""
    return FileResponse("static/index.html")

# Create process manager instance
process_manager = ProcessManager()

# WebSocket connections for live updates
active_connections: List[WebSocket] = []

async def broadcast_status():
    """Broadcast status to all connected clients"""
    while True:
        status = process_manager.get_status()
        # Remove closed connections
        for connection in active_connections.copy():
            try:
                await connection.send_json(status)
            except:
                active_connections.remove(connection)
        await asyncio.sleep(1)  # Update every second

@app.on_event("startup")
async def startup_event():
    """Start the status broadcast task when the app starts"""
    asyncio.create_task(broadcast_status())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.post("/process/start")
async def start_process(magazin_name: str, start_index: Optional[int] = 1, home_magazine: Optional[bool] = False):
    """Start the card processing"""
    try:
        process_manager.start_process(
            magazin_name=magazin_name,
            start_index=start_index,
            home_magazine=home_magazine
        )
        return {"status": "started"}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/process/stop")
async def stop_process(emergency: Optional[bool] = False):
    """Stop the current process"""
    process_manager.stop_process(emergency=emergency)
    return {"status": "stopping"}

@app.get("/process/status")
async def get_status():
    """Get current process status"""
    return process_manager.get_status()

@app.post("/csv/export-all")
async def export_all_cards():
    """Export all processed cards to CSV"""
    path = process_manager.export_all_cards_csv()
    return {"csv_path": path}

@app.get("/cards")
async def get_cards(magazin_name: Optional[str] = None):
    """Get list of processed cards, optionally filtered by magazine"""
    cards = process_manager.get_processed_cards(magazin_name)
    return {"cards": cards}