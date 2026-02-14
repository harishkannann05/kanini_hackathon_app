from typing import Dict, Set
from fastapi import WebSocket
import asyncio
import json


class WSManager:
    def __init__(self):
        # doctor_id -> set of websockets
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, doctor_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            if doctor_id not in self.connections:
                self.connections[doctor_id] = set()
            self.connections[doctor_id].add(websocket)

    async def disconnect(self, doctor_id: str, websocket: WebSocket):
        async with self.lock:
            if doctor_id in self.connections and websocket in self.connections[doctor_id]:
                self.connections[doctor_id].remove(websocket)
                if not self.connections[doctor_id]:
                    del self.connections[doctor_id]

    async def broadcast_to_doctor(self, doctor_id: str, message: dict):
        # send JSON message to all websockets for a doctor
        msg_text = json.dumps(message)
        async with self.lock:
            sockets = list(self.connections.get(doctor_id, []))
        for ws in sockets:
            try:
                await ws.send_text(msg_text)
            except Exception:
                # ignore broken sockets
                pass


manager = WSManager()

async def notify_doctor_queue_update(doctor_id: str, payload: dict):
    await manager.broadcast_to_doctor(doctor_id, payload)
