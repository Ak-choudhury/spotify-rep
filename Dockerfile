FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create default dirs (db + thumbs)
RUN mkdir -p /app/data /app/thumbnails

EXPOSE 5000

# Use gunicorn (better than python run.py in Docker)
RUN pip install --no-cache-dir gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
