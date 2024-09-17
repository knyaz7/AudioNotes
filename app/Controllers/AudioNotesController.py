import os
import uuid
import wave
import g4f
import speech_recognition as sr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.AudioNote import AudioNote
from Schemas.AudioNoteSchema import AudioNoteResponse


class AudioNotesController:
    @staticmethod
    def get_duration(filename):
        with wave.open(filename, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
        return duration

    @staticmethod
    def generate_unique_filename(extension="wav"):
        return f"{uuid.uuid4().hex}.{extension}"

    @staticmethod
    def save_file(file_content: bytes, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file:
            file.write(file_content)

    @staticmethod
    def recognize_audio(file_path: str):
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            try:
                return recognizer.recognize_google(audio_data, language="ru-RU")
            except sr.UnknownValueError:
                return "Речь не распознана"
            except sr.RequestError as e:
                return f"Ошибка при запросе к сервису распознавания; {e}"

    @staticmethod
    async def generate_title_and_description(audio_text: str):
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user",
                           "content": f"На основе этого текста аудиозаписи: '{audio_text}', сгенерируй краткое название и описание аудиозаметки."
                                      f"В первой строке укажи название, во второй строке укажи описание и ничего больше."}],
                stream=True,
            )
            result = "".join([message for message in response])
            split_text = result.split("\n")
            title = split_text[0] if len(split_text) > 0 else "Название"
            description = split_text[1] if len(split_text) > 1 else "Описание"
        except Exception:
            title = "Название по умолчанию"
            description = "Описание по умолчанию"
        return title, description

    @staticmethod
    async def create_note(file_content: bytes, session: AsyncSession):
        # Шаг 1: Генерация уникального имени файла и сохранение файла
        unique_filename = AudioNotesController.generate_unique_filename()
        file_path = os.path.join("audionotes", unique_filename)
        AudioNotesController.save_file(file_content, file_path)

        # Шаг 2: Получение длительности аудио
        duration = AudioNotesController.get_duration(file_path)

        # Шаг 3: Распознавание речи
        audio_text = AudioNotesController.recognize_audio(file_path)

        # Шаг 4: Генерация заголовка и описания на основе текста
        title, description = await AudioNotesController.generate_title_and_description(audio_text)

        # Шаг 5: Сохранение заметки в базе данных
        new_note = AudioNote(
            file_path=file_path,
            title=title,
            description=description,
            duration=duration
        )
        session.add(new_note)
        await session.commit()

        return AudioNoteResponse(
            id=new_note.id,
            title=new_note.title,
            description=new_note.description,
            tags=new_note.tags,
            duration=duration
        )

    @staticmethod
    async def get_notes(session: AsyncSession):
        result = await session.execute(select(AudioNote))
        notes = result.scalars().all()
        return [
            AudioNoteResponse(
                id=note.id, title=note.title, description=note.description,
                tags=note.tags, duration=note.duration
            ).dict() for note in notes
        ]

    @staticmethod
    async def get_note_by_id(note_id: int, session: AsyncSession):
        note = await session.get(AudioNote, note_id)
        if not note:
            raise ValueError(f"Note with id {note_id} not found")
        return note

    @staticmethod
    async def update_note(note_id: int, update_data: dict, session: AsyncSession):
        note = await AudioNotesController.get_note_by_id(note_id, session)

        if "title" in update_data:
            note.title = update_data["title"]
        if "description" in update_data:
            note.description = update_data["description"]
        if "add_tag" in update_data:
            new_tags = set(note.tags or [])  # Используем set для предотвращения дублирования
            new_tags.add(update_data["add_tag"])
            note.tags = list(new_tags)  # Преобразуем обратно в список
        if "delete_tag" in update_data and note.tags:
            new_tags = set(note.tags)  # Используем set для удобства
            new_tags.discard(update_data["delete_tag"])  # Удаляем тег, если он существует
            note.tags = list(new_tags)  # Преобразуем обратно в список

        await session.commit()
        return AudioNoteResponse(id=note.id, title=note.title, description=note.description, tags=note.tags,
                                 duration=note.duration)

    @staticmethod
    async def delete_note(note_id: int, session: AsyncSession):
        note = await AudioNotesController.get_note_by_id(note_id, session)

        # Удаляем файл
        if os.path.exists(str(note.file_path)):
            os.remove(str(note.file_path))

        await session.delete(note)
        await session.commit()
