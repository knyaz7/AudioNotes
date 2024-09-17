import asyncio
import websockets
import json

async def send_audio_note():
    uri = "ws://localhost:8000/ws"  
    async with websockets.connect(uri) as websocket:
        # Откройте файл и прочитайте его содержимое
        with open("your_file.wav", "rb") as audio_file:
            audio_content = audio_file.read()
        
        # Отправьте запрос на создание заметки
        await websocket.send(json.dumps({"action": "create_note"}))
        
        # Отправьте содержимое файла
        await websocket.send(audio_content)
        
        # Опционально: получите ответ от сервера
        response = await websocket.recv()
        print("Server response:", response)

async def get_notes():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        request = json.dumps({"action": "get_notes"})
        await websocket.send(request)

        async for message in websocket:
            if isinstance(message, bytes):
                notes_data = message.decode('utf-8')
                print("Notes data received:", notes_data)
                break
            else:
                print("Received non-binary message:", message)

async def get_note(note_id):
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri, max_size=10**10) as websocket:  # Увеличьте max_size по необходимости
        request = json.dumps({"action": "get_note", "note_id": note_id}) # Указываем id нужной аудиозаметки
        await websocket.send(request)

        async for message in websocket:
            if isinstance(message, bytes):
                with open("received_audio.wav", "wb") as f:
                    f.write(message)
                print("File received and saved as 'received_audio.wav'")
                break
            else:
                print("Received non-binary message:", message)

async def update_note(note_id):
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        request = {
            "action": "update_note",
            "note_id": note_id,
            "update_data": {
                "add_tag": "test"
            }
        }
        await websocket.send(json.dumps(request))
        
        # Опционально: получите ответ от сервера
        response = await websocket.recv()
        print("Server response:", response)

async def delete_note(note_id):
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        request = json.dumps({"action": "delete_note", "note_id": note_id})
        await websocket.send(request)

        async for message in websocket:
            if isinstance(message, bytes):
                notes_data = message.decode('utf-8')
                print("Notes data received:", notes_data)
                break
            else:
                print("Received non-binary message:", message)

# Запросы в приложение

asyncio.run(send_audio_note()) # Добавление заметки
#asyncio.run(get_notes())  # Получение всех заметок
#asyncio.run(get_note(1)) # Получение заметки по id
#asyncio.run(update_note(1))  # Обновление заметки
#asyncio.run(delete_note(1)) # Удаление заметки

