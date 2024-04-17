FROM python:latest
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY longterm.py .

CMD ["python3", "longterm.py"]