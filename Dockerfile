FROM python:3.9-slim-buster
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
ARG REPOSITORY_MONITOR_APP_PK_PEM

RUN echo $REPOSITORY_MONITOR_APP_PK_PEM > /app/utils/repository_monitor_app_pk.pem

EXPOSE 5000
ENV FLASK_APP=app.py
CMD ["quart", "run", "--host", "0.0.0.0"]