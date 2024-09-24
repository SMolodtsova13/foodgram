FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt ./

RUN pip install -r requirements.txt --no-cache-dir

COPY ./ ./

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]