FROM ubuntu:latest

WORKDIR /app

COPY    requirements.txt \
        streamlit_app.py \
        busca_na_api.py \
        ./

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y python3 python3-pip \
    && pip install upgrade-pip \
    && pip install -r requirements.txt 

EXPOSE 8501

CMD [ "streamlit", "run", "streamlit_app.py" ]
