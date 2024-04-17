
FROM python:latest

COPY requirements.txt .
COPY health_checky.py .

RUN pip install -r requirements.txt

CMD python3 health_check.py