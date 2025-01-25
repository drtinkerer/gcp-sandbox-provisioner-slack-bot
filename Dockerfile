FROM python:3.12-slim

COPY ./app /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["python3", "/app/main.py"]
