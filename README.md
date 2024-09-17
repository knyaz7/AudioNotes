# Сервис аудиозаметок

Добро пожаловать в репозиторий проекта сервиса аудиозаметок 

## Описание

Проект представляет собой сервис для записи аудиозаметок с названием, описанием и тегами.

## Файловая система

app/app.py - основной файл бэкенда
`uvicorn app:app`  
Для запуска рекомендуется использовать docker из директории app `docker-compose up --build`

## Реализация бэкенда

#### Архитектура бэкенда:
##### Фреймворк FastAPI
Для работы с базой данных PostGRE используется SQLAlchemy, что обеспечивает удобство и безопасность операций с базой данных.  
В качестве протокола передачи данных выбран WebSockets.

Для проекта выбран архитектурный шаблон MVC. В бэкенде представлены контроллеры и модели, отвечающие принципам модульности и гибкости для обеспечения качества разработки в дальнейшем. Модели, целью которых является взаимодействие с базой данных, отвечают принципам отказоустойчивости.  
Приложение предоставляет функционал конвертации аудио в текст, а также дальнейшую автоматическую генерацию описания и темы аудиозаметки.

