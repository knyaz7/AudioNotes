import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from Controllers.AudioNotesController import AudioNotesController
from ConnectionManager import ConnectionManager

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
    """
        Вебсокет для взаимодействия с аудиозаметками.

        - **action**: Действие, которое клиент хочет выполнить. Возможные значения:
          - "create_note": Создание новой аудиозаметки.
          - "get_notes": Получение списка всех заметок.
          - "get_note": Получение конкретной заметки по ID.
          - "update_note": Обновление заметки.
          - "delete_note": Удаление заметки.
        - **file_content**: Данные аудиофайла для создания заметки (только для "create_note").
        - **note_id**: ID заметки (требуется для "get_note", "update_note", "delete_note").
        - **update_data**: Данные для обновления заметки (только для "update_note").
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "create_note":
                file_content = await websocket.receive_bytes()
                note_response = await AudioNotesController.create_note(file_content, session)
                await manager.send_message({"action": "note_created", "data": note_response.dict()}, websocket)

            elif action == "get_notes":
                notes_response = await AudioNotesController.get_notes(session)
                await manager.send_message({"action": "notes_list", "data": notes_response}, websocket)

            elif action == "get_note":
                note_id = data.get("note_id")
                try:
                    note = await AudioNotesController.get_note_by_id(note_id, session)
                    if os.path.exists(str(note.file_path)):
                        with open(str(note.file_path), "rb") as file:
                            file_content = file.read()
                        await websocket.send_bytes(file_content)
                    else:
                        await manager.send_message({"action": "error", "message": "File not found"}, websocket)
                except ValueError as e:
                    await manager.send_message({"action": "error", "message": str(e)}, websocket)

            elif action == "update_note":
                note_id = data.get("note_id")
                update_data = data.get("update_data", {})
                try:
                    note_response = await AudioNotesController.update_note(note_id, update_data, session)
                    await manager.send_message({"action": "note_updated", "data": note_response.dict()}, websocket)
                except ValueError as e:
                    await manager.send_message({"action": "error", "message": str(e)}, websocket)

            elif action == "delete_note":
                note_id = data.get("note_id")
                try:
                    await AudioNotesController.delete_note(note_id, session)
                    await manager.send_message({"action": "note_deleted", "id": note_id}, websocket)
                except ValueError as e:
                    await manager.send_message({"action": "error", "message": str(e)}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
