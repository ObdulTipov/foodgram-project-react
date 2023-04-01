FROM python:3.7-slim

WORKDIR /app

RUN pip install --upgrade pip --no-cache-dir

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]