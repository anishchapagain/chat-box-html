from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Store active websocket connections
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("Agent Dashboard Connected. Total:", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("Agent Dashboard Disconnected. Total:", len(self.active_connections))

    async def broadcast(self, message: dict):
        """Send a JSON message to all connected agent dashboards."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending message to websocket: {e}")

manager = ConnectionManager()

@router.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect much *incoming* data from the dashboard via WS initially,
            # mostly it will be listening. Actions (like sending replies) will use standard REST POSTs.
            data = await websocket.receive_text()
            print(f"Received from Dashboard: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)