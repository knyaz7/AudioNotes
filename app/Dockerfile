FROM python:slim

RUN pip install uv

WORKDIR /app
COPY . ./

RUN uv pip install --no-cache --system -r requirements.lock

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]