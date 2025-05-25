from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
from app.utils.auth import get_current_user_from_ws
from app.schemas.core import UserOut
import datetime

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.history: List[dict] = []

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for ws in self.active_connections.values():
            await ws.send_json(message)

    def save_history(self, message: dict):
        self.history.append(message)
        # Giới hạn lịch sử 1000 tin nhắn gần nhất
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

    def get_history(self, limit: int = 50):
        return self.history[-limit:]

manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    user = await get_current_user_from_ws(websocket)
    if user is None or user.role not in ["admin", "employee", "buyer", "superadmin"]:
        await websocket.close(code=1008)  # Policy Violation
        return
    username = user.username
    await manager.connect(websocket, username)
    # Gửi lịch sử chat cho user mới
    await websocket.send_json({"type": "history", "messages": manager.get_history()})
    try:
        while True:
            data = await websocket.receive_text()
            msg = {
                "type": "chat",
                "user": username,
                "role": user.role,
                "content": data,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            manager.save_history(msg)
            await manager.broadcast(msg)
    except WebSocketDisconnect:
        manager.disconnect(username)
        leave_msg = {
            "type": "system",
            "user": username,
            "role": user.role,
            "content": f"{username} left the chat",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        manager.save_history(leave_msg)
        await manager.broadcast(leave_msg)
