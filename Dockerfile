FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/thumbnails

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
