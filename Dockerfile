FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["functions-framework", "--target=voice_to_form", "--source=src/main.py", "--port=8080"]