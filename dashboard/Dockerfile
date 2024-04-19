FROM python:latest

WORKDIR /app

COPY streamlit_app.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD streamlit run main.py