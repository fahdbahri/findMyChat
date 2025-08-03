FROM python:3.10.17

WORKDIR /app

RUN pip install --upgrade pip



COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
