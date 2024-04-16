# 1. Base image
FROM python:latest

# 2. Copy files
COPY requirements.txt .
COPY extract.py .
COPY main.py .

# 3. Install dependencies
RUN pip install -r requirements.txt

CMD python3 main.py