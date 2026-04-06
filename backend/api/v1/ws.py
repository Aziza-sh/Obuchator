from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.websocket import manager

router = APIRouter()

@router.websocket("/ws/news")
async def websocket_news(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)