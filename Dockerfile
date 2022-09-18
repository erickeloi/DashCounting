FROM python:3.10.7-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8501

COPY streamlit_app.py .
COPY busca_na_api.py .

CMD [ "streamlit", "run", "streamlit_app.py" ]

